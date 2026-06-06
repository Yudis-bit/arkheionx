import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"
ACTION = REPO_ROOT / ".github" / "actions" / "pre-audit" / "action.yml"


class DeliveryOutputTests(unittest.TestCase):
    def run_delivery_scan(self, sprint_days: str = "5") -> tuple[Path, dict]:
        tmp_path = Path(tempfile.mkdtemp())
        command = [
            "python3",
            str(SCANNER),
            "--root",
            str(REPO_ROOT / "examples/oracle-staking-fixture"),
            "--protocol-type",
            "auto",
            "--output",
            str(tmp_path / "report.md"),
            "--json-output",
            str(tmp_path / "report.json"),
            "--sarif-output",
            str(tmp_path / "report.sarif.json"),
            "--baseline-output",
            str(tmp_path / "baseline.json"),
            "--issue-plan-output",
            str(tmp_path / "issue-plan.json"),
            "--issue-checklist-output",
            str(tmp_path / "issue-checklist.md"),
            "--launch-report-output",
            str(tmp_path / "launch-report.md"),
            "--sprint-plan-output",
            str(tmp_path / "sprint-plan.md"),
            "--sprint-days",
            sprint_days,
            "--contest-readiness-output",
            str(tmp_path / "contest-readiness.md"),
            "--executive-summary-output",
            str(tmp_path / "executive-summary.md"),
            "--remediation-roadmap-output",
            str(tmp_path / "remediation-roadmap.md"),
        ]
        subprocess.run(command, cwd=REPO_ROOT, check=True, text=True, capture_output=True)
        return tmp_path, json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

    def test_delivery_outputs_are_generated_and_safe(self) -> None:
        tmp_path, report = self.run_delivery_scan("5")
        outputs = [
            "launch-report.md",
            "sprint-plan.md",
            "contest-readiness.md",
            "executive-summary.md",
            "remediation-roadmap.md",
        ]
        for name in outputs:
            path = tmp_path / name
            self.assertTrue(path.exists(), name)
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("not a formal audit", text)
            self.assertNotIn("guaranteed secure", text)
            self.assertNotIn("audit replacement", text)
            self.assertNotIn("bounty guaranteed", text)

        self.assertIn("## executive summary", (tmp_path / "launch-report.md").read_text(encoding="utf-8").lower())
        self.assertIn("day 1", (tmp_path / "sprint-plan.md").read_text(encoding="utf-8").lower())
        self.assertIn("day 5", (tmp_path / "sprint-plan.md").read_text(encoding="utf-8").lower())
        self.assertIn("scope preparation checklist", (tmp_path / "contest-readiness.md").read_text(encoding="utf-8").lower())
        self.assertIn("phase 1", (tmp_path / "remediation-roadmap.md").read_text(encoding="utf-8").lower())
        self.assertIn("delivery_outputs", report)
        self.assertIn("delivery_summary", report)
        self.assertTrue(report["delivery_outputs"]["launch_report"])

    def test_sprint_day_options_are_supported(self) -> None:
        for days in ["3", "5", "7", "10"]:
            tmp_path, _ = self.run_delivery_scan(days)
            text = (tmp_path / "sprint-plan.md").read_text(encoding="utf-8").lower()
            self.assertIn("day 1", text)
            self.assertIn(f"day {days}", text)

    def test_invalid_sprint_days_fails(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(SCANNER),
                "--root",
                str(REPO_ROOT / "examples/oracle-staking-fixture"),
                "--output",
                "/tmp/arkheionx-invalid-sprint.md",
                "--sprint-plan-output",
                "/tmp/arkheionx-invalid-sprint-plan.md",
                "--sprint-days",
                "4",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_action_exposes_delivery_inputs(self) -> None:
        text = ACTION.read_text(encoding="utf-8")
        for key in [
            "launch-report-output",
            "sprint-plan-output",
            "contest-readiness-output",
            "executive-summary-output",
            "remediation-roadmap-output",
        ]:
            self.assertIn(key, text)


if __name__ == "__main__":
    unittest.main()
