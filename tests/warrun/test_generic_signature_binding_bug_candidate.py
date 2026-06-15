import unittest

from arkheionx.severity import models as S

from ._helpers import run_fixture


class GenericSignatureBindingBugCandidateTest(unittest.TestCase):
    def test_missing_destination_is_promoted(self):
        result = run_fixture("generic_signature_binding_bug")
        candidate = next(
            item for item in result["graph"].candidates
            if item.invariant_family == "SIGNATURE_OPERATION_BINDING"
        )
        self.assertIn(candidate.economic_severity, (
            S.SUBMIT_HIGH_CANDIDATE,
            S.SUBMIT_CRITICAL_CANDIDATE,
        ))


if __name__ == "__main__":
    unittest.main()
