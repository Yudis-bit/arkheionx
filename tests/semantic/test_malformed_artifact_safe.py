import tempfile
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.semantic import models as M


class MalformedArtifactSafetyTest(unittest.TestCase):
    def test_malformed_artifact_does_not_abort(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "artifacts" / "broken.json"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("{not-json", encoding="utf-8")
            smap = build_semantic_map(root)
            self.assertEqual(smap.artifact_mode, M.FALLBACK_ONLY)
            self.assertTrue(any("malformed" in warning for warning in smap.warnings))


if __name__ == "__main__":
    unittest.main()
