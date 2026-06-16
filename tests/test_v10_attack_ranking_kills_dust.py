"""V10 attack engine: ranking down-ranks dust and role-gated candidates."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.attack.models import AttackGraph

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _graph(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    return build_candidates(smap, emap, tmap, invset)


class CandidateRankingTest(unittest.TestCase):
    def test_dust_reconciliation_ranks_below_collateral(self):
        g = ranking.rank(_graph("loan_repay_rounding_fixture"))
        by_family = {c.invariant_family: c for c in g.candidates}
        recon = by_family["DEBT_REPAYMENT_RECONCILIATION"]
        coll = by_family["COLLATERAL_STATUS_RELEASE"]
        self.assertLess(recon.rank_score, coll.rank_score)
        self.assertTrue(any("dust" in r or "rounding" in r for r in recon.rank_reasons))

    def test_role_gated_candidate_scored_lowest(self):
        g = ranking.rank(_graph("trusted_role_fixture"))
        c = g.candidates[0]
        self.assertTrue(c.role_gated)
        self.assertLessEqual(c.rank_score, 5.0)
        self.assertTrue(any("role-gated" in r for r in c.rank_reasons))

    def test_dust_loses_to_double_use_across_targets(self):
        # Merge a dust candidate with a deposit double-use candidate and rank.
        loan = _graph("loan_repay_rounding_fixture")
        dep = _graph("deposit_double_use_fixture")
        merged = AttackGraph(root="merged", candidates=loan.candidates + dep.candidates)
        ranking.rank(merged)
        top = merged.candidates[0]
        self.assertEqual(top.invariant_family, "DEPOSIT_CONSUMPTION")


if __name__ == "__main__":
    unittest.main()
