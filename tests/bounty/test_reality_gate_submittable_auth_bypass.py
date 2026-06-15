import unittest

from arkheionx.bounty.models import BountyRealityInput, BountyRealityVerdict as V
from arkheionx.bounty.reality_gate import evaluate

from ._helpers import candidate, severity


class SubmittableAuthorizationBypassRealityTest(unittest.TestCase):
    def test_proven_unprivileged_threshold_bypass(self):
        result = evaluate(BountyRealityInput(
            attack_candidate=candidate("THRESHOLD_AUTHORIZATION_BYPASS"),
            severity_result=severity(),
            attacker_profit=True,
            victim_loss=True,
            unprivileged=True,
            proof_quality="LOCAL_POC_PASSING",
            not_duplicate=True,
            not_oos=True,
        ))
        self.assertEqual(result.verdict, V.SUBMITTABLE)
        self.assertFalse(result.blocked)


if __name__ == "__main__":
    unittest.main()
