"""V10 invariant engine: vault share/asset reconciliation."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class VaultShareInvariantTest(unittest.TestCase):
    def setUp(self):
        smap = build_semantic_map(_GODEYE / "vault_share_inflation_fixture")
        emap = build_defi_entities(smap)
        tmap = build_transitions(smap, emap)
        self.invset = build_invariants(smap, emap, tmap)

    def test_vault_share_invariant_suspicious(self):
        share = [i for i in self.invset.invariants
                 if i.family == "VAULT_SHARE_ASSET_RECONCILIATION"]
        self.assertTrue(share)
        self.assertTrue(any(i.suspicious for i in share))

    def test_reasons_mention_inflation(self):
        share = next(i for i in self.invset.invariants
                     if i.family == "VAULT_SHARE_ASSET_RECONCILIATION" and i.suspicious)
        joined = " ".join(share.suspicion_reasons).lower()
        self.assertTrue("inflate" in joined or "donation" in joined or "zero-share" in joined)

    def test_invariant_set_json_safe(self):
        import json
        json.dumps(self.invset.to_dict())


if __name__ == "__main__":
    unittest.main()
