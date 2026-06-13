"""CLI tests for `arkheionx lens-pack` (v7.5) on the toy fixture."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "morpho_midnight_toy"
SCOPE = FIXTURE / "scope.md"

REQUIRED_FILES = [
    "00-run-context.md", "01-scope-map.md", "02-protocol-model.md", "03-value-flow-map.md",
    "04-behavior-promises.md", "05-economic-invariants.md", "06-temporal-windows.md",
    "07-periphery-bundle-map.md", "08-evidence-map.md", "09-review-lanes.md",
    "10-scope-tasks.md", "11-blindspot-ranking.md", "12-evidence-rubric.md",
    "13-report-filter.md", "agent-input.md", "lens-pack.json",
]


def run_cli(*args: str):
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class LensPackCliTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        self.assertIn("lens-pack", run_cli("--help").stdout)

    def test_writes_all_files_namespaced_by_lens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "lens-pack"
            result = run_cli("lens-pack", str(FIXTURE), "--lens", "morpho-midnight",
                             "--scope-file", str(SCOPE), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            pack = out / "morpho-midnight"
            for name in REQUIRED_FILES:
                self.assertTrue((pack / name).is_file(), name)

    def test_manifest_json_valid_and_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "lens-pack"
            run_cli("lens-pack", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            manifest = json.loads((out / "morpho-midnight" / "lens-pack.json").read_text())
            self.assertEqual(manifest["kind"], "lens-pack-manifest")
            self.assertEqual(manifest["lens"]["lens_id"], "morpho-midnight")
            self.assertTrue(manifest["human_review_required"])
            self.assertTrue(manifest["safety_flags"]["no_vulnerability_claims"])
            self.assertTrue(manifest["safety_flags"]["no_severity_claims"])
            self.assertTrue(manifest["safety_flags"]["no_protocol_source_modification"])
            c = manifest["counts"]
            self.assertEqual(c["behavior_promises"], 14)
            self.assertEqual(c["economic_invariants"], 12)
            self.assertEqual(c["review_lanes"], 10)
            self.assertGreaterEqual(c["scope_tasks"], 10)
            self.assertEqual(c["blind_spots"], 10)

    def test_markdown_has_boundary_notices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "lens-pack"
            run_cli("lens-pack", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            pack = out / "morpho-midnight"
            blob = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                             for p in pack.iterdir() if p.suffix == ".md").lower()
        self.assertIn("planning artifact, not a finding", blob)
        self.assertIn("human review required", blob)
        self.assertIn("evidence quality is not vulnerability validity", blob)

    def test_no_write_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "lens-pack"
            run_cli("lens-pack", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out), "--no-write")
            self.assertFalse(out.exists())

    def test_json_flag_prints_manifest(self) -> None:
        result = run_cli("lens-pack", str(FIXTURE), "--scope-file", str(SCOPE), "--no-write", "--json")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["kind"], "lens-pack-manifest")


if __name__ == "__main__":
    unittest.main()
