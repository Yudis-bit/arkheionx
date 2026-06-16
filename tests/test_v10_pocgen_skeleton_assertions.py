"""V10 PoC skeleton engine: every skeleton carries assertions."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.pocgen import build_skeletons

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"

_FIXTURES = [
    "loan_repay_rounding_fixture",
    "borrow_swapdata_consent_fixture",
    "vault_share_inflation_fixture",
    "deposit_double_use_fixture",
]


def _skeletons(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
    return build_skeletons(graph, smap, top_n=4)


class SkeletonAssertionsTest(unittest.TestCase):
    def test_every_skeleton_has_assertion_and_invariant_comment(self):
        for fx in _FIXTURES:
            for s in _skeletons(fx):
                with self.subTest(fixture=fx, file=s.file_name):
                    self.assertTrue(s.assertions, "no assertion lines")
                    has_assert = ("assert" in s.source) or ("expectRevert" in s.source)
                    self.assertTrue(has_assert, "skeleton missing assertions")
                    self.assertIn("INVARIANT", s.source)
                    self.assertTrue(s.test_name.startswith("test_"))

    def test_skeletons_never_contain_secrets_or_broadcast(self):
        for fx in _FIXTURES:
            for s in _skeletons(fx):
                with self.subTest(fixture=fx, file=s.file_name):
                    # No actual broadcast calls (the disclaimer says "no broadcast").
                    self.assertNotIn("vm.broadcast", s.source)
                    self.assertNotIn("startBroadcast", s.source)
                    self.assertNotIn("PRIVATE_KEY", s.source)
                    self.assertNotIn("http://", s.source)
                    self.assertNotIn("https://", s.source)


if __name__ == "__main__":
    unittest.main()
