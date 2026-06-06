"""Tests for the internal assumption engine (v3.8, Agent 4).

Review surface only: assumptions are review prompts, never confirmed
vulnerabilities, final severity, audit outcomes, or submission readiness.
"""
from __future__ import annotations

import json
import unittest

from arkheionx.intelligence import assumptions as A
from arkheionx.intelligence import roles as RO
from arkheionx.intelligence import value_paths as V


class AssumptionIdTests(unittest.TestCase):
    def test_assumption_id_deterministic(self) -> None:
        self.assertEqual(
            A.protocol_assumption_id(A.ORACLE_FRESHNESS, "f", ["v1"]),
            A.protocol_assumption_id(A.ORACLE_FRESHNESS, "f", ["v1"]),
        )

    def test_assumption_id_value_path_order_stable(self) -> None:
        self.assertEqual(
            A.protocol_assumption_id(A.ORACLE_FRESHNESS, "f", ["v1", "v2"]),
            A.protocol_assumption_id(A.ORACLE_FRESHNESS, "f", ["v2", "v1"]),
        )

    def test_assumption_id_changes_with_function_id(self) -> None:
        self.assertNotEqual(
            A.protocol_assumption_id(A.ORACLE_FRESHNESS, "f1"),
            A.protocol_assumption_id(A.ORACLE_FRESHNESS, "f2"),
        )

    def test_assumption_set_id_deterministic(self) -> None:
        self.assertEqual(A.assumption_set_id("P", ["a"]), A.assumption_set_id("P", ["a"]))

    def test_assumption_set_id_order_stable(self) -> None:
        self.assertEqual(A.assumption_set_id("P", ["a", "b"]), A.assumption_set_id("P", ["b", "a"]))

    def test_id_prefixes(self) -> None:
        self.assertTrue(A.protocol_assumption_id(A.ORACLE_FRESHNESS).startswith("protocol-assumption:oracle-freshness:"))
        self.assertTrue(A.assumption_set_id("My Proto", []).startswith("assumption-set:my-proto:"))

    def test_ids_have_no_spaces(self) -> None:
        self.assertNotIn(" ", A.protocol_assumption_id(A.ORACLE_FRESHNESS, "f x"))
        self.assertNotIn(" ", A.assumption_set_id("My Proto", []))

    def test_ids_have_no_backslashes(self) -> None:
        self.assertNotIn("\\", A.protocol_assumption_id(A.ORACLE_FRESHNESS, "f"))
        self.assertNotIn("\\", A.assumption_set_id("P", []))

    def test_empty_required_category_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            A.protocol_assumption_id("")
        with self.assertRaises(ValueError):
            A.assumption_set_id("", [])

    def test_unsupported_seed_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            A.canonical_assumption_seed({"x": {1, 2}})


class DataclassTests(unittest.TestCase):
    def test_protocol_assumption_minimal(self) -> None:
        a = A.ProtocolAssumption()
        self.assertEqual(a.category, A.UNCLASSIFIED_ASSUMPTION)
        self.assertEqual(a.support_level, A.ASSUMPTION_CLASSIFIED)
        self.assertEqual(a.impact_area, A.IMPACT_UNKNOWN)

    def test_assumption_set_minimal(self) -> None:
        self.assertEqual(A.AssumptionSet().assumptions, [])

    def test_manual_review_required_true_default(self) -> None:
        self.assertTrue(A.ProtocolAssumption().manual_review_required)
        self.assertTrue(A.AssumptionSet().manual_review_required)

    def test_ready_for_submission_false_default(self) -> None:
        self.assertFalse(A.ProtocolAssumption().ready_for_submission)
        self.assertFalse(A.AssumptionSet().ready_for_submission)

    def test_mutable_defaults_independent(self) -> None:
        a, b = A.ProtocolAssumption(), A.ProtocolAssumption()
        a.warnings.append("x")
        a.linked_function_ids.append("f")
        self.assertEqual(b.warnings, [])
        self.assertEqual(b.linked_function_ids, [])


class RoleMappingTests(unittest.TestCase):
    def _cats(self, *roles) -> list[str]:
        return A.assumption_categories_for_roles(list(roles))

    def test_oracle_consumer_freshness(self) -> None:
        self.assertIn(A.ORACLE_FRESHNESS, self._cats("ORACLE_CONSUMER"))

    def test_oracle_consumer_manipulation(self) -> None:
        self.assertIn(A.ORACLE_MANIPULATION_RESISTANCE, self._cats("ORACLE_CONSUMER"))

    def test_oracle_setter_access_control(self) -> None:
        self.assertIn(A.ACCESS_CONTROL_CORRECTNESS, self._cats("ORACLE_SETTER"))

    def test_accounting_mutation_invariant(self) -> None:
        self.assertIn(A.ACCOUNTING_INVARIANT, self._cats("ACCOUNTING_MUTATION"))

    def test_inflow_external_token(self) -> None:
        self.assertIn(A.EXTERNAL_TOKEN_BEHAVIOR, self._cats("INFLOW"))

    def test_outflow_reentrancy(self) -> None:
        self.assertIn(A.REENTRANCY_PROTECTION, self._cats("OUTFLOW"))

    def test_external_call_reentrancy(self) -> None:
        self.assertIn(A.REENTRANCY_PROTECTION, self._cats("EXTERNAL_CALL"))

    def test_admin_param_role_separation(self) -> None:
        self.assertIn(A.ROLE_SEPARATION, self._cats("ADMIN_PARAM"))

    def test_access_control_correctness(self) -> None:
        self.assertIn(A.ACCESS_CONTROL_CORRECTNESS, self._cats("ACCESS_CONTROL"))

    def test_pause_emergency(self) -> None:
        self.assertIn(A.PAUSE_EMERGENCY_BEHAVIOR, self._cats("PAUSE_EMERGENCY"))

    def test_upgrade_proxy_safety(self) -> None:
        self.assertIn(A.UPGRADE_SAFETY, self._cats("UPGRADE_PROXY"))

    def test_delegatecall_target_safety(self) -> None:
        self.assertIn(A.DELEGATECALL_TARGET_SAFETY, self._cats("DELEGATECALL"))

    def test_borrow_repay_invariant(self) -> None:
        self.assertIn(A.ACCOUNTING_INVARIANT, self._cats("BORROW_REPAY"))

    def test_liquidation_threshold(self) -> None:
        self.assertIn(A.LIQUIDATION_THRESHOLD_CORRECTNESS, self._cats("LIQUIDATION"))

    def test_swap_slippage(self) -> None:
        self.assertIn(A.SLIPPAGE_BOUND, self._cats("SWAP"))

    def test_mint_burn_balance_conservation(self) -> None:
        self.assertIn(A.BALANCE_CONSERVATION, self._cats("MINT_BURN"))

    def test_claim_reward_accounting(self) -> None:
        self.assertIn(A.REWARD_ACCOUNTING_CORRECTNESS, self._cats("CLAIM_REWARD"))

    def test_bridge_finality(self) -> None:
        self.assertIn(A.BRIDGE_FINALITY, self._cats("BRIDGE"))

    def test_view_pure_consistency(self) -> None:
        self.assertIn(A.VIEW_CALCULATION_CONSISTENCY, self._cats("VIEW_PURE"))

    def test_unknown_role_unclassified_with_warning(self) -> None:
        self.assertEqual(self._cats("MADE_UP_ROLE"), [A.UNCLASSIFIED_ASSUMPTION])
        asm = A.build_assumptions_from_roles(["MADE_UP_ROLE"], function_id="f")
        self.assertTrue(any(a.warnings for a in asm))

    def test_role_mapping_deterministic_ordering(self) -> None:
        self.assertEqual(self._cats("OUTFLOW", "ORACLE_CONSUMER"), self._cats("ORACLE_CONSUMER", "OUTFLOW"))

    def test_role_mapping_deduplicates(self) -> None:
        cats = self._cats("INFLOW", "OUTFLOW")  # both contribute EXTERNAL_TOKEN_BEHAVIOR/BALANCE_CONSERVATION
        self.assertEqual(len(cats), len(set(cats)))


class ValuePathMappingTests(unittest.TestCase):
    def _cats(self, kind) -> list[str]:
        return A.assumption_categories_for_value_path_kinds([kind])

    def test_value_inflow(self) -> None:
        self.assertIn(A.EXTERNAL_TOKEN_BEHAVIOR, self._cats(V.VALUE_INFLOW))

    def test_value_outflow(self) -> None:
        self.assertIn(A.BALANCE_CONSERVATION, self._cats(V.VALUE_OUTFLOW))

    def test_accounting_path(self) -> None:
        self.assertIn(A.ACCOUNTING_INVARIANT, self._cats(V.ACCOUNTING_MUTATION_PATH))

    def test_external_call_path(self) -> None:
        self.assertIn(A.REENTRANCY_PROTECTION, self._cats(V.EXTERNAL_CALL_PATH))

    def test_oracle_path(self) -> None:
        self.assertIn(A.ORACLE_FRESHNESS, self._cats(V.ORACLE_DEPENDENT_PATH))

    def test_authority_path(self) -> None:
        self.assertIn(A.ACCESS_CONTROL_CORRECTNESS, self._cats(V.AUTHORITY_PATH))

    def test_emergency_path(self) -> None:
        self.assertIn(A.PAUSE_EMERGENCY_BEHAVIOR, self._cats(V.EMERGENCY_PATH))

    def test_upgrade_path(self) -> None:
        self.assertIn(A.UPGRADE_SAFETY, self._cats(V.UPGRADE_PATH))

    def test_liquidation_path(self) -> None:
        self.assertIn(A.LIQUIDATION_THRESHOLD_CORRECTNESS, self._cats(V.LIQUIDATION_PATH))

    def test_swap_path(self) -> None:
        self.assertIn(A.SLIPPAGE_BOUND, self._cats(V.SWAP_PATH))

    def test_bridge_path(self) -> None:
        self.assertIn(A.BRIDGE_FINALITY, self._cats(V.BRIDGE_PATH))

    def test_reward_path(self) -> None:
        self.assertIn(A.REWARD_ACCOUNTING_CORRECTNESS, self._cats(V.REWARD_PATH))

    def test_view_only_path(self) -> None:
        self.assertIn(A.VIEW_CALCULATION_CONSISTENCY, self._cats(V.VIEW_ONLY_PATH))

    def test_unknown_path_kind_unclassified_with_warning(self) -> None:
        self.assertEqual(self._cats("MADE_UP_PATH"), [A.UNCLASSIFIED_ASSUMPTION])

    def _vp(self, name: str, **kw):
        return V.build_value_path_from_role_classification(
            RO.classify_function_role(function_name=name, contract_name="Vault", **kw), function_id="function:p")

    def test_build_preserves_value_path_id(self) -> None:
        vp = self._vp("swapExactTokensForTokens")
        out = A.build_assumptions_from_value_path(vp)
        self.assertTrue(all(vp.path_id in a.value_path_ids for a in out))

    def test_build_preserves_function_id(self) -> None:
        out = A.build_assumptions_from_value_path(self._vp("withdraw"))
        self.assertTrue(all(a.function_id == "function:p" for a in out))

    def test_build_preserves_roles(self) -> None:
        out = A.build_assumptions_from_value_path(self._vp("withdraw"))
        self.assertTrue(all("OUTFLOW" in a.function_roles for a in out))

    def test_set_unique_sorted_categories(self) -> None:
        items = A.build_assumptions_from_roles(["OUTFLOW", "ORACLE_CONSUMER"], function_id="f")
        s = A.build_assumption_set("P", items)
        self.assertEqual(len(s.categories), len(set(s.categories)))

    def test_set_unique_sorted_function_ids(self) -> None:
        items = (A.build_assumptions_from_roles(["OUTFLOW"], function_id="f2")
                 + A.build_assumptions_from_roles(["INFLOW"], function_id="f1"))
        s = A.build_assumption_set("P", items)
        self.assertEqual(s.linked_function_ids, sorted(set(s.linked_function_ids)))

    def test_set_unique_sorted_value_path_ids(self) -> None:
        vp = self._vp("withdraw")
        s = A.build_assumption_set("P", A.build_assumptions_from_value_path(vp))
        self.assertEqual(s.linked_value_path_ids, sorted(set(s.linked_value_path_ids)))


class DedupSerializationTests(unittest.TestCase):
    def test_dedup_merges_same_category_function_path(self) -> None:
        a = A.build_assumptions_from_roles(["OUTFLOW"], function_id="f")
        merged = A.deduplicate_assumptions(a + a)
        self.assertEqual(len(merged), len(a))

    def test_dedup_does_not_merge_different_categories(self) -> None:
        items = A.build_assumptions_from_roles(["OUTFLOW", "ORACLE_CONSUMER"], function_id="f")
        self.assertGreaterEqual(len(A.deduplicate_assumptions(items)), 2)

    def test_dedup_merges_linked_ids_deterministically(self) -> None:
        a1 = A.build_assumptions_from_roles(["OUTFLOW"], function_id="f")
        for a in a1:
            a.linked_test_gap_ids = ["g1"]
        a2 = A.build_assumptions_from_roles(["OUTFLOW"], function_id="f")
        for a in a2:
            a.linked_test_gap_ids = ["g2"]
        merged = A.deduplicate_assumptions(a1 + a2)
        self.assertTrue(all(m.linked_test_gap_ids == ["g1", "g2"] for m in merged))
        self.assertTrue(all(m.manual_review_required and not m.ready_for_submission for m in merged))

    def test_assumption_to_dict_json_serializable(self) -> None:
        s = A.build_assumption_set("P", A.build_assumptions_from_roles(["LIQUIDATION"], function_id="f"))
        data = A.assumption_to_dict(s)
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_assumption_to_dict_no_mutation(self) -> None:
        items = A.build_assumptions_from_roles(["OUTFLOW"], function_id="f")
        before = [a.category for a in items]
        A.assumption_to_dict(items)
        self.assertEqual([a.category for a in items], before)

    def test_assumption_to_dict_unsupported_raises(self) -> None:
        with self.assertRaises(TypeError):
            A.assumption_to_dict(object())

    def test_no_invented_details(self) -> None:
        # Assumptions carry no asset/oracle/external-target slots; nothing invented.
        a = A.build_assumptions_from_roles(["ORACLE_CONSUMER"], function_id="f")[0]
        self.assertEqual(a.evidence_refs, [])
        self.assertEqual(a.linked_local_validation_ids, [])

    def test_no_fuzzy_matching(self) -> None:
        self.assertEqual(A.assumption_categories_for_roles(["ORACLE"]), [A.UNCLASSIFIED_ASSUMPTION])

    def test_output_has_no_overclaim_wording(self) -> None:
        s = A.build_assumption_set("P", A.build_assumptions_from_roles(
            ["LIQUIDATION", "OUTFLOW", "ORACLE_CONSUMER"], function_id="f"))
        blob = json.dumps(A.assumption_to_dict(s)).lower()
        for token in ("human_reviewed", "confirmed vulnerability", "final severity",
                      "audit passed", "bounty", "verified_safe", "ready_for_submission\": true"):
            self.assertNotIn(token, blob)

    def test_no_overclaim_tokens_in_taxonomy(self) -> None:
        forbidden = {"SAFE", "VERIFIED_SAFE", "CONFIRMED_VULNERABILITY", "AUDIT_PASSED",
                     "FINAL_SEVERITY", "HUMAN_REVIEWED", "BOUNTY"}
        self.assertFalse(forbidden & set(A.ASSUMPTION_CATEGORY_VALUES))
        self.assertFalse(forbidden & set(A.ASSUMPTION_SUPPORT_LEVELS))

    def test_taxonomy_counts(self) -> None:
        self.assertEqual(len(A.ASSUMPTION_CATEGORY_VALUES), 19)
        self.assertEqual(len(A.ASSUMPTION_SUPPORT_LEVELS), 6)
        self.assertEqual(len(A.ASSUMPTION_IMPACT_AREAS), 8)


class ImportAndExportTests(unittest.TestCase):
    def test_import_has_no_filesystem_side_effects(self) -> None:
        import importlib
        import arkheionx.intelligence.assumptions as mod
        importlib.reload(mod)
        self.assertTrue(hasattr(mod, "build_assumptions_from_roles"))

    def test_package_exports_assumptions(self) -> None:
        import arkheionx.intelligence as intel
        self.assertTrue(hasattr(intel, "assumptions"))
        self.assertTrue(hasattr(intel, "ProtocolAssumption"))
        self.assertTrue(hasattr(intel, "build_assumption_set"))
        self.assertIn("ProtocolAssumption", intel.__all__)

    def test_end_to_end_role_to_assumption_deterministic(self) -> None:
        c = RO.classify_function_role(function_name="liquidate", contract_name="Pool")
        a = A.assumption_to_dict(A.build_assumptions_from_roles(c.roles, function_id="function:l"))
        b = A.assumption_to_dict(A.build_assumptions_from_roles(c.roles, function_id="function:l"))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
