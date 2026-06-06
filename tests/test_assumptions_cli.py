"""Focused Assumptions CLI tests.

The command is a thin view over review-map ``assumptions.json`` artifacts and
the existing ReviewMap builder. Static runs normally exit 1 for heuristic review
guidance; 2 is reserved for usage/input failures.
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


class AssumptionsCommandTests(unittest.TestCase):
    def _copy_demo(self, tmp: str) -> Path:
        repo = Path(tmp) / "demo"
        copied = run_cli("demo", "--copy", "lending-vault", str(repo))
        self.assertEqual(copied.returncode, 0, copied.stderr)
        return repo

    def test_help_lists_assumptions(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("assumptions", result.stdout)

    def test_assumptions_help(self) -> None:
        result = run_cli("assumptions", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--top", "--json", "--no-write", "--include-low-confidence", "--target"):
            self.assertIn(opt, result.stdout)

    def test_human_output_is_bounded_and_safe(self) -> None:
        result = run_cli("assumptions", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("Assumptions", result.stdout)
        self.assertIn("Local/static review guidance only", result.stdout)
        self.assertIn("review prompts, not confirmed bugs", result.stdout)
        self.assertIn("Priority is review order, not severity", result.stdout)
        self.assertIn("Human review required", result.stdout)
        self.assertIn("Total assumptions", result.stdout)
        self.assertIn("Categories", result.stdout)
        self.assertIn("Related targets", result.stdout)
        self.assertIn("Oracle price is fresh and trusted", result.stdout)
        self.assertIn("arkheionx review-map", result.stdout)
        self.assertIn("arkheionx value-paths", result.stdout)
        self.assertIn("arkheionx test-gap-map", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("Confirmed vulnerability", result.stdout)
        self.assertLessEqual(len(result.stdout.splitlines()), 60)

    def test_human_output_points_to_written_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            result = run_cli("assumptions", str(repo), "--out", str(out), "--top", "1")
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertIn("Artifacts", result.stdout)
            self.assertIn("assumptions.json", result.stdout)
            self.assertTrue((out / "assumptions.json").is_file())

    def test_json_is_valid_pure_and_has_artifact_shape(self) -> None:
        result = run_cli("assumptions", str(FIXTURE), "--json", "--no-write", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotRegex(result.stdout, ANSI)
        for chrome in ("ARKHEIONX", "Boundary", "Top Assumptions"):
            self.assertNotIn(chrome, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload), {"schema_version", "generated_at", "repo_path", "assumptions"})
        self.assertTrue(payload["assumptions"])

    def test_json_matches_written_assumptions_artifact_when_building(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            result = run_cli("assumptions", str(repo), "--json", "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            stdout_payload = json.loads(result.stdout)
            artifact_payload = json.loads((out / "assumptions.json").read_text(encoding="utf-8"))
            self.assertEqual(stdout_payload, artifact_payload)
            self.assertTrue((out / "review-map.json").is_file())
            self.assertTrue((out / "value-paths.json").is_file())
            self.assertTrue((out / "test-gap-map.json").is_file())

    def test_no_write_with_unused_out_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            unused = Path(tmp) / "unused-out"
            result = run_cli("assumptions", str(repo), "--no-write", "--out", str(unused))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertFalse(unused.exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "review-map").exists())

    def test_reads_existing_artifact_without_rebuilding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            built = run_cli("review-map", str(repo), "--out", str(out))
            self.assertIn(built.returncode, (0, 1), built.stderr)

            artifact = out / "assumptions.json"
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            payload["artifact_sentinel"] = "assumptions-read-existing"
            artifact.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

            result = run_cli("assumptions", str(repo), "--json", "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertEqual(json.loads(result.stdout)["artifact_sentinel"], "assumptions-read-existing")
            saved = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(saved["artifact_sentinel"], "assumptions-read-existing")

    def test_derives_in_memory_when_artifact_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            missing = Path(tmp) / "missing-out"
            result = run_cli("assumptions", str(repo), "--json", "--no-write", "--out", str(missing))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            payload = json.loads(result.stdout)
            self.assertGreater(len(payload["assumptions"]), 0)
            self.assertFalse(missing.exists())

    def test_target_filter_uses_review_map_builder(self) -> None:
        result = run_cli(
            "assumptions",
            str(FIXTURE),
            "--json",
            "--no-write",
            "--target",
            "LendingVaultFixture.borrow",
        )
        self.assertIn(result.returncode, (0, 1), result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["assumptions"])
        for assumption in payload["assumptions"]:
            self.assertIn("LendingVaultFixture.borrow", assumption["used_by"])


if __name__ == "__main__":
    unittest.main()
