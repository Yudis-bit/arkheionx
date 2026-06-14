"""V10 attack engine: candidate construction from suspicious invariants."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _candidates(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    return smap, build_candidates(smap, emap, tmap, invset)


class AttackCandidateFromInvariantTest(unittest.TestCase):
    def test_repay_candidate_is_complete(self):
        _, graph = _candidates("loan_repay_rounding_fixture")
        recon = [c for c in graph.candidates
                 if c.invariant_family == "DEBT_REPAYMENT_RECONCILIATION"]
        self.assertTrue(recon)
        c = recon[0]
        # Every candidate must explain attacker, victim, asset, transition, invariant, PoC path.
        self.assertTrue(c.attacker_capability)
        self.assertTrue(c.victim)
        self.assertTrue(c.asset)
        self.assertEqual(c.entry_function, "LoanRouter.repay")
        self.assertTrue(c.broken_invariant)
        self.assertTrue(c.root_cause)
        self.assertTrue(c.call_sequence)
        self.assertTrue(c.state_transition)
        self.assertIn(c.proof_strategy, ("local", "fork", "manual"))

    def test_call_sequence_reaches_distribute(self):
        _, graph = _candidates("loan_repay_rounding_fixture")
        c = next(c for c in graph.candidates
                 if c.invariant_family == "DEBT_REPAYMENT_RECONCILIATION")
        joined = " ".join(c.call_sequence)
        self.assertIn("_distribute", joined)

    def test_required_conditions_present(self):
        _, graph = _candidates("loan_repay_rounding_fixture")
        c = next(c for c in graph.candidates
                 if c.invariant_family == "DEBT_REPAYMENT_RECONCILIATION")
        self.assertTrue(c.required_conditions)


if __name__ == "__main__":
    unittest.main()
