import tempfile
import unittest

from arkheionx.memory.models import MemoryEntry
from arkheionx.memory.store import MemoryStore
from arkheionx.severity import models as S

from ._helpers import ROOT, run_fixture


class WarRunRejectedRoundingTest(unittest.TestCase):
    def test_rejected_rounding_never_submittable(self):
        with tempfile.TemporaryDirectory() as temp:
            store = MemoryStore(temp)
            store.add("findings", MemoryEntry(
                target="rejected_rounding_reconciliation_benchmark",
                root_cause=(
                    "repayment asymmetric rounding between aggregate borrower "
                    "repayment and per-tranche lender distribution"
                ),
                status="rejected",
                do_not_resubmit=True,
            ))
            result = run_fixture(
                "rejected_rounding_reconciliation_benchmark",
                memory_dir=temp,
                asset_decimals=6,
            )
            candidate = next(
                item for item in result["graph"].candidates
                if item.invariant_family == "DEBT_REPAYMENT_RECONCILIATION"
            )
            self.assertNotIn(candidate.economic_severity, S.SUBMIT_LABELS)
            reality = next(
                item for item in result["reality_results"]
                if item.candidate_id == candidate.id
            )
            self.assertTrue(reality.blocked)
            self.assertIn("PREVIOUSLY_REJECTED", reality.verdict)


if __name__ == "__main__":
    unittest.main()
