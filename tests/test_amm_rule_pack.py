import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AmmRulePackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.tmp_path = Path(cls.tmp.name)
        cls.report = cls.tmp_path / "amm-report.md"
        cls.json_report = cls.tmp_path / "amm-report.json"
        cls.sarif = cls.tmp_path / "amm.sarif.json"
        cls.issue_plan = cls.tmp_path / "amm-issue-plan.json"
        result = subprocess.run(
            [
                "python3",
                "scripts/pre_audit_scan.py",
                "--root",
                "examples/amm-fixture",
                "--protocol-type",
                "amm",
                "--output",
                str(cls.report),
                "--json-output",
                str(cls.json_report),
                "--sarif-output",
                str(cls.sarif),
                "--issue-plan-output",
                str(cls.issue_plan),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def load_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def test_amm_fixture_triggers_amm_findings(self) -> None:
        data = self.load_json(self.json_report)
        ids = {item["id"] for item in data["findings"]}
        self.assertEqual(data["protocol_type"], "amm")
        for finding_id in ["ARK-AMM-001", "ARK-AMM-002", "ARK-AMM-003", "ARK-AMM-004", "ARK-AMM-005"]:
            self.assertIn(finding_id, ids)
        self.assertTrue(data["rule_packs"]["amm"]["detected"])
        self.assertIn("docs/AMM_RULE_PACK.md", data["rule_packs"]["amm"]["docs"])

    def test_amm_outputs_include_sarif_and_issue_plan_ids(self) -> None:
        sarif = self.load_json(self.sarif)
        sarif_ids = {item["ruleId"] for item in sarif["runs"][0]["results"]}
        self.assertIn("ARK-AMM-001", sarif_ids)
        self.assertIn("ARK-AMM-005", sarif_ids)

        issue_plan = self.load_json(self.issue_plan)
        issue_ids = {item["finding_id"] for item in issue_plan["issues"]}
        self.assertIn("ARK-AMM-002", issue_ids)
        self.assertTrue(all("related_knowledge" in item for item in issue_plan["issues"]))

    def test_amm_report_mentions_rule_pack_without_unsafe_claims(self) -> None:
        text = self.report.read_text(encoding="utf-8")
        self.assertIn("AMM Rule Pack", text)
        self.assertIn("ARK-AMM", text)
        self.assertIn("not a formal audit", text.lower())
        self.assertNotIn("vulnerability confirmed", text.lower())


if __name__ == "__main__":
    unittest.main()
