import unittest

from ._helpers import analyze


class DelegatecallBindingTest(unittest.TestCase):
    def test_delegatecall_type_not_bound(self):
        result = analyze("generic_multisig_delegatecall_unbound.sol")
        delegate = result.delegatecall_analyses[0]
        self.assertFalse(delegate.operation_type_bound)
        self.assertTrue(delegate.storage_control_risk)
        self.assertIn("DELEGATECALL_STORAGE_CONTROL", [item.family for item in result.candidates])


if __name__ == "__main__":
    unittest.main()
