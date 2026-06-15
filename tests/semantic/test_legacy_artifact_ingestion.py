import tempfile
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.semantic import models as M

from ._artifact_helpers import SOURCE, write_json


class LegacyArtifactIngestionTest(unittest.TestCase):
    def test_legacy_source_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "contracts" / "GenericArtifactContract.sol"
            source.parent.mkdir(parents=True)
            source.write_text(SOURCE, encoding="utf-8")
            write_json(root / "build" / "contracts" / "GenericArtifactContract.json", {
                "contractName": "GenericArtifactContract",
                "sourcePath": "contracts/GenericArtifactContract.sol",
                "source": SOURCE,
                "compiler": {"version": "generic"},
                "abi": [],
                "bytecode": "0x",
                "deployedBytecode": "0x",
            })
            smap = build_semantic_map(root)
            self.assertEqual(smap.artifact_mode, M.LEGACY_ARTIFACT_PLUS_FALLBACK)
            self.assertIsNotNone(smap.contract("GenericArtifactContract"))


if __name__ == "__main__":
    unittest.main()
