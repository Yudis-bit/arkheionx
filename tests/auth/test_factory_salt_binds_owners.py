import unittest

from ._helpers import analyze


class FactorySaltBindingTest(unittest.TestCase):
    def test_safe_factory_binds_owner_and_initializes_atomically(self):
        factory = analyze("generic_factory_create2_safe.sol").factory_init_analyses[0]
        self.assertTrue(factory.signer_or_owner_bound_in_salt)
        self.assertTrue(factory.parent_or_controller_bound_in_salt)
        self.assertTrue(factory.atomic_init)
        self.assertFalse(factory.takeover_risk)


if __name__ == "__main__":
    unittest.main()
