"""V10 invariant engine: lender consent on value-affecting calldata (route-buffer-like)."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class LenderConsentInvariantTest(unittest.TestCase):
    def setUp(self):
        smap = build_semantic_map(_GODEYE / "borrow_swapdata_consent_fixture")
        emap = build_defi_entities(smap)
        tmap = build_transitions(smap, emap)
        self.invset = build_invariants(smap, emap, tmap)

    def test_consent_invariant_generated_and_suspicious(self):
        consent = [i for i in self.invset.invariants
                   if i.family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA"]
        self.assertTrue(consent)
        self.assertTrue(consent[0].suspicious)

    def test_consent_invariant_requires_fork(self):
        consent = next(i for i in self.invset.invariants
                       if i.family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")
        self.assertEqual(consent.testability, "fork")

    def test_reasons_mention_hash_and_guard(self):
        consent = next(i for i in self.invset.invariants
                       if i.family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")
        joined = " ".join(consent.suspicion_reasons).lower()
        self.assertIn("hash", joined)
        self.assertTrue("min-refund" in joined or "guard" in joined or "minout" in joined)


if __name__ == "__main__":
    unittest.main()
