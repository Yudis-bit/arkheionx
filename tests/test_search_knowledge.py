import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class SearchKnowledgeTests(unittest.TestCase):
    def run_search(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/search_knowledge.py", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_oracle_query_returns_oracle_finding(self) -> None:
        result = self.run_search("oracle stale price")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ARK-ORC-001", result.stdout)
        self.assertIn("stale", result.stdout.lower())

    def test_vault_query_returns_vault_context(self) -> None:
        result = self.run_search("vault accounting invariant")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ARK-VLT", result.stdout)

    def test_json_output_parses(self) -> None:
        result = self.run_search("missing invariant", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["query"], "missing invariant")
        self.assertTrue(payload["matches"])

    def test_type_filter(self) -> None:
        result = self.run_search("oracle", "--type", "finding")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Type: finding", result.stdout)


if __name__ == "__main__":
    unittest.main()
