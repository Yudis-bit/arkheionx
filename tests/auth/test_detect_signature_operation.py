import unittest

from ._helpers import analyze


class SignatureOperationDetectionTest(unittest.TestCase):
    def test_detects_signed_operation(self):
        result = analyze("generic_multisig_safe.sol")
        self.assertTrue(result.active)
        self.assertEqual(len(result.signed_operations), 1)
        self.assertEqual(result.signed_operations[0].function, "execute")


if __name__ == "__main__":
    unittest.main()
