"""V10 economic severity gate: route-buffer consent is fork/low, not fake high."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.severity import apply_gate
from arkheionx.severity import models as S

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _gated(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
    apply_gate(graph)
    return {c.invariant_family: c for c in graph.candidates}


class RouteBufferSeverityTest(unittest.TestCase):
    def setUp(self):
        self.c = _gated("borrow_swapdata_consent_fixture")["LENDER_CONSENT_VALUE_AFFECTING_CALLDATA"]

    def test_not_classified_high(self):
        self.assertNotEqual(self.c.economic_severity, S.SUBMIT_HIGH_CANDIDATE)

    def test_needs_fork_proof(self):
        self.assertEqual(self.c.economic_severity, S.NEEDS_FORK_PROOF)

    def test_cap_is_buffer_and_same_token_immune(self):
        d = self.c.severity_detail
        self.assertIn("buffer", d["cap"].lower())
        self.assertIn("same-token", d["realism"].lower())


if __name__ == "__main__":
    unittest.main()
