"""V10 invariant engine: debt-repayment reconciliation (#567-like)."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _invariants(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    return build_invariants(smap, emap, tmap)


class RepayReconciliationInvariantTest(unittest.TestCase):
    def setUp(self):
        self.invset = _invariants("loan_repay_rounding_fixture")

    def test_reconciliation_invariant_is_generated_and_suspicious(self):
        recon = [i for i in self.invset.invariants
                 if i.family == "DEBT_REPAYMENT_RECONCILIATION"]
        self.assertTrue(recon)
        self.assertTrue(recon[0].suspicious)

    def test_reasons_mention_flooring_and_settlement(self):
        recon = next(i for i in self.invset.invariants
                     if i.family == "DEBT_REPAYMENT_RECONCILIATION")
        joined = " ".join(recon.suspicion_reasons).lower()
        self.assertIn("floor", joined)
        self.assertTrue("settlement" in joined or "distribution" in joined)

    def test_collateral_release_invariant_present(self):
        self.assertIn("COLLATERAL_STATUS_RELEASE", self.invset.families())

    def test_testability_is_local(self):
        recon = next(i for i in self.invset.invariants
                     if i.family == "DEBT_REPAYMENT_RECONCILIATION")
        self.assertEqual(recon.testability, "local")


if __name__ == "__main__":
    unittest.main()
