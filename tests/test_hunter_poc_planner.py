"""Tests for the hunter PoC planner."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def smoke():
    b = FX / "fresh_state_machine_value_flow"
    return build_hunter_pack(b, scope_file=str(b / "scope.md"),
                             known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)


class PocPlannerTests(unittest.TestCase):
    def test_plans_only_for_pursueable_leads(self) -> None:
        res = smoke()
        pursueable_ids = {l.lead_id for l in res["pack"].leads if l.decision in M.PURSUEABLE}
        plan_ids = {p.lead_id for p in res["pack"].poc_plans}
        self.assertTrue(plan_ids)
        self.assertEqual(plan_ids, pursueable_ids,
                         "a PoC plan must exist exactly for the pursueable leads")

    def test_no_plan_for_killed_lead(self) -> None:
        b = FX / "duplicate_public_test"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        killed = {l.lead_id for l in res["pack"].leads if l.decision in M.KILL_DECISIONS}
        plan_ids = {p.lead_id for p in res["pack"].poc_plans}
        self.assertFalse(plan_ids & killed, "no PoC plan for a killed/duplicate/OOS/trusted-role lead")

    def test_every_plan_has_report_condition(self) -> None:
        res = smoke()
        for p in res["pack"].poc_plans:
            self.assertEqual(p.report_condition, "Do not write a report until the expected assertion passes.")
            self.assertIn(p.status, M.POC_STATUSES)
            self.assertTrue(p.expected_assertion)
            self.assertTrue(p.kill_condition)
            self.assertTrue(p.minimal_skeleton)

    def test_lead_links_to_plan(self) -> None:
        res = smoke()
        plan_ids = {p.poc_plan_id for p in res["pack"].poc_plans}
        for lead in res["pack"].leads:
            if lead.decision in M.PURSUEABLE:
                self.assertIn(lead.poc_plan_id, plan_ids)


if __name__ == "__main__":
    unittest.main()
