"""CLI tests for `arkheionx scope-lanes` (v7)."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "scope-fixture"
SCOPE = FIXTURE / "scope-note.md"

_ALLOWED_PRIORITY = {"very-high", "high", "medium", "monitor"}


def run_cli(*args: str):
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class ScopeLanesCliTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        self.assertIn("scope-lanes", run_cli("--help").stdout)

    def test_creates_relevant_lanes_json(self) -> None:
        result = run_cli("scope-lanes", str(FIXTURE), "--scope-file", str(SCOPE), "--json")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["kind"], "scope-lanes")
        self.assertGreaterEqual(data["lane_count"], 5)
        names = " ".join(lane["lane_name"] for lane in data["lanes"]).lower()
        # The synthetic scope exercises several generic lanes.
        self.assertIn("oracle", names)
        self.assertIn("compliance", names)
        for lane in data["lanes"]:
            self.assertIn(lane["priority"], _ALLOWED_PRIORITY)
            self.assertTrue(lane["human_review_required"])
            self.assertTrue(lane["evidence_required"])
        self.assertIn("filters", data)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "scope-lanes"
            run_cli("scope-lanes", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            self.assertTrue((out / "scope-lanes.md").is_file())
            self.assertTrue((out / "scope-lanes.json").is_file())
            self.assertIn("Review lanes are planning artifacts", (out / "scope-lanes.md").read_text())


if __name__ == "__main__":
    unittest.main()
