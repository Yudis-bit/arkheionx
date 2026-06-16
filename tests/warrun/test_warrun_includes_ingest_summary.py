import unittest

from ._helpers import run_fixture


class WarRunIngestArtifactTest(unittest.TestCase):
    def test_includes_ingest_summary(self):
        result = run_fixture("hardhat_style_basic")
        self.assertIn("ingest-summary.json", result["jsons"])
        self.assertIn("ingest-summary.md", result["contents"])
        self.assertIn("ingest_summary", result["triage"])


if __name__ == "__main__":
    unittest.main()
