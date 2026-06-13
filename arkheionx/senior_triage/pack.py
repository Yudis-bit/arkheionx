"""Build the Senior Triage Pack — orchestrates every senior-triage step.

Order: review map -> eligibility -> leads -> known-issue dedup -> freshness ->
scoring/decision -> deployment reality -> target decision -> render -> JSON. Writes a
local pack under ``.arkheionx/triage`` by default. Local/static only: no RPC by
default, no live-chain calls, no auto-submit, human review required.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.version import PACKAGE_VERSION

from . import deployment as deploy
from . import eligibility as elig
from . import freshness as fresh
from . import known_issues as ki
from . import leads as lead_gen
from . import models as M
from . import render
from . import scoring
from .corpus import collect_known_corpus, collect_repo_corpus

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
    "No RPC by default, no live-chain calls, no transaction execution, no private keys.",
    "No exploit automation and no auto-submit.",
    "Dedup, freshness, and eligibility are heuristic; human review is required for every call.",
)

_TRUSTED_WORDS = ("trusted", "admin", "owner", "governance", "guardian", "privileged", "role")


def default_triage_dir(root: Path | str) -> Path:
    return Path(root) / ".arkheionx" / "triage"


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _mask_endpoint(raw: str) -> str:
    if not raw:
        return ""
    raw = raw.strip()
    scheme = raw.split("://", 1)[0] if "://" in raw else "endpoint"
    return f"{scheme}://***masked***"


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
        low = line.lower()
        if any(word in low for word in _TRUSTED_WORDS):
            return True
    # An explicit trusted-role exclusion line also counts.
    for line in eligibility.trusted_role_traps:
        low = line.lower()
        if "out of scope" in low or "out-of-scope" in low or "excluded" in low or "not in scope" in low:
            return True
    return False


def _target_decision(eligibility: M.EligibilitySignal, leads: list[M.LeadCandidate]) -> M.TargetDecision:
    pursue = [x for x in leads if x.decision == M.LEAD_PURSUE]
    park = [x for x in leads if x.decision == M.LEAD_PARK]
    if not eligibility.scope_provided:
        return M.TargetDecision(
            decision=M.TARGET_NEEDS_CONTEXT,
            confidence=M.CONF_LOW,
            reason="No scope file; eligibility cannot be confirmed. Local technical leads are ranked, but the target decision needs program context.",
        )
    if pursue:
        top = max(x.research_priority_score for x in pursue)
        conf = M.CONF_HIGH if top >= 85 else M.CONF_MEDIUM
        return M.TargetDecision(
            decision=M.TARGET_TOUCH,
            confidence=conf,
            reason=f"{len(pursue)} lead(s) clear the pursue bar; touch only those and kill the rest.",
        )
    if park:
        return M.TargetDecision(
            decision=M.TARGET_NEEDS_CONTEXT,
            confidence=M.CONF_MEDIUM,
            reason="Leads exist but need dedup, freshness, or proof context before they are worth touching.",
        )
    return M.TargetDecision(
        decision=M.TARGET_SKIP,
        confidence=M.CONF_MEDIUM,
        reason="No lead clears the bar — too duplicate-prone, too stale/over-audited, or out of scope. Skip for now.",
    )


def _do_not_touch_item(lead: M.LeadCandidate) -> dict:
    status = lead.dedup_status
    mapping = {
        M.KNOWN_OUT_OF_SCOPE: (
            "OUT_OF_SCOPE",
            "Scope excludes this surface (trusted role or explicit exclusion).",
            "A scope change that brings this surface in scope.",
        ),
        M.KNOWN_PUBLIC_TEST: (
            "PUBLIC_TEST_COVERED",
            "A public/local test already exercises this behavior.",
            "A fresh, implementation-specific variant after the latest test/audit with no public coverage.",
        ),
        M.KNOWN_LIKELY_DUP: (
            "LIKELY_DUPLICATE",
            "Same surface and behavior appear in known/audit material.",
            "A fresh post-audit path with unique accounting and no public coverage.",
        ),
        M.KNOWN_ACK_RISK: (
            "ACKNOWLEDGED_RISK",
            "Found near an acknowledged / by-design / won't-fix note.",
            "Evidence the accepted behavior is violated under realistic in-scope conditions.",
        ),
        M.KNOWN_DOCUMENTED: (
            "DOCUMENTED_BEHAVIOR",
            "Behavior is documented in the repository as expected.",
            "Evidence the documented behavior is violated for attacker profit.",
        ),
        M.KNOWN_TRUSTED_ROLE: (
            "TRUSTED_ROLE_ONLY",
            "Reachable only through a trusted/privileged role.",
            "A non-privileged path to the same effect, or scope that rewards trusted-role abuse.",
        ),
    }
    if status in mapping:
        reason, blocking, change = mapping[status]
    elif lead.freshness_status == M.STALE:
        reason, blocking, change = (
            "STALE_AND_OVER_AUDITED",
            "Stale, heavily audited surface with no fresh change.",
            "A fresh change to this surface after the last audit.",
        )
    elif lead.materiality_score < 50:
        reason, blocking, change = (
            "LOW_MATERIALITY",
            "Little or no value moves through this surface.",
            "A value-bearing path or accounting impact on this surface.",
        )
    elif lead.attacker_reachability_score <= 40:
        reason, blocking, change = (
            "NO_ATTACKER_REACHABILITY",
            "No external-attacker path reaches this surface.",
            "An externally reachable entry point to the same effect.",
        )
    else:
        reason, blocking, change = (
            "NO_CLEAR_PROOF_PATH",
            "No clear local proof path within reasonable time cost.",
            "A concrete, low-cost local proof path.",
        )
    return {
        "id": lead.id,
        "title": lead.title,
        "reason": reason,
        "blocking_factor": blocking,
        "what_would_change": change,
    }


def _guard_no_forbidden(blobs: list[str]) -> None:
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
    out_dir: Path | str | None = None,
    command: str = "",
    write: bool = True,
) -> dict:
    root = Path(root)
    out = Path(out_dir).expanduser() if out_dir else default_triage_dir(root)
    rpc_provided = bool((rpc_endpoint or "").strip())
    rpc_mode = "provided_not_run" if rpc_provided else "not_provided"
    masked = _mask_endpoint(rpc_endpoint)

    ctx = M.TriageContext(
        repo_path=str(root),
        command=command or f"triage {root}",
        scope_file=scope_file or "",
        known_path=known_path or "",
        audits_path=audits_path or "",
        addresses_file=addresses_file or "",
        baseline_ref=baseline_ref or "",
        since_date=since_date or "",
        rpc_mode=rpc_mode,
        rpc_endpoint_masked=masked,
        out_dir=str(out),
    )

    scope_text = _read_scope(scope_file)
    known_docs = collect_known_corpus(known_path, audits_path)
    repo_docs = collect_repo_corpus(root)
    docs = known_docs + repo_docs
    corpus_provided = bool(known_path or audits_path)

    eligibility = elig.assess_eligibility(ctx, scope_text, known_docs)

    rm = build_review_map(root)
    leads = lead_gen.generate_leads(rm)

    trusted_role_oos = _trusted_role_oos(eligibility)

    known_map: list[M.KnownIssueSignal] = []
    fresh_signals = fresh.assess_freshness(ctx, root, leads, docs)
    fresh_by_id = {f.lead_id: f for f in fresh_signals}

    for lead in leads:
        known = ki.map_known_issue(
            lead, docs, trusted_role_oos=trusted_role_oos, corpus_provided=corpus_provided
        )
        known_map.append(known)
        freshness_signal = fresh_by_id.get(lead.id, M.FreshnessSignal(lead_id=lead.id))
        scoring.apply_score(
            lead, eligibility, known, freshness_signal,
            repo=str(root), scope_file=scope_file or "",
        )

    # Stable senior ordering.
    order = {M.LEAD_PURSUE: 0, M.LEAD_PARK: 1, M.LEAD_KILL: 2}
    leads.sort(key=lambda x: (-x.research_priority_score, order.get(x.decision, 9), x.id))

    deployment = deploy.assess_deployment(ctx)
    target = _target_decision(eligibility, leads)

    do_not_touch = [
        _do_not_touch_item(lead)
        for lead in leads
        if lead.decision == M.LEAD_KILL or lead.dedup_status in M.KNOWN_BLOCKING
    ]
    # De-duplicate by id, keep order.
    seen: set[str] = set()
    do_not_touch = [d for d in do_not_touch if not (d["id"] in seen or seen.add(d["id"]))]

    missing_context = list(eligibility.missing_context)
    if deployment.status == M.DEPLOY_NOT_RUN and not addresses_file:
        missing_context.append("Deployed addresses (--addresses) for a deployment-reality plan.")

    counts = {
        "leads": len(leads),
        "pursue": sum(1 for x in leads if x.decision == M.LEAD_PURSUE),
        "park": sum(1 for x in leads if x.decision == M.LEAD_PARK),
        "kill": sum(1 for x in leads if x.decision == M.LEAD_KILL),
        "do_not_touch": len(do_not_touch),
        "top_leads": min(
            sum(1 for x in leads if x.decision in (M.LEAD_PURSUE, M.LEAD_PARK)), M.TOP_LEAD_LIMIT
        ),
    }

    pack = M.SeniorTriagePack(
        context=ctx,
        generated_at=_now(),
        arkheionx_version=PACKAGE_VERSION,
        target_decision=target,
        eligibility=eligibility,
        deployment_reality=deployment,
        leads=leads,
        known_issue_map=known_map,
        freshness_diff=fresh_signals,
        do_not_touch=do_not_touch,
        missing_context=missing_context,
        counts=counts,
    )

    contents = render.render_all(pack)
    triage_json = _build_triage_json(pack)
    manifest = _build_manifest(pack)

    # Safety net: no forbidden outcome wording may ever reach an artifact.
    _guard_no_forbidden(list(contents.values()) + [json.dumps(triage_json), json.dumps(manifest)])

    artifact_paths = list(render.ARTIFACT_ORDER) + ["triage.json", "manifest.json"]
    written: dict[str, str] = {}
    if write:
        out.mkdir(parents=True, exist_ok=True)
        for name, text in contents.items():
            (out / name).write_text(text, encoding="utf-8")
            written[name] = str(out / name)
        written["triage.json"] = _write_json(out / "triage.json", triage_json)
        written["manifest.json"] = _write_json(out / "manifest.json", manifest)

    return {
        "out_dir": str(out),
        "manifest": manifest,
        "triage": triage_json,
        "contents": contents,
        "artifacts": written,
        "artifact_paths": artifact_paths,
        "counts": counts,
        "pack": pack,
    }


def _build_triage_json(pack: M.SeniorTriagePack) -> dict:
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
        "known_issue_map": [k.to_dict() for k in pack.known_issue_map],
        "freshness_diff": [f.to_dict() for f in pack.freshness_diff],
        "deployment_reality": pack.deployment_reality.to_dict(),
        "lead_scoreboard": [lead.to_dict() for lead in pack.leads],
        "top_3_leads": [lead.to_dict() for lead in pack.top_leads()],
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
