"""Tests for the hunter freshness engine (evidence-based, fail-closed)."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


class FreshnessTests(unittest.TestCase):
    def test_audited_function_not_boosted_without_evidence(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        legacy = [l for l in res["pack"].leads if l.contract == "LegacyVault"]
        self.assertTrue(legacy)
        for lead in legacy:
            self.assertEqual(lead.freshness_status, M.AUDIT_COVERED)
            self.assertNotIn(lead.freshness_status, M.FRESHNESS_POSITIVE)

    def test_state_machine_value_flow_is_fresh(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        wq = [l for l in res["pack"].leads if l.contract == "WithdrawalQueue"]
        self.assertTrue(wq)
        self.assertTrue(any(l.freshness_status == M.NEW_STATE_MACHINE_VALUE_FLOW for l in wq))

    def test_freshness_unknown_caps_lead(self) -> None:
        # Known corpus only (so dedup is not blind) but no baseline of any kind.
        b = FX / "queue_double_claim"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        for lead in res["pack"].leads:
            self.assertIn(lead.freshness_status, M.FRESHNESS_NO_BASELINE + (M.SOURCE_RECOVERED_NO_BASELINE,))
            self.assertNotIn(lead.decision, M.PURSUEABLE,
                             "no-baseline lead must not be pursueable without a clear signal")

    def test_fresh_allowlist_marks_fresh(self) -> None:
        b = FX / "adapter_withdrawability"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                fresh_allowlist=["Adapter"], write=False)
        adapter = [l for l in res["pack"].leads if l.contract == "Adapter"]
        self.assertTrue(adapter)
        self.assertTrue(any(l.freshness_status == M.POST_AUDIT_CHANGE for l in adapter))


if __name__ == "__main__":
    unittest.main()
