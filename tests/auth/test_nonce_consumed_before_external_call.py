import unittest

from ._helpers import analyze


class NonceOrderingTest(unittest.TestCase):
    def test_nonce_consumed_before_call(self):
        replay = analyze("generic_multisig_safe.sol").replay_analyses[0]
        self.assertTrue(replay.nonce_present)
        self.assertTrue(replay.consumed_before_external_call)
        self.assertFalse(replay.replay_same_wallet)


if __name__ == "__main__":
    unittest.main()
