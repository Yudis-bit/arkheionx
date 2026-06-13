"""Tests for lens scope-task generation (precise, bounded tasks)."""
import unittest
from pathlib import Path

import arkheionx.protocol_lens as pl
from arkheionx.protocol_lens import models as m
from arkheionx.review_map import build_review_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "fixed_credit_market_toy"
SCOPE = FIXTURE / "scope.md"


class FixedCreditMarketScopeTasksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        lens = pl.get_lens("fixed-credit-market")
        rm = build_review_map(FIXTURE)
        ctx = pl.build_lens_context(lens, rm, FIXTURE, str(SCOPE))
        cls.data = pl.build_scope_tasks(ctx)

    def test_tasks_generated(self) -> None:
        self.assertGreaterEqual(self.data["task_count"], 10)
        self.assertEqual(self.data["task_count"], len(self.data["tasks"]))

    def test_task_ids_unique(self) -> None:
        ids = [t["id"] for t in self.data["tasks"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_each_task_is_precise(self) -> None:
        lane_ids = {f"LANE-{i:02d}" for i in range(1, 11)}
        for t in self.data["tasks"]:
            self.assertTrue(t["hypothesis"])
            self.assertIn(t["lane_id"], lane_ids)
            self.assertTrue(t["invariant_at_risk"])
            self.assertTrue(t["expected_safe_behavior"])
            self.assertTrue(t["failure_condition"])
            self.assertTrue(t["suggested_test_name"])
            self.assertTrue(t["decision_rule"])
            self.assertTrue(t["duplicate_risk"])
            # Tasks are research instructions; never an exploit instruction.
            self.assertIn("local", t["exploit_attempt_description"].lower())

    def test_kind(self) -> None:
        self.assertEqual(self.data["kind"], m.KIND_LENS_TASKS)


if __name__ == "__main__":
    unittest.main()
