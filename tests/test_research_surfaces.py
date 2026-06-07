"""Unit tests for the v4.1 research surface engine.

Exercises coverage weakness ranking, authorization-surface detection,
periphery/core flow mapping, and behavior-mismatch heuristics against the two
local fixtures. Detection is heuristic; these tests lock the observable signals
and their determinism, and confirm comments/strings do not produce code signals.
"""
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.research import build_research_surfaces, generate_hypotheses
from arkheionx.research import signals as sig

REPO_ROOT = Path(__file__).resolve().parents[1]
VAULT = REPO_ROOT / "examples" / "vault-strategy-oracle-fixture"
AUTH = REPO_ROOT / "examples" / "periphery-auth-fixture"


def surfaces_for(path: Path):
    rm = build_review_map(path)
    return rm, build_research_surfaces(rm, path)


class CoverageRankingTests(unittest.TestCase):
    def test_tested_vs_untested_on_vault(self) -> None:
        rm, s = surfaces_for(VAULT)
        by_surface = {r["surface"]: r for r in s.coverage_ranking}
        # deposit is tested in the fixture; withdraw is not.
        self.assertEqual(by_surface["Vault.deposit"]["coverage_signal"], "tested")
        self.assertNotEqual(by_surface["Vault.deposit"]["weakness_priority"], "inspect-first")
        self.assertEqual(by_surface["Vault.withdraw"]["coverage_signal"], "no direct test observed")
        # withdraw is a high-value value-exit with weak coverage -> inspect first.
        self.assertEqual(by_surface["Vault.withdraw"]["weakness_priority"], "inspect-first")

    def test_rows_are_labelled_heuristic_and_have_reasons(self) -> None:
        _rm, s = surfaces_for(VAULT)
        self.assertTrue(s.coverage_ranking)
        for row in s.coverage_ranking:
            self.assertIn("heuristic", row["basis"])
            self.assertTrue(row["reason"])
            self.assertIn(row["weakness_priority"],
                          {"inspect-first", "important-lower-priority", "maybe-later", "monitor"})


class AuthorizationSurfaceTests(unittest.TestCase):
    def test_vault_detects_ownable(self) -> None:
        _rm, s = surfaces_for(VAULT)
        signals = {r["signal"] for r in s.authorization_surfaces}
        self.assertIn("ownable", signals)
        for row in s.authorization_surfaces:
            self.assertTrue(row["source"])
            self.assertTrue(row["suggested_local_tests"])

    def test_auth_fixture_detects_signature_and_merkle(self) -> None:
        _rm, s = surfaces_for(AUTH)
        signals = {r["signal"] for r in s.authorization_surfaces}
        for expected in ("ecrecover", "EIP712", "MerkleProof", "nonce", "deadline"):
            self.assertIn(expected, signals, f"missing {expected}; got {signals}")

    def test_prose_gate_does_not_create_ratifier_signal(self) -> None:
        # "Gate a claim" appears only in a comment; it must not match the gate signal.
        _rm, s = surfaces_for(AUTH)
        self.assertNotIn("ratifier", {r["signal"] for r in s.authorization_surfaces})


class PeripherySurfaceTests(unittest.TestCase):
    def test_vault_cross_contract_calls(self) -> None:
        _rm, s = surfaces_for(VAULT)
        targets = {r["target"] for r in s.periphery_surfaces}
        self.assertIn("Vault.rebalance", targets)
        rebalance = next(r for r in s.periphery_surfaces if r["target"] == "Vault.rebalance")
        self.assertIn("cross-contract-call", rebalance["interaction_type"])
        self.assertIn("strategy", rebalance["core_targets"])
        joined = "; ".join(rebalance["suggested_local_tests"]).lower()
        self.assertIn("direct call vs periphery", joined)

    def test_bundler_try_catch_and_skip_suggestion(self) -> None:
        _rm, s = surfaces_for(AUTH)
        bundle = next(r for r in s.periphery_surfaces if r["target"] == "OfferBundler.executeBundle")
        self.assertIn("try-catch", bundle["interaction_type"])
        self.assertTrue(any("skip-on-revert" in t for t in bundle["suggested_local_tests"]))

    def test_internal_helper_not_periphery_from_contract_name(self) -> None:
        _rm, s = surfaces_for(AUTH)
        self.assertNotIn("OfferBundler._normalize", {r["target"] for r in s.periphery_surfaces})


class BehaviorMismatchTests(unittest.TestCase):
    def test_vault_revert_comment_attributed_to_getprice(self) -> None:
        _rm, s = surfaces_for(VAULT)
        rows = {(r["target"], r["signal"]) for r in s.behavior_mismatch_surfaces}
        self.assertIn(("PriceOracle.getPrice", "revert"), rows)
        # The setPrice doc comment is on the line above getPrice; it must not be misattributed.
        self.assertNotIn(("PriceOracle.setPrice", "revert"), rows)

    def test_bundler_skip_signals(self) -> None:
        _rm, s = surfaces_for(AUTH)
        signals = {r["signal"] for r in s.behavior_mismatch_surfaces if r["target"] == "OfferBundler.executeBundle"}
        self.assertTrue({"skip", "best-effort", "malformed"} & signals, signals)
        for row in s.behavior_mismatch_surfaces:
            self.assertEqual(row["label"], "Potential behavior-mismatch review surface")

    def test_doc_comment_does_not_trigger_code_trycatch(self) -> None:
        # _normalize's doc comment mentions "try/catch" but the body has none.
        _rm, s = surfaces_for(AUTH)
        normalize = [r for r in s.behavior_mismatch_surfaces
                     if r["target"] == "OfferBundler._normalize" and r["signal"] == "try-catch"]
        self.assertEqual(normalize, [])


class HypothesisGenerationTests(unittest.TestCase):
    def test_ids_are_stable_and_open(self) -> None:
        rm, s = surfaces_for(AUTH)
        hyps = generate_hypotheses(rm, s)
        ids = [h["id"] for h in hyps]
        self.assertEqual(ids[0], "HYP-001")
        self.assertEqual(ids, sorted(ids))
        self.assertTrue(all(h["status"] == "open" for h in hyps))
        self.assertTrue(all(h["manual_review_required"] for h in hyps))

    def test_bug_classes_cover_signature_and_periphery(self) -> None:
        rm, s = surfaces_for(AUTH)
        classes = {h["bug_class"] for h in generate_hypotheses(rm, s)}
        self.assertIn("signature replay", classes)
        self.assertIn("periphery/core mismatch", classes)

    def test_strip_comments_strings_helper(self) -> None:
        lines = ['uint x = 1; // skip this', 'require(a, "revert reason");', '/* block */ y = 2;']
        stripped = sig.strip_comments_strings(lines)
        self.assertNotIn("skip", stripped[0])
        self.assertIn("uint x", stripped[0])
        self.assertNotIn("revert", stripped[1])
        self.assertIn("require(a,", stripped[1].replace(" ", "") or stripped[1])
        self.assertIn("y = 2", stripped[2])


if __name__ == "__main__":
    unittest.main()
