"""Tests for evidence protocol-graph context (v3.8, Agent 8).

Supporting review context only: a graph warning is not a vulnerability and a
graph error is not a final severity. Evidence readiness semantics are unchanged.
"""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.evidence.builder import build_evidence, build_protocol_graph_context
from arkheionx.evidence.render import evidence_text, render_evidence
from arkheionx.evidence.validate import validate_protocol_graph_context
from arkheionx.intelligence import assumptions as A
from arkheionx.intelligence import coverage as COV
from arkheionx.intelligence import graph as G
from arkheionx.intelligence import roles as R
from arkheionx.intelligence import test_gaps as TG
from arkheionx.intelligence import value_paths as V
from arkheionx.proof.payloads import target_slug
from arkheionx.protocol.detector import analyze

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


class GraphContextHelperTests(unittest.TestCase):
    def test_none_when_inputs_absent(self) -> None:
        self.assertIsNone(build_protocol_graph_context(None, None))

    def test_graph_only_includes_graph_id(self) -> None:
        g, _ = _graph_and_coverage()
        self.assertEqual(build_protocol_graph_context(g)["graph_id"], g.graph_id)

    def test_graph_only_includes_counts(self) -> None:
        g, _ = _graph_and_coverage()
        ctx = build_protocol_graph_context(g)
        for key in ("node_count", "edge_count", "warning_count", "error_count"):
            self.assertIn(key, ctx)
        self.assertGreaterEqual(ctx["node_count"], 1)

    def test_graph_only_includes_linked_ids(self) -> None:
        g, _ = _graph_and_coverage()
        ctx = build_protocol_graph_context(g)
        self.assertIn("function:w", ctx["linked_function_ids"])
        self.assertTrue(ctx["linked_value_path_ids"])
        self.assertTrue(ctx["linked_assumption_ids"])
        self.assertTrue(ctx["linked_test_gap_ids"])

    def test_coverage_only_includes_counts(self) -> None:
        _, cov = _graph_and_coverage()
        ctx = build_protocol_graph_context(None, cov)
        self.assertGreaterEqual(ctx["coverage_count"], 1)
        self.assertGreaterEqual(ctx["tested_count"], 1)
        self.assertIn("trace_bound_count", ctx)

    def test_combined_includes_graph_and_coverage(self) -> None:
        ctx = _ctx()
        self.assertGreaterEqual(ctx["node_count"], 1)
        self.assertGreaterEqual(ctx["coverage_count"], 1)

    def test_manual_review_true(self) -> None:
        self.assertTrue(_ctx()["manual_review_required"])

    def test_ready_false(self) -> None:
        self.assertFalse(_ctx()["ready_for_submission"])

    def test_support_note_non_final(self) -> None:
        note = _ctx()["support_note"].lower()
        self.assertIn("supporting review context only", note)
        for token in ("confirmed vulnerability", "final severity", "audit passed", "safe"):
            self.assertNotIn(token, note)

    def test_no_mutation_of_graph(self) -> None:
        g, cov = _graph_and_coverage()
        before = G.graph_to_dict(g)
        build_protocol_graph_context(g, cov)
        self.assertEqual(G.graph_to_dict(g), before)

    def test_no_mutation_of_coverage(self) -> None:
        g, cov = _graph_and_coverage()
        before = COV.coverage_to_dict(cov)
        build_protocol_graph_context(g, cov)
        self.assertEqual(COV.coverage_to_dict(cov), before)

    def test_json_serializable(self) -> None:
        ctx = _ctx()
        self.assertEqual(json.loads(json.dumps(ctx)), ctx)


class EvidenceBuildTests(unittest.TestCase):
    def _match(self):
        analysis = analyze(FIXTURE)
        return next(f for f in analysis.all_functions if f.function_name == "stake"), analysis

    def _write_proof(self, writer, slug, *, with_trace):
        proof = {
            "proof_receipt_id": f"proof:{slug}", "target_id": "t", "review_map_target": "OracleRewardFixture.stake",
            "evidence_level": "EXECUTION_CONFIRMED", "status": "tested_passed",
            "foundry": {"test_command": "forge test"},
            "test_result": {"tests_run": 1, "passed": 1, "failed": 0, "skipped": 0,
                            "failed_tests": [], "skipped_tests": [], "raw_output_path": "x.txt"},
            "generated_files": [],
        }
        writer.write_text(f"proof/{slug}/proof.json", json.dumps(proof))
        if with_trace:
            writer.write_text(f"proof/{slug}/trace.json", json.dumps({
                "trace_receipt_id": f"trace:{slug}", "review_map_target": "OracleRewardFixture.stake",
                "evidence_level": "EXECUTION_CONFIRMED", "status": "tested_passed",
                "reverts": [], "call_sequence": ["A::b()"], "assertion_failures": [], "logs": [],
            }))

    def _build(self, tmp, *, with_trace, with_graph):
        writer = ArtifactWriter(Path(tmp))
        match, analysis = self._match()
        self._write_proof(writer, target_slug(match.display_id), with_trace=with_trace)
        graph, cov = _graph_and_coverage() if with_graph else (None, None)
        return build_evidence(match, FIXTURE, writer, analysis, protocol_graph=graph, coverage_summary=cov)

    def test_build_without_graph_context_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = self._build(tmp, with_trace=True, with_graph=False)
            self.assertNotIn("protocol_graph_context", pkg.payload)
            self.assertEqual(pkg.evidence_level, "EVIDENCE_READY")

    def test_build_attaches_graph_context_when_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = self._build(tmp, with_trace=True, with_graph=True)
            self.assertIn("protocol_graph_context", pkg.payload)
            self.assertTrue(pkg.payload["protocol_graph_context"]["observed"])

    def test_readiness_unchanged_with_graph_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._build(tmp, with_trace=True, with_graph=True).evidence_level, "EVIDENCE_READY")

    def test_tested_only_coverage_does_not_create_evidence_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = self._build(tmp, with_trace=False, with_graph=True)
            self.assertEqual(pkg.evidence_level, "EXECUTION_CONFIRMED")  # not EVIDENCE_READY

    def test_trace_bound_coverage_does_not_override_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # No trace artifact -> stays EXECUTION_CONFIRMED even with trace-bound graph coverage.
            pkg = self._build(tmp, with_trace=False, with_graph=True)
            self.assertNotEqual(pkg.evidence_level, "EVIDENCE_READY")


class EvidenceRenderTests(unittest.TestCase):
    def _payload_with_ctx(self):
        return {
            "target": "C.f", "evidence_level": "EXECUTION_CONFIRMED", "status": "tested_passed",
            "generated_at": "t",
            "proof_summary": {"status": "tested_passed", "tests_run": 1, "passed": 1, "failed": 0,
                              "skipped": 0, "foundry_command": "forge test"},
            "impact_notes": {"candidate_impact": "x", "affected_components": ["C"], "limitations": ["l"]},
            "source_artifacts": {"proof_json": "p"},
            "protocol_graph_context": _ctx(),
        }

    def test_render_includes_section_when_present(self) -> None:
        self.assertIn("Protocol Graph Context", evidence_text(self._payload_with_ctx()))

    def test_render_omits_section_when_absent(self) -> None:
        payload = self._payload_with_ctx()
        del payload["protocol_graph_context"]
        self.assertNotIn("Protocol Graph Context", evidence_text(payload))


class EvidenceValidationTests(unittest.TestCase):
    def test_accepts_safe_graph_context(self) -> None:
        self.assertEqual(validate_protocol_graph_context(_ctx()), [])

    def test_flags_ready_for_submission_true(self) -> None:
        ctx = _ctx(); ctx["ready_for_submission"] = True
        self.assertTrue(any("ready_for_submission" in i for i in validate_protocol_graph_context(ctx)))

    def test_flags_manual_review_false(self) -> None:
        ctx = _ctx(); ctx["manual_review_required"] = False
        self.assertTrue(any("manual review" in i for i in validate_protocol_graph_context(ctx)))

    def test_flags_human_reviewed(self) -> None:
        ctx = _ctx(); ctx["warnings"] = ["HUMAN_REVIEWED"]
        self.assertTrue(any("HUMAN_REVIEWED" in i for i in validate_protocol_graph_context(ctx)))

    def test_flags_confirmed_vulnerability(self) -> None:
        ctx = _ctx(); ctx["support_note"] = "this is a confirmed vulnerability"
        self.assertTrue(any("disallowed phrase" in i for i in validate_protocol_graph_context(ctx)))

    def test_flags_final_severity(self) -> None:
        ctx = _ctx(); ctx["support_note"] = "final severity assigned"
        self.assertTrue(any("disallowed phrase" in i for i in validate_protocol_graph_context(ctx)))

    def test_flags_audit_passed(self) -> None:
        ctx = _ctx(); ctx["support_note"] = "audit passed"
        self.assertTrue(any("disallowed phrase" in i for i in validate_protocol_graph_context(ctx)))

    def test_flags_bounty_eligibility(self) -> None:
        ctx = _ctx(); ctx["support_note"] = "bounty eligible now"
        self.assertTrue(any("disallowed phrase" in i for i in validate_protocol_graph_context(ctx)))

    def test_non_dict_ignored(self) -> None:
        self.assertEqual(validate_protocol_graph_context(None), [])

    def test_graph_warning_not_vulnerability_claim(self) -> None:
        ctx = _ctx(); ctx["warning_count"] = 5  # warnings are counts, not findings
        self.assertEqual(validate_protocol_graph_context(ctx), [])

    def test_graph_error_not_final_severity(self) -> None:
        ctx = _ctx(); ctx["error_count"] = 3  # errors are structural, not severity
        self.assertEqual(validate_protocol_graph_context(ctx), [])


if __name__ == "__main__":
    unittest.main()
