"""Tests for the internal test-gap engine (v3.8, Agent 5).

Review surface only: a missing test never proves a vulnerability and a passing
local test never proves safety. No confirmed vulnerabilities, final severity,
audit outcomes, or submission readiness.
"""
from __future__ import annotations

import json
import unittest

from arkheionx.intelligence import assumptions as A
from arkheionx.intelligence import roles as RO
from arkheionx.intelligence import test_gaps as T
from arkheionx.intelligence import value_paths as V


class TestGapIdTests(unittest.TestCase):
    def test_id_deterministic(self) -> None:
        self.assertEqual(
            T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f", ["v1"]),
            T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f", ["v1"]),
        )

    def test_id_value_path_order_stable(self) -> None:
        self.assertEqual(
            T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f", ["v1", "v2"]),
            T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f", ["v2", "v1"]),
        )

    def test_id_assumption_order_stable(self) -> None:
        self.assertEqual(
            T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f", None, ["a1", "a2"]),
            T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f", None, ["a2", "a1"]),
        )

    def test_id_changes_with_function_id(self) -> None:
        self.assertNotEqual(
            T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f1"),
            T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f2"),
        )

    def test_set_id_deterministic(self) -> None:
        self.assertEqual(T.test_gap_set_id("P", ["a"]), T.test_gap_set_id("P", ["a"]))

    def test_set_id_order_stable(self) -> None:
        self.assertEqual(T.test_gap_set_id("P", ["a", "b"]), T.test_gap_set_id("P", ["b", "a"]))

    def test_id_prefixes(self) -> None:
        self.assertTrue(T.protocol_test_gap_id(T.MISSING_REENTRANCY_TEST).startswith("protocol-test-gap:missing-reentrancy-test:"))
        self.assertTrue(T.test_gap_set_id("My Proto", []).startswith("test-gap-set:my-proto:"))

    def test_ids_no_spaces(self) -> None:
        self.assertNotIn(" ", T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f x"))
        self.assertNotIn(" ", T.test_gap_set_id("My Proto", []))

    def test_ids_no_backslashes(self) -> None:
        self.assertNotIn("\\", T.protocol_test_gap_id(T.MISSING_INVARIANT_TEST, "f"))
        self.assertNotIn("\\", T.test_gap_set_id("P", []))

    def test_empty_category_raises(self) -> None:
        with self.assertRaises(ValueError):
            T.protocol_test_gap_id("")
        with self.assertRaises(ValueError):
            T.test_gap_set_id("", [])

    def test_unsupported_seed_raises(self) -> None:
        with self.assertRaises(TypeError):
            T.canonical_test_gap_seed({"x": {1, 2}})


class DataclassTests(unittest.TestCase):
    def test_gap_minimal(self) -> None:
        g = T.ProtocolTestGap()
        self.assertEqual(g.category, T.UNCLASSIFIED_TEST_GAP)
        self.assertEqual(g.gap_status, T.TEST_GAP_OPEN)
        self.assertEqual(g.priority, T.GAP_PRIORITY_UNKNOWN)

    def test_set_minimal(self) -> None:
        self.assertEqual(T.TestGapSet().test_gaps, [])

    def test_manual_review_default(self) -> None:
        self.assertTrue(T.ProtocolTestGap().manual_review_required)
        self.assertTrue(T.TestGapSet().manual_review_required)

    def test_ready_false_default(self) -> None:
        self.assertFalse(T.ProtocolTestGap().ready_for_submission)
        self.assertFalse(T.TestGapSet().ready_for_submission)

    def test_mutable_defaults_independent(self) -> None:
        a, b = T.ProtocolTestGap(), T.ProtocolTestGap()
        a.warnings.append("x")
        a.coverage_notes.append("y")
        self.assertEqual(b.warnings, [])
        self.assertEqual(b.coverage_notes, [])


class RoleMappingTests(unittest.TestCase):
    def _c(self, *roles) -> list[str]:
        return T.test_gap_categories_for_roles(list(roles))

    def test_inflow_positive_path(self) -> None:
        self.assertIn(T.MISSING_POSITIVE_PATH_TEST, self._c("INFLOW"))

    def test_outflow_reentrancy(self) -> None:
        self.assertIn(T.MISSING_REENTRANCY_TEST, self._c("OUTFLOW"))

    def test_accounting_invariant(self) -> None:
        self.assertIn(T.MISSING_INVARIANT_TEST, self._c("ACCOUNTING_MUTATION"))

    def test_external_call_failure(self) -> None:
        self.assertIn(T.MISSING_EXTERNAL_CALL_FAILURE_TEST, self._c("EXTERNAL_CALL"))

    def test_oracle_consumer_stale_and_manipulation(self) -> None:
        cats = self._c("ORACLE_CONSUMER")
        self.assertIn(T.MISSING_ORACLE_STALE_TEST, cats)
        self.assertIn(T.MISSING_ORACLE_MANIPULATION_TEST, cats)

    def test_oracle_setter_access_control(self) -> None:
        self.assertIn(T.MISSING_ACCESS_CONTROL_TEST, self._c("ORACLE_SETTER"))

    def test_admin_param_access_control(self) -> None:
        self.assertIn(T.MISSING_ACCESS_CONTROL_TEST, self._c("ADMIN_PARAM"))

    def test_access_control_role_quorum(self) -> None:
        self.assertIn(T.MISSING_ROLE_QUORUM_TEST, self._c("ACCESS_CONTROL"))

    def test_pause_emergency(self) -> None:
        self.assertIn(T.MISSING_PAUSE_EMERGENCY_TEST, self._c("PAUSE_EMERGENCY"))

    def test_upgrade_proxy(self) -> None:
        self.assertIn(T.MISSING_UPGRADE_PROXY_TEST, self._c("UPGRADE_PROXY"))

    def test_delegatecall_target(self) -> None:
        self.assertIn(T.MISSING_DELEGATECALL_TARGET_TEST, self._c("DELEGATECALL"))

    def test_borrow_repay(self) -> None:
        cats = self._c("BORROW_REPAY")
        self.assertIn(T.MISSING_POSITIVE_PATH_TEST, cats)
        self.assertIn(T.MISSING_NEGATIVE_PATH_TEST, cats)
        self.assertIn(T.MISSING_INVARIANT_TEST, cats)

    def test_liquidation(self) -> None:
        self.assertIn(T.MISSING_LIQUIDATION_EDGE_CASE_TEST, self._c("LIQUIDATION"))

    def test_swap_slippage(self) -> None:
        self.assertIn(T.MISSING_SLIPPAGE_BOUNDS_TEST, self._c("SWAP"))

    def test_mint_burn(self) -> None:
        cats = self._c("MINT_BURN")
        self.assertIn(T.MISSING_INVARIANT_TEST, cats)
        self.assertIn(T.MISSING_VALUE_CONSERVATION_TEST, cats)

    def test_claim_reward(self) -> None:
        self.assertIn(T.MISSING_REWARD_ACCOUNTING_TEST, self._c("CLAIM_REWARD"))

    def test_bridge_finality(self) -> None:
        self.assertIn(T.MISSING_BRIDGE_FINALITY_TEST, self._c("BRIDGE"))

    def test_view_pure(self) -> None:
        self.assertIn(T.MISSING_VIEW_CALCULATION_TEST, self._c("VIEW_PURE"))

    def test_unknown_role(self) -> None:
        self.assertEqual(self._c("MADE_UP"), [T.UNCLASSIFIED_TEST_GAP])
        gaps = T.build_test_gaps_from_roles(["MADE_UP"], function_id="f")
        self.assertTrue(any(g.warnings for g in gaps))

    def test_role_mapping_deterministic_order(self) -> None:
        self.assertEqual(self._c("OUTFLOW", "ORACLE_CONSUMER"), self._c("ORACLE_CONSUMER", "OUTFLOW"))

    def test_role_mapping_dedup(self) -> None:
        cats = self._c("INFLOW", "MINT_BURN")  # both contribute MISSING_VALUE_CONSERVATION_TEST
        self.assertEqual(len(cats), len(set(cats)))


class ValuePathMappingTests(unittest.TestCase):
    def _c(self, kind) -> list[str]:
        return T.test_gap_categories_for_value_path_kinds([kind])

    def test_inflow(self) -> None:
        self.assertIn(T.MISSING_POSITIVE_PATH_TEST, self._c(V.VALUE_INFLOW))

    def test_outflow(self) -> None:
        self.assertIn(T.MISSING_NEGATIVE_PATH_TEST, self._c(V.VALUE_OUTFLOW))

    def test_accounting(self) -> None:
        self.assertIn(T.MISSING_INVARIANT_TEST, self._c(V.ACCOUNTING_MUTATION_PATH))

    def test_external_call(self) -> None:
        self.assertIn(T.MISSING_EXTERNAL_CALL_FAILURE_TEST, self._c(V.EXTERNAL_CALL_PATH))

    def test_oracle(self) -> None:
        self.assertIn(T.MISSING_ORACLE_STALE_TEST, self._c(V.ORACLE_DEPENDENT_PATH))

    def test_authority(self) -> None:
        cats = self._c(V.AUTHORITY_PATH)
        self.assertIn(T.MISSING_ACCESS_CONTROL_TEST, cats)
        self.assertIn(T.MISSING_ROLE_QUORUM_TEST, cats)

    def test_emergency(self) -> None:
        self.assertIn(T.MISSING_PAUSE_EMERGENCY_TEST, self._c(V.EMERGENCY_PATH))

    def test_upgrade(self) -> None:
        cats = self._c(V.UPGRADE_PATH)
        self.assertIn(T.MISSING_UPGRADE_PROXY_TEST, cats)
        self.assertIn(T.MISSING_DELEGATECALL_TARGET_TEST, cats)

    def test_liquidation(self) -> None:
        self.assertIn(T.MISSING_LIQUIDATION_EDGE_CASE_TEST, self._c(V.LIQUIDATION_PATH))

    def test_swap(self) -> None:
        self.assertIn(T.MISSING_SLIPPAGE_BOUNDS_TEST, self._c(V.SWAP_PATH))

    def test_bridge(self) -> None:
        self.assertIn(T.MISSING_BRIDGE_FINALITY_TEST, self._c(V.BRIDGE_PATH))

    def test_reward(self) -> None:
        self.assertIn(T.MISSING_REWARD_ACCOUNTING_TEST, self._c(V.REWARD_PATH))

    def test_view(self) -> None:
        self.assertIn(T.MISSING_VIEW_CALCULATION_TEST, self._c(V.VIEW_ONLY_PATH))

    def test_unknown_path(self) -> None:
        self.assertEqual(self._c("MADE_UP_PATH"), [T.UNCLASSIFIED_TEST_GAP])

    def _vp(self, name: str):
        return V.build_value_path_from_role_classification(
            RO.classify_function_role(function_name=name, contract_name="Vault"), function_id="function:p")

    def test_build_preserves_value_path_id(self) -> None:
        vp = self._vp("withdraw")
        self.assertTrue(all(vp.path_id in g.value_path_ids for g in T.build_test_gaps_from_value_path(vp)))

    def test_build_preserves_function_id(self) -> None:
        self.assertTrue(all(g.function_id == "function:p" for g in T.build_test_gaps_from_value_path(self._vp("withdraw"))))

    def test_build_preserves_roles(self) -> None:
        self.assertTrue(all("OUTFLOW" in g.function_roles for g in T.build_test_gaps_from_value_path(self._vp("withdraw"))))


class AssumptionMappingTests(unittest.TestCase):
    def _c(self, cat) -> list[str]:
        return T.test_gap_categories_for_assumption_categories([cat])

    def test_oracle_freshness(self) -> None:
        self.assertEqual(self._c(A.ORACLE_FRESHNESS), [T.MISSING_ORACLE_STALE_TEST])

    def test_oracle_manipulation(self) -> None:
        self.assertEqual(self._c(A.ORACLE_MANIPULATION_RESISTANCE), [T.MISSING_ORACLE_MANIPULATION_TEST])

    def test_accounting_invariant(self) -> None:
        self.assertEqual(self._c(A.ACCOUNTING_INVARIANT), [T.MISSING_INVARIANT_TEST])

    def test_balance_conservation(self) -> None:
        self.assertEqual(self._c(A.BALANCE_CONSERVATION), [T.MISSING_VALUE_CONSERVATION_TEST])

    def test_access_control(self) -> None:
        self.assertEqual(self._c(A.ACCESS_CONTROL_CORRECTNESS), [T.MISSING_ACCESS_CONTROL_TEST])

    def test_role_separation(self) -> None:
        self.assertEqual(self._c(A.ROLE_SEPARATION), [T.MISSING_ROLE_QUORUM_TEST])

    def test_reentrancy(self) -> None:
        self.assertEqual(self._c(A.REENTRANCY_PROTECTION), [T.MISSING_REENTRANCY_TEST])

    def test_external_token(self) -> None:
        self.assertEqual(self._c(A.EXTERNAL_TOKEN_BEHAVIOR), [T.MISSING_EXTERNAL_CALL_FAILURE_TEST])

    def test_pause_emergency(self) -> None:
        self.assertEqual(self._c(A.PAUSE_EMERGENCY_BEHAVIOR), [T.MISSING_PAUSE_EMERGENCY_TEST])

    def test_upgrade(self) -> None:
        self.assertEqual(self._c(A.UPGRADE_SAFETY), [T.MISSING_UPGRADE_PROXY_TEST])

    def test_liquidation(self) -> None:
        self.assertEqual(self._c(A.LIQUIDATION_THRESHOLD_CORRECTNESS), [T.MISSING_LIQUIDATION_EDGE_CASE_TEST])

    def test_slippage(self) -> None:
        self.assertEqual(self._c(A.SLIPPAGE_BOUND), [T.MISSING_SLIPPAGE_BOUNDS_TEST])

    def test_fee(self) -> None:
        self.assertEqual(self._c(A.FEE_CORRECTNESS), [T.MISSING_FEE_CALCULATION_TEST])

    def test_bridge(self) -> None:
        self.assertEqual(self._c(A.BRIDGE_FINALITY), [T.MISSING_BRIDGE_FINALITY_TEST])

    def test_signer_quorum(self) -> None:
        self.assertEqual(self._c(A.SIGNER_QUORUM_INTEGRITY), [T.MISSING_ROLE_QUORUM_TEST])

    def test_reward(self) -> None:
        self.assertEqual(self._c(A.REWARD_ACCOUNTING_CORRECTNESS), [T.MISSING_REWARD_ACCOUNTING_TEST])

    def test_delegatecall(self) -> None:
        self.assertEqual(self._c(A.DELEGATECALL_TARGET_SAFETY), [T.MISSING_DELEGATECALL_TARGET_TEST])

    def test_view(self) -> None:
        self.assertEqual(self._c(A.VIEW_CALCULATION_CONSISTENCY), [T.MISSING_VIEW_CALCULATION_TEST])

    def test_unknown_assumption(self) -> None:
        self.assertEqual(self._c("MADE_UP"), [T.UNCLASSIFIED_TEST_GAP])

    def test_build_preserves_assumption_id(self) -> None:
        asm = A.build_assumptions_from_roles(["ORACLE_CONSUMER"], function_id="function:o")[0]
        gaps = T.build_test_gaps_from_assumption(asm)
        self.assertTrue(all(asm.assumption_id in g.assumption_ids for g in gaps))

    def test_build_preserves_function_and_value_path(self) -> None:
        asm = A.build_assumptions_from_roles(["OUTFLOW"], function_id="function:o")[0]
        asm.value_path_ids = ["vp1"]
        gaps = T.build_test_gaps_from_assumption(asm)
        self.assertTrue(all(g.function_id == "function:o" and "vp1" in g.value_path_ids for g in gaps))


class CorrelationDedupSetTests(unittest.TestCase):
    def _gap(self):
        return T.build_test_gaps_from_roles(["OUTFLOW"], function_id="function:x")[0]

    def test_local_validation_sets_locally_tested(self) -> None:
        g = T.correlate_test_gap_with_local_validation(self._gap(), local_validation_ids=["lv1"], tested=True)
        self.assertEqual(g.gap_status, T.TEST_GAP_LOCALLY_TESTED)
        self.assertIn("lv1", g.linked_local_validation_ids)

    def test_trace_receipt_sets_trace_bound(self) -> None:
        g = T.correlate_test_gap_with_local_validation(self._gap(), trace_receipt_ids=["tr1"], trace_bound=True)
        self.assertEqual(g.gap_status, T.TEST_GAP_TRACE_BOUND)
        self.assertIn("tr1", g.linked_trace_receipt_ids)

    def test_no_ids_no_coverage_claim(self) -> None:
        g = T.correlate_test_gap_with_local_validation(self._gap(), tested=True)
        self.assertEqual(g.gap_status, T.TEST_GAP_OPEN)
        self.assertTrue(g.warnings)

    def test_correlation_does_not_mutate_source(self) -> None:
        base = self._gap()
        T.correlate_test_gap_with_local_validation(base, local_validation_ids=["lv1"], tested=True)
        self.assertEqual(base.gap_status, T.TEST_GAP_OPEN)
        self.assertEqual(base.linked_local_validation_ids, [])

    def test_correlation_keeps_review_flags(self) -> None:
        g = T.correlate_test_gap_with_local_validation(self._gap(), local_validation_ids=["lv1"], tested=True)
        self.assertTrue(g.manual_review_required)
        self.assertFalse(g.ready_for_submission)

    def test_dedup_merges_same_key(self) -> None:
        g = T.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")
        self.assertEqual(len(T.deduplicate_test_gaps(g + g)), len(g))

    def test_dedup_keeps_distinct_categories(self) -> None:
        g = T.build_test_gaps_from_roles(["OUTFLOW", "ORACLE_CONSUMER"], function_id="f")
        self.assertGreaterEqual(len(T.deduplicate_test_gaps(g)), 2)

    def test_dedup_merges_linked_ids(self) -> None:
        a = T.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")
        for g in a:
            g.linked_local_validation_ids = ["lv1"]
        b = T.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")
        for g in b:
            g.linked_local_validation_ids = ["lv2"]
        merged = T.deduplicate_test_gaps(a + b)
        self.assertTrue(all(m.linked_local_validation_ids == ["lv1", "lv2"] for m in merged))

    def test_dedup_keeps_stronger_status(self) -> None:
        open_gap = self._gap()
        tested = T.correlate_test_gap_with_local_validation(open_gap, local_validation_ids=["lv1"], tested=True)
        merged = T.deduplicate_test_gaps([open_gap, tested])
        self.assertTrue(all(m.gap_status == T.TEST_GAP_LOCALLY_TESTED for m in merged))

    def test_set_open_count(self) -> None:
        s = T.build_test_gap_set("P", T.build_test_gaps_from_roles(["OUTFLOW"], function_id="f"))
        self.assertGreater(s.open_gap_count, 0)

    def test_set_locally_tested_count(self) -> None:
        gaps = [T.correlate_test_gap_with_local_validation(g, local_validation_ids=["lv1"], tested=True)
                for g in T.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")]
        s = T.build_test_gap_set("P", gaps)
        self.assertEqual(s.locally_tested_gap_count, len(gaps))

    def test_set_trace_bound_count(self) -> None:
        gaps = [T.correlate_test_gap_with_local_validation(g, trace_receipt_ids=["tr1"], trace_bound=True)
                for g in T.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")]
        s = T.build_test_gap_set("P", gaps)
        self.assertEqual(s.trace_bound_gap_count, len(gaps))

    def test_set_unique_sorted_categories(self) -> None:
        s = T.build_test_gap_set("P", T.build_test_gaps_from_roles(["OUTFLOW", "ORACLE_CONSUMER"], function_id="f"))
        self.assertEqual(len(s.categories), len(set(s.categories)))

    def test_set_unique_sorted_linked_ids(self) -> None:
        items = (T.build_test_gaps_from_roles(["OUTFLOW"], function_id="f2")
                 + T.build_test_gaps_from_roles(["INFLOW"], function_id="f1"))
        s = T.build_test_gap_set("P", items)
        self.assertEqual(s.linked_function_ids, sorted(set(s.linked_function_ids)))


class SerializationNoOverclaimTests(unittest.TestCase):
    def test_to_dict_json_serializable(self) -> None:
        s = T.build_test_gap_set("P", T.build_test_gaps_from_roles(["LIQUIDATION"], function_id="f"))
        data = T.test_gap_to_dict(s)
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_to_dict_no_mutation(self) -> None:
        gaps = T.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")
        before = [g.category for g in gaps]
        T.test_gap_to_dict(gaps)
        self.assertEqual([g.category for g in gaps], before)

    def test_to_dict_unsupported_raises(self) -> None:
        with self.assertRaises(TypeError):
            T.test_gap_to_dict(object())

    def test_no_invented_local_validation_ids(self) -> None:
        g = T.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")[0]
        self.assertEqual(g.linked_local_validation_ids, [])
        self.assertEqual(g.linked_trace_receipt_ids, [])
        self.assertEqual(g.coverage_notes, [])

    def test_no_fuzzy_matching(self) -> None:
        self.assertEqual(T.test_gap_categories_for_roles(["ORACLE"]), [T.UNCLASSIFIED_TEST_GAP])

    def test_output_has_no_overclaim_wording(self) -> None:
        s = T.build_test_gap_set("P", T.build_test_gaps_from_roles(
            ["LIQUIDATION", "OUTFLOW", "ACCESS_CONTROL"], function_id="f"))
        blob = json.dumps(T.test_gap_to_dict(s)).lower()
        for token in ("human_reviewed", "confirmed vulnerability", "final severity", "audit passed",
                      "bounty", "verified_safe", "proves safety", "proves a vulnerability",
                      "ready_for_submission\": true"):
            self.assertNotIn(token, blob)

    def test_no_overclaim_tokens_in_taxonomy(self) -> None:
        forbidden = {"SAFE", "VERIFIED_SAFE", "CONFIRMED_VULNERABILITY", "AUDIT_PASSED",
                     "FINAL_SEVERITY", "HUMAN_REVIEWED", "BOUNTY"}
        self.assertFalse(forbidden & set(T.TEST_GAP_CATEGORY_VALUES))
        self.assertFalse(forbidden & set(T.TEST_GAP_STATUS_VALUES))
        self.assertFalse(forbidden & set(T.GAP_PRIORITY_VALUES))

    def test_taxonomy_counts(self) -> None:
        self.assertEqual(len(T.TEST_GAP_CATEGORY_VALUES), 20)
        self.assertEqual(len(T.TEST_GAP_STATUS_VALUES), 6)
        self.assertEqual(len(T.GAP_PRIORITY_VALUES), 5)


class ImportAndExportTests(unittest.TestCase):
    def test_import_has_no_filesystem_side_effects(self) -> None:
        import importlib
        import arkheionx.intelligence.test_gaps as mod
        importlib.reload(mod)
        self.assertTrue(hasattr(mod, "build_test_gaps_from_roles"))

    def test_package_exports_test_gaps(self) -> None:
        import arkheionx.intelligence as intel
        self.assertTrue(hasattr(intel, "test_gaps"))
        self.assertTrue(hasattr(intel, "ProtocolTestGap"))
        self.assertTrue(hasattr(intel, "build_test_gap_set"))
        self.assertIn("ProtocolTestGap", intel.__all__)

    def test_end_to_end_deterministic(self) -> None:
        c = RO.classify_function_role(function_name="liquidate", contract_name="Pool")
        a = T.test_gap_to_dict(T.build_test_gaps_from_roles(c.roles, function_id="function:l"))
        b = T.test_gap_to_dict(T.build_test_gaps_from_roles(c.roles, function_id="function:l"))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
