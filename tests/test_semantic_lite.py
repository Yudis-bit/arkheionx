import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"


class SemanticLiteAnalysisTests(unittest.TestCase):
    def run_scanner(self, root: str, extra_args: list[str] | None = None) -> tuple[dict, dict, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_path = tmp_path / "report.json"
            sarif_path = tmp_path / "report.sarif.json"
            issue_plan_path = tmp_path / "issue-plan.json"
            command = [
                "python3",
                str(SCANNER),
                "--root",
                str(REPO_ROOT / root),
                "--protocol-type",
                "auto",
                "--output",
                str(tmp_path / "report.md"),
                "--json-output",
                str(json_path),
                "--sarif-output",
                str(sarif_path),
                "--issue-plan-output",
                str(issue_plan_path),
            ]
            if extra_args:
                command.extend(extra_args)
            subprocess.run(command, cwd=REPO_ROOT, check=True, text=True, capture_output=True)
            return (
                json.loads(json_path.read_text(encoding="utf-8")),
                json.loads(sarif_path.read_text(encoding="utf-8")),
                json.loads(issue_plan_path.read_text(encoding="utf-8")),
            )

    def test_semantic_lite_extracts_structure_and_attaches_evidence(self) -> None:
        report, sarif, issue_plan = self.run_scanner("examples/semantic-lite-fixture")

        self.assertEqual(report["version"], "1.0.0")
        self.assertEqual(report["schema_version"], "1.0.0")
        self.assertEqual(report["analysis_quality"]["semantic_lite"], "enabled")
        self.assertGreaterEqual(report["analysis_quality"]["semantic_contracts"], 2)
        contracts = {item["name"] for item in report["semantic_lite"]["contracts"]}
        self.assertIn("RealOracleConsumer", contracts)

        functions = {
            function["name"]
            for contract in report["semantic_lite"]["contracts"]
            for function in contract["functions"]
        }
        self.assertIn("readPrice", functions)
        self.assertTrue(report["findings"])
        for finding in report["findings"]:
            self.assertIn("confidence_reason", finding)
            self.assertIn("detection_sources", finding)
            self.assertIn("evidence", finding)

        low_confidence_ids = {
            finding["id"]
            for finding in report["findings"]
            if finding["confidence"] == "low"
        }
        self.assertIn("ARK-RWD-001", low_confidence_ids)
        self.assertIn("excluded_low_confidence_findings", issue_plan)
        self.assertGreaterEqual(len(issue_plan["excluded_low_confidence_findings"]), 1)

        locations = []
        for result in sarif["runs"][0]["results"]:
            for location in result.get("locations", []):
                artifact = location.get("physicalLocation", {}).get("artifactLocation", {})
                locations.append(artifact.get("uri", ""))
        self.assertIn("src/RealOracleConsumer.sol", locations)

    def test_slither_unavailable_is_graceful(self) -> None:
        report, _, _ = self.run_scanner("examples/semantic-lite-fixture", ["--slither"])

        self.assertTrue(report["slither"]["enabled"])
        self.assertIn(report["slither"]["source"], {"generated", "provided", "unavailable"})
        self.assertIn(report["analysis_quality"]["slither"].split(" ")[0], {"enabled", "unavailable"})


if __name__ == "__main__":
    unittest.main()
