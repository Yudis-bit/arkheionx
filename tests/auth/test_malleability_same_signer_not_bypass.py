import unittest

from ._helpers import analyze


class SignatureMalleabilityTest(unittest.TestCase):
    def test_same_signer_does_not_bypass_unique_count(self):
        result = analyze("generic_multisig_safe.sol")
        threshold = result.threshold_analyses[0]
        self.assertTrue(threshold.duplicate_signer_check)
        self.assertIn("cannot increase", threshold.malleability_impact)
        self.assertNotIn("THRESHOLD_AUTHORIZATION_BYPASS", [item.family for item in result.candidates])


if __name__ == "__main__":
    unittest.main()
