"""Tests for the hunter submission-risk engine."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"
RISK_VALUES = (M.RISK_LOW, M.RISK_MEDIUM, M.RISK_HIGH)


class SubmissionRiskTests(unittest.TestCase):
    def test_every_lead_has_a_submission_risk(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        lead_ids = {l.lead_id for l in res["pack"].leads}
        risk_ids = {r.lead_id for r in res["pack"].submission_risks}
        self.assertEqual(lead_ids, risk_ids)

    def test_risk_fields_are_valid(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        for r in res["pack"].submission_risks:
            self.assertIn(r.expected_severity_ceiling, M.SEVERITY_CEILINGS)
            for field in (r.duplicate_rejection_risk, r.oos_rejection_risk, r.trusted_role_rejection_risk,
                          r.known_corpus_gap_risk, r.deployment_context_gap_risk, r.materiality_risk,
                          r.proof_difficulty_risk):
                self.assertIn(field, RISK_VALUES)
            self.assertTrue(r.submit_ready_threshold)

    def test_blind_corpus_has_known_corpus_gap_risk(self) -> None:
        b = FX / "dedup_blind"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        for r in res["pack"].submission_risks:
            self.assertEqual(r.known_corpus_gap_risk, M.RISK_HIGH)

    def test_duplicate_lead_explains_rejection(self) -> None:
        b = FX / "duplicate_public_test"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        risks = res["pack"].submission_risks
        self.assertTrue(risks)
        self.assertTrue(any(r.reviewer_pushback for r in risks),
                        "a public-test-covered lead should explain rejection risk")


if __name__ == "__main__":
    unittest.main()
