import unittest

from arkheionx.bounty.models import BountyRealityInput, BountyRealityVerdict as V
from arkheionx.bounty.reality_gate import evaluate
from arkheionx.bounty.reviewer_outcome import ReviewerOutcome
from arkheionx.memory.models import MemoryEntry
from arkheionx.severity import models as S

from ._helpers import candidate, severity


class RejectedRoundingRealityTest(unittest.TestCase):
    def test_rejected_rounding_is_not_bounty_worthy(self):
        item = candidate("ROUNDING_REPAYMENT_RECONCILIATION")
        result = evaluate(BountyRealityInput(
            attack_candidate=item,
            severity_result=severity(cap_type=S.ROUNDING_UNIT_CAPPED, impact_type=S.DUST_ONLY),
            memory_match=MemoryEntry(status="rejected", do_not_resubmit=True),
            attacker_profit=False,
            victim_loss=True,
            victim_opt_in=True,
            reviewer_outcome_memory=[ReviewerOutcome(
                status="duplicate",
                reason_tags=[
                    "duplicate", "dust", "no_profit", "victim_opt_in",
                    "precision_rounding", "no_significant_risk",
                ],
            )],
        ))
        self.assertIn(result.verdict, (V.DO_NOT_SUBMIT_PREVIOUSLY_REJECTED, V.DO_NOT_SUBMIT_DUPLICATE))
        self.assertIn(V.DO_NOT_SUBMIT_DUST, result.secondary_verdicts)
        self.assertIn(V.DO_NOT_SUBMIT_NO_PROFIT, result.secondary_verdicts)
        self.assertIn(V.DO_NOT_SUBMIT_VICTIM_OPT_IN, result.secondary_verdicts)
        self.assertEqual(result.final_verdict, V.VALID_CODE_BUG_BUT_NOT_BOUNTY_WORTHY)


if __name__ == "__main__":
    unittest.main()
