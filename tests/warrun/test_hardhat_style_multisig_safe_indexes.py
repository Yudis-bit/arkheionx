import unittest

from arkheionx.severity import models as S

from ._helpers import run_fixture


class HardhatStyleMultisigSafeTest(unittest.TestCase):
    def test_indexes_and_activates_auth_without_submit_auth_candidate(self):
        result = run_fixture("hardhat_style_multisig_safe")
        self.assertGreater(result["counts"]["contracts_indexed"], 0)
        self.assertTrue(result["auth_analysis"].active)
        auth_families = {item.family for item in result["auth_analysis"].candidates}
        self.assertFalse(auth_families)
        self.assertFalse(any(
            candidate.invariant_family.startswith(("SIGNATURE_", "THRESHOLD_", "DELEGATECALL_"))
            and candidate.economic_severity in S.SUBMIT_LABELS
            for candidate in result["graph"].candidates
        ))


if __name__ == "__main__":
    unittest.main()
