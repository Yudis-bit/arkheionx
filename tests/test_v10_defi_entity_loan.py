"""V10 DeFi entity detection: loan-router shape."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.defi import entities as E

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class DefiEntityLoanTest(unittest.TestCase):
    def setUp(self):
        smap = build_semantic_map(_GODEYE / "loan_repay_rounding_fixture")
        self.emap = build_defi_entities(smap)

    def test_loan_entities_detected(self):
        types = self.emap.types()
        for expected in (E.LOAN, E.DEBT, E.COLLATERAL, E.TRANCHE, E.LENDER, E.BORROWER, E.REPAYMENT):
            self.assertIn(expected, types, f"missing {expected}")

    def test_repayment_direction_is_in(self):
        rep = self.emap.by_type(E.REPAYMENT)
        self.assertIsNotNone(rep)
        self.assertEqual(rep.value_direction, E.DIR_IN)

    def test_entities_have_evidence(self):
        for e in self.emap.entities:
            self.assertTrue(e.source_symbols)
            self.assertTrue(e.evidence_lines)
            self.assertTrue(e.related_contracts)


if __name__ == "__main__":
    unittest.main()
