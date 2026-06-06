"""Tests for the `arkheionx review-package` CLI command (v3.6)."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_JSON_KEYS = {
    "command", "package_root", "manifest_path", "validation_path", "readme_path",
    "limitations_path", "checksums_path", "artifact_count", "validation_status",
    "manual_review_required", "ready_for_submission", "written", "no_write",
    "warnings", "errors",
}


def _seed(repo: Path) -> None:
    out = repo / ".arkheionx" / "out"
    for rel in ("review-map/review-map.json", "review-map/evidence-links.json", "artifacts-index.json"):
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"k": 1}', encoding="utf-8")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, ARKHEIONX_COLOR="never")
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", "review-package", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


class ReviewPackageCliTests(unittest.TestCase):
    def test_command_in_help(self) -> None:
        env = dict(os.environ, ARKHEIONX_COLOR="never")
        result = subprocess.run(["python3", "-m", "arkheionx.cli.main", "help"],
                                cwd=REPO_ROOT, text=True, capture_output=True, env=env)
        self.assertIn("review-package", result.stdout)

    def test_json_no_write_is_pure_and_creates_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = _run(tmp, "--json", "--no-write")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("\x1b[", result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["no_write"])
            self.assertFalse(payload["written"])
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package").exists())

    def test_json_keys_and_safety_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            payload = json.loads(_run(tmp, "--json").stdout)
            self.assertTrue(_JSON_KEYS.issubset(payload))
            self.assertEqual(payload["command"], "review-package")
            self.assertTrue(payload["manual_review_required"])
            self.assertFalse(payload["ready_for_submission"])
            self.assertTrue(payload["validation_status"])
            self.assertIsInstance(payload["warnings"], list)
            self.assertIsInstance(payload["errors"], list)

    def test_json_paths_are_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            payload = json.loads(_run(tmp, "--json").stdout)
            for key in ("package_root", "manifest_path", "validation_path", "readme_path"):
                self.assertFalse(str(payload[key]).startswith("/"), key)
            self.assertEqual(payload["package_root"], ".arkheionx/out/review-package")

    def test_write_creates_package_dir_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = _run(tmp, "--json")
            self.assertEqual(result.returncode, 0)
            self.assertTrue(json.loads(result.stdout)["written"])
            pkg = Path(tmp) / ".arkheionx" / "out" / "review-package"
            for rel in ("manifest.json", "validation.json", "README.md", "limitations.md"):
                self.assertTrue((pkg / rel).is_file(), rel)

    def test_human_mode_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = _run(tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("Review Package", result.stdout)
            self.assertIn("Ready for submission: False", result.stdout)
            self.assertIn("Manual review required: True", result.stdout)

    def test_human_no_write_states_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = _run(tmp, "--no-write")
            self.assertIn("no-write", result.stdout.lower())
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package").exists())

    def test_bad_repo_returns_failure(self) -> None:
        result = _run("/no/such/dir/xyz123", "--json")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
