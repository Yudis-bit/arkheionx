import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class CliScanTests(unittest.TestCase):
    def test_cli_scan_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            report = out_dir / "cli-amm-report.md"
            json_report = out_dir / "cli-amm-report.json"
            sarif = out_dir / "cli-amm.sarif.json"
            issue_plan = out_dir / "cli-amm-issue-plan.json"
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "arkheionx.cli.main",
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
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Readiness score:", result.stdout)
            self.assertIn("Fix First:", result.stdout)
            for path in [report, json_report, sarif, issue_plan]:
                self.assertTrue(path.exists(), str(path))
            self.assertIn("Fix First", report.read_text(encoding="utf-8"))
            data = json.loads(json_report.read_text(encoding="utf-8"))
            self.assertEqual(data["version"], "2.0.0")
            self.assertTrue(data["fix_first"])
            self.assertTrue(any(item["id"].startswith("ARK-AMM-") for item in data["findings"]))
            sarif_payload = json.loads(sarif.read_text(encoding="utf-8"))
            self.assertEqual(sarif_payload["version"], "2.1.0")
            plan = json.loads(issue_plan.read_text(encoding="utf-8"))
            self.assertTrue(plan["issues"])

    def test_cli_scan_respects_config_output_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_report = Path(tmp) / "configured.json"
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "arkheionx.cli.main",
                    "scan",
                    "examples/amm-lending-hybrid-fixture",
                    "--config",
                    "examples/configs/ci.config.json",
                    "--output",
                    str(Path(tmp) / "configured.md"),
                    "--json-output",
                    str(json_report),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(json_report.read_text(encoding="utf-8"))
            self.assertEqual(data["config_summary"]["output_profile"], "ci")


if __name__ == "__main__":
    unittest.main()
