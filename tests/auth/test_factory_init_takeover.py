import unittest

from ._helpers import analyze


class FactoryInitializationTakeoverTest(unittest.TestCase):
    def test_uninitialized_account_can_be_taken_over(self):
        result = analyze("generic_factory_init_takeover.sol")
        factory = result.factory_init_analyses[0]
        self.assertTrue(factory.initializer_callable)
        self.assertFalse(factory.initializer_guard)
        self.assertTrue(factory.takeover_risk)
        self.assertIn("FACTORY_INITIALIZATION_TAKEOVER", [item.family for item in result.candidates])


if __name__ == "__main__":
    unittest.main()
