"""CLI tests for `arkheionx scope-pack` (v7)."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "scope-fixture"
SCOPE = FIXTURE / "scope-note.md"

REQUIRED_FILES = [
    "00-README.md", "01-scope-map.md", "02-review-lanes.md", "03-scope-tasks.md",
    "04-do-not-waste-time.md", "05-evidence-template.md", "06-evidence-judge-rubric.md",
    "07-report-filter-checklist.md", "08-human-review-checklist.md", "09-agent-input.md",
    "10-case-study-template.md", "manifest.json",
]


def run_cli(*args: str):
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class ScopePackCliTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        self.assertIn("scope-pack", run_cli("--help").stdout)

    def test_writes_required_files_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "scope-pack"
            result = run_cli("scope-pack", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            for name in REQUIRED_FILES:
                self.assertTrue((out / name).is_file(), name)
            for sidecar in ("scope-map.json", "scope-lanes.json", "scope-tasks.json", "report-filter.json"):
                self.assertTrue((out / sidecar).is_file(), sidecar)

    def test_manifest_parses_and_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "scope-pack"
            run_cli("scope-pack", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["kind"], "scope-pack-manifest")
            self.assertEqual(manifest["command"], "scope-pack")
            self.assertTrue(manifest["human_review_required"])
            self.assertTrue(manifest["safety_flags"]["no_vulnerability_claims"])
            self.assertTrue(manifest["safety_flags"]["no_severity_claims"])
            self.assertEqual(len(manifest["generated_artifacts"]), 12)

    def test_no_write_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "scope-pack"
            run_cli("scope-pack", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out), "--no-write")
            self.assertFalse(out.exists())

    def test_no_unsafe_claims_in_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "scope-pack"
            run_cli("scope-pack", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            blob = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                             for p in out.iterdir() if p.is_file()).lower()
        for phrase in ("vulnerability confirmed", "exploit generated", "critical found",
                       "high found", "guaranteed", "audit replacement", "we found a bug"):
            self.assertNotIn(phrase, blob)


if __name__ == "__main__":
    unittest.main()
