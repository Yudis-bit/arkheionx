import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"


class SlitherIntegrationTests(unittest.TestCase):
    def test_provided_slither_json_is_normalized_and_used_as_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            slither_json = tmp_path / "slither.json"
            slither_json.write_text(
                json.dumps(
                    {
                        "results": {
                            "detectors": [
                                {
                                    "check": "reentrancy-eth",
                                    "impact": "High",
                                    "confidence": "Medium",
                                    "description": "Local fixture detector output.",
                                    "elements": [
                                        {
                                            "name": "claimReward",
                                            "type": "function",
                                            "source_mapping": {
                                                "filename_relative": "src/OracleRewardFixture.sol",
                                                "lines": [91],
                                            },
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            report_json = tmp_path / "report.json"
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
                    str(report_json),
                    "--slither-json",
                    str(slither_json),
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            report = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertTrue(report["slither"]["enabled"])
            self.assertTrue(report["slither"]["available"])
            self.assertEqual(report["slither"]["source"], "provided")
            self.assertEqual(report["slither"]["detectors"][0]["check"], "reentrancy-eth")
            reentrancy = [finding for finding in report["findings"] if finding["id"] == "ARK-REENT-001"]
            self.assertTrue(reentrancy)
            self.assertIn("slither", reentrancy[0]["detection_sources"])
            self.assertTrue(any(item["type"] == "slither" for item in reentrancy[0]["evidence"]))


if __name__ == "__main__":
    unittest.main()
