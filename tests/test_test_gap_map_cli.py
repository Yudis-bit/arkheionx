"""Focused Test Gap Map CLI tests.

The command is a thin view over review-map artifacts and the existing
Test Gap Map builder. Static runs normally exit 1 for heuristic review guidance;
2 is reserved for usage/input failures.
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


class TestGapMapCommandTests(unittest.TestCase):
    def _copy_demo(self, tmp: str) -> Path:
        repo = Path(tmp) / "demo"
        copied = run_cli("demo", "--copy", "lending-vault", str(repo))
        self.assertEqual(copied.returncode, 0, copied.stderr)
        return repo

    def test_help_lists_test_gap_map(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("test-gap-map", result.stdout)

    def test_test_gap_map_help(self) -> None:
        result = run_cli("test-gap-map", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--top", "--json", "--no-write", "--include-low-confidence", "--target"):
            self.assertIn(opt, result.stdout)

    def test_human_output_is_bounded_and_safe(self) -> None:
        result = run_cli("test-gap-map", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("Test Gap Map", result.stdout)
        self.assertIn("Local/static review guidance only", result.stdout)
        self.assertIn("Priority is review order, not severity", result.stdout)
        self.assertIn("suggestions, not confirmed bugs", result.stdout)
        self.assertIn("Human review required", result.stdout)
        self.assertIn("Total test gaps", result.stdout)
        self.assertIn("Priority buckets", result.stdout)
        self.assertIn("Evidence-linked", result.stdout)
        self.assertIn("Proof suggestion", result.stdout)
        self.assertIn("arkheionx review-map", result.stdout)
        self.assertIn("arkheionx prove", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("Critical severity", result.stdout)
        self.assertNotIn("Confirmed vulnerability", result.stdout)
        self.assertLessEqual(len(result.stdout.splitlines()), 60)

    def test_json_is_valid_pure_and_has_expected_keys(self) -> None:
        result = run_cli("test-gap-map", str(FIXTURE), "--json", "--no-write", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotRegex(result.stdout, ANSI)
        for chrome in ("ARKHEIONX", "Boundary", "Top Test Gaps"):
            self.assertNotIn(chrome, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(
            set(payload),
            {"schema_version", "generated_at", "repo_path", "mode", "summary", "items"},
        )
        self.assertIn("total_test_gaps", payload["summary"])
        self.assertGreater(payload["summary"]["total_test_gaps"], 0)
        self.assertTrue(payload["items"])

    def test_json_matches_written_artifact_when_building(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            result = run_cli("test-gap-map", str(repo), "--json", "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            stdout_payload = json.loads(result.stdout)
            artifact_payload = json.loads((out / "test-gap-map.json").read_text(encoding="utf-8"))
            self.assertEqual(stdout_payload, artifact_payload)
            self.assertTrue((out / "review-map.json").is_file())
            self.assertTrue((out / "test-gap-map.md").is_file())

    def test_no_write_with_unused_out_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            unused = Path(tmp) / "unused-out"
            result = run_cli("test-gap-map", str(repo), "--no-write", "--out", str(unused))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertFalse(unused.exists())
            self.assertFalse((repo / ".arkheionx" / "out" / "review-map").exists())

    def test_reads_existing_artifact_without_rebuilding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            out = Path(tmp) / "review-map-out"
            built = run_cli("review-map", str(repo), "--out", str(out))
            self.assertIn(built.returncode, (0, 1), built.stderr)

            artifact = out / "test-gap-map.json"
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            payload["generated_at"] = "artifact-sentinel"
            artifact.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

            result = run_cli("test-gap-map", str(repo), "--json", "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertEqual(json.loads(result.stdout)["generated_at"], "artifact-sentinel")
            self.assertEqual(json.loads(artifact.read_text(encoding="utf-8"))["generated_at"], "artifact-sentinel")

    def test_derives_in_memory_when_artifact_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy_demo(tmp)
            missing = Path(tmp) / "missing-out"
            result = run_cli("test-gap-map", str(repo), "--json", "--no-write", "--out", str(missing))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            payload = json.loads(result.stdout)
            self.assertGreater(payload["summary"]["total_test_gaps"], 0)
            self.assertFalse(missing.exists())

    def test_target_filter_uses_review_map_builder(self) -> None:
        result = run_cli(
            "test-gap-map",
            str(FIXTURE),
            "--json",
            "--no-write",
            "--target",
            "LendingVaultFixture.borrow",
        )
        self.assertIn(result.returncode, (0, 1), result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["items"])
        self.assertEqual({item["target"] for item in payload["items"]}, {"LendingVaultFixture.borrow"})


if __name__ == "__main__":
    unittest.main()
