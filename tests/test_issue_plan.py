import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"
ISSUE_SCRIPT = REPO_ROOT / "scripts" / "create_github_issues.py"


class IssuePlanTests(unittest.TestCase):
    def test_issue_plan_contains_markers_disclaimers_and_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plan_path = tmp_path / "issue-plan.json"
            checklist_path = tmp_path / "checklist.md"
            subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/vault-risk-fixture"),
                    "--protocol-type",
                    "vault",
                    "--output",
                    str(tmp_path / "report.md"),
                    "--json-output",
                    str(tmp_path / "report.json"),
                    "--issue-plan-output",
                    str(plan_path),
                    "--issue-checklist-output",
                    str(checklist_path),
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan["version"], "0.6.0")
            self.assertTrue(plan["issues"])
            first = plan["issues"][0]
            self.assertTrue(first["marker"].startswith("<!-- arkheionx-issue:ARK-"))
            self.assertIn("not a formal audit finding", first["body"])
            self.assertIn("does not confirm a vulnerability", first["body"])
            self.assertIn("confidence_reason", first)
            self.assertIn("evidence", first)
            self.assertIn("## Evidence", first["body"])
            self.assertIn("arkheionx", first["labels"])
            self.assertIn("pre-audit-readiness", first["labels"])
            self.assertIn("Convert This Checklist Into GitHub Issues", checklist_path.read_text(encoding="utf-8"))

    def test_create_github_issues_dry_run_makes_no_api_call(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plan_path = tmp_path / "issue-plan.json"
            dry_run_path = tmp_path / "dry-run.md"
            subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/vault-risk-fixture"),
                    "--protocol-type",
                    "vault",
                    "--output",
                    str(tmp_path / "report.md"),
                    "--json-output",
                    str(tmp_path / "report.json"),
                    "--issue-plan-output",
                    str(plan_path),
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            result = subprocess.run(
                [
                    "python3",
                    str(ISSUE_SCRIPT),
                    "--issue-plan",
                    str(plan_path),
                    "--mode",
                    "dry-run",
                    "--dry-run-output",
                    str(dry_run_path),
                    "--max-issues",
                    "3",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("No GitHub API calls were made.", result.stdout)
            self.assertTrue(dry_run_path.exists())
            self.assertLessEqual(result.stdout.count("<!-- arkheionx-issue:"), 3)

    def test_create_mode_without_token_skips_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plan_path = tmp_path / "issue-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "tool": "Arkheionx Pre-Audit Scanner",
                        "issues": [
                            {
                                "marker": "<!-- arkheionx-issue:ARK-TEST-001 -->",
                                "title": "[Arkheionx][High] ARK-TEST-001 - Test",
                                "body": "<!-- arkheionx-issue:ARK-TEST-001 -->\nBody",
                                "priority": "High readiness gap",
                                "labels": ["arkheionx"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(ISSUE_SCRIPT), "--issue-plan", str(plan_path), "--mode", "create"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                env={},
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("requires GitHub token and repository", result.stderr)


if __name__ == "__main__":
    unittest.main()
