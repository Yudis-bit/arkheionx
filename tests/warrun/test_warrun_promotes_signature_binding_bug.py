import unittest

from arkheionx.severity import models as S

from ._helpers import run_fixture


class WarRunSignatureBindingPromotionTest(unittest.TestCase):
    def test_unbound_destination_is_high_or_critical_candidate(self):
        result = run_fixture("generic_signature_binding_bug")
        candidate = next(
            item for item in result["graph"].candidates
            if item.invariant_family == "SIGNATURE_OPERATION_BINDING"
        )
        self.assertIn(candidate.economic_severity, (
            S.SUBMIT_HIGH_CANDIDATE,
            S.SUBMIT_CRITICAL_CANDIDATE,
        ))
        self.assertEqual(candidate.bounty_reality["verdict"], "NEEDS_MORE_PROOF")


if __name__ == "__main__":
    unittest.main()
