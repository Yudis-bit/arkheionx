"""Step 5 — research-priority scoring v2 and the senior decision.

The score (0-100) is a research-priority ordering, not a severity and not a validity
claim. v2 adds a deployment-reality dimension and a known-issue-confidence dimension,
hard blockers, hard boosts (e.g. a live implementation mismatch on a value-bearing
contract), and fail-closed decision caps when context is missing. Every score is
explained with a breakdown, boosts, and caps.
"""
from __future__ import annotations

from . import models as M
from .known_issues import trusted_role_risk

# Component weights (sum = 100). "inverse" components reward a *low* raw score.
WEIGHTS = {
    "scope_confidence": 12,
    "freshness": 18,
    "attacker_reachability": 13,
    "materiality": 13,
    "duplicate_risk_inverse": 13,
    "trusted_role_risk_inverse": 8,
    "deployment_reality": 10,
    "known_issue_confidence_inverse": 5,
    "proof_difficulty_inverse": 4,
    "time_cost_inverse": 4,
}

_PURSUE_MIN = 75
_PARK_MIN = 45
_PARK_CAP = 60  # capping a lead to this keeps it out of the PURSUE band

_SCOPE_CONF_SCORE = {M.CONF_LOW: 30, M.CONF_MEDIUM: 60, M.CONF_HIGH: 85}

# Higher = more likely the behavior is already known.
_KNOWN_CONFIDENCE = {
    M.KNOWN_PUBLIC_TEST: 90, M.KNOWN_LIKELY_DUP: 85, M.KNOWN_ACK_RISK: 82,
    M.KNOWN_DOCUMENTED: 78, M.KNOWN_OUT_OF_SCOPE: 70, M.KNOWN_TRUSTED_ROLE: 65,
    M.KNOWN_SIMILAR: 50, M.KNOWN_NO_MATCH: 15, M.KNOWN_UNKNOWN: 45,
}

_DEPLOYMENT_BOOST_STATUSES = (M.DEPLOY_IMPLEMENTATION_CHANGED, M.DEPLOY_LIVE_SOURCE_MISMATCH,
                              M.DEPLOY_REGISTRY_CHANGED, M.DEPLOY_ORACLE_CHANGED)


def _scope_confidence_score(eligibility: M.EligibilitySignal) -> int:
    if not eligibility.scope_provided:
        return 20
    return _SCOPE_CONF_SCORE.get(eligibility.scope_confidence, 30)


def _next_command(decision: str, surface: str, repo: str, scope_file: str) -> str:
    scope_flag = f" --scope-file {scope_file}" if scope_file else ""
    if decision == M.LEAD_PURSUE:
        return f"arkheionx review {repo}{scope_flag} --out .arkheionx/review"
    if decision == M.LEAD_PARK:
        return "Add scope/known/audit/deployment context, then re-run arkheionx triage."
    return "Do not spend time here now; see 07-do-not-touch.md."


def apply_score(
    lead: M.LeadCandidate,
    eligibility: M.EligibilitySignal,
    known: M.KnownIssueSignal,
    freshness: M.FreshnessSignal,
    *,
    repo: str,
    scope_file: str,
    deployment_score: int | None = None,
    deployment_status: str = "",
    strict_context: bool = False,
    caps_context: dict | None = None,
) -> M.LeadScore:
    # Pull verdicts from the upstream signals onto the lead.
    lead.scope_confidence = _scope_confidence_score(eligibility)
    lead.duplicate_risk_score = known.duplicate_risk_score
    lead.dedup_status = known.status
    lead.dedup_similarity_score = known.similarity_score
    lead.dedup_confidence = known.confidence
    lead.dedup_evidence = known.evidence
    lead.known_issue_confidence = _KNOWN_CONFIDENCE.get(known.status, 45)
    lead.trusted_role_risk_score = trusted_role_risk(lead, known)
    lead.freshness_score = freshness.score
    lead.freshness_status = freshness.status
    if deployment_score is not None:
        lead.deployment_effect = deployment_score
    if deployment_status:
        lead.deployment_status = deployment_status
    lead.expected_severity_ceiling = (
        eligibility.severity_ceiling if eligibility.scope_provided else M.SEV_UNKNOWN
    )

    comps = {
        "scope_confidence": lead.scope_confidence / 100 * WEIGHTS["scope_confidence"],
        "freshness": lead.freshness_score / 100 * WEIGHTS["freshness"],
        "attacker_reachability": lead.attacker_reachability_score / 100 * WEIGHTS["attacker_reachability"],
        "materiality": lead.materiality_score / 100 * WEIGHTS["materiality"],
        "duplicate_risk_inverse": (100 - lead.duplicate_risk_score) / 100 * WEIGHTS["duplicate_risk_inverse"],
        "trusted_role_risk_inverse": (100 - lead.trusted_role_risk_score) / 100 * WEIGHTS["trusted_role_risk_inverse"],
        "deployment_reality": lead.deployment_effect / 100 * WEIGHTS["deployment_reality"],
        "known_issue_confidence_inverse": (100 - lead.known_issue_confidence) / 100 * WEIGHTS["known_issue_confidence_inverse"],
        "proof_difficulty_inverse": (100 - lead.proof_difficulty_score) / 100 * WEIGHTS["proof_difficulty_inverse"],
        "time_cost_inverse": (100 - lead.time_cost_score) / 100 * WEIGHTS["time_cost_inverse"],
    }
    raw = max(0, min(int(round(sum(comps.values()))), 100))
    lead.score_breakdown = {k: round(v, 2) for k, v in comps.items()}

    reasons = _reasons(lead, known, freshness, eligibility)
    boosts: list[str] = []
    caps: list[str] = []
    score = raw
    value_bearing = lead.materiality_score >= 60 or "value-out" in lead.notes

    # --- hard boosts ---------------------------------------------------------
    if lead.deployment_status in _DEPLOYMENT_BOOST_STATUSES and value_bearing:
        score = min(100, score + 6)
        boosts.append("Deployment: live implementation differs from expected on a value-bearing contract.")
    if lead.freshness_status in (M.NEW_ADAPTER, M.NEW_VALUE_OUT_PATH) and "value-out" in lead.notes and known.status == M.KNOWN_NO_MATCH:
        score = min(100, score + 4)
        boosts.append("Freshness: new value-out surface after baseline with no known match.")
    if lead.freshness_status == M.POST_AUDIT_CHANGE and lead.attacker_reachability_score >= 70:
        score = min(100, score + 3)
        boosts.append("Freshness: post-audit change on an externally reachable surface.")

    strong_freshness = lead.freshness_status in M.FRESHNESS_PRIORITY and lead.freshness_score >= 75

    # --- hard blockers / caps ------------------------------------------------
    forced_kill = False
    if known.status == M.KNOWN_OUT_OF_SCOPE:
        forced_kill = True
        caps.append("Out of scope -> forced KILL.")
    elif lead.deployment_status == M.DEPLOY_ADDRESS_NO_CODE:
        forced_kill = True
        caps.append("Deployed address has no code -> forced KILL (nothing to attack there).")
    elif known.status == M.KNOWN_PUBLIC_TEST and not strong_freshness:
        forced_kill = True
        caps.append("Public-test covered -> forced KILL (no strong freshness angle).")

    if known.status in (M.KNOWN_LIKELY_DUP, M.KNOWN_ACK_RISK, M.KNOWN_DOCUMENTED, M.KNOWN_PUBLIC_TEST):
        high_conf = known.confidence == M.CONF_HIGH
        if known.status == M.KNOWN_LIKELY_DUP and high_conf and not strong_freshness:
            forced_kill = True
            caps.append("Likely duplicate (HIGH confidence) -> forced KILL.")
        elif strong_freshness:
            if score > _PARK_CAP:
                score = _PARK_CAP
                caps.append("High duplicate risk with a freshness angle -> capped to PARK band.")
        elif score > _PARK_MIN - 1:
            score = _PARK_MIN - 1
            caps.append("High duplicate risk -> capped below PURSUE/PARK threshold.")

    capped_out_of_pursue = False
    if known.status == M.KNOWN_TRUSTED_ROLE and score > _PARK_CAP:
        score = _PARK_CAP
        capped_out_of_pursue = True
        caps.append("Trusted-role-only -> capped out of PURSUE.")
    if not eligibility.scope_provided and score > _PARK_CAP:
        score = _PARK_CAP
        capped_out_of_pursue = True
        caps.append("No scope file -> capped out of PURSUE.")

    # --- fail-closed context caps (only when pack supplies caps_context) ------
    if caps_context is not None:
        deployment_strong = lead.deployment_status in _DEPLOYMENT_BOOST_STATUSES
        score, capped_out_of_pursue = _apply_fail_closed(
            lead, known, caps_context, strict_context, strong_freshness or deployment_strong,
            score, capped_out_of_pursue, caps,
        )

    lead.research_priority_score = score
    lead.priority_boosts = boosts
    lead.decision_caps = caps

    # Decision.
    if forced_kill or score < _PARK_MIN:
        decision = M.LEAD_KILL
    elif score >= _PURSUE_MIN and not _blocked(known) and eligibility.scope_provided and not capped_out_of_pursue:
        decision = M.LEAD_PURSUE
    else:
        decision = M.LEAD_PARK
    lead.decision = decision

    if decision == M.LEAD_KILL:
        lead.submit_readiness = M.DO_NOT_SUBMIT
    elif not eligibility.scope_provided:
        lead.submit_readiness = M.NEEDS_SCOPE_CONFIRMATION
    elif lead.deployment_status in (M.DEPLOY_ADDRESSES_PROVIDED, "") and _needs_deploy(lead) and caps_context and not caps_context.get("rpc_ran"):
        lead.submit_readiness = M.NOT_READY
    elif known.status in (M.KNOWN_UNKNOWN, M.KNOWN_SIMILAR) or lead.duplicate_risk_score >= 55:
        lead.submit_readiness = M.NEEDS_DEDUP
    else:
        lead.submit_readiness = M.NEEDS_LOCAL_PROOF

    lead.next_command = _next_command(decision, lead.surface, repo, scope_file)
    lead.score_reasons = reasons + boosts + caps

    return M.LeadScore(total=score, components=lead.score_breakdown, caps_applied=caps,
                       boosts=boosts, reasons=reasons)


def _apply_fail_closed(lead, known, ctx, strict, clear, score, capped, caps):
    """Senior mode fails closed: cap PURSUE when key context is missing.

    ``clear`` is True when there is a strong, unambiguous signal (strong freshness or
    a verified live deployment mismatch) that justifies pursuing despite thin context.
    """
    # No known/audit material: do not pursue weak-dedup leads unless the signal is clear.
    if not clear and not ctx.get("known_provided") and known.status in (M.KNOWN_NO_MATCH, M.KNOWN_UNKNOWN):
        if score > _PARK_CAP:
            score = _PARK_CAP
            capped = True
            caps.append("No known/audit material -> dedup confidence LOW, capped to PARK.")
    # Live-wiring-dependent lead without verified deployment.
    if _needs_deploy(lead) and not ctx.get("rpc_ran"):
        if score > _PARK_CAP:
            score = _PARK_CAP
            capped = True
            caps.append("Lead depends on live wiring but deployment was not verified -> capped to PARK.")
    # No freshness baseline at all.
    if not clear and lead.freshness_status == M.UNKNOWN_FRESHNESS and not ctx.get("baseline_provided"):
        if score > _PARK_CAP:
            score = _PARK_CAP
            capped = True
            caps.append("Unknown freshness without a baseline -> capped to PARK.")
    # Strict mode is more aggressive: any missing scope keeps everything below PURSUE.
    if strict and not ctx.get("scope_provided") and score > _PARK_MIN - 1:
        score = _PARK_MIN - 1
        capped = True
        caps.append("Strict context + no scope -> capped below PARK.")
    return score, capped


def _needs_deploy(lead: M.LeadCandidate) -> bool:
    # Only leads whose *value depends on deployed state* (proxy implementation,
    # registry pointer, migration target) need live verification. A fresh source
    # adapter is locally testable, so it is not parked merely for lack of RPC.
    deploy_signals = {"registry", "migration", "proxy"}
    if deploy_signals & set(lead.notes):
        return True
    return lead.freshness_status in (M.NEW_REGISTRY_ENTRY, M.NEW_IMPLEMENTATION, M.NEW_MIGRATION_PATH)


def _blocked(known: M.KnownIssueSignal) -> bool:
    return known.status in M.KNOWN_BLOCKING


def _reasons(lead, known, freshness, eligibility):
    out = []
    if lead.freshness_status in M.FRESHNESS_PRIORITY:
        out.append(f"+ freshness: {freshness.status} ({lead.freshness_score}).")
    elif lead.freshness_status == M.STALE:
        out.append(f"- freshness: stale / over-audited ({lead.freshness_score}).")
    else:
        out.append(f". freshness: {freshness.status} ({lead.freshness_score}).")
    if lead.materiality_score >= 70:
        out.append(f"+ materiality: value-bearing surface ({lead.materiality_score}).")
    if lead.attacker_reachability_score >= 70:
        out.append(f"+ reachability: externally reachable ({lead.attacker_reachability_score}).")
    elif lead.attacker_reachability_score <= 40:
        out.append(f"- reachability: limited external reachability ({lead.attacker_reachability_score}).")
    if lead.deployment_status in _DEPLOYMENT_BOOST_STATUSES:
        out.append(f"+ deployment: {lead.deployment_status} (live differs from source).")
    elif lead.deployment_status == M.DEPLOY_ADDRESS_NO_CODE:
        out.append("- deployment: address has no code.")
    elif lead.deployment_status == M.DEPLOY_LIVE_SOURCE_MATCH:
        out.append(". deployment: live implementation matches expected.")
    if known.status == M.KNOWN_NO_MATCH:
        out.append(f"+ dedup: no known match found (similarity {known.similarity_score}, {known.confidence}).")
    elif known.status != M.KNOWN_UNKNOWN:
        out.append(f"- dedup: {known.status} (dup risk {lead.duplicate_risk_score}, {known.confidence}).")
    else:
        out.append("- dedup: no known-issue material provided; confidence low.")
    if lead.proof_difficulty_score >= 70:
        out.append(f"- proof difficulty: requires a non-trivial local harness ({lead.proof_difficulty_score}).")
    if not eligibility.scope_provided:
        out.append("- scope: no scope file; cannot confirm eligibility.")
    return out
