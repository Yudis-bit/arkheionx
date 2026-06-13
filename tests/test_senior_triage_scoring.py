"""Scoring + senior-decision tests for `arkheionx triage`."""
import unittest

from arkheionx.senior_triage import models as M
from arkheionx.senior_triage import scoring


def _eligibility(scope_provided: bool = True) -> M.EligibilitySignal:
    return M.EligibilitySignal(
        scope_provided=scope_provided,
        scope_confidence=M.CONF_HIGH if scope_provided else M.CONF_LOW,
        target_decision=M.TARGET_TOUCH if scope_provided else M.TARGET_NEEDS_CONTEXT,
        severity_ceiling=M.SEV_HIGH if scope_provided else M.SEV_UNKNOWN,
    )


def _lead(lead_id: str = "LEAD-001") -> M.LeadCandidate:
    # A clean, reachable, value-bearing surface.
    return M.LeadCandidate(
        id=lead_id,
        title="Value-out surface",
        surface="Vault.withdraw",
        reason="moves value out",
        linked_functions=["Vault.withdraw"],
        attacker_reachability_score=85,
        materiality_score=85,
        proof_difficulty_score=50,
        time_cost_score=45,
        kill_condition="Kill if a local test shows value cannot move without authorization.",
        notes=["value-out"],
    )


def _known(status: str, dup: int) -> M.KnownIssueSignal:
    return M.KnownIssueSignal(lead_id="LEAD-001", status=status, duplicate_risk_score=dup)


def _fresh(status: str, score: int) -> M.FreshnessSignal:
    return M.FreshnessSignal(lead_id="LEAD-001", status=status, score=score)


class ScoringTests(unittest.TestCase):
    def test_weights_sum_to_100(self) -> None:
        self.assertEqual(sum(scoring.WEIGHTS.values()), 100)

    def test_fresh_post_audit_increases_score(self) -> None:
        elig = _eligibility()
        known = _known(M.KNOWN_NO_MATCH, 15)
        fresh_lead, stale_lead = _lead(), _lead()
        fresh_score = scoring.apply_score(
            fresh_lead, elig, known, _fresh(M.NEW_ADAPTER, 85), repo=".", scope_file="scope.md")
        stale_score = scoring.apply_score(
            stale_lead, elig, known, _fresh(M.STALE, 20), repo=".", scope_file="scope.md")
        self.assertGreater(fresh_score.total, stale_score.total)
        self.assertGreaterEqual(fresh_lead.research_priority_score, 75)

    def test_high_duplicate_risk_caps_score(self) -> None:
        elig = _eligibility()
        clean = _lead()
        dup = _lead()
        scoring.apply_score(clean, elig, _known(M.KNOWN_NO_MATCH, 15), _fresh(M.FRESH, 60),
                            repo=".", scope_file="scope.md")
        scoring.apply_score(dup, elig, _known(M.KNOWN_LIKELY_DUP, 85), _fresh(M.FRESH, 60),
                            repo=".", scope_file="scope.md")
        self.assertLess(dup.research_priority_score, clean.research_priority_score)
        self.assertNotEqual(dup.decision, M.LEAD_PURSUE)

    def test_out_of_scope_forces_kill(self) -> None:
        lead = _lead()
        scoring.apply_score(lead, _eligibility(), _known(M.KNOWN_OUT_OF_SCOPE, 60),
                            _fresh(M.NEW_ADAPTER, 85), repo=".", scope_file="scope.md")
        self.assertEqual(lead.decision, M.LEAD_KILL)
        self.assertEqual(lead.submit_readiness, M.DO_NOT_SUBMIT)

    def test_public_test_covered_forces_kill(self) -> None:
        lead = _lead()
        scoring.apply_score(lead, _eligibility(), _known(M.KNOWN_PUBLIC_TEST, 90),
                            _fresh(M.STALE, 20), repo=".", scope_file="scope.md")
        self.assertEqual(lead.decision, M.LEAD_KILL)

    def test_trusted_role_only_never_pursue(self) -> None:
        lead = _lead()
        lead.notes = ["value-out", "privileged"]
        scoring.apply_score(lead, _eligibility(), _known(M.KNOWN_TRUSTED_ROLE, 40),
                            _fresh(M.NEW_ADAPTER, 85), repo=".", scope_file="scope.md")
        self.assertIn(lead.decision, (M.LEAD_PARK, M.LEAD_KILL))
        self.assertNotEqual(lead.decision, M.LEAD_PURSUE)

    def test_no_scope_never_pursue(self) -> None:
        lead = _lead()
        scoring.apply_score(lead, _eligibility(scope_provided=False), _known(M.KNOWN_NO_MATCH, 15),
                            _fresh(M.NEW_ADAPTER, 85), repo=".", scope_file="")
        self.assertNotEqual(lead.decision, M.LEAD_PURSUE)

    def test_score_is_explainable(self) -> None:
        lead = _lead()
        result = scoring.apply_score(lead, _eligibility(), _known(M.KNOWN_NO_MATCH, 15),
                                     _fresh(M.NEW_ADAPTER, 85), repo=".", scope_file="scope.md")
        self.assertTrue(result.reasons)
        self.assertTrue(lead.score_reasons)
        self.assertTrue(0 <= lead.research_priority_score <= 100)


if __name__ == "__main__":
    unittest.main()
