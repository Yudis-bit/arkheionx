import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"


class ReportUXTests(unittest.TestCase):
    def run_scan(self, extra_args: list[str] | None = None) -> tuple[str, dict, dict]:
        extra_args = extra_args or []
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report_path = tmp_path / "report.md"
            json_path = tmp_path / "report.json"
            plan_path = tmp_path / "issue-plan.json"
            result = subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/amm-fixture"),
                    "--protocol-type",
                    "amm",
                    "--output",
                    str(report_path),
                    "--json-output",
                    str(json_path),
                    "--issue-plan-output",
                    str(plan_path),
                    *extra_args,
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return (
                report_path.read_text(encoding="utf-8"),
                json.loads(json_path.read_text(encoding="utf-8")),
                json.loads(plan_path.read_text(encoding="utf-8")),
            )

    def test_markdown_and_json_include_report_ux_sections(self) -> None:
        report, data, plan = self.run_scan()
        self.assertIn("## Fix First", report)
        self.assertIn("## Config Summary", report)
        self.assertIn("## Suppression Summary", report)
        self.assertIn("Findings by Rule Family", report)
        self.assertTrue(data["fix_first"])
        self.assertIn("amm", data["findings_by_rule_family"])
        self.assertIn("high", data["findings_by_confidence"])
        self.assertIn("suppression_summary", data)
        self.assertTrue(plan["fix_first"])
        self.assertIn("fix_first_rank", plan["issues"][0])
        self.assertIn("rule_family", plan["issues"][0])
        self.assertIn("## Suggested Tests", plan["issues"][0]["body"])

    def test_terminal_summary_includes_score_and_fix_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/amm-fixture"),
                    "--protocol-type",
                    "amm",
                    "--output",
                    str(Path(tmp) / "report.md"),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Readiness score:", result.stdout)
            self.assertIn("Active findings:", result.stdout)
            self.assertIn("Fix First:", result.stdout)

    def test_suppression_summary_is_visible_with_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_path = tmp_path / "suppress.json"
            report_path = tmp_path / "report.md"
            json_path = tmp_path / "report.json"
            config_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.7.0",
                        "protocol_type": "vault",
                        "suppressions": [
                            {
                                "id": "ARK-VLT",
                                "reason": "Temporary scoped test suppression.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/vault-risk-fixture"),
                    "--protocol-type",
                    "vault",
                    "--config",
                    str(config_path),
                    "--output",
                    str(report_path),
                    "--json-output",
                    str(json_path),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = report_path.read_text(encoding="utf-8")
            data = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertIn("## Suppression Summary", report)
            self.assertGreater(data["suppression_summary"]["suppressions_applied"], 0)
            self.assertTrue(data["suppressed_findings"])

    def test_docs_exist(self) -> None:
        for path in [
            "docs/REPORT_UX.md",
            "docs/OUTPUT_PROFILES.md",
            "docs/FIX_FIRST.md",
            "docs/NOISE_REDUCTION.md",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)


if __name__ == "__main__":
    unittest.main()
