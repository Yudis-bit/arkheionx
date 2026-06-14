"""V10 PoC skeleton engine: borrow/swap consent skeleton (fork)."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.pocgen import build_skeletons

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class BorrowSwapSkeletonTest(unittest.TestCase):
    def setUp(self):
        smap = build_semantic_map(_GODEYE / "borrow_swapdata_consent_fixture")
        emap = build_defi_entities(smap)
        tmap = build_transitions(smap, emap)
        invset = build_invariants(smap, emap, tmap)
        graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
        self.sk = build_skeletons(graph, smap, top_n=6)
        self.consent = next(s for s in self.sk
                            if s.family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")

    def test_honest_vs_attacker_route_and_refund_delta(self):
        src = self.consent.source
        self.assertIn("honestRoute", src)
        self.assertIn("attackerRoute", src)
        self.assertIn("refund", src.lower())

    def test_fork_required_and_env_only(self):
        self.assertTrue(self.consent.required_fork_env)
        src = self.consent.source
        self.assertIn("FORK_RPC_URL", src)
        # secret safety: the env VAR NAME appears, never a URL.
        self.assertNotIn("http://", src)
        self.assertNotIn("https://", src)

    def test_invariant_comment_present(self):
        self.assertIn("INVARIANT", self.consent.source)


if __name__ == "__main__":
    unittest.main()
