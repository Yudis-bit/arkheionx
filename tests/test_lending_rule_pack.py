import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class LendingRulePackTests(unittest.TestCase):
    def run_scan(self, fixture: str, protocol_type: str) -> tuple[dict, dict, dict, str]:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report = tmp_path / "report.md"
            json_report = tmp_path / "report.json"
            sarif = tmp_path / "report.sarif.json"
            issue_plan = tmp_path / "issue-plan.json"
            result = subprocess.run(
                [
                    "python3",
                    "scripts/pre_audit_scan.py",
                    "--root",
                    fixture,
                    "--protocol-type",
                    protocol_type,
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
            return (
                json.loads(json_report.read_text(encoding="utf-8")),
                json.loads(sarif.read_text(encoding="utf-8")),
                json.loads(issue_plan.read_text(encoding="utf-8")),
                report.read_text(encoding="utf-8"),
            )

    def test_lending_fixture_triggers_lending_findings(self) -> None:
        data, sarif, issue_plan, report_text = self.run_scan("examples/lending-fixture", "lending")
        ids = {item["id"] for item in data["findings"]}
        self.assertEqual(data["protocol_type"], "lending")
        for finding_id in ["ARK-LEND-001", "ARK-LEND-002", "ARK-LEND-003", "ARK-LEND-004", "ARK-LEND-005"]:
            self.assertIn(finding_id, ids)
        self.assertTrue(data["rule_packs"]["lending"]["detected"])
        self.assertIn("Lending Rule Pack", report_text)
        self.assertIn("ARK-LEND-004", {item["ruleId"] for item in sarif["runs"][0]["results"]})
        self.assertIn("ARK-LEND-001", {item["finding_id"] for item in issue_plan["issues"]})

    def test_hybrid_fixture_detects_amm_and_lending_signals(self) -> None:
        data, sarif, issue_plan, _ = self.run_scan("examples/amm-lending-hybrid-fixture", "auto")
        ids = {item["id"] for item in data["findings"]}
        self.assertTrue(any(item.startswith("ARK-AMM-") for item in ids))
        self.assertTrue(any(item.startswith("ARK-LEND-") for item in ids))
        self.assertTrue(data["rule_packs"]["amm"]["detected"])
        self.assertTrue(data["rule_packs"]["lending"]["detected"])
        sarif_ids = {item["ruleId"] for item in sarif["runs"][0]["results"]}
        self.assertTrue(any(item.startswith("ARK-AMM-") for item in sarif_ids))
        self.assertTrue(any(item.startswith("ARK-LEND-") for item in sarif_ids))
        issue_ids = {item["finding_id"] for item in issue_plan["issues"]}
        self.assertTrue(any(item.startswith("ARK-AMM-") for item in issue_ids))
        self.assertTrue(any(item.startswith("ARK-LEND-") for item in issue_ids))

    def test_docs_and_release_checks_cover_lending_pack(self) -> None:
        for path in [
            "docs/AMM_RULE_PACK.md",
            "docs/LENDING_RULE_PACK.md",
            "examples/amm-fixture/README.md",
            "examples/lending-fixture/README.md",
            "examples/amm-lending-hybrid-fixture/README.md",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)
        for command in [
            ["python3", "scripts/check_version_consistency.py", "--check"],
            ["python3", "scripts/check_docs_links.py", "--check"],
            ["python3", "scripts/check_safety_wording.py", "--strict"],
        ]:
            result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
