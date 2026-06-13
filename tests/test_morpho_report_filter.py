"""Tests for the lens report filter and evidence judge (never auto-confirm/submit)."""
import unittest
from pathlib import Path

import arkheionx.protocol_lens as pl
from arkheionx.protocol_lens import models as m
from arkheionx.review_map import build_review_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "morpho_midnight_toy"
SCOPE = FIXTURE / "scope.md"


class MorphoReportFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lens = pl.get_lens("morpho-midnight")
        cls.rm = build_review_map(FIXTURE)
        cls.ctx = pl.build_lens_context(cls.lens, cls.rm, FIXTURE, str(SCOPE))
        cls.judge = pl.judge_evidence(cls.ctx, FIXTURE)
        cls.report = pl.build_report_filter(cls.ctx, FIXTURE)

    def test_evidence_judge_never_auto_validates(self) -> None:
        # Static analysis cannot confirm a vulnerability; no grade A and no
        # VALIDATED_CANDIDATE may be auto-emitted.
        for g in self.judge["grades"]:
            self.assertNotEqual(g["grade"], m.GRADE_A)
            self.assertNotEqual(g["decision"], m.JUDGE_VALIDATED_CANDIDATE)
        self.assertEqual(self.judge["grade_counts"].get(m.GRADE_A, 0), 0)
        self.assertEqual(self.judge["decision_counts"].get(m.JUDGE_VALIDATED_CANDIDATE, 0), 0)

    def test_report_filter_checklist_and_outcomes(self) -> None:
        self.assertEqual(len(self.report["checklist"]), 15)
        for d in self.report["decisions"]:
            self.assertIn(d["outcome"], m.REPORT_OUTCOMES)

    def test_report_filter_blocks_weak_candidates(self) -> None:
        # On a fixture with no human-run PoC, nothing is READY; weak candidates are
        # held back (NEEDS_MORE_EVIDENCE or a DO_NOT_SUBMIT_* outcome).
        outcomes = {d["outcome"] for d in self.report["decisions"]}
        self.assertNotIn(m.REPORT_READY_FOR_HUMAN_REVIEW, outcomes)
        blocking = {
            m.REPORT_NEEDS_MORE_EVIDENCE,
            m.REPORT_DO_NOT_SUBMIT_DUPLICATE_RISK,
            m.REPORT_DO_NOT_SUBMIT_OUT_OF_SCOPE,
            m.REPORT_DO_NOT_SUBMIT_WEAK_IMPACT,
            m.REPORT_DO_NOT_SUBMIT_INVALID_SETUP,
        }
        self.assertTrue(outcomes.issubset(blocking) or not outcomes)
        self.assertIn("human decision required", self.report["note"].lower())


if __name__ == "__main__":
    unittest.main()
