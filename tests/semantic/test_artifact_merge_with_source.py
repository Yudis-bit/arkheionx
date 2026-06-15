import tempfile
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.semantic import models as M

from ._artifact_helpers import SOURCE, write_json


class ArtifactSourceMergeTest(unittest.TestCase):
    def test_artifact_confidence_merges_with_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "contracts" / "GenericArtifactContract.sol"
            source.parent.mkdir(parents=True)
            source.write_text(SOURCE, encoding="utf-8")
            write_json(root / "artifacts" / "GenericArtifactContract.json", {
                "contractName": "GenericArtifactContract",
                "sourceName": "contracts/GenericArtifactContract.sol",
                "abi": [{"type": "function", "name": "setValue", "inputs": [], "outputs": []}],
                "bytecode": "0x",
                "deployedBytecode": "0x",
            })
            smap = build_semantic_map(root)
            contract = smap.contract("GenericArtifactContract")
            self.assertEqual(smap.artifact_mode, M.ABI_PLUS_FALLBACK)
            self.assertEqual(contract.confidence, M.HIGH)
            self.assertTrue(any("merged" in warning for warning in contract.warnings))


if __name__ == "__main__":
    unittest.main()
