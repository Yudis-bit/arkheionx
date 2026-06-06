"""Cross-command integration checks for focused review-map commands."""
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

COMMANDS = {
    "test-gap-map": {
        "artifact": "test-gap-map.json",
        "payload_key": "items",
    },
    "value-paths": {
        "artifact": "value-paths.json",
        "payload_key": "value_paths",
    },
    "assumptions": {
        "artifact": "assumptions.json",
        "payload_key": "assumptions",
    },
    "proof-plan": {
        "artifact": "proof-plan.json",
        "payload_key": "proof_suggestions",
    },
    "evidence-links": {
        "artifact": "evidence-links.json",
        "payload_key": "evidence_links",
        "allow_empty": True,
    },
}

SHARED_OPTIONS = (
    "--out",
    "--top",
    "--json",
    "--no-write",
    "--include-low-confidence",
    "--target",
)


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


class FocusedReviewCommandsIntegrationTests(unittest.TestCase):
    def _copy_demo(self, tmp: str) -> Path:
        repo = Path(tmp) / "demo"
        copied = run_cli("demo", "--copy", "lending-vault", str(repo))
        self.assertEqual(copied.returncode, 0, copied.stderr)
        return repo

    def _write_execution_proof_and_trace(self, repo: Path) -> Path:
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
        }
        trace = {
            "schema_version": "1.0.0",
            "target": "LendingVaultFixture.borrow",
            "target_id": "LendingVaultFixture.borrow",
            "trace_receipt_id": "trace:LendingVaultFixture_borrow",
            "review_map_target": "LendingVaultFixture.borrow",
            "source_proof_json": str(proof_dir / "proof.json"),
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
        }
        proof_path = proof_dir / "proof.json"
        proof_path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
        (proof_dir / "trace.json").write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
        return proof_path

    def assert_guidance_rc(self, result: subprocess.CompletedProcess[str], name: str = "") -> None:
        self.assertIn(result.returncode, (0, 1), f"{name}: {result.stderr}")

    def test_help_surface_is_consistent(self) -> None:
        top = run_cli("--help")
        self.assertEqual(top.returncode, 0, top.stderr)
        for command in COMMANDS:
            with self.subTest(command=command):
                self.assertIn(command, top.stdout)
                help_result = run_cli(command, "--help")
                self.assertEqual(help_result.returncode, 0, help_result.stderr)
                for option in SHARED_OPTIONS:
                    self.assertIn(option, help_result.stdout)
                self.assertNotIn("--run", help_result.stdout)

    def test_json_output_is_pure_across_focused_commands(self) -> None:
        for command, spec in COMMANDS.items():
            with self.subTest(command=command):
                result = run_cli(command, str(FIXTURE), "--json", "--no-write", color="always")
                self.assert_guidance_rc(result, command)
                self.assertEqual(result.stderr, "")
                self.assertNotRegex(result.stdout, ANSI)
                for chrome in ("ARKHEIONX", "Boundary", "Top "):
                    self.assertNotIn(chrome, result.stdout)
                payload = json.loads(result.stdout)
                self.assertIn(spec["payload_key"], payload)
                if not spec.get("allow_empty"):
                    self.assertTrue(payload[spec["payload_key"]])

    def test_no_write_matrix_does_not_create_output_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            for command in COMMANDS:
                missing = Path(tmp) / f"no-write-{command}"
                with self.subTest(command=command):
                    result = run_cli(command, str(repo), "--no-write", "--out", str(missing))
                    self.assert_guidance_rc(result, command)
                    self.assertFalse(missing.exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "review-map").exists())
            for name in ("proof", "evidence", "report"):
                self.assertFalse((repo / ".arkheionx" / "out" / name).exists())

    def test_existing_artifacts_are_read_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            built = run_cli("review-map", str(repo), "--out", str(out))
            self.assert_guidance_rc(built, "review-map")

            for command, spec in COMMANDS.items():
                artifact = out / spec["artifact"]
                payload = json.loads(artifact.read_text(encoding="utf-8"))
                payload["agent5_sentinel"] = f"{command}-existing-artifact"
                original = json.dumps(payload, indent=2) + "\n"
                artifact.write_text(original, encoding="utf-8")

                with self.subTest(command=command):
                    result = run_cli(command, str(repo), "--json", "--out", str(out))
                    self.assert_guidance_rc(result, command)
                    self.assertEqual(json.loads(result.stdout)["agent5_sentinel"], f"{command}-existing-artifact")
                    self.assertEqual(artifact.read_text(encoding="utf-8"), original)

    def test_target_filter_matrix_uses_review_map_builder(self) -> None:
        target = "LendingVaultFixture.borrow"
        for command in COMMANDS:
            with self.subTest(command=command):
                result = run_cli(command, str(FIXTURE), "--target", target, "--json", "--no-write")
                self.assert_guidance_rc(result, command)
                payload = json.loads(result.stdout)
                if command == "test-gap-map":
                    self.assertEqual({item["target"] for item in payload["items"]}, {target})
                elif command == "value-paths":
                    self.assertEqual({item["exit_function"] for item in payload["value_paths"]}, {target})
                elif command == "assumptions":
                    for item in payload["assumptions"]:
                        self.assertIn(target, item["used_by"])
                elif command == "proof-plan":
                    self.assertEqual({item["target"] for item in payload["proof_suggestions"]}, {target})
                elif command == "evidence-links":
                    for item in payload["evidence_links"]:
                        self.assertEqual(item["related_target"], target)

    def test_focused_commands_do_not_create_execution_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "focused-out"
            for command in COMMANDS:
                with self.subTest(command=command):
                    result = run_cli(command, str(repo), "--out", str(out))
                    self.assert_guidance_rc(result, command)
                    self.assertTrue((out / COMMANDS[command]["artifact"]).is_file())
            for root in (repo / ".arkheionx" / "out", out):
                for name in ("proof", "evidence", "report"):
                    self.assertFalse((root / name).exists(), f"{root / name} should not exist")

    def test_proof_trace_evidence_report_backfill_reaches_focused_and_review_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            proof_path = self._write_execution_proof_and_trace(repo)

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

            links = run_cli("evidence-links", str(repo), "--json", "--no-write")
            self.assert_guidance_rc(links, "evidence-links")
            focused_payload = json.loads(links.stdout)
            self.assertTrue(any(item.get("evidence_package_id") == evidence_payload["evidence_package_id"] for item in focused_payload["evidence_links"]))
            self.assertTrue(any(item.get("proof_receipt_id") == "proof:LendingVaultFixture_borrow" for item in focused_payload["evidence_links"]))
            self.assertTrue(any(item.get("trace_receipt_id") == "trace:LendingVaultFixture_borrow" for item in focused_payload["evidence_links"]))
            self.assertTrue(any(item.get("artifacts", {}).get("report_json", "").endswith("report.json") for item in focused_payload["evidence_links"]))

            review_map = run_cli("review-map", str(repo))
            self.assert_guidance_rc(review_map, "review-map")
            artifact = repo / ".arkheionx" / "out" / "review-map" / "evidence-links.json"
            review_payload = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(focused_payload["evidence_links"], review_payload["evidence_links"])


if __name__ == "__main__":
    unittest.main()
