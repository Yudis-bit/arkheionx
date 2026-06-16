"""V10 PoC skeleton engine: repay reconciliation skeleton."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.pocgen import build_skeletons
from arkheionx.pocgen.models import REQUIRES_MANUAL_FILL

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _skeletons(name, top_n=6):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
    return graph, build_skeletons(graph, smap, top_n=top_n)


class RepaySkeletonTest(unittest.TestCase):
    def setUp(self):
        _, self.sk = _skeletons("loan_repay_rounding_fixture")
        self.recon = next(s for s in self.sk
                          if s.family == "DEBT_REPAYMENT_RECONCILIATION")

    def test_skeleton_generated_for_reconciliation(self):
        self.assertTrue(self.recon.file_name.endswith(".t.sol"))
        self.assertEqual(self.recon.compile_ready_level, REQUIRES_MANUAL_FILL)

    def test_asserts_debt_vs_credit_and_severity_cap(self):
        src = self.recon.source
        self.assertIn("debtBefore", src)
        self.assertIn("assert", src)
        self.assertIn("SEVERITY CAP", src)
        self.assertIn("dust", src.lower())

    def test_does_not_claim_compiles(self):
        self.assertIn("will not compile unmodified", self.recon.source)
        self.assertNotIn("vm.broadcast", self.recon.source)
        self.assertNotIn("startBroadcast", self.recon.source)


if __name__ == "__main__":
    unittest.main()
