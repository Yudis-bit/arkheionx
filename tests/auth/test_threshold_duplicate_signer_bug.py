import unittest

from ._helpers import analyze


class DuplicateSignerThresholdTest(unittest.TestCase):
    def test_duplicate_signer_bypasses_threshold(self):
        result = analyze("generic_multisig_duplicate_signer_bug.sol")
        threshold = result.threshold_analyses[0]
        self.assertEqual(threshold.verdict, "DUPLICATE_SIGNER_THRESHOLD_BYPASS")
        self.assertFalse(threshold.duplicate_signer_check)
        self.assertIn("THRESHOLD_AUTHORIZATION_BYPASS", [item.family for item in result.candidates])


if __name__ == "__main__":
    unittest.main()
