"""Tests for report protocol-graph context (v3.8, Agent 8).

Supporting review context only: the report stays a draft requiring manual review;
graph warnings are reviewer orientation, never confirmed findings.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.evidence.builder import build_evidence, build_protocol_graph_context
from arkheionx.intelligence import assumptions as A
from arkheionx.intelligence import coverage as COV
from arkheionx.intelligence import graph as G
from arkheionx.intelligence import roles as R
from arkheionx.intelligence import test_gaps as TG
from arkheionx.intelligence import value_paths as V
from arkheionx.proof.payloads import target_slug
from arkheionx.protocol.detector import analyze
from arkheionx.reporting.builder import build_report
from arkheionx.reporting.render import render_report

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "oracle-staking-fixture"


def _graph_and_coverage():
    cls = R.classify_function_role(function_name="withdraw", contract_name="Vault")
    cls.metadata["function_id"] = "function:w"
    vp = V.build_value_path_from_role_classification(cls, function_id="function:w")
    asms = A.build_assumptions_from_value_path(vp)
    gaps = []
    for a in asms:
        gaps += TG.build_test_gaps_from_assumption(a)
    gaps[0] = TG.correlate_test_gap_with_local_validation(gaps[0], local_validation_ids=["lv1"], tested=True)
    graph = G.build_protocol_intelligence_graph("Proto", [cls], [vp], asms, gaps, local_validation_ids=["lv1"])
    cov = COV.correlate_local_validation_coverage("Proto", graph=graph, test_gaps=gaps, local_validation_ids=["lv1"])
    return graph, cov


def _ctx():
    g, cov = _graph_and_coverage()
    return build_protocol_graph_context(g, cov)


def _build_report(tmp, *, with_graph):
    writer = ArtifactWriter(Path(tmp))
    analysis = analyze(FIXTURE)
    match = next(f for f in analysis.all_functions if f.function_name == "stake")
    slug = target_slug(match.display_id)
    writer.write_text(f"proof/{slug}/proof.json", json.dumps({
        "proof_receipt_id": f"proof:{slug}", "target_id": "t", "review_map_target": "OracleRewardFixture.stake",
        "evidence_level": "EXECUTION_CONFIRMED", "status": "tested_passed",
        "foundry": {"test_command": "forge test"},
        "test_result": {"tests_run": 1, "passed": 1, "failed": 0, "skipped": 0,
                        "failed_tests": [], "skipped_tests": [], "raw_output_path": "x.txt"},
        "generated_files": [],
    }))
    writer.write_text(f"proof/{slug}/trace.json", json.dumps({
        "trace_receipt_id": f"trace:{slug}", "review_map_target": "OracleRewardFixture.stake",
        "evidence_level": "EXECUTION_CONFIRMED", "status": "tested_passed",
        "reverts": [], "call_sequence": ["A::b()"], "assertion_failures": [], "logs": [],
    }))
    graph, cov = _graph_and_coverage() if with_graph else (None, None)
    pkg = build_evidence(match, FIXTURE, writer, analysis, protocol_graph=graph, coverage_summary=cov)
    return build_report(pkg.payload, FIXTURE, writer)


class ReportBuildTests(unittest.TestCase):
    def test_build_without_graph_context_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = _build_report(tmp, with_graph=False)
            self.assertNotIn("protocol_graph_context", draft.payload)

    def test_build_summarizes_evidence_graph_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = _build_report(tmp, with_graph=True)
            self.assertIn("protocol_graph_context", draft.payload)
            self.assertTrue(draft.payload["protocol_graph_context"]["observed"])

    def test_graph_context_includes_graph_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = _build_report(tmp, with_graph=True)
            expected = draft.payload["protocol_graph_context"]["graph_id"]
            self.assertTrue(expected.startswith("protocol-intelligence-graph:"))
            # round-trip: report graph_id matches the evidence graph context graph_id
            self.assertEqual(draft.payload["protocol_graph_context"]["graph_id"], expected)

    def _rctx(self, tmp):
        return _build_report(tmp, with_graph=True).payload["protocol_graph_context"]

    def test_includes_function_role_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertGreaterEqual(self._rctx(tmp)["function_role_count"], 1)

    def test_includes_value_path_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertGreaterEqual(self._rctx(tmp)["value_path_count"], 1)

    def test_includes_assumption_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertGreaterEqual(self._rctx(tmp)["assumption_count"], 1)

    def test_includes_test_gap_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertGreaterEqual(self._rctx(tmp)["test_gap_count"], 1)

    def test_includes_coverage_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertGreaterEqual(self._rctx(tmp)["coverage_count"], 1)

    def test_includes_tested_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertGreaterEqual(self._rctx(tmp)["tested_count"], 1)

    def test_includes_trace_bound_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn("trace_bound_count", self._rctx(tmp))


class ReportSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.draft = _build_report(self.tmp, with_graph=True)
        self.payload = self.draft.payload

    def test_report_remains_draft(self) -> None:
        self.assertEqual(self.payload["review_status"], "NEEDS_HUMAN_REVIEW")

    def test_report_manual_review_required(self) -> None:
        self.assertTrue(self.payload["protocol_graph_context"]["manual_review_required"])

    def test_report_ready_false(self) -> None:
        self.assertFalse(self.payload["protocol_graph_context"]["ready_for_submission"])
        self.assertFalse(self.payload["report_readiness"].get("ready_for_submission", False))

    def test_no_human_reviewed(self) -> None:
        self.assertNotIn("HUMAN_REVIEWED", json.dumps(self.payload["protocol_graph_context"]))

    def test_no_confirmed_vulnerability(self) -> None:
        self.assertNotIn("confirmed vulnerability", json.dumps(self.payload["protocol_graph_context"]).lower())

    def test_no_final_severity(self) -> None:
        self.assertNotIn("final severity", json.dumps(self.payload["protocol_graph_context"]).lower())

    def test_no_audit_passed(self) -> None:
        self.assertNotIn("audit passed", json.dumps(self.payload["protocol_graph_context"]).lower())

    def test_no_bounty_eligibility(self) -> None:
        self.assertNotIn("bounty eligible", json.dumps(self.payload["protocol_graph_context"]).lower())

    def test_claim_references_remain_needs_human_review(self) -> None:
        for claim in self.payload.get("claim_references", []):
            self.assertEqual(claim.get("status"), "needs_human_review")

    def test_graph_warnings_remain_context_only(self) -> None:
        # warning_count is a count, never a confirmed finding.
        self.assertIsInstance(self.payload["protocol_graph_context"]["warning_count"], int)

    def test_json_serializable(self) -> None:
        data = self.payload["protocol_graph_context"]
        self.assertEqual(json.loads(json.dumps(data)), data)


class ReportRenderTests(unittest.TestCase):
    def test_render_includes_section_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = _build_report(tmp, with_graph=True)
            self.assertIn("Protocol Graph Context", render_report(draft, "proj"))

    def test_render_omits_section_when_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = _build_report(tmp, with_graph=False)
            self.assertNotIn("Protocol Graph Context", render_report(draft, "proj"))


if __name__ == "__main__":
    unittest.main()
