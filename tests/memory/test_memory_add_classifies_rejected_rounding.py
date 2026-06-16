import unittest

from ._helpers import run_memory_add


class MemoryAddRejectedRoundingTest(unittest.TestCase):
    def test_classifies_and_hashes(self):
        temp, code, output = run_memory_add(
            "--target", "rejected_rounding_reconciliation_benchmark",
            "--root-cause",
            "repayment asymmetric rounding between aggregate borrower repayment "
            "and per-tranche lender distribution",
            "--status", "rejected",
            "--do-not-resubmit",
        )
        self.addCleanup(temp.cleanup)
        self.assertEqual(code, 0)
        self.assertIn("family=ROUNDING_REPAYMENT_RECONCILIATION", output)
        self.assertRegex(output, r"hash=[0-9a-f]{16}")


if __name__ == "__main__":
    unittest.main()
