"""Engine self-evaluation for hunter mode.

Produces an honest, non-marketing assessment of the run: how good scope parsing,
source recovery, dedup, freshness, deployment reality, value-flow, and state-machine
detection actually were, plus false-positive / false-negative / missed-surface risk,
the manual-review dependency, the biggest uncertainty, what the engine got wrong, and
what to fix next. Scores are 0-10 and are deliberately conservative.
"""
from __future__ import annotations

from . import models as M


def _band_text(score: int, good: str, mid: str, weak: str) -> str:
    if score >= 7:
        return good
    if score >= 4:
        return mid
    return weak


def evaluate(
    *,
    program_identity: M.ProgramIdentity,
    source_provenance: M.SourceProvenance,
    dedup_quality: M.DedupQuality,
    freshness_verdicts: list,
    deployment: M.DeploymentReality,
    registry_diff: M.RegistryDiff,
    value_paths: list,
    state_machines: list,
    leads: list,
    poc_plans: list,
    rpc_ran: bool,
    baseline_provided: bool,
) -> M.EngineEvaluation:
    scope = {M.SCOPE_OK: 8, M.SCOPE_PARTIAL: 5, M.SCOPE_COLLISION: 3, M.SCOPE_MISSING: 2}.get(
        program_identity.scope_status, 4)
    src = {M.SOURCE_LOCAL: 8, M.SOURCE_PROVIDED: 8, M.SOURCE_SOURCIFY_EXACT: 8,
           M.SOURCE_ETHERSCAN_VERIFIED: 7, M.SOURCE_ARTIFACT: 6, M.SOURCE_SOURCIFY_PARTIAL: 5,
           M.SOURCE_ABI_ONLY: 3, M.SOURCE_MISSING: 2, M.SOURCE_RECOVERY_FAILED: 2}.get(
        source_provenance.overall_status, 4)
    dedup = {M.DEDUP_STRONG: 9, M.DEDUP_USABLE: 7, M.DEDUP_PARTIAL: 4, M.DEDUP_BLIND: 2}.get(
        dedup_quality.status, 3)
    positive_fresh = sum(1 for f in freshness_verdicts if f.freshness_status in M.FRESHNESS_POSITIVE)
    freshness = 7 if positive_fresh else (6 if baseline_provided else 3)
    deploy = 8 if rpc_ran else (5 if deployment.addresses_provided else 3)
    if registry_diff.status not in (M.REGISTRY_NOT_RUN, M.REGISTRY_DIFF_UNKNOWN):
        deploy = min(9, deploy + 1)
    vflow = 7 if len(value_paths) >= 3 else (6 if value_paths else 3)
    sm_val = sum(1 for s in state_machines if s.touches_value)
    sm = 7 if sm_val else (5 if state_machines else 4)
    pursueable = sum(1 for x in leads if x.decision in M.PURSUEABLE)
    lead_disc = 7 if pursueable else (5 if leads else 3)
    poc = 7 if poc_plans else (5 if pursueable == 0 else 3)
    sub_risk = 7 if leads else 4
    overall = int(round((scope + dedup + freshness + deploy + vflow + sm + lead_disc + poc + sub_risk) / 9))

    wrong: list = []
    if dedup_quality.status == M.DEDUP_BLIND:
        wrong.append("Dedup was blind (no known/audit corpus); any 'no duplicate' result is unverified.")
    if not baseline_provided:
        wrong.append("No freshness baseline; positive freshness rests only on deployment/registry/audit-gap evidence.")
    if not rpc_ran and deployment.addresses_provided:
        wrong.append("Addresses were provided but live wiring was not verified (no read-only RPC).")
    if source_provenance.overall_status in M.SOURCE_INADEQUATE:
        wrong.append("Authoritative source was not fully recovered; source-level reasoning is limited.")
    if not value_paths:
        wrong.append("No value paths were extracted; the target may use patterns the static scan missed.")
    if not wrong:
        wrong.append("Nothing obviously wrong, but all signals are heuristic and unconfirmed.")

    fix_next: list = []
    if dedup_quality.status in (M.DEDUP_BLIND, M.DEDUP_PARTIAL):
        fix_next.append("Add known issues / audits / public tests (--known/--audits) to raise dedup quality.")
    if not baseline_provided:
        fix_next.append("Provide --baseline-ref / --since-date / --audit-date for evidence-based freshness.")
    if not rpc_ran:
        fix_next.append("Provide a read-only --rpc-url + --addresses to verify live deployment and registry wiring.")
    if source_provenance.overall_status in M.SOURCE_INADEQUATE:
        fix_next.append("Provide --source-dir or enable source recovery for the deployed contracts.")
    fix_next.append("Manually confirm each top lead's root behavior and run the PoC before any report.")

    return M.EngineEvaluation(
        scope_parsing_quality=_band_text(scope, "Scope parsed with reward/exclusion structure.",
                                         "Scope partially parsed.", "Scope missing or collided."),
        source_recovery_quality=_band_text(src, "Authoritative source available.",
                                           "Partial source.", "Source largely unavailable."),
        known_corpus_quality=f"{dedup_quality.status}: " + "; ".join(dedup_quality.reasons[:2]),
        dedup_quality=_band_text(dedup, "Evidence-backed dedup.", "Limited dedup.", "Blind dedup."),
        freshness_quality=_band_text(freshness, "Evidence-based freshness signal present.",
                                     "Weak baseline.", "No baseline; freshness unknown."),
        deployment_reality_quality=_band_text(deploy, "Live read-only verification ran.",
                                              "Static plan only.", "No deployment context."),
        value_flow_quality=_band_text(vflow, "Value paths extracted.", "Few value paths.", "No value paths."),
        state_machine_quality=_band_text(sm, "Value-gating state machines detected.",
                                         "State machines detected (value link unclear).", "No state machines."),
        top_lead_quality=_band_text(lead_disc, "Pursueable leads identified.",
                                    "Leads found but parked.", "No strong leads."),
        poc_planner_usefulness=_band_text(poc, "Minimal PoC plans for pursueable leads.",
                                          "Few/limited PoC plans.", "No pursueable leads to plan."),
        submission_risk_usefulness=_band_text(sub_risk, "Per-lead rejection-risk model produced.",
                                              "Partial risk model.", "Insufficient leads."),
        false_positive_risk="MEDIUM — heuristic detectors can over-flag; every lead needs manual confirmation.",
        false_negative_risk=("HIGH — dedup blind / no baseline can hide both duplicates and fresh bugs."
                             if (dedup_quality.status == M.DEDUP_BLIND or not baseline_provided)
                             else "MEDIUM — static scan may miss non-obvious value paths."),
        missed_surface_risk="MEDIUM — only statically reachable Solidity surfaces were scanned (no compiler, no fork).",
        manual_review_dependency="HIGH — hunter mode prioritizes attention; it does not confirm bugs.",
        biggest_uncertainty=_biggest_uncertainty(dedup_quality, baseline_provided, rpc_ran, source_provenance),
        what_arkheionx_got_wrong=wrong,
        what_to_fix_next=fix_next,
        scores={
            "scope": scope, "dedup": dedup, "freshness": freshness, "deployment": deploy,
            "value_flow": vflow, "state_machine": sm, "lead_discovery": lead_disc,
            "poc_planning": poc, "submission_risk": sub_risk, "overall": overall,
        },
    )


def _biggest_uncertainty(dedup_quality, baseline_provided, rpc_ran, source_provenance) -> str:
    if dedup_quality.status == M.DEDUP_BLIND:
        return "Whether the top leads are already-known duplicates (no dedup corpus was parsed)."
    if not baseline_provided:
        return "Whether the surface is actually fresh (no audit/git baseline to diff against)."
    if not rpc_ran:
        return "Whether the deployed wiring matches source (no read-only RPC verification ran)."
    if source_provenance.overall_status in M.SOURCE_INADEQUATE:
        return "Whether the analyzed source matches the deployed bytecode (source not fully recovered)."
    return "Whether each top lead's root behavior is materially exploitable by an unprivileged attacker."
