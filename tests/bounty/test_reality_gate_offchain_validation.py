import unittest

from arkheionx.bounty.models import BountyRealityInput, BountyRealityVerdict as V
from arkheionx.bounty.program_policy import ProgramPolicy
from arkheionx.bounty.reality_gate import evaluate

from ._helpers import candidate, severity


class OffchainValidationRealityTest(unittest.TestCase):
    def test_offchain_validation_carveout(self):
        result = evaluate(BountyRealityInput(
            attack_candidate=candidate("OFFCHAIN_VALIDATION_OMISSION"),
            severity_result=severity(),
            scope_policy=ProgramPolicy(excludes_offchain_validation=True),
        ))
        self.assertEqual(result.verdict, V.DO_NOT_SUBMIT_OFFCHAIN_VALIDATION)


if __name__ == "__main__":
    unittest.main()
