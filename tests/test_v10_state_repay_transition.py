"""V10 state transition engine: repay lifecycle."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.state import transitions as T

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class RepayTransitionTest(unittest.TestCase):
    def setUp(self):
        smap = build_semantic_map(_GODEYE / "loan_repay_rounding_fixture")
        emap = build_defi_entities(smap)
        self.tmap = build_transitions(smap, emap)
        self.repay = self.tmap.for_function("LoanRouter.repay")

    def test_repay_transition_exists(self):
        self.assertIsNotNone(self.repay)
        self.assertEqual(self.repay.lifecycle, T.LC_REPAY)

    def test_has_division_flag_from_distribute(self):
        # repay folds in _distribute, which floors per-tranche shares.
        self.assertIn("has_division", self.repay.flags)

    def test_reconciliation_invariant_hinted(self):
        self.assertIn("DEBT_REPAYMENT_RECONCILIATION", self.repay.possible_invariants)
        self.assertIn("COLLATERAL_STATUS_RELEASE", self.repay.possible_invariants)

    def test_status_change_repaid_no_comparison_noise(self):
        joined = " ".join(self.repay.status_changes)
        self.assertIn("loan.status = 1", joined)
        # The `loan.status == 0` comparison in a require must not be captured.
        self.assertNotIn("== 0", joined)

    def test_assets_out_present(self):
        self.assertTrue(self.repay.assets_out)


if __name__ == "__main__":
    unittest.main()
