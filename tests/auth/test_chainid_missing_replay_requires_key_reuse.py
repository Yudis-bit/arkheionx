import unittest

from ._helpers import analyze


class MissingReplayDomainTest(unittest.TestCase):
    def test_missing_domain_requires_key_reuse(self):
        result = analyze("generic_multisig_missing_chainid.sol")
        replay = result.replay_analyses[0]
        self.assertEqual(replay.verdict, "KEY_REUSE_REPLAY")
        self.assertTrue(replay.requires_key_reuse)
        self.assertNotIn(
            "SUBMIT_HIGH_CANDIDATE",
            [item.severity_hint for item in result.candidates],
        )


if __name__ == "__main__":
    unittest.main()
