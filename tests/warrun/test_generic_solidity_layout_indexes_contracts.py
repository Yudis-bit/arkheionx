import unittest

from ._helpers import run_fixture


class GenericSolidityLayoutWarRunTest(unittest.TestCase):
    def test_indexes_contracts(self):
        result = run_fixture("generic_solidity_basic")
        self.assertGreater(result["counts"]["contracts_indexed"], 0)
        self.assertEqual(result["ingest_summary"].framework, "generic_solidity")


if __name__ == "__main__":
    unittest.main()
