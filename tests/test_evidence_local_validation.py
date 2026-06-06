"""Tests for local-validation support in the evidence workflow (v3.7)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from arkheionx import local_validation as lv
from arkheionx.artifacts import ArtifactWriter
from arkheionx.evidence.builder import build_evidence, build_local_validation_support
from arkheionx.evidence.render import evidence_text, render_evidence
from arkheionx.proof.payloads import target_slug
from arkheionx.protocol.detector import analyze

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "oracle-staking-fixture"


def _match(name: str = "stake"):
    analysis = analyze(FIXTURE)
    return next(f for f in analysis.all_functions if f.function_name == name), analysis


def _write_proof(writer: ArtifactWriter, slug: str, *, with_trace: bool) -> None:
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


def _result(name, status, *, contract="C", function="f", trace=False, linked=None):
    return lv.LocalTestResult(
        test_name=name, contract_name=contract, function_name=function, status=status,
        linked_function_ids=list(linked or []), metadata={"trace": {"call_count": 1}} if trace else {})


def _write_lv(repo: Path, results) -> None:
    parsed = lv.ParsedFoundryOutput(test_results=list(results))
    build = lv.build_local_validation_from_parsed(parsed, repo_fingerprint=lv.repo_fingerprint(str(repo)))
    lv.write_local_validation_artifacts(build, repo_path=str(repo))


def _support(repo: Path, **kw):
    return build_local_validation_support(ArtifactWriter(repo), **kw)


class SupportBuilderTests(unittest.TestCase):
    def test_missing_folder_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(_support(Path(tmp)))

    def test_passing_test_is_support_tested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_lv(Path(tmp), [_result("testA()", lv.TEST_PASSED)])
            block = _support(Path(tmp))
            self.assertEqual(block["tested_count"], 1)
            self.assertEqual(block["trace_bound_count"], 0)
            self.assertEqual(block["entries"][0]["support_level"], "SUPPORT_TESTED")

    def test_failed_skipped_error_are_not_positive_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_lv(Path(tmp), [_result("f()", lv.TEST_FAILED), _result("s()", lv.TEST_SKIPPED),
                                  _result("e()", lv.TEST_ERROR)])
            block = _support(Path(tmp))
            self.assertEqual(block["tested_count"], 0)
            self.assertEqual(block["trace_bound_count"], 0)
            self.assertEqual(block["needs_review_count"], 3)
            for e in block["entries"]:
                self.assertEqual(e["support_level"], "SUPPORT_NONE")
                self.assertTrue(e["warnings"])

    def test_trace_bound_only_with_explicit_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_lv(Path(tmp), [_result("withTrace()", lv.TEST_PASSED, trace=True),
                                  _result("noTrace()", lv.TEST_PASSED, trace=False)])
            block = _support(Path(tmp))
            levels = {e["test_name"]: e["support_level"] for e in block["entries"]}
            self.assertEqual(levels["withTrace()"], "SUPPORT_TRACE_BOUND")
            self.assertEqual(levels["noTrace()"], "SUPPORT_TESTED")
            self.assertEqual(block["trace_bound_count"], 1)

    def test_no_human_reviewed_or_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_lv(Path(tmp), [_result("testA()", lv.TEST_PASSED)])
            block = _support(Path(tmp))
            self.assertIs(block["manual_review_required"], True)
            self.assertIs(block["ready_for_submission"], False)
            self.assertNotIn("HUMAN_REVIEWED", json.dumps(block))

    def test_linked_ids_copied_not_invented(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_lv(Path(tmp), [_result("testA()", lv.TEST_PASSED, linked=["function:abc"])])
            entry = _support(Path(tmp))["entries"][0]
            self.assertEqual(entry["linked_function_ids"], ["function:abc"])
            self.assertEqual(entry["linked_assumption_ids"], [])

    def test_unlinked_test_is_context_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_lv(Path(tmp), [_result("testA()", lv.TEST_PASSED)])
            entry = _support(Path(tmp))["entries"][0]
            self.assertEqual(entry["linked_function_ids"], [])
            self.assertEqual(entry["support_level"], "SUPPORT_TESTED")

    def test_target_filter_exact_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_lv(Path(tmp), [_result("a()", lv.TEST_PASSED, contract="LendingVault", function="deposit")])
            self.assertIsNotNone(_support(Path(tmp), contract_name="LendingVault", function_name="deposit"))
            self.assertIsNone(_support(Path(tmp), contract_name="LendingVault", function_name="deposi"))

    def test_malformed_result_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_lv(Path(tmp), [_result("testA()", lv.TEST_PASSED)])
            bad = Path(tmp) / ".arkheionx" / "out" / "local-validation" / "results" / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            block = _support(Path(tmp))  # does not raise
            self.assertEqual(block["tested_count"], 1)

    def test_block_is_json_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_lv(Path(tmp), [_result("testA()", lv.TEST_PASSED)])
            json.dumps(_support(Path(tmp)))


class EvidenceIntegrationTests(unittest.TestCase):
    def _build(self, tmp, *, with_trace, with_lv):
        writer = ArtifactWriter(Path(tmp))
        match, analysis = _match("stake")
        _write_proof(writer, target_slug(match.display_id), with_trace=with_trace)
        if with_lv:
            _write_lv(Path(tmp), [_result("testStake()", lv.TEST_PASSED, trace=False)])
        return build_evidence(match, FIXTURE, writer, analysis)

    def test_missing_local_validation_does_not_break_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = self._build(tmp, with_trace=True, with_lv=False)
            self.assertNotIn("local_validation_support", pkg.payload)
            self.assertEqual(pkg.evidence_level, "EVIDENCE_READY")

    def test_evidence_includes_support_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = self._build(tmp, with_trace=True, with_lv=True)
            self.assertIn("local_validation_support", pkg.payload)
            self.assertEqual(pkg.payload["local_validation_support"]["tested_count"], 1)

    def test_tested_only_support_does_not_create_evidence_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = self._build(tmp, with_trace=False, with_lv=True)
            self.assertEqual(pkg.evidence_level, "EXECUTION_CONFIRMED")  # not EVIDENCE_READY
            self.assertEqual(pkg.payload["local_validation_support"]["tested_count"], 1)

    def test_trace_bounded_evidence_ready_rule_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._build(tmp, with_trace=True, with_lv=True).evidence_level, "EVIDENCE_READY")

    def test_support_does_not_set_ready_or_human_reviewed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = self._build(tmp, with_trace=True, with_lv=True)
            blob = json.dumps(pkg.payload["local_validation_support"])
            self.assertNotIn("HUMAN_REVIEWED", blob)
            self.assertIs(pkg.payload["local_validation_support"]["ready_for_submission"], False)

    def test_render_includes_section_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = self._build(tmp, with_trace=True, with_lv=True)
            self.assertIn("Local Validation Support", evidence_text(pkg.payload))
            self.assertIn("Local Validation Support", render_evidence(pkg, "."))

    def test_render_omits_section_when_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = self._build(tmp, with_trace=True, with_lv=False)
            self.assertNotIn("Local Validation Support", evidence_text(pkg.payload))


if __name__ == "__main__":
    unittest.main()
