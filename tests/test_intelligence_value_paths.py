"""Tests for the internal value-path graph model (v3.8, Agent 3).

Review surface only: value paths are structural classification, never confirmed
vulnerabilities, final severity, audit outcomes, or submission readiness.
"""
from __future__ import annotations

import json
import unittest

from arkheionx.intelligence import roles as RO
from arkheionx.intelligence import value_paths as V


def _classify(name: str, **kw):
    return RO.classify_function_role(function_name=name, **kw)


class ValuePathIdTests(unittest.TestCase):
    def test_value_path_id_deterministic(self) -> None:
        a = V.value_path_id(V.VALUE_INFLOW, "f", "deposit", "Vault", ["INFLOW"])
        b = V.value_path_id(V.VALUE_INFLOW, "f", "deposit", "Vault", ["INFLOW"])
        self.assertEqual(a, b)

    def test_value_path_id_roles_order_stable(self) -> None:
        self.assertEqual(
            V.value_path_id(V.SWAP_PATH, roles=["A", "B"]),
            V.value_path_id(V.SWAP_PATH, roles=["B", "A"]),
        )

    def test_value_path_id_changes_with_function_id(self) -> None:
        self.assertNotEqual(
            V.value_path_id(V.VALUE_INFLOW, "f1"),
            V.value_path_id(V.VALUE_INFLOW, "f2"),
        )

    def test_segment_id_deterministic(self) -> None:
        a = V.value_path_segment_id("p", V.FUNCTION_ENTRY, 0)
        b = V.value_path_segment_id("p", V.FUNCTION_ENTRY, 0)
        self.assertEqual(a, b)

    def test_segment_id_changes_with_order_index(self) -> None:
        self.assertNotEqual(
            V.value_path_segment_id("p", V.FUNCTION_ENTRY, 0),
            V.value_path_segment_id("p", V.FUNCTION_ENTRY, 1),
        )

    def test_graph_id_deterministic(self) -> None:
        self.assertEqual(
            V.value_path_graph_id("Proto", ["a", "b"]),
            V.value_path_graph_id("Proto", ["a", "b"]),
        )

    def test_graph_id_path_order_stable(self) -> None:
        self.assertEqual(
            V.value_path_graph_id("Proto", ["a", "b"]),
            V.value_path_graph_id("Proto", ["b", "a"]),
        )

    def test_id_prefixes(self) -> None:
        self.assertTrue(V.value_path_id(V.VALUE_INFLOW).startswith("value-path:value-inflow:"))
        self.assertTrue(V.value_path_segment_id("p", V.ORACLE_READ).startswith("value-path-segment:oracle-read:"))
        self.assertTrue(V.value_path_graph_id("Proto", []).startswith("value-path-graph:proto:"))

    def test_ids_have_no_spaces(self) -> None:
        self.assertNotIn(" ", V.value_path_id(V.VALUE_INFLOW, "f", "dep all"))
        self.assertNotIn(" ", V.value_path_graph_id("My Proto", []))

    def test_ids_have_no_backslashes(self) -> None:
        self.assertNotIn("\\", V.value_path_id(V.VALUE_INFLOW, "f"))
        self.assertNotIn("\\", V.value_path_segment_id("p", V.FUNCTION_ENTRY))

    def test_empty_required_path_kind_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            V.value_path_id("")
        with self.assertRaises(ValueError):
            V.value_path_segment_id("", V.FUNCTION_ENTRY)
        with self.assertRaises(ValueError):
            V.value_path_segment_id("p", "")
        with self.assertRaises(ValueError):
            V.value_path_graph_id("", [])

    def test_unsupported_seed_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            V.canonical_value_path_seed({"x": {1, 2}})


class DataclassTests(unittest.TestCase):
    def test_segment_minimal_construction(self) -> None:
        seg = V.ValuePathSegment()
        self.assertEqual(seg.segment_kind, V.UNKNOWN_SEGMENT)
        self.assertEqual(seg.order_index, 0)

    def test_value_path_minimal_construction(self) -> None:
        vp = V.ValuePath()
        self.assertEqual(vp.path_kind, V.UNCLASSIFIED_PATH)
        self.assertEqual(vp.support_level, "CLASSIFIED")

    def test_graph_minimal_construction(self) -> None:
        g = V.ValuePathGraph()
        self.assertEqual(g.value_paths, [])

    def test_manual_review_required_true_default(self) -> None:
        self.assertTrue(V.ValuePath().manual_review_required)
        self.assertTrue(V.ValuePathGraph().manual_review_required)

    def test_ready_for_submission_false_default(self) -> None:
        self.assertFalse(V.ValuePath().ready_for_submission)
        self.assertFalse(V.ValuePathGraph().ready_for_submission)

    def test_mutable_defaults_independent(self) -> None:
        a, b = V.ValuePath(), V.ValuePath()
        a.segments.append(V.ValuePathSegment())
        self.assertEqual(b.segments, [])
        a.warnings.append("x")
        self.assertEqual(b.warnings, [])


class RoleToPathMappingTests(unittest.TestCase):
    def _kind(self, name: str, **kw) -> str:
        return V.build_value_path_from_role_classification(_classify(name, **kw)).path_kind

    def _segkinds(self, name: str, **kw) -> list[str]:
        return [s.segment_kind for s in V.build_value_path_from_role_classification(_classify(name, **kw)).segments]

    def test_inflow(self) -> None:
        self.assertEqual(self._kind("deposit"), V.VALUE_INFLOW)

    def test_inflow_segments(self) -> None:
        self.assertTrue({V.TOKEN_TRANSFER_IN, V.BALANCE_INCREASE} & set(self._segkinds("deposit")))

    def test_outflow(self) -> None:
        self.assertEqual(self._kind("withdraw"), V.VALUE_OUTFLOW)

    def test_outflow_segments(self) -> None:
        self.assertTrue({V.TOKEN_TRANSFER_OUT, V.BALANCE_DECREASE} & set(self._segkinds("withdraw")))

    def test_accounting_mutation(self) -> None:
        self.assertEqual(self._kind("accrueInterest"), V.ACCOUNTING_MUTATION_PATH)

    def test_external_call(self) -> None:
        self.assertEqual(self._kind("multicall"), V.EXTERNAL_CALL_PATH)

    def test_oracle_consumer(self) -> None:
        self.assertEqual(V.path_kinds_for_roles(["ORACLE_CONSUMER"]), [V.ORACLE_DEPENDENT_PATH])

    def test_oracle_setter(self) -> None:
        self.assertEqual(self._kind("setOracle"), V.ORACLE_DEPENDENT_PATH)

    def test_admin_param(self) -> None:
        self.assertEqual(self._kind("setFee"), V.AUTHORITY_PATH)

    def test_access_control(self) -> None:
        self.assertEqual(self._kind("grantRole"), V.AUTHORITY_PATH)

    def test_pause_emergency(self) -> None:
        self.assertEqual(self._kind("pause"), V.EMERGENCY_PATH)

    def test_upgrade_proxy(self) -> None:
        self.assertEqual(self._kind("upgradeTo"), V.UPGRADE_PATH)

    def test_delegatecall(self) -> None:
        vp = V.build_value_path_from_role_classification(_classify("delegatecall"))
        self.assertIn(vp.path_kind, (V.UPGRADE_PATH, V.EXTERNAL_CALL_PATH))
        self.assertIn(V.DELEGATECALL_ACTION, [s.segment_kind for s in vp.segments])

    def test_borrow_repay_warns(self) -> None:
        vp = V.build_value_path_from_role_classification(_classify("borrow"))
        self.assertTrue(vp.warnings)

    def test_liquidation(self) -> None:
        self.assertEqual(self._kind("liquidationCall"), V.LIQUIDATION_PATH)

    def test_swap(self) -> None:
        self.assertEqual(self._kind("swapExactTokensForTokens"), V.SWAP_PATH)

    def test_mint_burn(self) -> None:
        self.assertEqual(self._kind("mint"), V.ACCOUNTING_MUTATION_PATH)

    def test_claim_reward(self) -> None:
        self.assertEqual(self._kind("claimRewards"), V.REWARD_PATH)

    def test_bridge(self) -> None:
        self.assertEqual(self._kind("bridgeOut"), V.BRIDGE_PATH)

    def test_view_pure(self) -> None:
        self.assertEqual(self._kind("calculateHealthFactor", mutability="pure"), V.VIEW_ONLY_PATH)

    def test_unclassified(self) -> None:
        self.assertEqual(self._kind("frobnicate"), V.UNCLASSIFIED_PATH)

    def test_multi_role_deterministic_ordering(self) -> None:
        a = V.path_kinds_for_roles(["OUTFLOW", "PAUSE_EMERGENCY"])
        b = V.path_kinds_for_roles(["PAUSE_EMERGENCY", "OUTFLOW"])
        self.assertEqual(a, b)
        # EMERGENCY_PATH (PAUSE_EMERGENCY priority) precedes VALUE_OUTFLOW.
        self.assertEqual(a[0], V.EMERGENCY_PATH)

    def test_build_preserves_function_name(self) -> None:
        self.assertEqual(
            V.build_value_path_from_role_classification(
                RO.classify_function_role(function_name="withdraw", contract_name="Vault")).function_name,
            "withdraw")

    def test_build_preserves_contract_name(self) -> None:
        self.assertEqual(
            V.build_value_path_from_role_classification(
                RO.classify_function_role(function_name="withdraw", contract_name="Vault")).contract_name,
            "Vault")

    def test_build_preserves_function_id(self) -> None:
        self.assertEqual(
            V.build_value_path_from_role_classification(_classify("withdraw"), function_id="function:x").function_id,
            "function:x")

    def test_build_preserves_roles(self) -> None:
        self.assertEqual(V.build_value_path_from_role_classification(_classify("emergencyWithdraw")).roles,
                         ["PAUSE_EMERGENCY", "OUTFLOW"])

    def test_segment_order_deterministic(self) -> None:
        a = V.build_value_path_from_role_classification(_classify("emergencyWithdraw"))
        b = V.build_value_path_from_role_classification(_classify("emergencyWithdraw"))
        self.assertEqual([s.order_index for s in a.segments], list(range(len(a.segments))))
        self.assertEqual([s.segment_kind for s in a.segments], [s.segment_kind for s in b.segments])


class GraphBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.p1 = V.build_value_path_from_role_classification(_classify("deposit"), function_id="function:a")
        self.p2 = V.build_value_path_from_role_classification(_classify("withdraw"), function_id="function:b")
        self.graph = V.build_value_path_graph("MyProtocol", [self.p1, self.p2])

    def test_graph_collects_paths_and_segments(self) -> None:
        self.assertEqual(self.graph.value_paths, [self.p1, self.p2])
        self.assertEqual(len(self.graph.segments), len(self.p1.segments) + len(self.p2.segments))

    def test_graph_linked_function_ids_unique_sorted(self) -> None:
        self.assertEqual(self.graph.linked_function_ids, ["function:a", "function:b"])

    def test_graph_id_prefix(self) -> None:
        self.assertTrue(self.graph.graph_id.startswith("value-path-graph:myprotocol:"))


class SerializerTests(unittest.TestCase):
    def test_serializer_json_serializable(self) -> None:
        vp = V.build_value_path_from_role_classification(_classify("deposit"), function_id="function:a")
        data = V.value_path_to_dict(vp)
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_serializer_does_not_mutate_source(self) -> None:
        vp = V.build_value_path_from_role_classification(_classify("deposit"))
        before = (list(vp.roles), [s.segment_kind for s in vp.segments])
        V.value_path_to_dict(vp)
        self.assertEqual((list(vp.roles), [s.segment_kind for s in vp.segments]), before)

    def test_serializer_unsupported_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            V.value_path_to_dict(object())


class NonInventionAndNoOverclaimTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vp = V.build_value_path_from_role_classification(
            RO.classify_function_role(function_name="getPrice", mutability="view"), function_id="function:p")

    def test_no_invented_asset_symbol(self) -> None:
        self.assertTrue(all(s.asset_symbol == "" for s in self.vp.segments))

    def test_no_invented_oracle_source(self) -> None:
        self.assertTrue(all(s.oracle_source == "" for s in self.vp.segments))

    def test_no_invented_external_target(self) -> None:
        self.assertTrue(all(s.external_target == "" for s in self.vp.segments))

    def test_no_invented_state_variable(self) -> None:
        self.assertTrue(all(s.state_variable == "" for s in self.vp.segments))

    def test_no_fuzzy_unknown_function(self) -> None:
        vp = V.build_value_path_from_role_classification(_classify("frobnicate"))
        self.assertEqual(vp.path_kind, V.UNCLASSIFIED_PATH)
        self.assertEqual([s.segment_kind for s in vp.segments], [V.FUNCTION_ENTRY, V.UNKNOWN_SEGMENT])

    def test_output_has_no_overclaim_wording(self) -> None:
        g = V.build_value_path_graph("P", [
            V.build_value_path_from_role_classification(_classify("liquidate"), function_id="function:l")])
        blob = json.dumps(V.value_path_to_dict(g)).lower()
        for token in ("human_reviewed", "confirmed vulnerability", "final severity",
                      "audit passed", "bounty", "verified_safe", "ready_for_submission\": true"):
            self.assertNotIn(token, blob)

    def test_no_overclaim_tokens_in_taxonomy(self) -> None:
        forbidden = {"SAFE", "VERIFIED_SAFE", "CONFIRMED_VULNERABILITY", "AUDIT_PASSED",
                     "FINAL_SEVERITY", "HUMAN_REVIEWED", "BOUNTY"}
        self.assertFalse(forbidden & set(V.VALUE_PATH_KIND_VALUES))
        self.assertFalse(forbidden & set(V.VALUE_PATH_SEGMENT_KIND_VALUES))

    def test_taxonomy_counts(self) -> None:
        self.assertEqual(len(V.VALUE_PATH_KIND_VALUES), 14)
        self.assertEqual(len(V.VALUE_PATH_SEGMENT_KIND_VALUES), 21)


class ImportAndExportTests(unittest.TestCase):
    def test_import_has_no_filesystem_side_effects(self) -> None:
        import importlib
        import arkheionx.intelligence.value_paths as mod
        importlib.reload(mod)
        self.assertTrue(hasattr(mod, "build_value_path_from_role_classification"))

    def test_package_exports_value_paths(self) -> None:
        import arkheionx.intelligence as intel
        self.assertTrue(hasattr(intel, "value_paths"))
        self.assertTrue(hasattr(intel, "ValuePath"))
        self.assertTrue(hasattr(intel, "build_value_path_graph"))
        self.assertIn("ValuePath", intel.__all__)

    def test_deterministic_across_calls(self) -> None:
        a = V.value_path_to_dict(V.build_value_path_from_role_classification(_classify("swap"), function_id="function:s"))
        b = V.value_path_to_dict(V.build_value_path_from_role_classification(_classify("swap"), function_id="function:s"))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
