import unittest

from pathlib import Path

from arkheionx.warrun import run_war_run


class GenericLegacyReplayRepositoryTest(unittest.TestCase):
    def test_replay_is_key_reuse_blocked(self):
        root = Path(__file__).resolve().parents[1] / "fixtures" / "repos" / "truffle_style_legacy_multisig_replay"
        result = run_war_run(root, write=False)
        reality = next(item for item in result["reality_results"] if item.family == "KEY_REUSE_REPLAY")
        self.assertEqual(reality.verdict, "DO_NOT_SUBMIT_KEY_REUSE")


if __name__ == "__main__":
    unittest.main()
