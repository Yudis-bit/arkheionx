"""Tests for lens review-lane generation (all mandatory lanes present)."""
import unittest
from pathlib import Path

import arkheionx.protocol_lens as pl
from arkheionx.protocol_lens import models as m
from arkheionx.review_map import build_review_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "morpho_midnight_toy"
SCOPE = FIXTURE / "scope.md"
_ALLOWED = set(m.PRIORITIES)


class MorphoReviewLanesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        lens = pl.get_lens("morpho-midnight")
        rm = build_review_map(FIXTURE)
        ctx = pl.build_lens_context(lens, rm, FIXTURE, str(SCOPE))
        cls.data = pl.build_review_lanes(ctx)

    def test_all_mandatory_lanes_present(self) -> None:
        self.assertEqual(self.data["lane_count"], 10)
        ids = {lane["id"] for lane in self.data["lanes"]}
        for i in range(1, 11):
            self.assertIn(f"LANE-{i:02d}", ids)
        self.assertEqual(set(self.data["mandatory_lane_ids"]), ids)

    def test_lane_fields(self) -> None:
        for lane in self.data["lanes"]:
            self.assertIn(lane["priority"], _ALLOWED)
            self.assertTrue(lane["human_review_required"])
            self.assertTrue(lane["required_evidence"])
            self.assertTrue(lane["first_hypotheses"])
            self.assertIn("not severity", lane["not_severity"].lower())

    def test_kind_and_safety(self) -> None:
        self.assertEqual(self.data["kind"], m.KIND_LENS_LANES)
        self.assertTrue(self.data["human_review_required"])
        self.assertIn("filters", self.data)


if __name__ == "__main__":
    unittest.main()
