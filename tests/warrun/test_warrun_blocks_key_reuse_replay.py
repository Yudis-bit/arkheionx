import unittest

from arkheionx.severity import models as S

from ._helpers import run_fixture


class WarRunKeyReuseReplayTest(unittest.TestCase):
    def test_key_reuse_replay_is_not_high(self):
        result = run_fixture("truffle_style_legacy_multisig_replay")
        candidate = next(
            item for item in result["graph"].candidates
            if item.invariant_family == "KEY_REUSE_REPLAY"
        )
        self.assertNotIn(candidate.economic_severity, (
            S.SUBMIT_HIGH_CANDIDATE,
            S.SUBMIT_CRITICAL_CANDIDATE,
        ))
        self.assertEqual(candidate.bounty_reality["verdict"], "DO_NOT_SUBMIT_KEY_REUSE")


if __name__ == "__main__":
    unittest.main()
