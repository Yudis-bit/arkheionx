import unittest

from arkheionx.ingest import discover_solidity

from ._helpers import ROOT


class HardhatContractsDirectoryMultipleFilesTest(unittest.TestCase):
    def test_indexes_multiple_contract_files(self):
        result = discover_solidity(ROOT / "hardhat_contracts_directory_with_multiple_solidity_files")
        self.assertEqual(result.files_indexed, 2)
        self.assertEqual(
            {source.rel for source in result.sources},
            {"contracts/GenericAlpha.sol", "contracts/GenericBeta.sol"},
        )


if __name__ == "__main__":
    unittest.main()
