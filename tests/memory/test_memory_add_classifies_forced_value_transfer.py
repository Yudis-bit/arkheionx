import unittest

from ._helpers import run_memory_add


class MemoryAddForcedValueTransferTest(unittest.TestCase):
    def test_classifies_forced_value_transfer(self):
        temp, code, output = run_memory_add(
            "--target", "forced_value_transfer_no_logic_flaw_benchmark",
            "--root-cause",
            "forced value transfer changes contract balance without logic flaw",
        )
        self.addCleanup(temp.cleanup)
        self.assertEqual(code, 0)
        self.assertIn("family=FORCED_VALUE_TRANSFER_NO_LOGIC_FLAW", output)


if __name__ == "__main__":
    unittest.main()
