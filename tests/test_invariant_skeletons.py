import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class InvariantSkeletonTests(unittest.TestCase):
    skeleton_paths = [
        "examples/reports/ArkheionxAMMInvariants.t.sol",
        "examples/reports/ArkheionxLendingInvariants.t.sol",
        "examples/reports/ArkheionxHybridInvariants.t.sol",
    ]

    template_paths = [
        "templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol",
        "templates/invariant_skeletons/vault_invariants.sol",
        "templates/invariant_skeletons/oracle_invariants.sol",
        "templates/invariant_skeletons/access_control_invariants.sol",
        "templates/invariant_skeletons/reentrancy_value_flow_invariants.sol",
        "templates/invariant_skeletons/reward_invariants.sol",
        "templates/invariant_skeletons/amm_invariants.sol",
        "templates/invariant_skeletons/lending_invariants.sol",
        "templates/invariant_skeletons/hybrid_invariants.sol",
    ]

    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def test_generated_skeletons_exist_with_disclaimers_and_todos(self) -> None:
        for path in self.skeleton_paths:
            text = self.read(path)
            self.assertIn("Arkheionx-generated defensive invariant skeleton", text)
            self.assertIn("Human review required", text)
            self.assertIn("TODO", text)
            self.assertIn("pragma solidity", text)

    def test_category_templates_exist(self) -> None:
        for path in self.template_paths:
            self.assertTrue((REPO_ROOT / path).exists(), path)
            text = self.read(path)
            self.assertIn("TODO", text)
            self.assertIn("pragma solidity", text)

    def test_skeletons_avoid_unsafe_terms(self) -> None:
        banned = [
            "private key",
            "mnemonic",
            "rpc url",
            "mainnet fork",
            "drain",
            "profit",
            "exploit payload",
            "live target",
            "guaranteed invariant coverage",
        ]
        for path in self.skeleton_paths + self.template_paths:
            text = self.read(path).lower()
            for phrase in banned:
                self.assertNotIn(phrase, text, f"{path} contains {phrase}")


if __name__ == "__main__":
    unittest.main()
