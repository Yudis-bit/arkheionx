import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"


class RulePackExpansionTests(unittest.TestCase):
    def test_oracle_staking_fixture_emits_new_rule_pack_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_path = tmp_path / "report.json"
            sarif_path = tmp_path / "report.sarif.json"
            subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/oracle-staking-fixture"),
                    "--protocol-type",
                    "auto",
                    "--output",
                    str(tmp_path / "report.md"),
                    "--json-output",
                    str(json_path),
                    "--sarif-output",
                    str(sarif_path),
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            report = json.loads(json_path.read_text(encoding="utf-8"))
            finding_ids = {finding["id"] for finding in report["findings"]}
            self.assertIn("rule_packs", report)
            self.assertTrue(report["rule_packs"]["oracle"]["detected"])
            self.assertTrue(report["rule_packs"]["reward_accounting"]["detected"])
            self.assertTrue(report["rule_packs"]["access_control_upgradeability"]["detected"])
            self.assertTrue(report["rule_packs"]["reentrancy_value_flow"]["detected"])
            self.assertIn("ARK-ORC-001", finding_ids)
            self.assertIn("ARK-RWD-001", finding_ids)
            self.assertIn("ARK-ACC-003", finding_ids)
            self.assertIn("ARK-REENT-001", finding_ids)

            sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
            rule_ids = {rule["id"] for rule in sarif["runs"][0]["tool"]["driver"]["rules"]}
            self.assertIn("ARK-ORC-001", rule_ids)
            self.assertIn("ARK-RWD-001", rule_ids)
            for result in sarif["runs"][0]["results"]:
                self.assertTrue(result["properties"]["not_a_vulnerability_confirmation"])


if __name__ == "__main__":
    unittest.main()
