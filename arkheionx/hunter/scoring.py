"""Decision policy + research-priority scoring for hunter mode.

The score (0-100) is a time-allocation ordering, not a severity and not a validity
claim. The decision is the senior call about where to spend the next 30-90 minutes:

    PURSUE_NOW / NEEDS_POC / PARK_SCOPE / PARK_DEDUP / PARK_DEPLOYMENT / PARK_SOURCE /
    PARK_BASELINE / KILL_* (duplicate, OOS, trusted-role, public-test, documented,
    low-only, no-material-impact, not-attacker-reachable).

Hard kills fire first. Hard boosts lift clear, evidence-backed signals. Fail-closed
caps then keep a lead out of PURSUE/NEEDS_POC when the context that would justify it
is missing (no known corpus, no baseline, no RPC for live wiring, missing source,
unresolved scope collision). A clear signal — a verified live deployment mismatch or
an evidence-backed post-audit freshness — bypasses the soft caps.
"""
from __future__ import annotations

from . import models as M
from . import reachability as R

WEIGHTS = {
    "scope_confidence": 12,
    "freshness": 20,
    "attacker_reachability": 14,
    "materiality": 14,
    "duplicate_risk_inverse": 14,
    "trusted_role_risk_inverse": 8,
    "proof_difficulty_inverse": 6,
    "source_quality": 6,
    "deployment": 6,
}

PURSUE_MIN = 78
POC_MIN = 52

_SOURCE_SCORE = {
    M.SOURCE_LOCAL: 92, M.SOURCE_PROVIDED: 90, M.SOURCE_SOURCIFY_EXACT: 88,
    M.SOURCE_ETHERSCAN_VERIFIED: 84, M.SOURCE_ARTIFACT: 70, M.SOURCE_SOURCIFY_PARTIAL: 55,
    M.SOURCE_ABI_ONLY: 30, M.SOURCE_MISSING: 12, M.SOURCE_RECOVERY_FAILED: 12,
}
_DEPLOY_SCORE = {
    M.DEPLOY_IMPLEMENTATION_CHANGED: 95, M.LIVE_SOURCE_MISMATCH: 95, M.BEACON_CHANGED: 95,
    M.ADMIN_CHANGED: 90, M.ADDRESS_NO_CODE: 5, M.IMPLEMENTATION_MATCH: 40, M.BEACON_MATCH: 40,
    M.LIVE_SOURCE_MATCH: 40,
}

# Known-match -> a duplicate-risk floor (higher = more likely already known).
_KNOWN_DUP_FLOOR = {
    M.PUBLIC_TEST_COVERED: 90, M.LIKELY_DUPLICATE: 85, M.ACKNOWLEDGED_RISK: 80,
    M.DOCUMENTED_BEHAVIOR: 78, M.OUT_OF_SCOPE: 70, M.TRUSTED_ROLE_ONLY: 60,
    M.SIMILAR_KNOWN: 50, M.NO_MATCH_FOUND: 12, M.KNOWN_UNKNOWN: 45,
}


def _severity_ceiling(lead: M.HunterLead) -> str:
    reach = lead.attacker_reachability
    if (reach == "INTERNAL_OR_GUARDED" or R.is_internal(reach) or R.is_non_value(reach)
            or R.is_trusted_role_gated(reach) or lead.known_match_status == M.TRUSTED_ROLE_ONLY):
        return M.LOW_ONLY
    mat = lead.materiality
    reach_ok = R.is_attacker_reachable(reach)
    value_out = lead.lead_type in (
        M.VALUE_OUT_PATH, M.STATE_MACHINE_VALUE_FLOW, M.WITHDRAWAL_QUEUE, M.CLAIM_QUEUE,
        M.ADAPTER_WITHDRAWABILITY, M.BRIDGE_MESSAGE_ACCOUNTING, M.CROSS_CHAIN_DOMAIN_SEPARATION,
        M.SHARE_ACCOUNTING, M.DEPLOYMENT_MISMATCH, M.EMERGENCY_EXIT_ACCOUNTING,
    )
    if mat == M.HIGH and reach_ok and value_out:
        if lead.lead_type in (M.CROSS_CHAIN_DOMAIN_SEPARATION, M.BRIDGE_MESSAGE_ACCOUNTING):
            return M.CRITICAL_POSSIBLE
        return M.HIGH_POSSIBLE
    if mat in (M.HIGH, M.MEDIUM) and reach_ok:
        return M.MEDIUM_POSSIBLE
    if mat == M.LOW:
        return M.LOW_ONLY
    return M.MEDIUM_POSSIBLE


def _base_score(lead: M.HunterLead) -> tuple[int, dict]:
    dup_floor = _KNOWN_DUP_FLOOR.get(lead.known_match_status, 45)
    dup_risk = max(lead.duplicate_risk_score, dup_floor if lead.known_match_status != M.NO_MATCH_FOUND else 0)
    lead.duplicate_risk_score = dup_risk
    source_q = _SOURCE_SCORE.get(lead.source_status, 50)
    deploy_q = _DEPLOY_SCORE.get(lead.deployment_status, 50)
    comps = {
        "scope_confidence": lead.scope_confidence_score / 100 * WEIGHTS["scope_confidence"],
        "freshness": lead.freshness_score / 100 * WEIGHTS["freshness"],
        "attacker_reachability": lead.attacker_reachability_score / 100 * WEIGHTS["attacker_reachability"],
        "materiality": lead.materiality_score / 100 * WEIGHTS["materiality"],
        "duplicate_risk_inverse": (100 - dup_risk) / 100 * WEIGHTS["duplicate_risk_inverse"],
        "trusted_role_risk_inverse": (100 - lead.trusted_role_risk_score) / 100 * WEIGHTS["trusted_role_risk_inverse"],
        "proof_difficulty_inverse": (100 - lead.proof_difficulty_score) / 100 * WEIGHTS["proof_difficulty_inverse"],
        "source_quality": source_q / 100 * WEIGHTS["source_quality"],
        "deployment": deploy_q / 100 * WEIGHTS["deployment"],
    }
    raw = max(0, min(int(round(sum(comps.values()))), 100))
    return raw, {k: round(v, 2) for k, v in comps.items()}


def _is_clear(lead: M.HunterLead) -> bool:
    """A signal strong enough to bypass the soft fail-closed caps."""
    hard_deploy = lead.deployment_status in M.DEPLOYMENT_MISMATCH_STATUSES
    strong_fresh = lead.freshness_status in M.FRESHNESS_POSITIVE and lead.freshness_score >= 80
    return hard_deploy or strong_fresh


def _value_bearing(lead: M.HunterLead) -> bool:
    return lead.materiality_score >= 60 or "value-out" in lead.notes or lead.lead_type in (
        M.VALUE_OUT_PATH, M.STATE_MACHINE_VALUE_FLOW, M.DEPLOYMENT_MISMATCH,
        M.WITHDRAWAL_QUEUE, M.CLAIM_QUEUE, M.SHARE_ACCOUNTING, M.ADAPTER_WITHDRAWABILITY,
    )


def _apply_boosts(lead: M.HunterLead, score: int, boosts: list) -> int:
    clear_deploy = lead.deployment_status in M.DEPLOYMENT_MISMATCH_STATUSES
    if clear_deploy and _value_bearing(lead):
        score = min(100, score + 8)
        boosts.append("Live implementation differs from expected on a value-bearing contract.")
    if lead.freshness_status == M.NEW_VALUE_OUT_SURFACE and lead.known_match_status == M.NO_MATCH_FOUND:
        score = min(100, score + 5)
        boosts.append("New post-audit value-out surface with no known match.")
    if (lead.lead_type == M.STATE_MACHINE_VALUE_FLOW
            and R.is_attacker_reachable(lead.attacker_reachability)):
        score = min(100, score + 5)
        boosts.append("State-machine value-flow with unprivileged reachability.")
    if lead.freshness_status == M.NEW_LIVE_REGISTRY_ENTRY:
        score = min(100, score + 4)
        boosts.append("New live registry entry (confirm in scope).")
    if lead.lead_type in (M.FEE_DISPATCH, M.REWARD_ACCOUNTING, M.WITHDRAWAL_QUEUE) and \
            "external-call-before-state-update" in (" ".join(lead.notes)):
        score = min(100, score + 3)
        boosts.append("Value path with suspicious external-call-before-state-update ordering.")
    return score


def _hard_kill(lead: M.HunterLead, clear: bool) -> str:
    ks = lead.known_match_status
    if ks == M.OUT_OF_SCOPE:
        return M.KILL_OOS
    if ks == M.PUBLIC_TEST_COVERED and not clear:
        return M.KILL_PUBLIC_TEST_COVERED
    if ks == M.DOCUMENTED_BEHAVIOR and not clear:
        return M.KILL_DOCUMENTED_BEHAVIOR
    if ks == M.LIKELY_DUPLICATE and lead.known_issue_confidence == M.HIGH and not clear:
        return M.KILL_DUPLICATE
    if R.is_non_value(lead.attacker_reachability):
        return M.KILL_NO_MATERIAL_IMPACT
    if R.is_internal(lead.attacker_reachability):
        return M.KILL_NOT_ATTACKER_REACHABLE
    # Unknown/context reachability is handled by a specific PARK_* cap below. Do not
    # let coarse trusted-role text matching or the legacy visibility score override it.
    if R.is_unknown_gated(lead.attacker_reachability) or R.is_context_gated(
            lead.attacker_reachability):
        return ""
    trusted_only = (
        ks == M.TRUSTED_ROLE_ONLY
        or R.is_trusted_role_gated(lead.attacker_reachability)
        or (lead.trusted_role_risk_score >= 60 and not R.is_attacker_reachable(lead.attacker_reachability))
    )
    if trusted_only and not R.is_attacker_reachable(lead.attacker_reachability):
        return M.KILL_TRUSTED_ROLE
    if lead.deployment_status == M.ADDRESS_NO_CODE:
        return M.KILL_NO_MATERIAL_IMPACT
    if not clear and lead.materiality_score < 35:
        return M.KILL_NO_MATERIAL_IMPACT
    if not clear and lead.attacker_reachability_score <= 30 and lead.lead_type != M.SOURCE_RECOVERY_GAP:
        return M.KILL_NOT_ATTACKER_REACHABLE
    return ""


def _cap_decision(lead: M.HunterLead, caps_ctx: dict, clear: bool, caps: list) -> str:
    """Return a forced PARK_* decision if a fail-closed cap applies, else ''."""
    # Scope collision / missing scope is the most fundamental cap.
    if caps_ctx.get("scope_collision"):
        caps.append("Scope collision unresolved -> PARK_SCOPE until the product/version/chain is confirmed.")
        return M.PARK_SCOPE
    if not caps_ctx.get("scope_provided"):
        caps.append("No scope file -> cannot confirm eligibility; capped to PARK_SCOPE.")
        return M.PARK_SCOPE
    # V9.1 reachability caps: who-can-call must be resolved before pursuit. Unknown
    # custom-modifier / auth-helper gating is parked (never assumed unprivileged);
    # proxy/initializer context needs deployment state.
    if R.is_unknown_gated(lead.attacker_reachability):
        caps.append("Reachability unresolved (custom modifier / auth helper) -> PARK_REACHABILITY "
                    "until an unprivileged path is proven; do not assume the function is callable.")
        return M.PARK_REACHABILITY
    if not clear and R.is_context_gated(lead.attacker_reachability):
        caps.append("Reachability is deployment/initialization-context gated -> PARK_DEPLOYMENT "
                    "until deployed state proves an attacker path.")
        return M.PARK_DEPLOYMENT
    # A live registry entry not in the listed scope set is a scope question first.
    if lead.lead_type == M.LIVE_REGISTRY_DIFF and lead.freshness_status == M.NEW_LIVE_REGISTRY_ENTRY:
        caps.append("Live registry entry not in the listed scope set -> PARK_SCOPE until the program confirms it is in scope.")
        return M.PARK_SCOPE
    # Source missing on a source-level lead (the source gap is the defining issue) is
    # checked before the dedup-blind cap so a SOURCE_RECOVERY_GAP parks on source.
    if lead.source_status in M.SOURCE_INADEQUATE and lead.deployment_status not in M.DEPLOYMENT_MISMATCH_STATUSES \
            and lead.deployment_status != M.ADDRESS_NO_CODE:
        caps.append("Source missing/ABI-only -> source-level lead capped to PARK_SOURCE.")
        return M.PARK_SOURCE
    # Dedup blind (unless a clear signal justifies pursuit).
    if not clear and caps_ctx.get("dedup_status") == M.DEDUP_BLIND:
        caps.append("DEDUP_BLIND corpus -> capped to PARK_DEDUP (no way to trust 'no duplicate').")
        return M.PARK_DEDUP
    # Live-wiring-dependent lead without verified deployment.
    needs_rpc = lead.lead_type in (M.DEPLOYMENT_MISMATCH, M.LIVE_REGISTRY_DIFF) or \
        lead.freshness_status in (M.NEW_DEPLOYED_IMPLEMENTATION, M.NEW_LIVE_REGISTRY_ENTRY)
    if needs_rpc and not caps_ctx.get("rpc_ran") and not clear:
        caps.append("Lead depends on live wiring but no read-only RPC verified it -> PARK_DEPLOYMENT.")
        return M.PARK_DEPLOYMENT
    # No freshness baseline (unless a clear signal justifies pursuit).
    if not clear and lead.freshness_status in M.FRESHNESS_NO_BASELINE:
        caps.append("Freshness unknown / no baseline -> capped to PARK_BASELINE.")
        return M.PARK_BASELINE
    if not clear and lead.freshness_status == M.SOURCE_RECOVERED_NO_BASELINE:
        caps.append("Source recovered but no baseline to diff -> capped to PARK_BASELINE.")
        return M.PARK_BASELINE
    return ""


def _pursue_ready(lead: M.HunterLead, clear: bool) -> bool:
    return (
        R.is_attacker_reachable(lead.attacker_reachability)
        and lead.materiality_score >= 70
        and (lead.dedup_status in (M.DEDUP_USABLE, M.DEDUP_STRONG) or clear)
        and (lead.freshness_status in M.FRESHNESS_POSITIVE or clear)
        and lead.known_match_status in (M.NO_MATCH_FOUND, M.SIMILAR_KNOWN, M.KNOWN_UNKNOWN)
    )


def score_leads(
    leads: list,
    *,
    program_identity: M.ProgramIdentity,
    dedup_quality: M.DedupQuality,
    caps_context: dict,
    strict_context: bool = False,
) -> None:
    caps_ctx = dict(caps_context or {})
    caps_ctx["dedup_status"] = dedup_quality.status
    caps_ctx["scope_collision"] = any(w in M.SCOPE_COLLISIONS for w in program_identity.scope_warnings)
    caps_ctx["scope_provided"] = program_identity.scope_status not in (M.SCOPE_MISSING,)

    for lead in leads:
        clear = _is_clear(lead)
        raw, breakdown = _base_score(lead)
        boosts: list = []
        caps: list = []
        reasons: list = []
        score = _apply_boosts(lead, raw, boosts)

        lead.expected_severity_ceiling = _severity_ceiling(lead)

        kill = _hard_kill(lead, clear)
        if kill:
            lead.decision = kill
            lead.score = min(score, 44)
            reasons.append(f"Hard kill: {kill}.")
        else:
            forced_park = _cap_decision(lead, caps_ctx, clear, caps)
            if strict_context and not caps_ctx.get("scope_provided"):
                forced_park = M.PARK_SCOPE
            if forced_park:
                lead.decision = forced_park
                lead.score = min(score, 60)
                reasons.append(f"Capped: {forced_park}.")
            elif score >= PURSUE_MIN and _pursue_ready(lead, clear):
                lead.decision = M.PURSUE_NOW
                lead.score = score
                reasons.append("Clears the pursue bar: in scope, fresh/mismatched, reachable, material, non-duplicate.")
            elif score >= POC_MIN:
                lead.decision = M.NEEDS_POC
                lead.score = score
                reasons.append("Worth a minimal PoC to prove or kill the lead.")
            else:
                # Low score but no specific cap: park on the weakest dimension.
                lead.decision = _weakest_park(lead, caps_ctx)
                lead.score = score
                reasons.append(f"Below the PoC bar; parked as {lead.decision}.")

        if clear:
            reasons.append("Clear signal (verified deployment mismatch or evidence-backed post-audit freshness) "
                           "bypasses soft caps.")
        lead.score_breakdown = breakdown
        lead.priority_boosts = boosts
        lead.decision_caps = caps
        lead.decision_reasons = reasons + boosts + caps
        lead.expected_payout_ev = _payout_ev(lead)
        lead.submission_risk = _coarse_risk(lead)


def _weakest_park(lead: M.HunterLead, caps_ctx: dict) -> str:
    if lead.freshness_status in M.FRESHNESS_NO_BASELINE:
        return M.PARK_BASELINE
    if lead.duplicate_risk_score >= 55:
        return M.PARK_DEDUP
    if lead.source_status in M.SOURCE_INADEQUATE:
        return M.PARK_SOURCE
    if lead.attacker_reachability_score <= 40:
        return M.KILL_NOT_ATTACKER_REACHABLE
    return M.PARK_BASELINE


def _payout_ev(lead: M.HunterLead) -> int:
    if lead.decision in M.KILL_DECISIONS:
        return 0
    ceiling_w = {M.CRITICAL_POSSIBLE: 100, M.HIGH_POSSIBLE: 80, M.MEDIUM_POSSIBLE: 55,
                 M.LOW_ONLY: 20, M.INFO_ONLY: 5, M.NOT_ELIGIBLE: 0}.get(lead.expected_severity_ceiling, 30)
    decision_w = {M.PURSUE_NOW: 1.0, M.NEEDS_POC: 0.7}.get(lead.decision, 0.4)
    return int(round(ceiling_w * decision_w))


def _coarse_risk(lead: M.HunterLead) -> str:
    if lead.decision == M.PURSUE_NOW:
        return M.PAYABLE_CANDIDATE
    if lead.decision == M.NEEDS_POC:
        return M.RISK_NEEDS_POC
    if lead.decision in M.PARK_DECISIONS:
        return {M.PARK_SCOPE: M.RISK_PARK_SCOPE, M.PARK_DEDUP: M.RISK_PARK_DEDUP,
                M.PARK_DEPLOYMENT: M.RISK_PARK_DEPLOYMENT, M.PARK_SOURCE: M.RISK_PARK_SOURCE,
                M.PARK_REACHABILITY: M.RISK_PARK_REACHABILITY,
                M.PARK_BASELINE: M.RISK_PARK_DEDUP}.get(lead.decision, M.RISK_NEEDS_POC)
    return {M.KILL_DUPLICATE: M.RISK_KILL_DUPLICATE, M.KILL_OOS: M.RISK_KILL_OOS,
            M.KILL_TRUSTED_ROLE: M.RISK_KILL_TRUSTED_ROLE,
            M.KILL_PUBLIC_TEST_COVERED: M.RISK_KILL_DUPLICATE,
            M.KILL_DOCUMENTED_BEHAVIOR: M.RISK_KILL_DUPLICATE,
            M.KILL_LOW_ONLY: M.RISK_KILL_LOW_ONLY,
            M.KILL_NO_MATERIAL_IMPACT: M.RISK_KILL_NO_MATERIAL_IMPACT,
            M.KILL_NOT_ATTACKER_REACHABLE: M.RISK_KILL_NO_MATERIAL_IMPACT}.get(lead.decision, M.RISK_NEEDS_POC)
