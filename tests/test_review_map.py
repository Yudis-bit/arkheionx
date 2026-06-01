"""Protocol Review Map: data model, detection, and build tests (v3.1.0)."""
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.review_map.detect import build_function_surface, value_direction
from arkheionx.review_map.model import HIGH

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "arkheionx" / "demo" / "fixtures"
DEMOS = ["oracle-staking", "amm-swap", "lending-vault"]


class VersionMetadataTests(unittest.TestCase):
    def test_version_metadata_is_v31_dev(self) -> None:
        from arkheionx.version import (
            CURRENT_MILESTONE,
            NEXT_MILESTONE,
            PACKAGE_VERSION,
            STABLE_RELEASE,
            __version__,
        )

        self.assertEqual(__version__, "3.1.0")
        self.assertEqual(PACKAGE_VERSION, "3.1.0")
        self.assertEqual(STABLE_RELEASE, "v3.0.0")
        self.assertEqual(CURRENT_MILESTONE, "v3.1.0")
        self.assertEqual(NEXT_MILESTONE, "v3.2.0")


class ValueDirectionTests(unittest.TestCase):
    def test_value_direction_classification(self) -> None:
        # transferFrom shadows the "transfer" substring; names disambiguate.
        self.assertEqual(value_direction("withdraw", ["transfer"]), "out")
        self.assertEqual(value_direction("deposit", ["transfer", "transferFrom"]), "in")
        self.assertEqual(value_direction("unstake", ["transfer"]), "out")  # not "in" despite "stake"
        self.assertEqual(value_direction("swapAForB", ["transfer", "transferFrom"]), "both")
        self.assertEqual(value_direction("getPrice", []), "none")


class TestGapMappingTests(unittest.TestCase):
    """Suggestions must be targeted per function type, not generic."""

    @staticmethod
    def _fs(name: str, direction: str = "none", risk=None):
        from arkheionx.review_map.model import FunctionSurface

        return FunctionSurface(contract="C", name=name, value_direction=direction,
                               risk_signals=risk or [], mutability="state-changing")

    def _suggest(self, name: str, direction: str = "none", risk=None) -> list[str]:
        from arkheionx.review_map.tests import suggested_tests_for

        return suggested_tests_for(self._fs(name, direction, risk))

    def test_swap_does_not_get_withdrawal_only(self) -> None:
        s = self._suggest("swapAForB", "both", ["value-out", "value-in"])
        self.assertIn("slippage bound", s)
        self.assertIn("invariant preservation", s)
        for withdrawal_only in ("withdrawal boundary", "full balance", "partial balance"):
            self.assertNotIn(withdrawal_only, s)

    def test_remove_liquidity_gets_withdrawal_and_sync(self) -> None:
        s = self._suggest("removeLiquidity", "out", ["value-out"])
        self.assertIn("withdrawal boundary", s)
        self.assertIn("reserve/accounting sync", s)

    def test_admin_gets_access_and_config(self) -> None:
        s = self._suggest("setFeeBps", "none", ["privileged"])
        self.assertIn("access control", s)
        self.assertIn("role revocation", s)
        self.assertNotIn("withdrawal boundary", s)

    def test_reward_gets_reward_specific(self) -> None:
        s = self._suggest("claimReward", "out", ["value-out"])
        self.assertIn("double claim", s)
        self.assertIn("reward index monotonicity", s)
        self.assertNotIn("withdrawal boundary", s)

    def test_borrow_gets_oracle_lending(self) -> None:
        s = self._suggest("borrow", "out", ["value-out"])
        self.assertIn("stale oracle rejection", s)
        self.assertIn("health factor boundary", s)
        self.assertNotIn("withdrawal boundary", s)

    def test_liquidate_gets_liquidation_specific(self) -> None:
        s = self._suggest("liquidate", "out", ["value-out", "debt-or-liquidation"])
        self.assertIn("liquidation threshold", s)
        self.assertIn("bad debt edge case", s)
        self.assertNotIn("borrow cap boundary", s)

    def test_plain_exit_gets_withdrawal(self) -> None:
        s = self._suggest("withdrawCollateral", "out", ["value-out"])
        self.assertIn("withdrawal boundary", s)
        self.assertIn("reentrancy receiver", s)


class BuildReviewMapTests(unittest.TestCase):
    def test_builds_on_all_demo_fixtures(self) -> None:
        for demo in DEMOS:
            with self.subTest(demo=demo):
                rm = build_review_map(FIXTURES / demo, top=10)
                self.assertGreaterEqual(rm.summary.contracts_analyzed, 1)
                self.assertGreater(rm.summary.functions_mapped, 0)
                self.assertGreater(rm.summary.value_paths, 0)
                self.assertGreater(rm.summary.assumptions, 0)
                self.assertGreater(rm.summary.test_gaps, 0)
                self.assertGreater(rm.summary.proof_suggestions, 0)

    def test_detects_value_sensitive_functions(self) -> None:
        rm = build_review_map(FIXTURES / "lending-vault", top=10)
        names = {f.name for f in rm.functions}
        self.assertIn("borrow", names)
        self.assertIn("withdrawCollateral", names)
        directions = {f.name: f.value_direction for f in rm.functions}
        self.assertEqual(directions["borrow"], "out")
        self.assertEqual(directions["depositCollateral"], "in")

    def test_value_out_functions_are_high_priority(self) -> None:
        rm = build_review_map(FIXTURES / "oracle-staking", top=10)
        by_name = {f.name: f for f in rm.functions}
        self.assertEqual(by_name["claimReward"].review_priority, HIGH)
        self.assertEqual(by_name["unstake"].review_priority, HIGH)

    def test_assumptions_and_test_gaps_link(self) -> None:
        rm = build_review_map(FIXTURES / "lending-vault", top=10)
        titles = {a.title for a in rm.assumptions}
        self.assertTrue(any("oracle" in t.lower() for t in titles))
        self.assertTrue(any("erc20" in t.lower() for t in titles))
        # Each test gap is heuristic and tied to a function.
        for gap in rm.test_gaps:
            self.assertEqual(gap.evidence_level, "HEURISTIC")
            self.assertTrue(gap.related_function)
            self.assertNotEqual(gap.confidence, "high")  # never overclaim

    def test_proof_suggestions_have_targets_and_hints(self) -> None:
        rm = build_review_map(FIXTURES / "amm-swap", top=10)
        self.assertTrue(rm.proof_suggestions)
        for ps in rm.proof_suggestions:
            self.assertTrue(ps.target)
            self.assertIn("arkheionx prove", ps.foundry_hint)

    def test_paths_are_relative(self) -> None:
        rm = build_review_map(FIXTURES / "amm-swap", top=10)
        for fn in rm.functions:
            self.assertFalse(Path(fn.path).is_absolute(), fn.path)

    def test_evidence_links_empty_without_artifacts(self) -> None:
        rm = build_review_map(FIXTURES / "amm-swap", top=10)
        self.assertEqual(rm.evidence_links, [])

    def test_evidence_links_populate_with_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / "src").mkdir(parents=True)
            (repo / "src" / "Vault.sol").write_text(
                "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\n"
                "interface IERC20Like { function transfer(address to, uint256 a) external returns (bool); }\n"
                "contract Vault {\n IERC20Like public token;\n mapping(address=>uint256) public bal;\n"
                " function withdraw(uint256 a) external { bal[msg.sender]-=a; require(token.transfer(msg.sender,a)); }\n}\n",
                encoding="utf-8",
            )
            proof_dir = repo / ".arkheionx" / "out" / "proof" / "Vault_withdraw"
            proof_dir.mkdir(parents=True)
            (proof_dir / "proof.json").write_text(
                '{"target":"Vault.withdraw","evidence_level":"EXECUTION_CONFIRMED","status":"tested_passed"}',
                encoding="utf-8",
            )
            rm = build_review_map(repo, top=10)
            self.assertTrue(rm.evidence_links)
            link = rm.evidence_links[0]
            self.assertEqual(link.source, "proof")
            self.assertFalse(Path(link.artifact_path).is_absolute())

    def test_unknown_target_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_review_map(FIXTURES / "amm-swap", target="Nope.nope")

    def test_target_filter_limits_output(self) -> None:
        rm = build_review_map(FIXTURES / "amm-swap", target="AMMSwapFixture.swapAForB")
        self.assertTrue(all(f.name == "swapAForB" for f in rm.functions))

    def test_no_solidity_path_builds_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rm = build_review_map(Path(tmp), top=5)
            self.assertEqual(rm.summary.functions_mapped, 0)

    def test_safety_boundaries_present_and_conservative(self) -> None:
        rm = build_review_map(FIXTURES / "oracle-staking", top=5)
        self.assertTrue(rm.safety.disclaimer)
        joined = " ".join(rm.safety.boundaries).lower()
        self.assertIn("no rpc", joined)
        self.assertIn("review guidance", joined)
        payload = str(rm.to_payload()).lower()
        for forbidden in ["critical vulnerability", "bounty", "guaranteed"]:
            self.assertNotIn(forbidden, payload)


if __name__ == "__main__":
    unittest.main()
