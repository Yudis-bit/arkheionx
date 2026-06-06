"""Focused Proof Plan CLI tests.

The command is a thin view over review-map ``proof-plan.json`` artifacts and
the existing ReviewMap builder. Static runs normally exit 1 for heuristic review
guidance; 2 is reserved for usage/input failures. This command plans local
proof work only; it must not execute proofs.
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


class ProofPlanCommandTests(unittest.TestCase):
    def _copy_demo(self, tmp: str) -> Path:
        repo = Path(tmp) / "demo"
        copied = run_cli("demo", "--copy", "lending-vault", str(repo))
        self.assertEqual(copied.returncode, 0, copied.stderr)
        return repo

    def test_help_lists_proof_plan(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("proof-plan", result.stdout)

    def test_proof_plan_help(self) -> None:
        result = run_cli("proof-plan", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--top", "--json", "--no-write", "--include-low-confidence", "--target"):
            self.assertIn(opt, result.stdout)
        self.assertNotIn("--run", result.stdout)

    def test_human_output_is_bounded_safe_and_planning_only(self) -> None:
        result = run_cli("proof-plan", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("Proof Plan", result.stdout)
        self.assertIn("Local/static review guidance only", result.stdout)
        self.assertIn("suggested local proof outlines, not executed proofs", result.stdout)
        self.assertIn("not confirmed bugs", result.stdout)
        self.assertIn("Priority is review order, not severity", result.stdout)
        self.assertIn("Human review required", result.stdout)
        self.assertIn("Total proof suggestions", result.stdout)
        self.assertIn("LendingVaultFixture.borrow", result.stdout)
        self.assertIn("Objective", result.stdout)
        self.assertIn("Assertions", result.stdout)
        self.assertIn("arkheionx review-map", result.stdout)
        self.assertIn("arkheionx test-gap-map", result.stdout)
        self.assertIn("arkheionx value-paths", result.stdout)
        self.assertIn("arkheionx assumptions", result.stdout)
        self.assertIn("arkheionx prove", result.stdout)
        self.assertIn("No proof was executed", result.stdout)
        for forbidden in ("Proof executed successfully", "EXECUTION_CONFIRMED", "EVIDENCE_READY"):
            self.assertNotIn(forbidden, result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertLessEqual(len(result.stdout.splitlines()), 70)

    def test_human_output_points_to_written_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            result = run_cli("proof-plan", str(repo), "--out", str(out), "--top", "1")
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertIn("Artifacts", result.stdout)
            self.assertIn("proof-plan.json", result.stdout)
            self.assertTrue((out / "proof-plan.json").is_file())

    def test_json_is_valid_pure_and_has_artifact_shape(self) -> None:
        result = run_cli("proof-plan", str(FIXTURE), "--json", "--no-write", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotRegex(result.stdout, ANSI)
        for chrome in ("ARKHEIONX", "Boundary", "Top Proof Suggestions"):
            self.assertNotIn(chrome, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload), {"schema_version", "generated_at", "repo_path", "proof_suggestions"})
        self.assertTrue(payload["proof_suggestions"])

    def test_json_matches_written_proof_plan_artifact_when_building(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            result = run_cli("proof-plan", str(repo), "--json", "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            stdout_payload = json.loads(result.stdout)
            artifact_payload = json.loads((out / "proof-plan.json").read_text(encoding="utf-8"))
            self.assertEqual(stdout_payload, artifact_payload)
            self.assertTrue((out / "review-map.json").is_file())
            self.assertTrue((out / "test-gap-map.json").is_file())
            self.assertFalse((repo / ".arkheionx" / "out" / "proof").exists())

    def test_no_write_with_unused_out_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            unused = Path(tmp) / "unused-out"
            result = run_cli("proof-plan", str(repo), "--no-write", "--out", str(unused))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertFalse(unused.exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "review-map").exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "proof").exists())

    def test_reads_existing_artifact_without_rebuilding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            built = run_cli("review-map", str(repo), "--out", str(out))
            self.assertIn(built.returncode, (0, 1), built.stderr)

            artifact = out / "proof-plan.json"
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            payload["artifact_sentinel"] = "proof-plan-read-existing"
            artifact.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

            result = run_cli("proof-plan", str(repo), "--json", "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertEqual(json.loads(result.stdout)["artifact_sentinel"], "proof-plan-read-existing")
            saved = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(saved["artifact_sentinel"], "proof-plan-read-existing")

    def test_derives_in_memory_when_artifact_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            missing = Path(tmp) / "missing-out"
            result = run_cli("proof-plan", str(repo), "--json", "--no-write", "--out", str(missing))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            payload = json.loads(result.stdout)
            self.assertGreater(len(payload["proof_suggestions"]), 0)
            self.assertFalse(missing.exists())

    def test_target_filter_uses_review_map_builder(self) -> None:
        result = run_cli(
            "proof-plan",
            str(FIXTURE),
            "--json",
            "--no-write",
            "--target",
            "LendingVaultFixture.borrow",
        )
        self.assertIn(result.returncode, (0, 1), result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["proof_suggestions"])
        self.assertEqual(
            {item["target"] for item in payload["proof_suggestions"]},
            {"LendingVaultFixture.borrow"},
        )


if __name__ == "__main__":
    unittest.main()
