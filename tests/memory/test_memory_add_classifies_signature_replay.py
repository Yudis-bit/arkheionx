import unittest

from ._helpers import run_memory_add


class MemoryAddSignatureReplayTest(unittest.TestCase):
    def test_classifies_signature_replay(self):
        temp, code, output = run_memory_add(
            "--target", "key_reuse_replay_carveout_benchmark",
            "--root-cause",
            "operation hash omits chain id and wallet address allowing replay across domains",
        )
        self.addCleanup(temp.cleanup)
        self.assertEqual(code, 0)
        self.assertIn("family=SIGNATURE_REPLAY_DOMAIN", output)


if __name__ == "__main__":
    unittest.main()
