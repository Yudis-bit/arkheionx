"""Tests for `arkheionx review-package --export zip` (v3.6)."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _seed(repo: Path) -> None:
    out = repo / ".arkheionx" / "out"
    for rel in ("review-map/review-map.json", "review-map/evidence-links.json", "artifacts-index.json"):
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"k": 1}', encoding="utf-8")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, ARKHEIONX_COLOR="never")
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", "review-package", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class CliExportTests(unittest.TestCase):
    def test_export_json_pure_and_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = _run(tmp, "--export", "zip", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("\x1b[", result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["export_requested"])
            self.assertTrue(payload["export_written"])
            self.assertEqual(payload["export_status"], "created")
            self.assertEqual(payload["export_format"], "zip")
            self.assertTrue(payload["export_path"].startswith(".arkheionx/out/review-package/exports/"))
            self.assertGreater(payload["export_file_count"], 0)
            self.assertTrue(payload["export_checksum_sha256"])
            self.assertTrue(payload["manual_review_required"])
            self.assertFalse(payload["ready_for_submission"])

    def test_export_archive_exists_and_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            _run(tmp, "--export", "zip")
            exports = Path(tmp) / ".arkheionx" / "out" / "review-package" / "exports"
            archives = list(exports.glob("*.zip"))
            self.assertEqual(len(archives), 1)
            with zipfile.ZipFile(archives[0]) as z:
                names = z.namelist()
            self.assertIn("arkheionx-review-package/manifest.json", names)
            self.assertIn("arkheionx-review-package/validation.json", names)
            self.assertFalse(any("exports/" in n for n in names))
            self.assertTrue(all(not n.startswith("/") for n in names))

    def test_no_write_export_creates_no_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            payload = json.loads(_run(tmp, "--no-write", "--export", "zip", "--json").stdout)
            self.assertTrue(payload["export_requested"])
            self.assertFalse(payload["export_written"])
            self.assertFalse(payload["written"])
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package").exists())

    def test_no_write_export_human_states_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = _run(tmp, "--no-write", "--export", "zip")
            self.assertIn("no-write", result.stdout.lower())
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package").exists())

    def test_unsupported_format_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = _run(tmp, "--export", "tar")
            self.assertEqual(result.returncode, 2)

    def test_human_export_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = _run(tmp, "--export", "zip")
            self.assertEqual(result.returncode, 0)
            self.assertIn("Export:", result.stdout)
            self.assertIn("Ready for submission: False", result.stdout)


if __name__ == "__main__":
    unittest.main()
