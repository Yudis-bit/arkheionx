import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"
SCHEMA_DIR = REPO_ROOT / "schemas"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_required(testcase: unittest.TestCase, payload: dict, schema_name: str) -> None:
    schema = load_json(SCHEMA_DIR / schema_name)
    testcase.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
    for field in schema.get("required", []):
        testcase.assertIn(field, payload, f"{schema_name} requires {field}")


class SchemaOutputTests(unittest.TestCase):
    def test_schema_files_exist_and_parse(self) -> None:
        for name in [
            "pre-audit-report.schema.json",
            "issue-plan.schema.json",
            "baseline.schema.json",
            "diff.schema.json",
            "security-memory-graph.schema.json",
            "finding-knowledge-map.schema.json",
            "rule-calibration-matrix.schema.json",
            "test_plan.schema.json",
        ]:
            payload = load_json(SCHEMA_DIR / name)
            self.assertIn("title", payload)
            self.assertIn("required", payload)

    def test_generated_outputs_have_v1_schema_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report = tmp_path / "report.json"
            issue_plan = tmp_path / "issue-plan.json"
            baseline = tmp_path / "baseline.json"
            diff_json = tmp_path / "diff.json"

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
                    str(report),
                    "--baseline-output",
                    str(baseline),
                    "--issue-plan-output",
                    str(issue_plan),
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/oracle-staking-fixture"),
                    "--protocol-type",
                    "auto",
                    "--compare-baseline",
                    str(baseline),
                    "--output",
                    str(tmp_path / "diff-report.md"),
                    "--diff-json-output",
                    str(diff_json),
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            report_data = load_json(report)
            plan_data = load_json(issue_plan)
            baseline_data = load_json(baseline)
            diff_data = load_json(diff_json)

            self.assertEqual(report_data["schema_version"], "1.0.0")
            self.assertEqual(report_data["version"], "2.0.1")
            self.assertEqual(plan_data["schema_version"], "1.0.0")
            self.assertEqual(baseline_data["schema_version"], "1.0.0")
            self.assertEqual(diff_data["schema_version"], "1.0.0")

            assert_required(self, report_data, "pre-audit-report.schema.json")
            assert_required(self, plan_data, "issue-plan.schema.json")
            assert_required(self, baseline_data, "baseline.schema.json")
            assert_required(self, diff_data, "diff.schema.json")

    def test_memory_graph_metadata_matches_schemas(self) -> None:
        assert_required(
            self,
            load_json(REPO_ROOT / "metadata/security_memory_graph.json"),
            "security-memory-graph.schema.json",
        )
        assert_required(
            self,
            load_json(REPO_ROOT / "metadata/finding_knowledge_map.json"),
            "finding-knowledge-map.schema.json",
        )
        assert_required(
            self,
            load_json(REPO_ROOT / "metadata/rule_calibration_matrix.json"),
            "rule-calibration-matrix.schema.json",
        )


if __name__ == "__main__":
    unittest.main()
