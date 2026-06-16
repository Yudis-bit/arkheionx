"""V10 semantic core: fallback-mode confidence and warnings."""
import tempfile
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.semantic import models as M

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class FallbackParserConfidenceTest(unittest.TestCase):
    def test_mode_is_fallback_with_medium_confidence(self):
        smap = build_semantic_map(_GODEYE / "vault_share_inflation_fixture")
        self.assertEqual(smap.mode, M.MODE_FALLBACK)
        self.assertEqual(smap.confidence, M.MEDIUM)
        self.assertGreaterEqual(smap.files_indexed, 1)

    def test_every_function_carries_confidence(self):
        smap = build_semantic_map(_GODEYE / "vault_share_inflation_fixture")
        fns = list(smap.iter_functions())
        self.assertTrue(fns)
        for fn in fns:
            self.assertIn(fn.confidence, (M.LOW, M.MEDIUM, M.HIGH))

    def test_empty_target_is_low_confidence_with_warning(self):
        with tempfile.TemporaryDirectory() as d:
            smap = build_semantic_map(d)
            self.assertEqual(smap.confidence, M.LOW)
            self.assertTrue(smap.warnings)

    def test_interface_vs_contract_kind(self):
        smap = build_semantic_map(_GODEYE / "vault_share_inflation_fixture")
        kinds = {c.name: c.kind for c in smap.contracts}
        self.assertEqual(kinds.get("IERC20"), M.KIND_INTERFACE)
        self.assertEqual(kinds.get("MiniVault"), M.KIND_CONTRACT)

    def test_to_dict_is_json_safe(self):
        import json
        smap = build_semantic_map(_GODEYE / "vault_share_inflation_fixture")
        json.dumps(smap.to_dict())  # must not raise


if __name__ == "__main__":
    unittest.main()
