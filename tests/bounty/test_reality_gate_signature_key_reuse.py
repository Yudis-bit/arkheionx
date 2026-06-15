import unittest

from arkheionx.bounty.models import BountyRealityInput, BountyRealityVerdict as V
from arkheionx.bounty.program_policy import ProgramPolicy
from arkheionx.bounty.reality_gate import evaluate

from ._helpers import candidate, severity


class SignatureKeyReuseRealityTest(unittest.TestCase):
    def test_key_reuse_carveout_blocks_submit(self):
        result = evaluate(BountyRealityInput(
            attack_candidate=candidate("SIGNATURE_REPLAY_DOMAIN"),
            severity_result=severity(),
            requires_key_reuse=True,
            scope_policy=ProgramPolicy(excludes_key_reuse=True),
        ))
        self.assertEqual(result.verdict, V.DO_NOT_SUBMIT_KEY_REUSE)
        self.assertTrue(result.blocked)


if __name__ == "__main__":
    unittest.main()
