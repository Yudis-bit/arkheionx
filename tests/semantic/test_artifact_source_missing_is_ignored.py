import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map

from ._artifact_helpers import SOURCE, write_json


ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "repos"


class ArtifactSourceMissingIgnoredTest(unittest.TestCase):
    def test_artifact_source_missing_is_ignored(self):
        root = ROOT / "artifact_source_missing_is_ignored"
        smap = build_semantic_map(root)
        self.assertIsNone(smap.contract("GenericMissingArtifact"))
        summary = smap._ingest_summary
        self.assertEqual(summary.stale_artifacts_ignored, 1)
        self.assertTrue(any("STALE_ARTIFACT_IGNORED" in w for w in summary.warnings))

    def test_temp_missing_source_artifact_is_ignored(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_json(root / "build" / "contracts" / "GenericMissingArtifact.json", {
                "contractName": "GenericMissingArtifact",
                "sourcePath": "contracts/GenericMissingArtifact.sol",
                "source": SOURCE,
                "compiler": {"version": "generic"},
                "abi": [],
            })
            smap = build_semantic_map(root)
            self.assertIsNone(smap.contract("GenericMissingArtifact"))
            self.assertTrue(any("ZERO_REAL_CONTRACTS_INDEXED" in w for w in smap.warnings))


if __name__ == "__main__":
    unittest.main()
