"""V10 semantic core: storage access map (alias-aware)."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class SemanticStorageMapTest(unittest.TestCase):
    def test_deposit_consume_writes_deposits(self):
        smap = build_semantic_map(_GODEYE / "deposit_double_use_fixture")
        writes = {(a.function, a.variable) for a in smap.storage_accesses if a.kind in ("write", "delete")}
        self.assertIn(("DepositManager.consume", "deposits"), writes)
        self.assertIn(("DepositManager.createDeposit", "deposits"), writes)

    def test_loan_repay_writes_loans(self):
        smap = build_semantic_map(_GODEYE / "loan_repay_rounding_fixture")
        writes = {(a.function, a.variable) for a in smap.storage_accesses if a.kind == "write"}
        self.assertIn(("LoanRouter.repay", "loans"), writes)

    def test_storage_access_lines_are_within_file(self):
        smap = build_semantic_map(_GODEYE / "loan_repay_rounding_fixture")
        self.assertTrue(smap.storage_accesses)
        for a in smap.storage_accesses:
            self.assertGreater(a.line, 0)
            self.assertIn(a.kind, ("read", "write", "delete"))

    def test_external_call_before_write_flags_reentrancy(self):
        smap = build_semantic_map(_GODEYE / "deposit_double_use_fixture")
        consume_calls = [x for x in smap.external_calls if x.function == "DepositManager.consume"]
        self.assertTrue(consume_calls)
        # token.transfer happens before the `active` (deposits) write is cleared.
        self.assertTrue(any(x.reentrancy_relevant and "deposits" in x.writes_after
                            for x in consume_calls))


if __name__ == "__main__":
    unittest.main()
