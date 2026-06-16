import tempfile
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.semantic import models as M

from ._artifact_helpers import SOURCE, write_json


class GenericArtifactIngestionTest(unittest.TestCase):
    def test_generic_ast_artifact_enriches_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "contracts" / "GenericArtifactContract.sol"
            source.parent.mkdir(parents=True)
            source.write_text(SOURCE, encoding="utf-8")
            write_json(root / "artifacts" / "GenericArtifactContract.json", {
                "contractName": "GenericArtifactContract",
                "sourceName": "contracts/GenericArtifactContract.sol",
                "abi": [{"type": "function", "name": "setValue", "inputs": [], "outputs": []}],
                "ast": {"nodeType": "SourceUnit"},
                "storageLayout": {"storage": [{"label": "value", "type": "t_uint256"}]},
            })
            smap = build_semantic_map(root)
            self.assertEqual(smap.artifact_mode, M.AST_PLUS_FALLBACK)
            self.assertIsNotNone(smap.contract("GenericArtifactContract"))


if __name__ == "__main__":
    unittest.main()
