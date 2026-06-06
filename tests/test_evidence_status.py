import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.evidence import index as idx
from arkheionx.evidence.status import build_status
from arkheionx.evidence.validate import validate_artifacts

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_SCHEMA = json.loads((REPO_ROOT / "schemas" / "artifacts-index.schema.json").read_text(encoding="utf-8"))


def _writer(tmp: str) -> ArtifactWriter:
    return ArtifactWriter(Path(tmp))


def _proof(writer, slug, level="EXECUTION_CONFIRMED", status="tested_passed", passed=1, failed=0):
    writer.write_text(f"proof/{slug}/proof.json", json.dumps({
        "schema_version": "1.0.0", "target": f"src/F.sol:{slug}", "status": status,
        "evidence_level": level, "foundry": {"test_command": "forge test"},
        "test_result": {"tests_run": passed + failed, "passed": passed, "failed": failed, "skipped": 0},
        "generated_files": [f"proof/{slug}/generated-test.sol"],
    }))


def _trace(writer, slug, level="EXECUTION_CONFIRMED"):
    writer.write_text(f"proof/{slug}/trace.json", json.dumps({
        "schema_version": "1.0.0", "target": f"src/F.sol:{slug}", "status": "tested_passed",
        "evidence_level": level, "tests_run": 1, "reverts": [],
    }))


def _evidence(writer, slug, level="EVIDENCE_READY", trace_path="", trace_status=None, extra=None):
    source_artifacts = {"proof_json": "", "trace_json": trace_path}
    if trace_status is not None:
        source_artifacts["trace_status"] = trace_status
    elif trace_path:
        source_artifacts["trace_status"] = "linked"
    payload = {
        "schema_version": "1.0.0", "target": f"src/F.sol:{slug}", "evidence_level": level,
        "status": "evidence_ready",
        "source_artifacts": source_artifacts,
        "impact_notes": {"candidate_impact": "x", "affected_components": [], "assumptions": [], "limitations": []},
    }
    if extra:
        payload.update(extra)
    writer.write_text(f"evidence/{slug}/evidence.json", json.dumps({
        **payload,
    }))


def _report(writer, slug, safety="Local defensive research only.", extra=None):
    payload = {
        "schema_version": "1.0.0", "target": f"src/F.sol:{slug}", "title": "t",
        "evidence_level": "EVIDENCE_READY", "summary": "s", "safety_notice": safety,
        "limitations": ["x"], "reproduction_steps": ["local only; no network"],
    }
    if extra:
        payload.update(extra)
    writer.write_text(f"reports/{slug}/report.json", json.dumps(payload))


class ReviewStatusTests(unittest.TestCase):
    def test_transitions(self) -> None:
        self.assertEqual(idx.compute_review_status(False, False, False, False), "NO_PROOF")
        self.assertEqual(idx.compute_review_status(True, False, False, False), "PROOF_ONLY")
        self.assertEqual(idx.compute_review_status(True, True, False, False), "TRACE_READY")
        self.assertEqual(idx.compute_review_status(True, True, True, False), "EVIDENCE_READY")
        self.assertEqual(idx.compute_review_status(True, True, True, True), "REPORT_DRAFTED")


class IndexTests(unittest.TestCase):
    def test_empty_scan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(idx.scan_targets(_writer(tmp)), [])

    def test_refresh_writes_index_and_schema_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _proof(w, "F_a")
            _trace(w, "F_a")
            payload = idx.refresh_index(".", w)
            self.assertTrue(w.path_for("artifacts-index.json").exists())
            for key in INDEX_SCHEMA["required"]:
                self.assertIn(key, payload)
            rec = payload["targets"][0]
            self.assertEqual(rec["review_status"], "TRACE_READY")


class EvidenceStatusTests(unittest.TestCase):
    def test_no_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = build_status(".", _writer(tmp))
            self.assertEqual(payload["status"], "no-artifacts")
            self.assertIn("hunt", payload["next_command"])

    def test_proof_only_needs_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _proof(w, "F_a", level="COMPILER_CONFIRMED", status="no_tests_matched", passed=0)
            payload = build_status(".", w)
            self.assertEqual(payload["status"], "warning")
            self.assertEqual(payload["needs_work"][0]["review_status"], "PROOF_ONLY")
            self.assertIn("trace", payload["needs_work"][0]["next"])

    def test_full_loop_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _proof(w, "F_a"); _trace(w, "F_a")
            _evidence(w, "F_a", trace_path=str(w.path_for("proof/F_a/trace.json")))
            _report(w, "F_a")
            payload = build_status(".", w)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["ready"][0]["review_status"], "REPORT_DRAFTED")

    def test_malformed_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            w.write_text("proof/F_a/proof.json", "{not json")
            records = idx.scan_targets(w)
            self.assertTrue(records[0].malformed)


class ValidateArtifactsTests(unittest.TestCase):
    def test_valid_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _proof(w, "F_a"); _trace(w, "F_a")
            _evidence(w, "F_a", trace_path=str(w.path_for("proof/F_a/trace.json")))
            _report(w, "F_a")
            counts, issues = validate_artifacts(w)
            self.assertEqual(issues, [])
            self.assertEqual(counts["report.json"], 1)

    def test_missing_safety_notice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _report(w, "F_a", safety="")
            _, issues = validate_artifacts(w)
            self.assertTrue(any("safety_notice" in i for i in issues))

    def test_execution_confirmed_without_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _proof(w, "F_a", level="EXECUTION_CONFIRMED", passed=0, failed=0)
            _, issues = validate_artifacts(w)
            self.assertTrue(any("EXECUTION_CONFIRMED but no executed tests" in i for i in issues))

    def test_evidence_references_missing_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _evidence(w, "F_a", trace_path=str(Path(tmp) / "nope" / "trace.json"))
            _, issues = validate_artifacts(w)
            self.assertTrue(any("missing trace.json" in i for i in issues))

    def test_evidence_ready_without_trace_status_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _trace(w, "F_a")
            _evidence(w, "F_a", trace_path=str(w.path_for("proof/F_a/trace.json")), trace_status="")
            _, issues = validate_artifacts(w)
            self.assertTrue(any("without trace_status" in i for i in issues))

    def test_evidence_ready_manifest_trace_linked_false_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _trace(w, "F_a")
            trace_path = str(w.path_for("proof/F_a/trace.json"))
            manifest = {
                "schema_version": "1.0.0",
                "package_id": "evidence:F_a:test",
                "target": "src/F.sol:F_a",
                "target_id": "src/F.sol:F_a",
                "evidence_level": "EVIDENCE_READY",
                "readiness": "evidence_ready",
                "source_count": 1,
                "sources": [{"kind": "proof", "path": "", "exists": False}],
                "checks": {
                    "proof_linked": True,
                    "trace_linked": False,
                    "trace_required_for_evidence_ready": True,
                    "source_paths_recorded": True,
                    "human_review_required": True,
                },
            }
            _evidence(
                w,
                "F_a",
                trace_path=trace_path,
                extra={"evidence_package_id": "evidence:F_a:test", "target_id": "src/F.sol:F_a", "manifest": manifest},
            )
            _, issues = validate_artifacts(w)
            self.assertTrue(any("manifest trace_linked is false" in i for i in issues))

    def test_report_disallowed_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _report(w, "F_a", extra={"summary": "this is ready to submit"})
            _, issues = validate_artifacts(w)
            self.assertTrue(any("disallowed phrase" in i for i in issues))

    def test_report_readiness_submission_ready_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _report(w, "F_a", extra={
                "report_readiness": {
                    "status": "draft",
                    "ready_for_submission": True,
                    "requires_manual_review": False,
                },
                "evidence_context": {"human_review_required": False},
                "claim_references": [{"status": "accepted"}],
            })
            _, issues = validate_artifacts(w)
            self.assertTrue(any("not ready for submission" in i for i in issues))
            self.assertTrue(any("must require manual review" in i for i in issues))
            self.assertTrue(any("evidence_context must require human review" in i for i in issues))
            self.assertTrue(any("claim_references must stay needs_human_review" in i for i in issues))

    def test_report_human_reviewed_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            w = _writer(tmp)
            _report(w, "F_a", extra={"review_status": "HUMAN_REVIEWED"})
            _, issues = validate_artifacts(w)
            self.assertTrue(any("must not emit HUMAN_REVIEWED" in i for i in issues))


if __name__ == "__main__":
    unittest.main()
