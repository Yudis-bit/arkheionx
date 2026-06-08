"""CLI tests for `arkheionx scope-map` (v7)."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "scope-fixture"
SCOPE = FIXTURE / "scope-note.md"


def run_cli(*args: str):
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class ScopeMapCliTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("scope-map", result.stdout)

    def test_parses_scope_note_json(self) -> None:
        result = run_cli("scope-map", str(FIXTURE), "--scope-file", str(SCOPE), "--json")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["kind"], "scope-map")
        self.assertTrue(data["scope_file_used"])
        self.assertTrue(data["human_review_required"])
        self.assertTrue(data["requires_medium_high"])
        self.assertGreater(len(data["known_issues"]), 0)
        self.assertGreater(len(data["accepted_risks"]), 0)
        self.assertGreater(len(data["invariants"]), 0)
        self.assertGreater(len(data["in_scope_surface_classes"]), 0)
        self.assertGreater(len(data["do_not_waste_time"]), 0)

    def test_generic_when_no_scope_file(self) -> None:
        data = json.loads(run_cli("scope-map", str(FIXTURE), "--json").stdout)
        self.assertFalse(data["scope_file_used"])
        self.assertIn("scope", data["scope_summary"].lower())

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "scope-map"
            run_cli("scope-map", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            self.assertTrue((out / "scope-map.md").is_file())
            self.assertTrue((out / "scope-map.json").is_file())
            md = (out / "scope-map.md").read_text()
            self.assertIn("# Arkheionx Scope Map", md)
            self.assertIn("Human review required", md)


if __name__ == "__main__":
    unittest.main()
