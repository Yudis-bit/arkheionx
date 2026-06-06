import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class CliCompatibilityTests(unittest.TestCase):
    def run_command(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)

    def test_old_script_entrypoints_still_work(self) -> None:
        commands = [
            ["python3", "scripts/pre_audit_scan.py", "--help"],
            ["python3", "scripts/validate_config.py", "--help"],
            ["python3", "scripts/generate_test_plan.py", "--help"],
            ["python3", "scripts/search_knowledge.py", "oracle stale price"],
            ["python3", "scripts/generate_test_plan.py", "--check"],
            ["python3", "scripts/validate_config.py", "--config", "examples/arkheionx.config.example.json"],
        ]
        for command in commands:
            result = self.run_command(command)
            self.assertEqual(result.returncode, 0, " ".join(command) + "\n" + result.stdout + result.stderr)

    def test_cli_test_plan_generates_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            report = out_dir / "test-plan.md"
            json_plan = out_dir / "test-plan.json"
            foundry = out_dir / "ArkheionxCLIInvariants.t.sol"
            result = self.run_command(
                [
                    "python3",
                    "-m",
                    "arkheionx.cli.main",
                    "test-plan",
                    "--report",
                    "examples/reports/amm-fixture-pre-audit-report.json",
                    "--output",
                    str(report),
                    "--json-output",
                    str(json_plan),
                    "--foundry-output",
                    str(foundry),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(report.exists())
            self.assertTrue(json_plan.exists())
            self.assertTrue(foundry.exists())
            payload = json.loads(json_plan.read_text(encoding="utf-8"))
            self.assertTrue(payload["suggested_tests"])
            self.assertIn("not formal verification", report.read_text(encoding="utf-8").lower())
            self.assertIn("TODO", foundry.read_text(encoding="utf-8"))

    def test_cli_test_plan_check_passes(self) -> None:
        result = self.run_command(["python3", "-m", "arkheionx.cli.main", "test-plan", "--check"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok: test plans up to date", result.stdout)


if __name__ == "__main__":
    unittest.main()
