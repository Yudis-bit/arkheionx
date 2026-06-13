"""Tests for the lens evidence map (conservative 9-status classification)."""
import unittest
from pathlib import Path

import arkheionx.protocol_lens as pl
from arkheionx.protocol_lens import models as m
from arkheionx.review_map import build_review_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "fixed_credit_market_toy"
SCOPE = FIXTURE / "scope.md"


class FixedCreditMarketEvidenceMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        lens = pl.get_lens("fixed-credit-market")
        rm = build_review_map(FIXTURE)
        ctx = pl.build_lens_context(lens, rm, FIXTURE, str(SCOPE))
        cls.data = pl.build_evidence_map(ctx, FIXTURE)

    def test_one_item_per_invariant(self) -> None:
        self.assertEqual(len(self.data["items"]), 12)
        self.assertEqual(self.data["summary"]["invariants"], 12)

    def test_statuses_are_within_vocabulary(self) -> None:
        for it in self.data["items"]:
            self.assertIn(it["status"], m.EVIDENCE_STATUSES)
            self.assertTrue(it["rationale"])

    def test_no_fabricated_strong_evidence(self) -> None:
        # The toy fixture has no test that explicitly targets an INV-FCM-* id, so the
        # classifier must not mark any invariant DIRECTLY_TESTED_STRONG or FORMALLY_PROVEN.
        for it in self.data["items"]:
            self.assertNotIn(it["status"], (m.EV_DIRECTLY_TESTED_STRONG, m.EV_FORMALLY_PROVEN))

    def test_counts_and_rules_present(self) -> None:
        self.assertEqual(self.data["kind"], m.KIND_LENS_EVIDENCE)
        self.assertEqual(set(self.data["counts"].keys()), set(m.EVIDENCE_STATUSES))
        self.assertTrue(self.data["rules"])


if __name__ == "__main__":
    unittest.main()
