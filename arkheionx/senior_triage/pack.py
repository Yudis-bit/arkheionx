"""Build the Senior Triage Pack (v2) — orchestrates every senior-triage step.

Order: review map -> v2 corpus -> eligibility -> leads -> semantic dedup v2 ->
freshness v2 -> read-only deployment reality -> per-lead deployment effect ->
scoring v2 (with fail-closed caps) -> target decision -> render -> JSON. Local/static
only: no RPC by default, no live-chain mutation, no auto-submit, human review required.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.version import PACKAGE_VERSION

from . import corpus_v2 as cv2
from . import dedup_v2
from . import deployment as deploy
from . import eligibility as elig
from . import freshness_v2 as fresh2
from . import leads as lead_gen
from . import models as M
from . import render
from . import scoring

SAFETY_FLAGS = {
    "no_rpc_by_default": True,
    "no_live_chain": True,
    "no_exploit_automation": True,
    "no_auto_submit": True,
    "no_vulnerability_claims": True,
    "no_severity_claims": True,
    "human_review_required": True,
}

SAFETY_BOUNDARIES = (
    "Local/static heuristic triage. Not a finding, not severity, not a confirmed vulnerability.",
    "A research-priority score orders attention; it does not prove validity.",
    "No RPC by default; only read-only RPC when --rpc-url is explicitly provided. No private keys, no transactions, no mutation.",
    "No exploit automation and no auto-submit.",
    "Dedup, freshness, and deployment reality are heuristic; a deployment mismatch is a priority signal, not a bug. Human review is required.",
)

_TRUSTED_WORDS = ("trusted", "admin", "owner", "governance", "guardian", "privileged", "role")

_DEPLOY_EFFECT = {
    M.DEPLOY_IMPLEMENTATION_CHANGED: 95,
    M.DEPLOY_LIVE_SOURCE_MISMATCH: 95,
    M.DEPLOY_REGISTRY_CHANGED: 90,
    M.DEPLOY_ORACLE_CHANGED: 90,
    M.DEPLOY_ADDRESS_NO_CODE: 10,
    M.DEPLOY_PAUSED_OR_DISABLED: 20,
    M.DEPLOY_LIVE_SOURCE_MATCH: 35,
    "CODE_PRESENT": 55,
    M.DEPLOY_RPC_CHECK_FAILED: 45,
}


def default_triage_dir(root: Path | str) -> Path:
    return Path(root) / ".arkheionx" / "triage"


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _mask_endpoint(raw: str) -> str:
    from .deployment_rpc import mask_endpoint
    return mask_endpoint(raw)


def _read_scope(scope_file: str) -> str:
    if not scope_file:
        return ""
    path = Path(scope_file).expanduser()
    try:
        return path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""
    except OSError:
        return ""


def _trusted_role_oos(eligibility: M.EligibilitySignal) -> bool:
    for line in eligibility.oos_traps:
        if any(word in line.lower() for word in _TRUSTED_WORDS):
            return True
    for line in eligibility.trusted_role_traps:
        low = line.lower()
        if any(m in low for m in ("out of scope", "out-of-scope", "excluded", "not in scope", "invalid", "ineligible")):
            return True
    return False


def _deployment_effect(lead: M.LeadCandidate, deployment: M.DeploymentRealitySignal) -> tuple:
    """Map deployment results onto a single lead (effect score, status, notes)."""
    if not deployment.results:
        return 50, "", []
    contract = lead.surface.split(".")[0].lower()
    for res in deployment.results:
        name = str(res.get("name", "")).lower()
        if not contract or contract not in name and name not in contract:
            continue
        status = res.get("status", "")
        score = _DEPLOY_EFFECT.get(status, 50)
        notes = []
        if status in (M.DEPLOY_IMPLEMENTATION_CHANGED, M.DEPLOY_LIVE_SOURCE_MISMATCH):
            notes.append(f"Deployed implementation differs from expected ({res.get('expected_implementation','?')} -> {res.get('implementation','?')}).")
        elif status == M.DEPLOY_ADDRESS_NO_CODE:
            notes.append("No code at the expected deployment address.")
        elif status == M.DEPLOY_LIVE_SOURCE_MATCH:
            notes.append("Live implementation matches the expected (audited) implementation.")
        return score, status, notes
    return 50, "", []


def _target_decision(eligibility, leads):
    pursue = [x for x in leads if x.decision == M.LEAD_PURSUE]
    park = [x for x in leads if x.decision == M.LEAD_PARK]
    if not eligibility.scope_provided:
        return M.TargetDecision(
            decision=M.TARGET_NEEDS_CONTEXT, confidence=M.CONF_LOW,
            reason="No scope file; eligibility cannot be confirmed. Local technical leads are ranked, but the target decision needs program context.",
        )
    if pursue:
        top = max(x.research_priority_score for x in pursue)
        return M.TargetDecision(
            decision=M.TARGET_TOUCH, confidence=M.CONF_HIGH if top >= 85 else M.CONF_MEDIUM,
            reason=f"{len(pursue)} lead(s) clear the pursue bar; touch only those and kill the rest.",
        )
    if park:
        return M.TargetDecision(
            decision=M.TARGET_NEEDS_CONTEXT, confidence=M.CONF_MEDIUM,
            reason="Leads exist but need dedup, freshness, deployment, or proof context before they are worth touching.",
        )
    return M.TargetDecision(
        decision=M.TARGET_SKIP, confidence=M.CONF_MEDIUM,
        reason="No lead clears the bar — too duplicate-prone, too stale/over-audited, or out of scope. Skip for now.",
    )


def _do_not_touch_item(lead: M.LeadCandidate) -> dict:
    status = lead.dedup_status
    mapping = {
        M.KNOWN_OUT_OF_SCOPE: ("OUT_OF_SCOPE", "Scope excludes this surface (trusted role or explicit exclusion).", "A scope change that brings this surface in scope."),
        M.KNOWN_PUBLIC_TEST: ("PUBLIC_TEST_COVERED", "A public/local test already exercises this behavior.", "A fresh, implementation-specific variant after the latest test/audit with no public coverage."),
        M.KNOWN_LIKELY_DUP: ("LIKELY_DUPLICATE", "Same surface and behavior appear in known/audit material.", "A fresh post-audit path with unique accounting and no public coverage."),
        M.KNOWN_ACK_RISK: ("ACKNOWLEDGED_RISK", "Found near an acknowledged / by-design / won't-fix note.", "Evidence the accepted behavior is violated under realistic in-scope conditions."),
        M.KNOWN_DOCUMENTED: ("DOCUMENTED_BEHAVIOR", "Behavior is documented in the repository as expected.", "Evidence the documented behavior is violated for attacker profit."),
        M.KNOWN_TRUSTED_ROLE: ("TRUSTED_ROLE_ONLY", "Reachable only through a trusted/privileged role.", "A non-privileged path to the same effect, or scope that rewards trusted-role abuse."),
    }
    if lead.deployment_status == M.DEPLOY_ADDRESS_NO_CODE:
        reason, blocking, change = ("ADDRESS_NO_CODE", "No code at the expected deployment address.", "A live deployment with code at the in-scope address.")
    elif status in mapping:
        reason, blocking, change = mapping[status]
    elif lead.freshness_status == M.STALE:
        reason, blocking, change = ("STALE_AND_OVER_AUDITED", "Stale, heavily audited surface with no fresh change.", "A fresh change to this surface after the last audit.")
    elif lead.materiality_score < 50:
        reason, blocking, change = ("LOW_MATERIALITY", "Little or no value moves through this surface.", "A value-bearing path or accounting impact on this surface.")
    elif lead.attacker_reachability_score <= 40:
        reason, blocking, change = ("NO_ATTACKER_REACHABILITY", "No external-attacker path reaches this surface.", "An externally reachable entry point to the same effect.")
    else:
        reason, blocking, change = ("NO_CLEAR_PROOF_PATH", "No clear local proof path within reasonable time cost.", "A concrete, low-cost local proof path.")
    return {"id": lead.id, "title": lead.title, "reason": reason,
            "blocking_factor": blocking, "what_would_change": change}


def _guard_no_forbidden(blobs: list) -> None:
    haystack = "\n".join(blobs)
    for term in M.FORBIDDEN_OUTCOME_TERMS:
        if term in haystack:
            raise ValueError(f"senior_triage guard: forbidden outcome term emitted: {term}")


def build_senior_triage_pack(
    root: Path | str,
    *,
    scope_file: str = "",
    known_path: str = "",
    audits_path: str = "",
    addresses_file: str = "",
    baseline_ref: str = "",
    since_date: str = "",
    rpc_endpoint: str = "",
    deployment_calls=None,
    rpc_transport=None,
    out_dir: Path | str | None = None,
    command: str = "",
    write: bool = True,
    strict_context: bool = False,
    top: int = M.TOP_LEAD_LIMIT,
    max_leads: int = M.RAW_LEAD_LIMIT,
) -> dict:
    root = Path(root)
    out = Path(out_dir).expanduser() if out_dir else default_triage_dir(root)
    rpc_provided = bool((rpc_endpoint or "").strip())
    rpc_mode = "read_only" if rpc_provided else "not_provided"
    masked = _mask_endpoint(rpc_endpoint)
    top = max(1, min(int(top or M.TOP_LEAD_LIMIT), 5))
    max_leads = max(1, min(int(max_leads or M.RAW_LEAD_LIMIT), 50))

    ctx = M.TriageContext(
        repo_path=str(root), command=command or f"triage {root}",
        scope_file=scope_file or "", known_path=known_path or "", audits_path=audits_path or "",
        addresses_file=addresses_file or "", baseline_ref=baseline_ref or "", since_date=since_date or "",
        rpc_mode=rpc_mode, rpc_endpoint_masked=masked, out_dir=str(out),
    )

    scope_text = _read_scope(scope_file)
    corpus = cv2.build_corpus(ctx, root)
    known_docs = [d for d in corpus if d.kind in ("known", "audit")]
    corpus_provided = bool(known_path or audits_path)

    eligibility = elig.assess_eligibility(ctx, scope_text, known_docs)
    rm = build_review_map(root)
    leads = lead_gen.generate_leads(rm)[:max_leads]
    trusted_role_oos = _trusted_role_oos(eligibility)

    deployment = deploy.assess_deployment(
        ctx, rpc_endpoint=rpc_endpoint, deployment_calls=deployment_calls, transport=rpc_transport,
    )
    rpc_ran = deployment.status == M.DEPLOY_RPC_READ_ONLY_CHECKED

    fresh_signals = fresh2.assess_freshness(ctx, root, leads, corpus)
    fresh_by_id = {f.lead_id: f for f in fresh_signals}

    caps_context = {
        "scope_provided": eligibility.scope_provided,
        "known_provided": corpus_provided,
        "addresses_provided": bool(addresses_file),
        "baseline_provided": bool(baseline_ref or since_date or known_docs),
        "rpc_ran": rpc_ran,
    }

    known_map: list = []
    for lead in leads:
        known = dedup_v2.classify(lead, corpus, trusted_role_oos=trusted_role_oos, corpus_provided=corpus_provided)
        known_map.append(known)
        deploy_score, deploy_status, deploy_notes = _deployment_effect(lead, deployment)
        lead.deployment_notes = deploy_notes
        freshness_signal = fresh_by_id.get(lead.id, M.FreshnessSignal(lead_id=lead.id))
        scoring.apply_score(
            lead, eligibility, known, freshness_signal, repo=str(root), scope_file=scope_file or "",
            deployment_score=deploy_score, deployment_status=deploy_status,
            strict_context=strict_context, caps_context=caps_context,
        )

    order = {M.LEAD_PURSUE: 0, M.LEAD_PARK: 1, M.LEAD_KILL: 2}
    leads.sort(key=lambda x: (-x.research_priority_score, order.get(x.decision, 9), x.id))

    target = _target_decision(eligibility, leads)
    do_not_touch: list = []
    seen: set = set()
    for lead in leads:
        if lead.decision == M.LEAD_KILL or lead.dedup_status in M.KNOWN_BLOCKING or lead.deployment_status == M.DEPLOY_ADDRESS_NO_CODE:
            if lead.id not in seen:
                seen.add(lead.id)
                do_not_touch.append(_do_not_touch_item(lead))

    missing_context = list(eligibility.missing_context)
    if deployment.status == M.DEPLOY_NOT_RUN and not addresses_file:
        missing_context.append("Deployed addresses (--addresses) for a deployment-reality plan.")
    if not rpc_ran and addresses_file:
        missing_context.append("Read-only RPC (--rpc-url) to verify live deployment vs source.")
    if not corpus_provided:
        missing_context.append("Known/audit material (--known/--audits): dedup confidence is LOW.")

    counts = {
        "leads": len(leads),
        "pursue": sum(1 for x in leads if x.decision == M.LEAD_PURSUE),
        "park": sum(1 for x in leads if x.decision == M.LEAD_PARK),
        "kill": sum(1 for x in leads if x.decision == M.LEAD_KILL),
        "do_not_touch": len(do_not_touch),
        "deployment_mismatches": len(deployment.mismatches),
        "top_leads": min(sum(1 for x in leads if x.decision in (M.LEAD_PURSUE, M.LEAD_PARK)), top),
    }

    pack = M.SeniorTriagePack(
        context=ctx, generated_at=_now(), arkheionx_version=PACKAGE_VERSION,
        target_decision=target, eligibility=eligibility, deployment_reality=deployment,
        leads=leads, known_issue_map=known_map, freshness_diff=fresh_signals,
        do_not_touch=do_not_touch, missing_context=missing_context, counts=counts,
    )

    contents = render.render_all(pack)
    triage_json = _build_triage_json(pack, corpus, top)
    manifest = _build_manifest(pack)
    _guard_no_forbidden(list(contents.values()) + [json.dumps(triage_json), json.dumps(manifest)])

    artifact_paths = list(render.ARTIFACT_ORDER) + ["triage.json", "manifest.json"]
    written: dict = {}
    if write:
        out.mkdir(parents=True, exist_ok=True)
        for name, text in contents.items():
            (out / name).write_text(text, encoding="utf-8")
            written[name] = str(out / name)
        written["triage.json"] = _write_json(out / "triage.json", triage_json)
        written["manifest.json"] = _write_json(out / "manifest.json", manifest)

    return {
        "out_dir": str(out), "manifest": manifest, "triage": triage_json, "contents": contents,
        "artifacts": written, "artifact_paths": artifact_paths, "counts": counts, "pack": pack,
    }


def _build_triage_json(pack: M.SeniorTriagePack, corpus: list, top: int) -> dict:
    ctx = pack.context
    return {
        "schema_version": M.SCHEMA_VERSION,
        "artifact_type": M.ARTIFACT_TYPE,
        "arkheionx_version": pack.arkheionx_version,
        "generated_at": pack.generated_at,
        "command": M.COMMAND,
        "repo_path": ctx.repo_path,
        "scope_file": ctx.scope_file,
        "known_path": ctx.known_path,
        "audits_path": ctx.audits_path,
        "addresses_file": ctx.addresses_file,
        "rpc_mode": ctx.rpc_mode,
        "rpc_enabled": False,
        "rpc_endpoint_masked": ctx.rpc_endpoint_masked,
        "target_decision": pack.target_decision.decision,
        "target_confidence": pack.target_decision.confidence,
        "target_reason": pack.target_decision.reason,
        "eligibility": pack.eligibility.to_dict(),
        "corpus_documents": [d.to_record() for d in corpus][:40],
        "known_issue_map": [k.to_dict() for k in pack.known_issue_map],
        "freshness_diff": [f.to_dict() for f in pack.freshness_diff],
        "deployment_reality": pack.deployment_reality.to_dict(),
        "deployment_mismatches": pack.deployment_reality.mismatches,
        "lead_scoreboard": [lead.to_dict() for lead in pack.leads],
        "top_3_leads": [lead.to_dict() for lead in pack.top_leads(3)],
        "top_leads": [lead.to_dict() for lead in pack.top_leads(top)],
        "do_not_touch": pack.do_not_touch,
        "missing_context": pack.missing_context,
        "counts": pack.counts,
        "safety_flags": dict(SAFETY_FLAGS),
        "safety_boundaries": list(SAFETY_BOUNDARIES),
        "human_review_required": True,
    }


def _build_manifest(pack: M.SeniorTriagePack) -> dict:
    ctx = pack.context
    artifact_paths = list(render.ARTIFACT_ORDER) + ["triage.json", "manifest.json"]
    return {
        "schema_version": M.SCHEMA_VERSION,
        "artifact_type": "senior_triage_manifest",
        "arkheionx_version": pack.arkheionx_version,
        "command": M.COMMAND,
        "repo_path": ctx.repo_path,
        "scope_file": ctx.scope_file,
        "known_path": ctx.known_path,
        "audits_path": ctx.audits_path,
        "addresses_file": ctx.addresses_file,
        "generated_at": pack.generated_at,
        "artifact_count": len(artifact_paths),
        "artifact_paths": artifact_paths,
        "rpc_mode": ctx.rpc_mode,
        "rpc_endpoint_masked": ctx.rpc_endpoint_masked,
        "safety_flags": dict(SAFETY_FLAGS),
        "safety_boundaries": list(SAFETY_BOUNDARIES),
        "human_review_required": True,
        "local_only": True,
        "no_push": True,
        "no_remote_write": True,
    }


def _write_json(path: Path, payload: dict) -> str:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(path)
