import unittest

from arkheionx.ingest import discover_solidity

from ._helpers import ROOT


class ContractsDirectoryDiscoveryTest(unittest.TestCase):
    def test_discovers_contracts_directory(self):
        result = discover_solidity(ROOT / "hardhat_style_basic")
        self.assertGreater(result.files_indexed, 0)
        self.assertIn("contracts/Wallet.sol", [source.rel for source in result.sources])


if __name__ == "__main__":
    unittest.main()
