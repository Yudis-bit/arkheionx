import unittest

from ._helpers import run_memory_add


class MemoryAddUnknownTest(unittest.TestCase):
    def test_unknown_still_hashes_and_warns(self):
        temp, code, output = run_memory_add(
            "--target", "generic_duplicate_rejection_fixture",
            "--root-cause", "unclassified semantic condition",
        )
        self.addCleanup(temp.cleanup)
        self.assertEqual(code, 0)
        self.assertIn("family=UNKNOWN", output)
        self.assertRegex(output, r"hash=[0-9a-f]{16}")
        self.assertIn("warnings=[low confidence]", output)


if __name__ == "__main__":
    unittest.main()
