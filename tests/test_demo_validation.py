import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class DemoValidationTests(unittest.TestCase):
    def test_public_demo_docs_and_templates_exist(self) -> None:
        required = [
            "docs/TRY_IN_5_MINUTES.md",
            "docs/PUBLIC_DEMO_WORKFLOW.md",
            "docs/RULE_CALIBRATION.md",
            "docs/FALSE_POSITIVE_REVIEW_WORKFLOW.md",
            "docs/EXTERNAL_VALIDATION.md",
            "docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md",
            "docs/case-studies/ORACLE_STAKING_BEFORE_AFTER.md",
            "templates/case_study_template.md",
            "reports/rule_calibration_summary.md",
            "docs/launch/V0_8_LAUNCH_POSTS.md",
        ]
        for relative in required:
            self.assertTrue((REPO_ROOT / relative).exists(), relative)

    def test_external_feedback_issue_templates_exist(self) -> None:
        required = [
            ".github/ISSUE_TEMPLATE/false_positive_calibration.yml",
            ".github/ISSUE_TEMPLATE/external_validation_feedback.yml",
        ]
        for relative in required:
            path = REPO_ROOT / relative
            self.assertTrue(path.exists(), relative)
            text = path.read_text(encoding="utf-8")
            self.assertIn("authorized", text.lower())
        self.assertTrue((REPO_ROOT / ".github/workflows/arkheionx-demo.yml").exists())

    def test_demo_generated_artifacts_exist_and_parse(self) -> None:
        required = [
            "examples/reports/demo-pre-audit-report.md",
            "examples/reports/demo-report.json",
            "examples/reports/demo.sarif.json",
            "examples/reports/demo.baseline.json",
            "examples/reports/demo-issue-plan.json",
            "examples/reports/demo-issue-checklist.md",
            "examples/reports/demo-launch-report.md",
            "examples/reports/demo-sprint-plan.md",
            "examples/reports/demo-contest-readiness.md",
            "examples/reports/demo-executive-summary.md",
            "examples/reports/demo-remediation-roadmap.md",
            "examples/reports/demo-issue-dry-run.md",
        ]
        for relative in required:
            self.assertTrue((REPO_ROOT / relative).exists(), relative)

        report = json.loads((REPO_ROOT / "examples/reports/demo-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["tool"], "Arkheionx Pre-Audit Scanner")
        self.assertIn("delivery_outputs", report)
        self.assertIn("delivery_summary", report)
        self.assertTrue(report["findings"])

        sarif = json.loads((REPO_ROOT / "examples/reports/demo.sarif.json").read_text(encoding="utf-8"))
        self.assertEqual(sarif["version"], "2.1.0")

        dry_run = (REPO_ROOT / "examples/reports/demo-issue-dry-run.md").read_text(encoding="utf-8")
        self.assertIn("No GitHub API calls were made.", dry_run)

    def test_before_after_fixture_and_reports_exist(self) -> None:
        required = [
            "examples/oracle-staking-fixture-fixed/README.md",
            "examples/oracle-staking-fixture-fixed/src/OracleRewardFixtureFixed.sol",
            "examples/oracle-staking-fixture-fixed/test/OracleRewardFixtureFixed.t.sol",
            "examples/reports/oracle-staking-fixture-fixed-pre-audit-report.md",
            "examples/reports/oracle-staking-fixture-fixed-pre-audit-report.json",
            "examples/reports/oracle-staking-fixture-fixed.baseline.json",
            "examples/reports/oracle-staking-fixture-fixed-launch-report.md",
            "examples/reports/oracle-staking-fixture-fixed-remediation-roadmap.md",
        ]
        for relative in required:
            self.assertTrue((REPO_ROOT / relative).exists(), relative)

    def test_launch_posts_avoid_unsafe_claims(self) -> None:
        text = (REPO_ROOT / "docs/launch/V0_8_LAUNCH_POSTS.md").read_text(encoding="utf-8").lower()
        unsafe = [
            "guaranteed secure",
            "audit replacement",
            "cheap audit",
            "fully verified database",
            "bounty guaranteed",
            "live exploit",
            "profit calculator",
            "attack live protocol",
            "autonomous exploit runner",
            "weaponize",
            "guaranteed bounty",
            "guaranteed findings",
            "auto exploit",
        ]
        for phrase in unsafe:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
