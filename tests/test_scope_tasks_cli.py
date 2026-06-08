"""CLI tests for `arkheionx scope-tasks` (v7)."""
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


class ScopeTasksCliTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        self.assertIn("scope-tasks", run_cli("--help").stdout)

    def test_creates_testable_tasks_json(self) -> None:
        result = run_cli("scope-tasks", str(FIXTURE), "--scope-file", str(SCOPE), "--json")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["kind"], "scope-tasks")
        self.assertGreaterEqual(data["task_count"], 8)
        for t in data["tasks"]:
            # Each task is concrete, bound, and evidence-oriented.
            self.assertRegex(t["task_id"], r"^TASK-\d{3}$")
            self.assertTrue(t["target"])
            self.assertTrue(t["hypothesis"])
            self.assertTrue(t["counterfactual"])
            self.assertTrue(t["required_assertions"])
            self.assertTrue(t["stop_condition"])
            self.assertIn("report_candidate_threshold", t)
            self.assertTrue(t["human_review_required"])
        self.assertIn("report_filters", data)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "scope-tasks"
            run_cli("scope-tasks", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            self.assertTrue((out / "scope-tasks.md").is_file())
            self.assertTrue((out / "scope-tasks.json").is_file())
            md = (out / "scope-tasks.md").read_text()
            self.assertIn("Tasks are not exploit instructions", md)


if __name__ == "__main__":
    unittest.main()
