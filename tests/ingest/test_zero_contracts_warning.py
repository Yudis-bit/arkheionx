import tempfile
import unittest

from arkheionx.ingest import discover_solidity


class ZeroContractsWarningTest(unittest.TestCase):
    def test_zero_contracts_is_explicit(self):
        with tempfile.TemporaryDirectory() as temp:
            result = discover_solidity(temp)
            self.assertEqual(result.files_indexed, 0)
            self.assertTrue(any("ZERO_CONTRACTS_INDEXED" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()
