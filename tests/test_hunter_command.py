"""CLI tests for `arkheionx hunter` (and `arkheionx triage --hunter`)."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"
SMOKE = FX / "fresh_state_machine_value_flow"

ARTIFACTS = [
    "00-run-context.md", "01-scope-map.md", "02-source-provenance.md", "03-known-issue-map.md",
    "04-freshness-map.md", "05-deployment-reality.md", "06-value-flow-map.md", "07-state-machine-map.md",
    "08-top-leads.md", "09-poc-plans.md", "10-submission-risk.md", "11-report-filter.md",
    "90-engine-evaluation.md", "triage.json", "manifest.json",
]


def run_cli(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


class HunterCommandTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        top = run_cli("--help")
        self.assertEqual(top.returncode, 0, top.stderr)
        self.assertIn("hunter", top.stdout)
        h = run_cli("hunter", "--help")
        self.assertEqual(h.returncode, 0, h.stderr)
        for flag in ("--scope-file", "--known", "--audits", "--addresses", "--source-dir",
                     "--source-recovery", "--no-source-recovery", "--rpc-url", "--deployment-calls",
                     "--registry-calls", "--baseline-ref", "--since-date", "--audit-date",
                     "--fresh-allowlist", "--strict-context", "--top", "--max-leads", "--out",
                     "--json", "--no-write"):
            self.assertIn(flag, h.stdout, flag)

    def test_creates_all_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "hunter"
            res = run_cli("hunter", str(SMOKE), "--scope-file", str(SMOKE / "scope.md"),
                          "--known", str(SMOKE / "known"), "--audits", str(SMOKE / "audits"),
                          "--out", str(out))
            self.assertIn(res.returncode, (0, 1), res.stderr)
            self.assertNotIn("Traceback", res.stderr)
            for name in ARTIFACTS:
                self.assertTrue((out / name).is_file(), f"missing artifact: {name}")

    def test_missing_optional_inputs_do_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "hunter"
            res = run_cli("hunter", str(FX / "dedup_blind"), "--out", str(out))
            self.assertIn(res.returncode, (0, 1), res.stderr)
            self.assertNotIn("Traceback", res.stderr)
            self.assertTrue((out / "triage.json").is_file())

    def test_bad_repo_is_clean_error(self) -> None:
        res = run_cli("hunter", "/path/that/does/not/exist")
        self.assertEqual(res.returncode, 2)
        self.assertNotIn("Traceback", res.stdout + res.stderr)
        self.assertIn("ArkheionX error", res.stdout + res.stderr)

    def test_no_write_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "hunter"
            run_cli("hunter", str(SMOKE), "--scope-file", str(SMOKE / "scope.md"),
                    "--out", str(out), "--no-write")
            self.assertFalse(out.exists())

    def test_json_flag_prints_hunter_triage(self) -> None:
        res = run_cli("hunter", str(SMOKE), "--scope-file", str(SMOKE / "scope.md"),
                      "--no-write", "--json")
        self.assertIn(res.returncode, (0, 1), res.stderr)
        data = json.loads(res.stdout)
        self.assertEqual(data["artifact_type"], "hunter_triage")
        self.assertEqual(data["schema_version"], "v9-universal-hunter")
        self.assertEqual(data["command"], "hunter")

    def test_triage_hunter_compat_routes_to_hunter(self) -> None:
        res = run_cli("triage", str(SMOKE), "--hunter", "--scope-file", str(SMOKE / "scope.md"),
                      "--no-write", "--json")
        self.assertIn(res.returncode, (0, 1), res.stderr)
        data = json.loads(res.stdout)
        self.assertEqual(data["artifact_type"], "hunter_triage")

    def test_classic_triage_still_senior(self) -> None:
        res = run_cli("triage", str(SMOKE), "--scope-file", str(SMOKE / "scope.md"),
                      "--no-write", "--json")
        self.assertIn(res.returncode, (0, 1), res.stderr)
        data = json.loads(res.stdout)
        self.assertEqual(data["artifact_type"], "senior_triage")


if __name__ == "__main__":
    unittest.main()
