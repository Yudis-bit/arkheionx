import unittest

from ._helpers import run_fixture


class HardhatStyleLayoutWarRunTest(unittest.TestCase):
    def test_indexes_contracts(self):
        result = run_fixture("hardhat_style_basic")
        self.assertGreater(result["counts"]["contracts_indexed"], 0)
        self.assertEqual(result["ingest_summary"].framework, "hardhat_style")


if __name__ == "__main__":
    unittest.main()
