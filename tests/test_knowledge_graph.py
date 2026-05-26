import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class KnowledgeGraphTests(unittest.TestCase):
    def test_security_memory_graph_exists_and_parses(self) -> None:
        graph_path = REPO_ROOT / "metadata/security_memory_graph.json"
        self.assertTrue(graph_path.exists())
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        self.assertEqual(graph["schema_version"], "1.0.0")
        self.assertTrue(graph["nodes"])
        self.assertTrue(graph["edges"])
        node_ids = {node["id"] for node in graph["nodes"]}
        node_types = {node["type"] for node in graph["nodes"]}
        self.assertIn("ARK-ORC-001", node_ids)
        self.assertIn("historical_pattern", node_types)
        self.assertIn("poc", node_types)

    def test_finding_knowledge_map_core_families(self) -> None:
        payload = json.loads((REPO_ROOT / "metadata/finding_knowledge_map.json").read_text(encoding="utf-8"))
        findings = payload["findings"]
        for finding_id in ["ARK-ORC-001", "ARK-VLT-001", "ARK-REENT-001", "ARK-ACC-001", "ARK-UPG-001", "ARK-RWD-001", "ARK-TST-002"]:
            self.assertIn(finding_id, findings)
            self.assertTrue(findings[finding_id]["historical_patterns"])
            self.assertTrue(findings[finding_id]["suggested_tests"])
        self.assertTrue(findings["ARK-ORC-001"]["related_pocs"])

    def test_rule_calibration_matrix_core_families(self) -> None:
        payload = json.loads((REPO_ROOT / "metadata/rule_calibration_matrix.json").read_text(encoding="utf-8"))
        families = {item["finding_family"] for item in payload["families"]}
        for family in ["ARK-VLT", "ARK-ORC", "ARK-ACC", "ARK-UPG", "ARK-REENT", "ARK-RWD", "ARK-TST", "ARK-DOC"]:
            self.assertIn(family, families)

    def test_generate_knowledge_graph_check_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/generate_knowledge_graph.py", "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("up to date", result.stdout)

    def test_reports_include_related_knowledge(self) -> None:
        report = (REPO_ROOT / "examples/reports/demo-pre-audit-report.md").read_text(encoding="utf-8")
        plan = (REPO_ROOT / "examples/reports/demo-issue-plan.json").read_text(encoding="utf-8")
        self.assertIn("Related Knowledge", report)
        self.assertIn("Related Knowledge", plan)
        data = json.loads((REPO_ROOT / "examples/reports/demo-report.json").read_text(encoding="utf-8"))
        self.assertIn("knowledge", data)
        self.assertTrue(all("knowledge" in item for item in data["findings"]))


if __name__ == "__main__":
    unittest.main()
