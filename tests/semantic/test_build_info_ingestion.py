import tempfile
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.semantic import models as M

from ._artifact_helpers import SOURCE, write_json


class BuildInfoIngestionTest(unittest.TestCase):
    def test_build_info_sources_and_contracts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_name = "contracts/GenericArtifactContract.sol"
            write_json(root / "artifacts" / "build-info" / "build.json", {
                "input": {"sources": {source_name: {"content": SOURCE}}},
                "output": {
                    "sources": {source_name: {"ast": {"nodeType": "SourceUnit"}}},
                    "contracts": {
                        source_name: {
                            "GenericArtifactContract": {
                                "abi": [{"type": "function", "name": "setValue"}],
                                "storageLayout": {"storage": []},
                            }
                        }
                    },
                },
            })
            smap = build_semantic_map(root)
            self.assertEqual(smap.artifact_mode, M.BUILD_INFO_PLUS_FALLBACK)
            self.assertIsNotNone(smap.contract("GenericArtifactContract"))


if __name__ == "__main__":
    unittest.main()
