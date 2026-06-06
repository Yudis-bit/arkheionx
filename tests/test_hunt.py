import unittest
from pathlib import Path

from arkheionx.hunt.ranker import rank_targets
from arkheionx.proof.generator import generate_scaffold, harness_name
from arkheionx.protocol.detector import analyze

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "oracle-staking-fixture"


class HuntTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analysis = analyze(FIXTURE)

    def test_targets_ranked_and_capped(self) -> None:
        targets = rank_targets(self.analysis.functions, "HEURISTIC", top=3)
        self.assertEqual(len(targets), 3)
        self.assertEqual([t.rank for t in targets], [1, 2, 3])
        scores = [t.score for t in targets]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_top_target_is_value_mover(self) -> None:
        top = self.analysis.hunter_targets[0]
        self.assertIn(top.target_id.split(".")[-1].split("#")[0], {"claimReward", "unstake", "stake"})
        self.assertTrue(top.bug_classes)
        self.assertTrue(top.suggested_tests)
        self.assertIn("prove", top.next_command)

    def test_bug_classes_are_defensive(self) -> None:
        for t in self.analysis.hunter_targets:
            for bc in t.bug_classes:
                self.assertIn("candidate", bc.lower())


class ProofScaffoldTests(unittest.TestCase):
    def test_scaffold_does_not_fake_proof(self) -> None:
        scaffold = generate_scaffold(
            "OracleRewardFixture", "claimReward",
            ["Call claimReward() twice in one block; assert second yields zero"],
            ["Sum of claimed rewards <= funded rewards"],
        )
        self.assertIn("vm.skip(true)", scaffold)
        self.assertIn(harness_name("OracleRewardFixture", "claimReward"), scaffold)
        # Must never assert a trivially-true condition just to pass.
        self.assertNotIn("assertTrue(true", scaffold)
        self.assertNotIn("assert(true)", scaffold)
        self.assertIn("not a proof", scaffold)


if __name__ == "__main__":
    unittest.main()
