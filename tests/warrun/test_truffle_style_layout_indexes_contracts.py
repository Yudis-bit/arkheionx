import unittest

from ._helpers import run_fixture


class TruffleStyleLayoutWarRunTest(unittest.TestCase):
    def test_indexes_contracts(self):
        result = run_fixture("truffle_style_basic")
        self.assertGreater(result["counts"]["contracts_indexed"], 0)
        self.assertEqual(result["ingest_summary"].framework, "truffle_style")


if __name__ == "__main__":
    unittest.main()
