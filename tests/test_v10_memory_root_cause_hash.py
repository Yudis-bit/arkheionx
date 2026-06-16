"""V10 memory: semantic root-cause hash."""
import unittest

from arkheionx.memory import root_cause_hash as rch
from arkheionx.attack.models import AttackCandidate


class RootCauseHashTest(unittest.TestCase):
    def test_same_inputs_same_hash(self):
        a = rch.root_cause_hash("DEBT_REPAYMENT_RECONCILIATION", "repay", "borrower")
        b = rch.root_cause_hash("DEBT_REPAYMENT_RECONCILIATION", "repay", "borrower")
        self.assertEqual(a, b)

    def test_different_family_differs(self):
        a = rch.root_cause_hash("DEBT_REPAYMENT_RECONCILIATION", "repay", "borrower")
        b = rch.root_cause_hash("LENDER_CONSENT_VALUE_AFFECTING_CALLDATA", "borrow", "borrower")
        self.assertNotEqual(a, b)

    def test_function_role_is_contract_agnostic(self):
        # Same root cause on different contracts/pools -> same role -> same hash.
        c1 = AttackCandidate(entry_function="PoolA.borrow",
                             invariant_family="LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
                             attacker_capability="borrower")
        c2 = AttackCandidate(entry_function="PoolB.borrow",
                             invariant_family="LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
                             attacker_capability="borrower")
        self.assertEqual(rch.components_for_candidate(c1)["root_cause_hash"],
                         rch.components_for_candidate(c2)["root_cause_hash"])

    def test_role_mapping(self):
        self.assertEqual(rch.function_role("LoanRouter.repay"), "repay")
        self.assertEqual(rch.function_role("X.originateLoan"), "borrow")
        self.assertEqual(rch.function_role("Treasury.sweep"), "admin_value_move")


if __name__ == "__main__":
    unittest.main()
