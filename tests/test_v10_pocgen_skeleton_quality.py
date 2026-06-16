"""V10 PoC skeleton quality: structure, family-specific assertions, honest readiness.

Skeletons must be structured attack tests (SPDX/pragma/import/contract/setUp/
arrange-act-assert/invariant assertion/severity + expected-violation comments),
must carry family-specific assertions for each benchmark family, and must never
claim compile/pass without an executed test.
"""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.pocgen import build_skeletons
from arkheionx.pocgen import models as PM

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"

_ALL_FIXTURES = [
    "loan_repay_rounding_fixture",
    "borrow_swapdata_consent_fixture",
    "vault_share_inflation_fixture",
    "deposit_double_use_fixture",
    "adapter_actual_received_vs_credited_fixture",
    "oracle_decimal_normalization_fixture",
    "cross_chain_supply_conservation_fixture",
]


def _skeletons(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
    return build_skeletons(graph, smap, top_n=5), graph


class SkeletonQualityFieldsTest(unittest.TestCase):
    def test_structure_and_quality_fields(self):
        for fx in _ALL_FIXTURES:
            skels, _ = _skeletons(fx)
            for s in skels:
                with self.subTest(fixture=fx, file=s.file_name):
                    src = s.source
                    self.assertIn("SPDX-License-Identifier", src)
                    self.assertIn("pragma solidity", src)
                    self.assertIn('import "forge-std/Test.sol";', src)
                    self.assertIn("function setUp() public", src)
                    self.assertIn(s.test_name, src)
                    self.assertIn("Economic severity", src)
                    self.assertIn("EXPECTED:", src)
                    self.assertIn("MANUAL FILL", src)
                    self.assertIn("Compile-readiness:", src)
                    self.assertTrue(s.actors)
                    self.assertTrue(s.setup_steps)
                    self.assertTrue(s.action_sequence)
                    self.assertTrue(s.assertions)

    def test_no_compile_claim_without_test(self):
        # A generated skeleton has no executed test, so it can never be claimed as
        # COMPILE_LIKELY or FIXTURE_TESTED_COMPILE.
        for fx in _ALL_FIXTURES:
            skels, _ = _skeletons(fx)
            for s in skels:
                with self.subTest(fixture=fx, file=s.file_name):
                    self.assertIn(s.compile_readiness, (PM.TEMPLATE_ONLY, PM.NEAR_COMPILE))
                    self.assertNotIn(s.compile_readiness,
                                     (PM.COMPILE_LIKELY, PM.FIXTURE_TESTED_COMPILE))
                    self.assertEqual(s.compile_ready_level, PM.REQUIRES_MANUAL_FILL)


class SkeletonFamilyAssertionsTest(unittest.TestCase):
    def _skeleton_for(self, fixture, family):
        skels, _ = _skeletons(fixture)
        return next(s for s in skels if s.family == family)

    def test_repayment_skeleton_assertions(self):
        s = self._skeleton_for("loan_repay_rounding_fixture",
                                "DEBT_REPAYMENT_RECONCILIATION")
        self.assertIn("debtBefore", s.source)
        self.assertIn("creditAfter", s.source)

    def test_consent_skeleton_assertions(self):
        s = self._skeleton_for("borrow_swapdata_consent_fixture",
                                "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")
        self.assertIn("refundHonest", s.source)
        self.assertIn("refundAttacker", s.source)

    def test_adapter_skeleton_assertions(self):
        s = self._skeleton_for("adapter_actual_received_vs_credited_fixture",
                                "SWAP_ACTUAL_RECEIVED_VS_CREDITED")
        self.assertIn("balanceOf", s.source)
        self.assertIn("credited", s.source)
        self.assertIn("actual", s.source)

    def test_oracle_skeleton_assertions(self):
        s = self._skeleton_for("oracle_decimal_normalization_fixture",
                                "ORACLE_DECIMAL_NORMALIZATION")
        self.assertIn("maxBorrow", s.source)
        self.assertIn("safeMax", s.source)
        self.assertIn("decimals", s.source.lower())

    def test_cross_chain_skeleton_assertions(self):
        s = self._skeleton_for("cross_chain_supply_conservation_fixture",
                                "CROSS_CHAIN_SUPPLY_CONSERVATION")
        self.assertIn("receiveMessage", s.source)
        self.assertIn("totalSupply", s.source)
        self.assertIn("replay", s.source.lower())


if __name__ == "__main__":
    unittest.main()
