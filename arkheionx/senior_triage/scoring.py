"""Step 5 — research-priority scoring and the senior decision.

The score (0-100) is a *research-priority ordering*, not a severity and not a
validity claim. It only decides where a human should spend time first. The rules are
deliberately strict: out-of-scope and public-test-covered leads are forced to KILL,
high duplicate risk caps the score, trusted-role-only leads can never be PURSUE, and
without a scope file nothing is PURSUE.
"""
from __future__ import annotations

from . import models as M
from .known_issues import trusted_role_risk

# Component weights (sum = 100). "inverse" components reward a *low* raw score.
WEIGHTS = {
    "scope_confidence": 15,
    "freshness": 20,
    "attacker_reachability": 15,
    "materiality": 15,
    "duplicate_risk_inverse": 15,
    "trusted_role_risk_inverse": 10,
    "proof_difficulty_inverse": 5,
    "time_cost_inverse": 5,
}

_PURSUE_MIN = 75
_PARK_MIN = 45

_SCOPE_CONF_SCORE = {M.CONF_LOW: 30, M.CONF_MEDIUM: 60, M.CONF_HIGH: 85}


def _scope_confidence_score(eligibility: M.EligibilitySignal) -> int:
    if not eligibility.scope_provided:
        return 20
    return _SCOPE_CONF_SCORE.get(eligibility.scope_confidence, 30)


def _next_command(decision: str, surface: str, repo: str, scope_file: str) -> str:
    scope_flag = f" --scope-file {scope_file}" if scope_file else ""
    if decision == M.LEAD_PURSUE:
        return f"arkheionx review {repo}{scope_flag} --out .arkheionx/review"
    if decision == M.LEAD_PARK:
        return "Add scope/known/audit context (--known, --audits, --scope-file), then re-run arkheionx triage."
    return "Do not spend time here now; see 07-do-not-touch.md."


def apply_score(
    lead: M.LeadCandidate,
    eligibility: M.EligibilitySignal,
    known: M.KnownIssueSignal,
    freshness: M.FreshnessSignal,
    *,
    repo: str,
    scope_file: str,
) -> M.LeadScore:
    # Pull verdicts from the upstream signals onto the lead.
    lead.scope_confidence = _scope_confidence_score(eligibility)
    lead.duplicate_risk_score = known.duplicate_risk_score
    lead.dedup_status = known.status
    lead.trusted_role_risk_score = trusted_role_risk(lead, known)
    lead.freshness_score = freshness.score
    lead.freshness_status = freshness.status
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
        "proof_difficulty_inverse": (100 - lead.proof_difficulty_score) / 100 * WEIGHTS["proof_difficulty_inverse"],
        "time_cost_inverse": (100 - lead.time_cost_score) / 100 * WEIGHTS["time_cost_inverse"],
    }
    raw = int(round(sum(comps.values())))
    raw = max(0, min(raw, 100))

    reasons = _reasons(lead, known, freshness, eligibility)
    caps: list[str] = []
    score = raw

    strong_freshness = (
        lead.freshness_status in M.FRESHNESS_PRIORITY and lead.freshness_score >= 75
    )

    forced_kill = False
    if known.status == M.KNOWN_OUT_OF_SCOPE:
        forced_kill = True
        caps.append("Out of scope -> forced KILL.")
    elif known.status == M.KNOWN_PUBLIC_TEST and not strong_freshness:
        forced_kill = True
        caps.append("Public-test covered -> forced KILL (no strong freshness angle).")

    # High duplicate risk caps the score so it cannot reach PURSUE.
    if known.status in (M.KNOWN_LIKELY_DUP, M.KNOWN_ACK_RISK, M.KNOWN_DOCUMENTED, M.KNOWN_PUBLIC_TEST):
        if strong_freshness:
            if score > 60:
                score = 60
                caps.append("High duplicate risk with a freshness angle -> capped to PARK band.")
        elif score > _PARK_MIN - 1:
            score = _PARK_MIN - 1
            caps.append("High duplicate risk -> capped below PURSUE/PARK threshold.")

    # Trusted-role-only can never be PURSUE.
    if known.status == M.KNOWN_TRUSTED_ROLE and score > 60:
        score = 60
        caps.append("Trusted-role-only -> capped out of PURSUE.")

    # No scope -> never PURSUE.
    if not eligibility.scope_provided and score > 60:
        score = 60
        caps.append("No scope file -> capped out of PURSUE.")

    lead.research_priority_score = score

    # Decision.
    if forced_kill or score < _PARK_MIN:
        decision = M.LEAD_KILL
    elif score >= _PURSUE_MIN and not _blocked(known) and eligibility.scope_provided:
        decision = M.LEAD_PURSUE
    else:
        decision = M.LEAD_PARK
    lead.decision = decision

    # Submit readiness (triage never declares READY without independent local proof).
    if decision == M.LEAD_KILL:
        lead.submit_readiness = M.DO_NOT_SUBMIT
    elif not eligibility.scope_provided:
        lead.submit_readiness = M.NEEDS_SCOPE_CONFIRMATION
    elif known.status in (M.KNOWN_UNKNOWN, M.KNOWN_SIMILAR) or lead.duplicate_risk_score >= 55:
        lead.submit_readiness = M.NEEDS_DEDUP
    else:
        lead.submit_readiness = M.NEEDS_LOCAL_PROOF

    lead.next_command = _next_command(decision, lead.surface, repo, scope_file)
    lead.score_reasons = reasons + caps

    return M.LeadScore(
        total=score,
        components={k: round(v, 2) for k, v in comps.items()},
        caps_applied=caps,
        reasons=reasons,
    )


def _blocked(known: M.KnownIssueSignal) -> bool:
    return known.status in M.KNOWN_BLOCKING


def _reasons(
    lead: M.LeadCandidate,
    known: M.KnownIssueSignal,
    freshness: M.FreshnessSignal,
    eligibility: M.EligibilitySignal,
) -> list[str]:
    out: list[str] = []
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
    if known.status == M.KNOWN_NO_MATCH:
        out.append("+ dedup: no known match found.")
    elif known.status != M.KNOWN_UNKNOWN:
        out.append(f"- dedup: {known.status} (duplicate risk {lead.duplicate_risk_score}).")
    else:
        out.append("- dedup: no known-issue material provided; confidence low.")
    if lead.proof_difficulty_score >= 70:
        out.append(f"- proof difficulty: requires a non-trivial local harness ({lead.proof_difficulty_score}).")
    if not eligibility.scope_provided:
        out.append("- scope: no scope file; cannot confirm eligibility.")
    return out
