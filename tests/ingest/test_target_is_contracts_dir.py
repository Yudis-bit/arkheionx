import unittest

from arkheionx.ingest import discover_solidity

from ._helpers import ROOT


class DirectContractsTargetTest(unittest.TestCase):
    def test_direct_contracts_target(self):
        result = discover_solidity(ROOT / "truffle_style_basic" / "contracts")
        self.assertGreater(result.files_indexed, 0)
        self.assertEqual(result.sources[0].rel, "LegacyWallet.sol")


if __name__ == "__main__":
    unittest.main()
