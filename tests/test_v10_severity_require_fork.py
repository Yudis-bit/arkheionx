"""V10 economic severity gate: fork requirement classification."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.severity import apply_gate, classify
from arkheionx.severity import models as S
from arkheionx.attack.models import AttackCandidate

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class RequireForkSeverityTest(unittest.TestCase):
    def test_fork_required_candidate_gets_needs_fork(self):
        smap = build_semantic_map(_GODEYE / "borrow_swapdata_consent_fixture")
        emap = build_defi_entities(smap)
        tmap = build_transitions(smap, emap)
        invset = build_invariants(smap, emap, tmap)
        graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
        apply_gate(graph)
        consent = next(c for c in graph.candidates
                       if c.invariant_family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")
        self.assertEqual(consent.economic_severity, S.NEEDS_FORK_PROOF)

    def test_swap_candidate_with_fork_requirement(self):
        # A synthetic swap candidate flagged fork-required must classify NEEDS_FORK_PROOF.
        c = AttackCandidate(id="AC-X", invariant_family="SWAP_ACTUAL_RECEIVED_VS_CREDITED",
                            fork_requirement=True, attacker_capability="user")
        v = classify(c)
        self.assertEqual(v.label, S.NEEDS_FORK_PROOF)


if __name__ == "__main__":
    unittest.main()
