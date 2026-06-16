import unittest

from arkheionx.bounty.models import BountyRealityInput, BountyRealityVerdict as V
from arkheionx.bounty.reality_gate import evaluate

from ._helpers import candidate, severity


class ForcedValueTransferRealityTest(unittest.TestCase):
    def test_forced_value_without_logic_flaw(self):
        result = evaluate(BountyRealityInput(
            attack_candidate=candidate("FORCED_VALUE_TRANSFER_NO_LOGIC_FLAW"),
            severity_result=severity(),
            no_contract_logic_flaw=True,
        ))
        self.assertEqual(result.verdict, V.DO_NOT_SUBMIT_FORCED_VALUE_TRANSFER_ONLY)


if __name__ == "__main__":
    unittest.main()
