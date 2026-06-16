"""Tests for the hunter report filter (default Submit: NO)."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack
from arkheionx.hunter.report_filter import SUBMIT_AFTER_POC, SUBMIT_NO

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def smoke():
    b = FX / "fresh_state_machine_value_flow"
    return build_hunter_pack(b, scope_file=str(b / "scope.md"),
                             known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)


class ReportFilterTests(unittest.TestCase):
    def test_every_lead_has_a_row(self) -> None:
        res = smoke()
        self.assertEqual({l.lead_id for l in res["pack"].leads},
                         {r.lead_id for r in res["pack"].report_filter})

    def test_submit_values_are_no_or_after_poc(self) -> None:
        res = smoke()
        for row in res["pack"].report_filter:
            self.assertIn(row.submit, (SUBMIT_NO, SUBMIT_AFTER_POC))
            self.assertNotEqual(row.submit, "YES", "the report filter must never emit a bare YES")

    def test_human_rewrite_always_required(self) -> None:
        res = smoke()
        for row in res["pack"].report_filter:
            self.assertTrue(row.human_rewrite_required)

    def test_killed_and_parked_default_to_no(self) -> None:
        b = FX / "dedup_blind"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        for row in res["pack"].report_filter:
            self.assertEqual(row.submit, SUBMIT_NO)

    def test_duplicate_kill_is_submit_no(self) -> None:
        b = FX / "duplicate_public_test"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        for row in res["pack"].report_filter:
            self.assertEqual(row.submit, SUBMIT_NO)
            self.assertTrue(row.reason)

    def test_report_filter_in_triage_json(self) -> None:
        res = smoke()
        rows = res["triage"]["report_filter"]
        self.assertTrue(rows)
        for row in rows:
            self.assertIn(row["submit"], (SUBMIT_NO, SUBMIT_AFTER_POC))
            self.assertTrue(row["human_rewrite_required"])


if __name__ == "__main__":
    unittest.main()
