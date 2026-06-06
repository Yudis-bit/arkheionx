"""Focused Evidence Links CLI tests.

The command is a thin view over review-map ``evidence-links.json`` artifacts and
the existing ReviewMap builder. It reads existing local proof/trace/evidence/
report references only; it must not create evidence or execute proofs.
"""
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "arkheionx" / "demo" / "fixtures" / "lending-vault"
ANSI = re.compile(r"\x1b\[")


def run_cli(*args: str, color: str = "never") -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = color
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        env=env,
    )


class EvidenceLinksCommandTests(unittest.TestCase):
    def _copy_demo(self, tmp: str) -> Path:
        repo = Path(tmp) / "demo"
        copied = run_cli("demo", "--copy", "lending-vault", str(repo))
        self.assertEqual(copied.returncode, 0, copied.stderr)
        return repo

    def _write_proof_artifact(self, repo: Path) -> Path:
        proof_dir = repo / ".arkheionx" / "out" / "proof" / "LendingVaultFixture_borrow"
        proof_dir.mkdir(parents=True)
        proof = {
            "schema_version": "1.0.0",
            "target": "LendingVaultFixture.borrow",
            "target_id": "LendingVaultFixture.borrow",
            "proof_receipt_id": "proof:LendingVaultFixture_borrow",
            "review_map_target": "LendingVaultFixture.borrow",
            "status": "tested_passed",
            "evidence_level": "EXECUTION_CONFIRMED",
            "foundry": {"test_command": "forge test --match-test (?i)borrow -vvvv"},
            "test_result": {
                "tests_run": 1,
                "passed": 1,
                "failed": 0,
                "skipped": 0,
                "failed_tests": [],
                "skipped_tests": [],
                "raw_output_path": "foundry-test.txt",
            },
            "generated_files": [],
            "limitations": ["A passing test does not prove the absence of bugs."],
        }
        path = proof_dir / "proof.json"
        path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
        return path

    def _write_trace_artifact(self, proof_path: Path) -> Path:
        trace = {
            "schema_version": "1.0.0",
            "target": "LendingVaultFixture.borrow",
            "target_id": "LendingVaultFixture.borrow",
            "trace_receipt_id": "trace:LendingVaultFixture_borrow",
            "review_map_target": "LendingVaultFixture.borrow",
            "source_proof_json": str(proof_path),
            "status": "tested_passed",
            "evidence_level": "EXECUTION_CONFIRMED",
            "tests_run": 1,
            "passed": 1,
            "failed": 0,
            "skipped": 0,
            "reverts": [],
            "assertion_failures": [],
            "call_sequence": ["LendingVaultFixture::borrow(uint256)"],
            "logs": [],
            "limitations": [],
        }
        path = proof_path.parent / "trace.json"
        path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
        return path

    def _write_repay_proof_artifact(self, repo: Path) -> Path:
        proof_dir = repo / ".arkheionx" / "out" / "proof" / "LendingVaultFixture_repay"
        proof_dir.mkdir(parents=True)
        proof = {
            "schema_version": "1.0.0",
            "target": "LendingVaultFixture.repay",
            "target_id": "LendingVaultFixture.repay",
            "proof_receipt_id": "proof:LendingVaultFixture_repay",
            "review_map_target": "LendingVaultFixture.repay",
            "status": "tested_passed",
            "evidence_level": "EXECUTION_CONFIRMED",
            "foundry": {"test_command": "forge test --match-test (?i)repay -vvvv"},
            "test_result": {"tests_run": 1, "passed": 1, "failed": 0, "skipped": 0},
            "generated_files": [],
        }
        path = proof_dir / "proof.json"
        path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
        return path

    def _build_evidence_and_report(self, repo: Path) -> tuple[dict, dict]:
        proof_path = self._write_proof_artifact(repo)
        self._write_trace_artifact(proof_path)
        evidence = run_cli(
            "evidence",
            str(repo),
            "--from-proof",
            str(proof_path),
            "--json",
            "--artifacts-dir",
            str(repo),
        )
        self.assertEqual(evidence.returncode, 0, evidence.stdout + evidence.stderr)
        evidence_payload = json.loads(evidence.stdout)
        evidence_path = repo / ".arkheionx" / "out" / "evidence" / "LendingVaultFixture_borrow" / "evidence.json"
        self.assertTrue(evidence_path.is_file())

        report = run_cli(
            "report",
            str(repo),
            "--from-evidence",
            str(evidence_path),
            "--json",
            "--artifacts-dir",
            str(repo),
        )
        self.assertEqual(report.returncode, 0, report.stdout + report.stderr)
        report_payload = json.loads(report.stdout)
        return evidence_payload, report_payload

    def test_help_lists_evidence_links(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("evidence-links", result.stdout)

    def test_evidence_links_help(self) -> None:
        result = run_cli("evidence-links", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--top", "--json", "--no-write", "--include-low-confidence", "--target"):
            self.assertIn(opt, result.stdout)
        for forbidden in ("--run", "--create", "--promote", "--reviewed", "--submit"):
            self.assertNotIn(forbidden, result.stdout)

    def test_human_output_is_bounded_safe_and_honest_when_empty(self) -> None:
        result = run_cli("evidence-links", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("Evidence Links", result.stdout)
        self.assertIn("Local/static review guidance only", result.stdout)
        self.assertIn("references to existing local", result.stdout)
        self.assertIn("does not create evidence", result.stdout)
        self.assertIn("not confirmed bugs", result.stdout)
        self.assertIn("not final severity", result.stdout)
        self.assertIn("Human review required", result.stdout)
        self.assertIn("Total evidence links", result.stdout)
        self.assertIn("No evidence links found", result.stdout)
        self.assertIn("arkheionx review-map", result.stdout)
        self.assertIn("arkheionx test-gap-map", result.stdout)
        self.assertIn("arkheionx value-paths", result.stdout)
        self.assertIn("arkheionx assumptions", result.stdout)
        self.assertIn("arkheionx proof-plan", result.stdout)
        self.assertIn("arkheionx evidence", result.stdout)
        self.assertIn("arkheionx report", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("Confirmed vulnerability", result.stdout)
        self.assertLessEqual(len(result.stdout.splitlines()), 70)

    def test_human_output_shows_existing_link_without_creating_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            proof_path = self._write_proof_artifact(repo)
            result = run_cli("evidence-links", str(repo), "--no-write")
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertIn("LendingVaultFixture.borrow", result.stdout)
            self.assertIn("EXECUTION_CONFIRMED", result.stdout)
            self.assertIn("proof", result.stdout)
            self.assertIn(proof_path.relative_to(repo).as_posix(), result.stdout)
            self.assertFalse((repo / ".arkheionx" / "out" / "evidence").exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "reports").exists())

    def test_json_backfills_evidence_package_and_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            evidence_payload, _report_payload = self._build_evidence_and_report(repo)

            result = run_cli("evidence-links", str(repo), "--json", "--no-write")
            self.assertIn(result.returncode, (0, 1), result.stderr)
            payload = json.loads(result.stdout)
            links = payload["evidence_links"]
            evidence_link = next(item for item in links if item["source"] == "evidence")

            self.assertEqual(evidence_link["target"], "LendingVaultFixture.borrow")
            self.assertIn("LendingVaultFixture.borrow", evidence_link["target_id"])
            self.assertEqual(evidence_link["evidence_level"], "EVIDENCE_READY")
            self.assertEqual(evidence_link["readiness"], "evidence_ready")
            self.assertEqual(evidence_link["evidence_package_id"], evidence_payload["evidence_package_id"])
            self.assertEqual(evidence_link["proof_receipt_id"], "proof:LendingVaultFixture_borrow")
            self.assertEqual(evidence_link["trace_receipt_id"], "trace:LendingVaultFixture_borrow")
            self.assertTrue(evidence_link["artifacts"]["evidence_json"].endswith("evidence/LendingVaultFixture_borrow/evidence.json"))
            self.assertEqual(evidence_link["review_status"], "NEEDS_HUMAN_REVIEW")
            self.assertTrue(evidence_link["manual_review_required"])
            self.assertIn("Manual review required.", evidence_link["limitations"])

    def test_json_backfills_report_draft_paths_and_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            _evidence_payload, report_payload = self._build_evidence_and_report(repo)

            result = run_cli("evidence-links", str(repo), "--json", "--no-write")
            self.assertIn(result.returncode, (0, 1), result.stderr)
            report_link = next(item for item in json.loads(result.stdout)["evidence_links"] if item["source"] == "report")

            self.assertTrue(report_link["artifacts"]["report_json"].endswith("reports/LendingVaultFixture_borrow/report.json"))
            self.assertTrue(report_link["artifacts"]["report_md"].endswith("reports/LendingVaultFixture_borrow/report.md"))
            self.assertEqual(report_link["report_status"], "draft")
            self.assertEqual(report_link["report_readiness"]["status"], "draft")
            self.assertTrue(report_link["report_readiness"]["requires_manual_review"])
            self.assertEqual(report_link["review_status"], "NEEDS_HUMAN_REVIEW")
            self.assertEqual(report_link["evidence_package_id"], report_payload["evidence_context"]["evidence_package_id"])

    def test_review_map_writes_enriched_evidence_links_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            evidence_payload, _report_payload = self._build_evidence_and_report(repo)

            result = run_cli("review-map", str(repo))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            artifact = repo / ".arkheionx" / "out" / "review-map" / "evidence-links.json"
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            links = payload["evidence_links"]
            self.assertTrue(any(item.get("evidence_package_id") == evidence_payload["evidence_package_id"] for item in links))
            self.assertTrue(any(item.get("artifacts", {}).get("report_json", "").endswith("report.json") for item in links))

    def test_human_output_surfaces_package_report_and_manual_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            evidence_payload, _report_payload = self._build_evidence_and_report(repo)

            result = run_cli("evidence-links", str(repo), "--no-write")
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertIn("Evidence packages:", result.stdout)
            self.assertIn(evidence_payload["evidence_package_id"], result.stdout)
            self.assertIn("Proof receipts:", result.stdout)
            self.assertIn("Trace receipts:", result.stdout)
            self.assertIn("Report drafts:", result.stdout)
            self.assertIn("draft/manual review", result.stdout)
            self.assertIn("Human review required", result.stdout)
            for forbidden in ("confirmed vulnerability", "final severity:", "audit passed", "HUMAN_REVIEWED"):
                self.assertNotIn(forbidden, result.stdout)

    def test_target_filter_does_not_overlink_similar_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            self._write_proof_artifact(repo)
            self._write_repay_proof_artifact(repo)

            result = run_cli(
                "evidence-links",
                str(repo),
                "--json",
                "--no-write",
                "--target",
                "LendingVaultFixture.borrow",
            )
            self.assertIn(result.returncode, (0, 1), result.stderr)
            links = json.loads(result.stdout)["evidence_links"]
            self.assertTrue(links)
            self.assertEqual({item["target"] for item in links}, {"LendingVaultFixture.borrow"})
            self.assertFalse(any(item.get("proof_receipt_id") == "proof:LendingVaultFixture_repay" for item in links))

    def test_json_is_valid_pure_and_has_artifact_shape(self) -> None:
        result = run_cli("evidence-links", str(FIXTURE), "--json", "--no-write", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertNotRegex(result.stdout, ANSI)
        for chrome in ("ARKHEIONX", "Boundary", "Top Evidence Links"):
            self.assertNotIn(chrome, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload), {"schema_version", "generated_at", "repo_path", "evidence_links"})
        self.assertIsInstance(payload["evidence_links"], list)

    def test_json_matches_written_evidence_links_artifact_when_building(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            result = run_cli("evidence-links", str(repo), "--json", "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            stdout_payload = json.loads(result.stdout)
            artifact_payload = json.loads((out / "evidence-links.json").read_text(encoding="utf-8"))
            self.assertEqual(stdout_payload, artifact_payload)
            self.assertTrue((out / "review-map.json").is_file())
            self.assertTrue((out / "evidence-links.json").is_file())
            self.assertFalse((repo / ".arkheionx" / "out" / "evidence").exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "reports").exists())

    def test_no_write_with_unused_out_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            unused = Path(tmp) / "unused-out"
            result = run_cli("evidence-links", str(repo), "--no-write", "--out", str(unused))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertFalse(unused.exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "review-map").exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "evidence").exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "reports").exists())

    def test_reads_existing_artifact_without_rebuilding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            built = run_cli("review-map", str(repo), "--out", str(out))
            self.assertIn(built.returncode, (0, 1), built.stderr)

            artifact = out / "evidence-links.json"
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            payload["artifact_sentinel"] = "evidence-links-read-existing"
            original = json.dumps(payload, indent=2) + "\n"
            artifact.write_text(original, encoding="utf-8")

            result = run_cli("evidence-links", str(repo), "--json", "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertEqual(json.loads(result.stdout)["artifact_sentinel"], "evidence-links-read-existing")
            self.assertEqual(artifact.read_text(encoding="utf-8"), original)

    def test_derives_in_memory_when_artifact_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            missing = Path(tmp) / "missing-out"
            result = run_cli("evidence-links", str(repo), "--json", "--no-write", "--out", str(missing))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("evidence_links", payload)
            self.assertFalse(missing.exists())

    def test_target_filter_uses_review_map_builder_without_faking_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            self._write_proof_artifact(repo)
            result = run_cli(
                "evidence-links",
                str(repo),
                "--json",
                "--no-write",
                "--target",
                "LendingVaultFixture.borrow",
            )
            self.assertIn(result.returncode, (0, 1), result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["evidence_links"])
            self.assertEqual(
                {item["related_target"] for item in payload["evidence_links"]},
                {"LendingVaultFixture.borrow"},
            )

    def test_invalid_target_is_clean_failure(self) -> None:
        result = run_cli("evidence-links", str(FIXTURE), "--target", "Nope.nope", "--no-write")
        self.assertEqual(result.returncode, 2)
        self.assertIn("could not resolve target", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
