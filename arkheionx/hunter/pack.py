"""Build the V9 hunter pack — orchestrates every hunter engine.

Order: addresses (parser v2) -> corpus -> review map -> program identity -> source
recovery -> dedup quality -> value-flow / state-machine / call-graph -> deployment
reality -> live registry diff -> senior leads -> per-lead dedup + freshness -> hunter
leads -> decision policy / scoring -> PoC plans -> submission risk -> report filter ->
engine evaluation -> render -> JSON. Local/static; read-only RPC only when explicitly
provided; no live-chain mutation; no auto-submit; human review required.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.senior_triage import corpus_v2 as cv2
from arkheionx.senior_triage import leads as senior_leads_mod
from arkheionx.senior_triage.deployment_rpc import mask_endpoint
from arkheionx.version import PACKAGE_VERSION

from . import addresses as addr_mod
from . import call_graph
from . import dedup_quality
from . import deployment as deploy_mod
from . import engine_eval
from . import freshness as fresh_mod
from . import identity
from . import lane_templates
from . import leads as lead_builder
from . import models as M
from . import poc_planner
from . import registry_diff as registry_mod
from . import render
from . import report_filter as rf_mod
from . import scoring
from . import source_recovery
from . import source_scan
from . import state_machine
from . import submission_risk
from . import value_flow
from .deployment import deployment_status_for_contract

SAFETY_FLAGS = {
    "no_live_chain_mutation": True,
    "read_only_rpc_only": True,
    "rpc_opt_in": True,
    "endpoint_masked": True,
    "no_auto_submit": True,
    "no_exploit_automation": True,
    "no_signing_keys": True,
    "no_vulnerability_claims": True,
    "no_severity_claims": True,
    "human_review_required": True,
}

SAFETY_BOUNDARIES = (
    "Local-first senior research decision engine. Not a finding, not a severity, not a confirmed vulnerability.",
    "A research-priority score and decision order attention; they do not prove validity or payout.",
    "No RPC by default; only read-only methods (eth_chainId/eth_getCode/eth_getStorageAt/eth_call) when --rpc-url is given.",
    "No transactions, no signing, no private keys, no live-chain mutation, no auto-submit, no exploitation.",
    "Endpoints are masked everywhere. Dedup/freshness/deployment are heuristic. A human makes the final call.",
)

_TRUSTED_WORDS = ("trusted", "admin", "owner", "governance", "guardian", "operator",
                  "privileged", "centralization", "multisig", "timelock", "role")
_OOS_MARKERS = ("out of scope", "out-of-scope", "excluded", "not in scope", "ineligible",
                "not rewarded", "will not be rewarded")


def default_hunter_dir(root: Path | str) -> Path:
    return Path(root) / ".arkheionx" / "hunter"


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _read_scope(scope_file: str) -> str:
    if not scope_file:
        return ""
    path = Path(scope_file).expanduser()
    try:
        return path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""
    except OSError:
        return ""


def _trusted_role_oos(scope_text: str) -> bool:
    for raw in (scope_text or "").splitlines():
        low = raw.lower()
        if any(t in low for t in _TRUSTED_WORDS) and any(m in low for m in _OOS_MARKERS):
            return True
    return False


def _overall_freshness(leads: list) -> str:
    for lead in leads:
        if lead.freshness_status in M.FRESHNESS_POSITIVE:
            return lead.freshness_status
    for lead in leads:
        if lead.freshness_status == M.AUDIT_COVERED:
            return M.AUDIT_COVERED
    return leads[0].freshness_status if leads else M.FRESHNESS_UNKNOWN


def _guard_no_forbidden(blobs: list) -> None:
    haystack = "\n".join(blobs)
    for term in M.FORBIDDEN_OUTCOME_TERMS:
        if term in haystack:
            raise ValueError(f"hunter guard: forbidden outcome term emitted: {term}")


def build_hunter_pack(
    root: Path | str,
    *,
    scope_file: str = "",
    known_path: str = "",
    audits_path: str = "",
    addresses_file: str = "",
    source_dir: str = "",
    baseline_ref: str = "",
    since_date: str = "",
    audit_date: str = "",
    fresh_allowlist=None,
    source_recovery_mode: str = "auto",
    rpc_endpoint: str = "",
    deployment_calls=None,
    registry_calls=None,
    rpc_transport=None,
    source_fetcher=None,
    out_dir: Path | str | None = None,
    command: str = "hunter",
    write: bool = True,
    strict_context: bool = False,
    top: int = M.TOP_LEAD_LIMIT,
    max_leads: int = M.RAW_LEAD_LIMIT,
) -> dict:
    root = Path(root)
    out = Path(out_dir).expanduser() if out_dir else default_hunter_dir(root)
    rpc_provided = bool((rpc_endpoint or "").strip())
    rpc_mode = M.READ_ONLY_RPC_ENABLED if rpc_provided else M.RPC_NOT_PROVIDED
    top = max(1, min(int(top or M.TOP_LEAD_LIMIT), M.TOP_LEAD_LIMIT))
    max_leads = max(1, min(int(max_leads or M.RAW_LEAD_LIMIT), 50))
    fresh_allowlist = list(fresh_allowlist or [])

    ctx = M.HunterContext(
        repo_path=str(root), command=command,
        scope_file=scope_file or "", known_path=known_path or "", audits_path=audits_path or "",
        addresses_file=addresses_file or "", source_dir=source_dir or "",
        baseline_ref=baseline_ref or "", since_date=since_date or "", audit_date=audit_date or "",
        fresh_allowlist=fresh_allowlist, source_recovery_mode=source_recovery_mode or "auto",
        rpc_mode=rpc_mode, rpc_endpoint_masked=mask_endpoint(rpc_endpoint),
        strict_context=strict_context, out_dir=str(out),
    )

    # --- inputs -------------------------------------------------------------
    scope_text = _read_scope(scope_file)
    address_parse = addr_mod.parse_addresses(addresses_file)
    corpus = cv2.build_corpus(ctx, root)
    rm = build_review_map(root)
    contract_names = [c.name for c in (getattr(rm, "contracts", []) or [])]

    program_identity = identity.build_program_identity(scope_text, address_parse, contract_names, corpus)
    source_provenance = source_recovery.recover_sources(ctx, root, address_parse, contract_names, fetcher=source_fetcher)
    known_provided, audits_provided = bool(known_path), bool(audits_path)
    dq = dedup_quality.assess_dedup_quality(corpus, known_provided=known_provided, audits_provided=audits_provided)

    # --- value flow / state machine / call graph ----------------------------
    sources = source_scan.load_contract_sources(rm, root)
    value_paths = value_flow.build_value_paths(rm, sources)
    state_machines = state_machine.detect_state_machines(rm, sources, value_paths)
    call_edges = call_graph.build_call_graph(rm, sources)
    value_sm_contracts = state_machine.value_state_machine_contracts(state_machines)

    # --- deployment reality + registry diff ---------------------------------
    deployment = deploy_mod.assess_deployment(
        ctx, address_parse, rpc_endpoint=rpc_endpoint, deployment_calls=deployment_calls, transport=rpc_transport)
    registry = registry_mod.assess_registry(
        address_parse, rpc_endpoint=rpc_endpoint, registry_calls=registry_calls, transport=rpc_transport)
    rpc_ran = deployment.status == M.READ_ONLY_RPC_ENABLED

    # --- senior review-map leads -> dedup + freshness ------------------------
    sleads = senior_leads_mod.generate_leads(rm)[:max_leads]
    trusted_oos = _trusted_role_oos(scope_text)
    corpus_provided = known_provided or audits_provided

    known_matches: list = []
    km_by_id: dict = {}
    deployment_status_by_lead: dict = {}
    for sl in sleads:
        km = dedup_quality.classify_lead(sl, corpus, dq, trusted_role_oos=trusted_oos, corpus_provided=corpus_provided)
        km_by_id[sl.id] = km
        known_matches.append(km)
        contract = (getattr(sl, "surface", "") or "").split(".")[0]
        deployment_status_by_lead[sl.id] = deployment_status_for_contract(deployment, contract)

    senior_freshness = fresh_mod.assess_freshness(
        ctx, root, sleads, corpus, deployment_status_by_lead=deployment_status_by_lead,
        value_state_machine_contracts=value_sm_contracts)
    fv_by_id = {f.lead_id: f for f in senior_freshness}

    # --- build hunter leads + score ------------------------------------------
    leads = lead_builder.build_leads(
        sleads, known_matches=km_by_id, freshness_verdicts=fv_by_id, value_paths=value_paths,
        state_machines=state_machines, deployment=deployment, registry_diff=registry,
        source_provenance=source_provenance, program_identity=program_identity)

    baseline_provided = bool(baseline_ref or since_date or audit_date or fresh_allowlist
                             or any(d.kind == "audit" for d in corpus))
    caps_context = {
        "scope_provided": program_identity.scope_status != M.SCOPE_MISSING,
        "baseline_provided": baseline_provided,
        "rpc_ran": rpc_ran,
        "addresses_provided": bool(address_parse.addresses),
    }
    scoring.score_leads(leads, program_identity=program_identity, dedup_quality=dq,
                        caps_context=caps_context, strict_context=strict_context)
    leads = _sorted(leads)

    # --- freshness/known verdict lists covering all leads (incl. synthetic) --
    freshness_verdicts = _freshness_for_all(leads, fv_by_id)
    known_matches = _known_for_all(leads, km_by_id)

    # --- PoC plans / submission risk / report filter / engine eval -----------
    poc_plans = poc_planner.build_poc_plans(leads, rpc_ran=rpc_ran, baseline_provided=baseline_provided)
    poc_status_by_lead = {p.lead_id: p.status for p in poc_plans}
    submission_risks = submission_risk.build_submission_risks(
        leads, rpc_ran=rpc_ran, scope_provided=caps_context["scope_provided"])
    scope_collision = any(w in M.SCOPE_COLLISIONS for w in program_identity.scope_warnings)
    report_rows = rf_mod.build_report_filter(
        leads, poc_status_by_lead=poc_status_by_lead, scope_collision=scope_collision, rpc_ran=rpc_ran)
    evaluation = engine_eval.evaluate(
        program_identity=program_identity, source_provenance=source_provenance, dedup_quality=dq,
        freshness_verdicts=freshness_verdicts, deployment=deployment, registry_diff=registry,
        value_paths=value_paths, state_machines=state_machines, leads=leads, poc_plans=poc_plans,
        rpc_ran=rpc_ran, baseline_provided=baseline_provided)

    counts = _counts(leads, top)
    hard_kills = [{"lead_id": x.lead_id, "title": x.title, "decision": x.decision}
                  for x in leads if x.decision in M.KILL_DECISIONS]
    decision_caps = sorted({c for x in leads for c in x.decision_caps})
    engine_warnings = _engine_warnings(program_identity, dq, address_parse, source_provenance,
                                       deployment, baseline_provided, rpc_ran)
    missing_context = _missing_context(program_identity, dq, address_parse, deployment, baseline_provided,
                                       rpc_ran, source_provenance)

    pack = M.HunterPack(
        context=ctx, generated_at=_now(), arkheionx_version=PACKAGE_VERSION,
        program_identity=program_identity, address_parse=address_parse,
        source_provenance=source_provenance, dedup_quality=dq, deployment_reality=deployment,
        registry_diff=registry, engine_evaluation=evaluation, leads=leads,
        known_matches=known_matches, freshness_verdicts=freshness_verdicts, value_paths=value_paths,
        state_machines=state_machines, call_edges=call_edges, poc_plans=poc_plans,
        submission_risks=submission_risks, report_filter=report_rows, hard_kills=hard_kills,
        decision_caps=decision_caps, engine_warnings=engine_warnings, missing_context=missing_context,
        counts=counts,
    )

    contents = render.render_all(pack)
    triage_json = _build_triage_json(pack)
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


def _sorted(leads: list) -> list:
    order = {d: i for i, d in enumerate(
        (M.PURSUE_NOW, M.NEEDS_POC) + M.PARK_DECISIONS + M.KILL_DECISIONS)}
    return sorted(leads, key=lambda x: (-x.score, order.get(x.decision, 99), x.lead_id))


def _freshness_for_all(leads: list, fv_by_id: dict) -> list:
    out: list = []
    for lead in leads:
        f = fv_by_id.get(lead.lead_id)
        if f is None:
            f = M.FreshnessVerdict(lead_id=lead.lead_id, freshness_status=lead.freshness_status,
                                   freshness_confidence=M.MEDIUM, score=lead.freshness_score,
                                   freshness_evidence=[{"source": "synthetic-lead", "reason": lead.lead_type}])
        out.append(f)
    return out


def _known_for_all(leads: list, km_by_id: dict) -> list:
    out: list = []
    for lead in leads:
        k = km_by_id.get(lead.lead_id)
        if k is None:
            k = M.KnownMatch(lead_id=lead.lead_id, dedup_status=lead.dedup_status,
                             known_match_status=lead.known_match_status, known_issue_confidence=M.MEDIUM,
                             dedup_reasoning=[f"Synthetic lead ({lead.lead_type}); dedup inferred from signal type."])
        out.append(k)
    return out


def _counts(leads: list, top: int) -> dict:
    return {
        "leads": len(leads),
        "pursue_now": sum(1 for x in leads if x.decision == M.PURSUE_NOW),
        "needs_poc": sum(1 for x in leads if x.decision == M.NEEDS_POC),
        "park": sum(1 for x in leads if x.decision in M.PARK_DECISIONS),
        "kill": sum(1 for x in leads if x.decision in M.KILL_DECISIONS),
        "top": top,
    }


def _engine_warnings(pi, dq, address_parse, sp, deployment, baseline_provided, rpc_ran) -> list:
    w: list = []
    if pi.scope_warnings:
        w.append(f"Scope warnings: {', '.join(pi.scope_warnings)}.")
    if dq.status == M.DEDUP_BLIND:
        w.append("DEDUP_BLIND: no usable known/audit/test corpus; 'no duplicate' is unverified.")
    if address_parse.status == M.ADDRESS_PARSE_ERROR:
        w.append(f"Address parse error: {address_parse.path}.")
    if sp.overall_status in M.SOURCE_INADEQUATE:
        w.append(f"Source inadequate ({sp.overall_status}); source-level leads capped.")
    if deployment.addresses_provided and not rpc_ran:
        w.append("Addresses provided but no read-only RPC verification ran.")
    if not baseline_provided:
        w.append("No freshness baseline; positive freshness rests on deployment/registry/audit-gap evidence only.")
    return w


def _missing_context(pi, dq, address_parse, deployment, baseline_provided, rpc_ran, sp) -> list:
    m: list = []
    if pi.scope_status == M.SCOPE_MISSING:
        m.append("Scope / program rules (--scope-file).")
    if dq.status in (M.DEDUP_BLIND, M.DEDUP_PARTIAL):
        m.append("Known issues / audits (--known/--audits) to raise dedup quality.")
    if not baseline_provided:
        m.append("Freshness baseline (--baseline-ref / --since-date / --audit-date).")
    if not address_parse.addresses:
        m.append("Deployed addresses (--addresses) for a deployment-reality plan.")
    if deployment.addresses_provided and not rpc_ran:
        m.append("Read-only RPC (--rpc-url) to verify live deployment vs source.")
    if sp.overall_status in M.SOURCE_INADEQUATE:
        m.append("Authoritative source (--source-dir / source recovery) for the deployed contracts.")
    return m


def _build_triage_json(pack: M.HunterPack) -> dict:
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
        "source_dir": ctx.source_dir,
        "rpc_mode": ctx.rpc_mode,
        "rpc_enabled": False,
        "rpc_endpoint_masked": ctx.rpc_endpoint_masked,
        "program_identity": pack.program_identity.to_dict(),
        "scope_status": pack.program_identity.scope_status,
        "scope_warnings": pack.program_identity.scope_warnings,
        "address_parse": pack.address_parse.to_dict(),
        "source_status": pack.source_provenance.overall_status,
        "source_provenance": pack.source_provenance.to_dict(),
        "dedup_status": pack.dedup_quality.status,
        "dedup_quality": pack.dedup_quality.to_dict(),
        "freshness_status": _overall_freshness(pack.leads),
        "deployment_status": pack.deployment_reality.status,
        "deployment_reality": pack.deployment_reality.to_dict(),
        "registry_diff": pack.registry_diff.to_dict(),
        "value_paths": [v.to_dict() for v in pack.value_paths],
        "state_machines": [s.to_dict() for s in pack.state_machines],
        "call_edges": [c.to_dict() for c in pack.call_edges],
        "known_matches": [k.to_dict() for k in pack.known_matches],
        "freshness_verdicts": [f.to_dict() for f in pack.freshness_verdicts],
        "leads": [lead.to_dict() for lead in pack.leads],
        "top_3_leads": [lead.to_dict() for lead in pack.top_leads(3)],
        "top_leads": [lead.to_dict() for lead in pack.top_leads(pack.counts.get("top", M.TOP_LEAD_LIMIT))],
        "poc_plans": [p.to_dict() for p in pack.poc_plans],
        "submission_risks": [s.to_dict() for s in pack.submission_risks],
        "report_filter": [r.to_dict() for r in pack.report_filter],
        "hard_kills": pack.hard_kills,
        "decision_caps": pack.decision_caps,
        "engine_warnings": pack.engine_warnings,
        "engine_evaluation": pack.engine_evaluation.to_dict(),
        "missing_context": pack.missing_context,
        "counts": pack.counts,
        "safety_flags": dict(SAFETY_FLAGS),
        "safety_boundaries": list(SAFETY_BOUNDARIES),
        "human_review_required": True,
    }


def _build_manifest(pack: M.HunterPack) -> dict:
    ctx = pack.context
    artifact_paths = list(render.ARTIFACT_ORDER) + ["triage.json", "manifest.json"]
    return {
        "schema_version": M.SCHEMA_VERSION,
        "artifact_type": M.MANIFEST_TYPE,
        "arkheionx_version": pack.arkheionx_version,
        "command": M.COMMAND,
        "branch": "private/v9-universal-senior-exploit-hunter",
        "generated_at": pack.generated_at,
        "repo_path": ctx.repo_path,
        "input_paths": {
            "scope_file": ctx.scope_file, "known_path": ctx.known_path, "audits_path": ctx.audits_path,
            "addresses_file": ctx.addresses_file, "source_dir": ctx.source_dir,
            "baseline_ref": ctx.baseline_ref, "since_date": ctx.since_date, "audit_date": ctx.audit_date,
        },
        "rpc_mode": ctx.rpc_mode,
        "rpc_endpoint_masked": ctx.rpc_endpoint_masked,
        "known_corpus_quality": pack.dedup_quality.status,
        "source_recovery_status": pack.source_provenance.overall_status,
        "artifact_count": len(artifact_paths),
        "artifact_paths": artifact_paths,
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
