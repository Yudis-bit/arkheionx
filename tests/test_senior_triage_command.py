"""CLI tests for the private `arkheionx triage` senior-triage command."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "senior_triage_toy"
SCOPE = FIXTURE / "scope.md"
KNOWN = FIXTURE / "known"
AUDITS = FIXTURE / "audits"
ADDRESSES = FIXTURE / "addresses.json"

ARTIFACTS = [
    "00-target-decision.md", "01-bounty-eligibility.md", "02-known-issue-map.md",
    "03-freshness-diff.md", "04-deployment-reality.md", "05-lead-scoreboard.md",
    "06-top-3-leads.md", "07-do-not-touch.md", "08-next-commands.md",
    "09-agent-brief.md", "triage.json", "manifest.json",
]


def run_cli(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


class TriageCommandTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        top = run_cli("--help")
        self.assertEqual(top.returncode, 0, top.stderr)
        self.assertIn("triage", top.stdout)
        help_out = run_cli("triage", "--help")
        self.assertEqual(help_out.returncode, 0, help_out.stderr)
        for flag in ("--scope-file", "--known", "--audits", "--addresses",
                     "--baseline-ref", "--since-date", "--rpc-url", "--out", "--json", "--no-write"):
            self.assertIn(flag, help_out.stdout, flag)

    def test_creates_all_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "triage"
            result = run_cli(
                "triage", str(FIXTURE), "--scope-file", str(SCOPE),
                "--known", str(KNOWN), "--audits", str(AUDITS),
                "--addresses", str(ADDRESSES), "--out", str(out),
            )
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            for name in ARTIFACTS:
                self.assertTrue((out / name).is_file(), f"missing artifact: {name}")

    def test_missing_optional_inputs_do_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "triage"
            # No scope, no known, no audits, no addresses.
            result = run_cli("triage", str(FIXTURE), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertTrue((out / "triage.json").is_file())
            data = json.loads((out / "triage.json").read_text())
            # No scope -> the target decision is not a confident TOUCH.
            self.assertEqual(data["target_decision"], "NEEDS_MORE_CONTEXT")

    def test_bad_repo_is_clean_error(self) -> None:
        result = run_cli("triage", "/path/that/does/not/exist")
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr + result.stdout)
        self.assertIn("ArkheionX error", result.stdout + result.stderr)

    def test_no_write_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "triage"
            run_cli("triage", str(FIXTURE), "--scope-file", str(SCOPE),
                    "--out", str(out), "--no-write")
            self.assertFalse(out.exists())

    def test_json_flag_prints_triage_json(self) -> None:
        result = run_cli("triage", str(FIXTURE), "--scope-file", str(SCOPE),
                         "--no-write", "--json")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["artifact_type"], "senior_triage")
        self.assertEqual(data["command"], "triage")

    def test_touch_exit_zero_with_full_context(self) -> None:
        result = run_cli(
            "triage", str(FIXTURE), "--scope-file", str(SCOPE),
            "--known", str(KNOWN), "--audits", str(AUDITS), "--no-write", "--json",
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["target_decision"], "TOUCH")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
