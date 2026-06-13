"""Tests for the Morpho Midnight lens model content and label vocabularies."""
import json
import unittest

import arkheionx.protocol_lens as pl
from arkheionx.protocol_lens import models as m


class MorphoMidnightLensModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lens = pl.get_lens("morpho-midnight")

    def test_fourteen_behavior_promises(self) -> None:
        promises = self.lens.behavior_promises()
        self.assertEqual(len(promises), 14)
        ids = [p.id for p in promises]
        self.assertEqual(ids, [f"PROMISE-MM-{i:02d}" for i in range(1, 15)])
        for p in promises:
            self.assertTrue(p.text)
            self.assertTrue(p.violation_condition)
            self.assertTrue(p.missing_evidence)

    def test_twelve_economic_invariants(self) -> None:
        invs = self.lens.economic_invariants()
        self.assertEqual(len(invs), 12)
        ids = [i.id for i in invs]
        self.assertEqual(ids, [f"INV-MM-{i:02d}" for i in range(1, 13)])
        for inv in invs:
            self.assertTrue(inv.statement)
            self.assertTrue(inv.impact_if_broken)

    def test_ten_review_lanes(self) -> None:
        lanes = self.lens.review_lanes()
        self.assertEqual(len(lanes), 10)
        ids = [ld.lane_id for ld in lanes]
        self.assertEqual(ids, [f"LANE-{i:02d}" for i in range(1, 11)])
        for ld in lanes:
            self.assertIn(ld.default_priority, m.PRIORITIES)
            self.assertTrue(ld.focus_keywords)
            self.assertTrue(ld.first_hypotheses)
            # Every lane's at-risk invariants must reference real invariant ids.
            for iid in ld.invariants_at_risk:
                self.assertIn(iid, self.lens.invariant_by_id())

    def test_extraction_groups_and_temporal_windows(self) -> None:
        groups = {g.group_id for g in self.lens.extraction_groups()}
        self.assertEqual(groups, {"markets", "positions", "market_state", "offers", "periphery"})
        self.assertGreaterEqual(len(self.lens.temporal_windows()), 1)

    def test_label_vocabulary_sizes(self) -> None:
        self.assertEqual(len(m.EVIDENCE_STATUSES), 9)
        self.assertEqual(len(m.GRADES), 5)
        self.assertEqual(len(m.JUDGE_DECISIONS), 6)
        self.assertEqual(len(m.REPORT_OUTCOMES), 6)
        self.assertEqual(m.SCOPE_INCOMPLETE_LOCAL_ONLY, "SCOPE_INCOMPLETE_LOCAL_ONLY")

    def test_model_dict_is_json_serializable(self) -> None:
        d = self.lens.to_model_dict()
        s = json.dumps(d)  # must not raise
        self.assertIn("morpho-midnight", s)
        self.assertEqual(d["lens"]["lens_id"], "morpho-midnight")
        self.assertEqual(len(d["behavior_promises"]), 14)
        self.assertEqual(len(d["economic_invariants"]), 12)
        self.assertEqual(len(d["review_lanes"]), 10)


if __name__ == "__main__":
    unittest.main()
