import unittest

from arkheionx.bounty.models import BountyRealityInput, BountyRealityVerdict as V
from arkheionx.bounty.reality_gate import evaluate

from ._helpers import candidate, severity


class RouteBufferRealityTest(unittest.TestCase):
    def test_small_unproven_buffer_is_not_medium(self):
        result = evaluate(BountyRealityInput(
            attack_candidate=candidate("LENDER_CONSENT_VALUE_FIELD_BINDING"),
            severity_result=severity(),
            official_buffer_small=True,
            capture_proven=False,
            safe_mode_exists=True,
        ))
        self.assertEqual(result.verdict, V.DO_NOT_SUBMIT_AS_MEDIUM)
        self.assertTrue(result.blocked)


if __name__ == "__main__":
    unittest.main()
