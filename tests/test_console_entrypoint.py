import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ConsoleEntrypointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        env = os.environ.copy()
        env["PIP_BREAK_SYSTEM_PACKAGES"] = "1"
        install = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".", "--no-build-isolation"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            env=env,
        )
        if install.returncode != 0:
            raise AssertionError(install.stdout + install.stderr)

    def run_console(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["arkheionx", *args], cwd=REPO_ROOT, text=True, capture_output=True)

    def test_console_help_doctor_validate_and_search(self) -> None:
        for args in [
            ("--help",),
            ("doctor",),
            ("validate-config", "--config", "examples/arkheionx.config.example.json"),
            ("search", "oracle stale price", "--limit", "2"),
        ]:
            result = self.run_console(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_console_scan_and_test_plan_outputs_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            report = out / "package-cli-amm-report.md"
            json_report = out / "package-cli-amm-report.json"
            sarif = out / "package-cli-amm.sarif.json"
            issue_plan = out / "package-cli-amm-issue-plan.json"
            scan = self.run_console(
                "scan",
                "examples/amm-fixture",
                "--protocol-type",
                "amm",
                "--output",
                str(report),
                "--json-output",
                str(json_report),
                "--sarif-output",
                str(sarif),
                "--issue-plan-output",
                str(issue_plan),
            )
            self.assertEqual(scan.returncode, 0, scan.stdout + scan.stderr)
            self.assertIn("Fix First:", scan.stdout)
            for path in [json_report, sarif, issue_plan]:
                self.assertTrue(path.exists(), str(path))
                json.loads(path.read_text(encoding="utf-8"))

            test_plan_json = out / "package-cli-test-plan.json"
            test_plan = self.run_console(
                "test-plan",
                "--report",
                str(json_report),
                "--output",
                str(out / "package-cli-test-plan.md"),
                "--json-output",
                str(test_plan_json),
                "--foundry-output",
                str(out / "ArkheionxPackageCLIInvariants.t.sol"),
            )
            self.assertEqual(test_plan.returncode, 0, test_plan.stdout + test_plan.stderr)
            payload = json.loads(test_plan_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["suggested_tests"])


if __name__ == "__main__":
    unittest.main()
