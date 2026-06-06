import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FeedbackLoopTests(unittest.TestCase):
    def load_json(self, path: str) -> dict:
        return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))

    def test_feedback_issue_templates_exist(self) -> None:
        for path in [
            ".github/ISSUE_TEMPLATE/false_positive.yml",
            ".github/ISSUE_TEMPLATE/false_positive_report.yml",
            ".github/ISSUE_TEMPLATE/false_negative.yml",
            ".github/ISSUE_TEMPLATE/report_quality_feedback.yml",
            ".github/ISSUE_TEMPLATE/rule_calibration_request.yml",
            ".github/ISSUE_TEMPLATE/external_evaluation_feedback.yml",
            ".github/ISSUE_TEMPLATE/github_action_feedback.yml",
        ]:
            template = REPO_ROOT / path
            self.assertTrue(template.exists(), path)
            text = template.read_text(encoding="utf-8")
            self.assertIn("Do not", text)
            self.assertRegex(text.lower(), r"secret|private key|private keys")

    def test_feedback_metadata_parses(self) -> None:
        schema = self.load_json("metadata/feedback_schema.json")
        examples = self.load_json("metadata/feedback_examples.json")
        backlog = self.load_json("metadata/rule_calibration_backlog.json")

        self.assertEqual(schema["schema_version"], "1.1.0")
        self.assertEqual(examples["schema_version"], "1.1.0")
        self.assertEqual(backlog["schema_version"], "1.1.0")
        self.assertGreaterEqual(len(schema["feedback_types"]), 6)
        self.assertTrue(examples["examples"])
        self.assertTrue(backlog["entries"])
        self.assertTrue(all(item["source_type"] == "synthetic_internal" for item in examples["examples"]))
        self.assertIn("synthetic/internal", examples["description"].lower())

    def test_feedback_dashboard_check_passes(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/generate_feedback_dashboard.py", "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_feedback_docs_and_reports_exist(self) -> None:
        for path in [
            "docs/FEEDBACK_LOOP.md",
            "docs/PUBLIC_FEEDBACK_GUIDE.md",
            "docs/FEEDBACK_TRIAGE_WORKFLOW.md",
            "docs/VALIDATION_LEVELS.md",
            "reports/feedback_dashboard.md",
            "reports/rule_calibration_backlog.md",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_feedback_docs_avoid_fake_adoption_claims(self) -> None:
        checked_paths = [
            "docs/FEEDBACK_LOOP.md",
            "docs/PUBLIC_FEEDBACK_GUIDE.md",
            "docs/VALIDATION_LEVELS.md",
            "reports/feedback_dashboard.md",
            "reports/rule_calibration_backlog.md",
            "metadata/feedback_examples.json",
        ]
        banned = [
            "used by top protocols",
            "trusted by auditors",
            "proven in production",
            "adopted by teams",
        ]
        for path in checked_paths:
            text = (REPO_ROOT / path).read_text(encoding="utf-8").lower()
            for phrase in banned:
                if phrase in text:
                    self.assertIn("disallowed", text, f"{phrase} appears outside a clear prohibition context in {path}")


if __name__ == "__main__":
    unittest.main()
