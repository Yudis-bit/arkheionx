"""V10 invariant engine: borrow conservation invariant is generated."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class BorrowConservationInvariantTest(unittest.TestCase):
    def test_borrow_conservation_invariant_generated(self):
        smap = build_semantic_map(_GODEYE / "borrow_swapdata_consent_fixture")
        emap = build_defi_entities(smap)
        tmap = build_transitions(smap, emap)
        invset = build_invariants(smap, emap, tmap)
        self.assertIn("BORROW_CONSERVATION", invset.families())

    def test_borrow_conservation_has_assertion_and_actors(self):
        smap = build_semantic_map(_GODEYE / "borrow_swapdata_consent_fixture")
        emap = build_defi_entities(smap)
        tmap = build_transitions(smap, emap)
        invset = build_invariants(smap, emap, tmap)
        inv = next(i for i in invset.invariants if i.family == "BORROW_CONSERVATION")
        self.assertTrue(inv.assertion_form)
        self.assertTrue(inv.attacker_capability)
        self.assertTrue(inv.victim)
        self.assertTrue(inv.asset)


if __name__ == "__main__":
    unittest.main()
