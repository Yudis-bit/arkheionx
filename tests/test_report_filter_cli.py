"""CLI tests for `arkheionx report-filter` (v7)."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "scope-fixture"
SCOPE = FIXTURE / "scope-note.md"

_CLASSES = {
    "potentially-reportable", "needs-more-evidence", "likely-known-issue", "likely-accepted-risk",
    "likely-trusted-role-assumption", "likely-out-of-scope", "likely-low-only", "duplicate-prone",
    "not-a-finding", "needs-human-review",
}


def run_cli(*args: str):
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class ReportFilterCliTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        self.assertIn("report-filter", run_cli("--help").stdout)

    def test_classifies_candidates(self) -> None:
        result = run_cli("report-filter", str(FIXTURE), "--scope-file", str(SCOPE), "--json")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["kind"], "report-filter")
        self.assertGreater(data["candidate_count"], 0)
        for c in data["candidates"]:
            self.assertIn(c["classification"], _CLASSES)
            self.assertTrue(c["human_review_required"])
        # The synthetic scope marks trusted roles and low-only patterns; some candidates
        # should be filtered into scope-aware buckets (not all potentially-reportable).
        used = {c["classification"] for c in data["candidates"]}
        self.assertTrue(used & {"likely-trusted-role-assumption", "likely-low-only",
                                "duplicate-prone", "needs-more-evidence"})
        self.assertIn("checklist", data)
        self.assertGreaterEqual(len(data["checklist"]), 8)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report-filter"
            run_cli("report-filter", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            self.assertTrue((out / "report-filter.md").is_file())
            self.assertTrue((out / "report-filter.json").is_file())
            self.assertIn("Report filter is not final triage", (out / "report-filter.md").read_text())


if __name__ == "__main__":
    unittest.main()
