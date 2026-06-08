"""CLI tests for `arkheionx evidence-judge` (v7, scope-aware)."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "scope-fixture"
SCOPE = FIXTURE / "scope-note.md"

_QUALITIES = {"strong", "medium", "weak", "invalid", "insufficient", "unknown"}
_JUDGMENTS = {
    "rejected-with-strong-evidence", "rejected-with-medium-evidence", "candidate-with-evidence",
    "insufficient-evidence", "invalid-test", "likely-known-issue", "likely-accepted-risk",
    "likely-trusted-role-assumption", "likely-out-of-scope", "likely-low-only", "needs-human-review",
}


def run_cli(*args: str):
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class EvidenceJudgeCliTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        self.assertIn("evidence-judge", run_cli("--help").stdout)

    def test_detects_weak_and_invalid(self) -> None:
        result = run_cli("evidence-judge", str(FIXTURE), "--scope-file", str(SCOPE), "--json")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["kind"], "evidence-judge")
        self.assertGreaterEqual(data["summary"]["evidence_items"], 3)
        by_file = {Path(e["source"]).name: e for e in data["judged_evidence"]}
        # The fixture has a deliberately strong, weak, and invalid test.
        self.assertEqual(by_file["ExampleOracleInvalid.t.sol"]["quality"], "invalid")
        self.assertEqual(by_file["ExampleOracleInvalid.t.sol"]["judgment"], "invalid-test")
        self.assertEqual(by_file["ExampleStablecoinWeak.t.sol"]["quality"], "weak")
        self.assertEqual(by_file["ExampleWithdrawalStrong.t.sol"]["quality"], "strong")
        for e in data["judged_evidence"]:
            self.assertIn(e["quality"], _QUALITIES)
            self.assertIn(e["judgment"], _JUDGMENTS)
            self.assertTrue(e["human_review_required"])

    def test_no_evidence_dir_is_graceful(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty"
            empty.mkdir()
            data = json.loads(run_cli("evidence-judge", str(FIXTURE), "--scope-file", str(SCOPE),
                                      "--evidence-dir", str(empty), "--json").stdout)
            self.assertEqual(data["summary"]["evidence_items"], 0)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "evidence-judge"
            run_cli("evidence-judge", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            self.assertTrue((out / "evidence-judge.md").is_file())
            self.assertTrue((out / "evidence-judge.json").is_file())
            self.assertIn("does not confirm vulnerabilities",
                          (out / "evidence-judge.md").read_text().lower())


if __name__ == "__main__":
    unittest.main()
