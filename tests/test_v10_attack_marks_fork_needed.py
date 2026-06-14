"""V10 attack engine: consent/route candidate is marked fork-needed."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class CandidateForkNeededTest(unittest.TestCase):
    def setUp(self):
        smap = build_semantic_map(_GODEYE / "borrow_swapdata_consent_fixture")
        emap = build_defi_entities(smap)
        tmap = build_transitions(smap, emap)
        invset = build_invariants(smap, emap, tmap)
        self.graph = build_candidates(smap, emap, tmap, invset)

    def test_consent_candidate_requires_fork(self):
        consent = next(c for c in self.graph.candidates
                       if c.invariant_family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")
        self.assertTrue(consent.fork_requirement)
        self.assertEqual(consent.proof_strategy, "fork")

    def test_local_candidate_not_marked_fork(self):
        local = [c for c in self.graph.candidates
                 if c.invariant_family == "BORROW_CONSERVATION"]
        self.assertTrue(local)
        self.assertFalse(local[0].fork_requirement)


if __name__ == "__main__":
    unittest.main()
