import unittest

from ._helpers import run_fixture


class RealisticHardhatNestedContractsTest(unittest.TestCase):
    def test_nested_hardhat_sources_are_indexed(self):
        result = run_fixture("hardhat_realistic_nested_contracts")
        summary = result["ingest_summary"]
        self.assertEqual(summary.framework, "hardhat_style")
        self.assertGreater(summary.solidity_files_indexed, 0)
        self.assertGreater(summary.contracts_indexed, 0)
        self.assertGreater(summary.real_contracts_indexed, 0)


if __name__ == "__main__":
    unittest.main()
