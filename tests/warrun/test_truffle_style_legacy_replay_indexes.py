import unittest

from ._helpers import run_fixture


class TruffleStyleLegacyReplayTest(unittest.TestCase):
    def test_indexes_and_flags_key_reuse_replay(self):
        result = run_fixture("truffle_style_legacy_multisig_replay")
        self.assertGreater(result["counts"]["contracts_indexed"], 0)
        self.assertTrue(result["auth_analysis"].active)
        self.assertIn("KEY_REUSE_REPLAY", [item.family for item in result["auth_analysis"].candidates])
        reality = next(item for item in result["reality_results"] if item.family == "KEY_REUSE_REPLAY")
        self.assertTrue(reality.blocked)


if __name__ == "__main__":
    unittest.main()
