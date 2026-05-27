import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


class TestPlanGeneratorTests(unittest.TestCase):
    def test_finding_test_plan_map_parses_and_covers_rule_families(self) -> None:
        payload = load_json("metadata/finding_test_plan_map.json")
        self.assertEqual(payload["schema_version"], "1.5.0")
        findings = payload["findings"]
        for finding_id in [
            "ARK-VLT-001",
            "ARK-ORC-001",
            "ARK-ACC-001",
            "ARK-UPG-001",
            "ARK-REENT-001",
            "ARK-RWD-001",
            "ARK-TST-002",
            "ARK-AMM-001",
            "ARK-LEND-001",
        ]:
            self.assertIn(finding_id, findings)
            self.assertTrue(findings[finding_id]["suggested_tests"])
            self.assertTrue(findings[finding_id]["invariant_candidates"])
            self.assertTrue(findings[finding_id]["foundry_skeleton_functions"])

    def test_generate_test_plan_check_passes(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/generate_test_plan.py", "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_committed_test_plan_outputs_exist_and_parse(self) -> None:
        for path in [
            "examples/reports/amm-fixture-test-plan.md",
            "examples/reports/amm-fixture-test-plan.json",
            "examples/reports/lending-fixture-test-plan.md",
            "examples/reports/lending-fixture-test-plan.json",
            "examples/reports/amm-lending-hybrid-fixture-test-plan.md",
            "examples/reports/amm-lending-hybrid-fixture-test-plan.json",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)
        for path in [
            "examples/reports/amm-fixture-test-plan.json",
            "examples/reports/lending-fixture-test-plan.json",
            "examples/reports/amm-lending-hybrid-fixture-test-plan.json",
        ]:
            data = load_json(path)
            self.assertEqual(data["tool"], "Arkheionx Test Plan Generator")
            self.assertEqual(data["version"], "2.0.0")
            self.assertIn("source_report", data)
            self.assertTrue(data["suggested_tests"])
            self.assertTrue(data["invariant_candidates"])
            self.assertTrue(data["manual_review_required"])

    def test_markdown_test_plan_has_safety_language(self) -> None:
        text = (REPO_ROOT / "examples/reports/amm-fixture-test-plan.md").read_text(encoding="utf-8").lower()
        self.assertIn("not formal verification", text)
        self.assertIn("not proof of safety", text)
        self.assertIn("human review", text)

    def test_scanner_findings_include_test_plan_fields(self) -> None:
        report = load_json("examples/reports/amm-fixture-pre-audit-report.json")
        amm_findings = [item for item in report["findings"] if item["id"].startswith("ARK-AMM-")]
        self.assertTrue(amm_findings)
        self.assertTrue(any(item.get("invariant_candidates") for item in amm_findings))
        self.assertTrue(all("test_plan" in item for item in amm_findings))
        plan = load_json("examples/reports/amm-fixture-issue-plan.json")
        issue = next(item for item in plan["issues"] if item["finding_id"].startswith("ARK-AMM-"))
        self.assertIn("invariant_candidates", issue)
        self.assertTrue(issue["suggested_tests"])


if __name__ == "__main__":
    unittest.main()
