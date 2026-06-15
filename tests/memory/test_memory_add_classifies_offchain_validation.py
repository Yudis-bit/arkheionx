import unittest

from ._helpers import run_memory_add


class MemoryAddOffchainValidationTest(unittest.TestCase):
    def test_classifies_offchain_validation(self):
        temp, code, output = run_memory_add(
            "--target", "offchain_validation_carveout_benchmark",
            "--root-cause", "zero address signer validation missing",
        )
        self.addCleanup(temp.cleanup)
        self.assertEqual(code, 0)
        self.assertIn("family=OFFCHAIN_VALIDATION_OMISSION", output)


if __name__ == "__main__":
    unittest.main()
