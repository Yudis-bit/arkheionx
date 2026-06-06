"""Tests for the internal protocol intelligence graph builder (v3.8, Agent 6).

Review surface only: graph consistency never proves protocol safety and a graph
warning never proves a vulnerability. Edges are exact-ID / explicit-alias only.
"""
from __future__ import annotations

import json
import unittest

from arkheionx.intelligence import assumptions as A
from arkheionx.intelligence import graph as G
from arkheionx.intelligence import roles as RO
from arkheionx.intelligence import test_gaps as TG
from arkheionx.intelligence import value_paths as V


def _role_node_with_function(name: str, function_id: str, contract: str = "Vault"):
    cls = RO.classify_function_role(function_name=name, contract_name=contract)
    cls.metadata["function_id"] = function_id
    return cls


def _slice(name: str = "withdraw", fid: str = "function:w"):
    cls = _role_node_with_function(name, fid)
    vp = V.build_value_path_from_role_classification(cls, function_id=fid)
    asms = A.build_assumptions_from_value_path(vp)
    gaps = []
    for a in asms:
        gaps += TG.build_test_gaps_from_assumption(a)
    return cls, vp, asms, gaps


class GraphIdTests(unittest.TestCase):
    def test_node_id_deterministic(self) -> None:
        self.assertEqual(
            G.protocol_graph_node_id(G.GRAPH_NODE_VALUE_PATH, "s"),
            G.protocol_graph_node_id(G.GRAPH_NODE_VALUE_PATH, "s"),
        )

    def test_node_id_changes_with_source(self) -> None:
        self.assertNotEqual(
            G.protocol_graph_node_id(G.GRAPH_NODE_VALUE_PATH, "s1"),
            G.protocol_graph_node_id(G.GRAPH_NODE_VALUE_PATH, "s2"),
        )

    def test_edge_id_deterministic(self) -> None:
        self.assertEqual(
            G.protocol_graph_edge_id(G.GRAPH_EDGE_FUNCTION_TO_VALUE_PATH, "a", "b"),
            G.protocol_graph_edge_id(G.GRAPH_EDGE_FUNCTION_TO_VALUE_PATH, "a", "b"),
        )

    def test_edge_id_changes_with_target(self) -> None:
        self.assertNotEqual(
            G.protocol_graph_edge_id(G.GRAPH_EDGE_FUNCTION_TO_VALUE_PATH, "a", "b1"),
            G.protocol_graph_edge_id(G.GRAPH_EDGE_FUNCTION_TO_VALUE_PATH, "a", "b2"),
        )

    def test_check_id_deterministic(self) -> None:
        self.assertEqual(
            G.protocol_graph_check_id(G.GRAPH_CHECK_ORPHAN_NODE, node_id="n"),
            G.protocol_graph_check_id(G.GRAPH_CHECK_ORPHAN_NODE, node_id="n"),
        )

    def test_graph_id_deterministic(self) -> None:
        self.assertEqual(
            G.protocol_intelligence_graph_id("P", ["a"], ["e"]),
            G.protocol_intelligence_graph_id("P", ["a"], ["e"]),
        )

    def test_graph_id_node_order_stable(self) -> None:
        self.assertEqual(
            G.protocol_intelligence_graph_id("P", ["a", "b"], []),
            G.protocol_intelligence_graph_id("P", ["b", "a"], []),
        )

    def test_graph_id_edge_order_stable(self) -> None:
        self.assertEqual(
            G.protocol_intelligence_graph_id("P", [], ["x", "y"]),
            G.protocol_intelligence_graph_id("P", [], ["y", "x"]),
        )

    def test_id_prefixes(self) -> None:
        self.assertTrue(G.protocol_graph_node_id(G.GRAPH_NODE_VALUE_PATH, "s").startswith("protocol-graph-node:"))
        self.assertTrue(G.protocol_graph_edge_id(G.GRAPH_EDGE_UNKNOWN, "a", "b").startswith("protocol-graph-edge:"))
        self.assertTrue(G.protocol_graph_check_id(G.GRAPH_CHECK_ORPHAN_NODE).startswith("protocol-graph-check:"))
        self.assertTrue(G.protocol_intelligence_graph_id("My P", [], []).startswith("protocol-intelligence-graph:my-p:"))

    def test_ids_no_spaces(self) -> None:
        self.assertNotIn(" ", G.protocol_graph_node_id(G.GRAPH_NODE_VALUE_PATH, "s 1", "lbl x"))
        self.assertNotIn(" ", G.protocol_intelligence_graph_id("My P", [], []))

    def test_ids_no_backslashes(self) -> None:
        self.assertNotIn("\\", G.protocol_graph_node_id(G.GRAPH_NODE_VALUE_PATH, "s"))

    def test_empty_kind_raises(self) -> None:
        with self.assertRaises(ValueError):
            G.protocol_graph_node_id("")
        with self.assertRaises(ValueError):
            G.protocol_graph_edge_id("", "a", "b")
        with self.assertRaises(ValueError):
            G.protocol_graph_edge_id("k", "", "b")
        with self.assertRaises(ValueError):
            G.protocol_graph_check_id("")
        with self.assertRaises(ValueError):
            G.protocol_intelligence_graph_id("", [], [])

    def test_unsupported_seed_raises(self) -> None:
        with self.assertRaises(TypeError):
            G.canonical_graph_seed({"x": {1, 2}})


class DataclassTests(unittest.TestCase):
    def test_node_minimal(self) -> None:
        self.assertEqual(G.ProtocolGraphNode().node_kind, G.GRAPH_NODE_UNKNOWN)

    def test_edge_minimal(self) -> None:
        self.assertEqual(G.ProtocolGraphEdge().edge_kind, G.GRAPH_EDGE_UNKNOWN)
        self.assertEqual(G.ProtocolGraphEdge().confidence, "LINKED")

    def test_check_minimal(self) -> None:
        self.assertEqual(G.ProtocolGraphCheck().severity, G.SEVERITY_WARNING)

    def test_graph_minimal(self) -> None:
        self.assertEqual(G.ProtocolIntelligenceGraph().nodes, [])

    def test_manual_review_default(self) -> None:
        self.assertTrue(G.ProtocolGraphNode().manual_review_required)
        self.assertTrue(G.ProtocolIntelligenceGraph().manual_review_required)

    def test_ready_false_default(self) -> None:
        self.assertFalse(G.ProtocolGraphNode().ready_for_submission)
        self.assertFalse(G.ProtocolIntelligenceGraph().ready_for_submission)

    def test_mutable_defaults_independent(self) -> None:
        a, b = G.ProtocolGraphNode(), G.ProtocolGraphNode()
        a.warnings.append("x")
        a.linked_ids.append("y")
        self.assertEqual(b.warnings, [])
        self.assertEqual(b.linked_ids, [])


class NodeBuilderTests(unittest.TestCase):
    def test_role_classification_node(self) -> None:
        nodes = G.graph_node_from_role_classification(RO.classify_function_role(function_name="deposit"))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].node_kind, G.GRAPH_NODE_FUNCTION_ROLE)

    def test_multi_role_deterministic(self) -> None:
        cls = RO.classify_function_role(function_name="emergencyWithdraw")
        a = G.graph_node_from_role_classification(cls)
        b = G.graph_node_from_role_classification(cls)
        self.assertEqual(G.graph_to_dict(a), G.graph_to_dict(b))
        self.assertEqual(a[0].metadata["roles"], ["PAUSE_EMERGENCY", "OUTFLOW"])

    def test_value_path_node(self) -> None:
        vp = _slice()[1]
        kinds = [n.node_kind for n in G.graph_nodes_from_value_path(vp)]
        self.assertIn(G.GRAPH_NODE_VALUE_PATH, kinds)

    def test_value_path_segment_nodes(self) -> None:
        vp = _slice()[1]
        kinds = [n.node_kind for n in G.graph_nodes_from_value_path(vp)]
        self.assertIn(G.GRAPH_NODE_VALUE_PATH_SEGMENT, kinds)

    def test_assumption_node(self) -> None:
        asm = _slice()[2][0]
        self.assertEqual(G.graph_nodes_from_assumption(asm)[0].node_kind, G.GRAPH_NODE_ASSUMPTION)

    def test_test_gap_node(self) -> None:
        gap = _slice()[3][0]
        self.assertEqual(G.graph_nodes_from_test_gap(gap)[0].node_kind, G.GRAPH_NODE_TEST_GAP)

    def test_node_preserves_source_id(self) -> None:
        vp = _slice()[1]
        vp_node = next(n for n in G.graph_nodes_from_value_path(vp) if n.node_kind == G.GRAPH_NODE_VALUE_PATH)
        self.assertEqual(vp_node.source_id, vp.path_id)

    def test_node_preserves_contract_function(self) -> None:
        vp = _slice()[1]
        vp_node = next(n for n in G.graph_nodes_from_value_path(vp) if n.node_kind == G.GRAPH_NODE_VALUE_PATH)
        self.assertEqual(vp_node.function_name, "withdraw")

    def test_node_preserves_category_path_status(self) -> None:
        vp = _slice()[1]
        vp_node = next(n for n in G.graph_nodes_from_value_path(vp) if n.node_kind == G.GRAPH_NODE_VALUE_PATH)
        self.assertEqual(vp_node.path_kind, vp.path_kind)
        gap_node = G.graph_nodes_from_test_gap(_slice()[3][0])[0]
        self.assertTrue(gap_node.status)
        self.assertTrue(gap_node.category)

    def test_no_invented_aliases(self) -> None:
        node = G.graph_node_from_role_classification(RO.classify_function_role(function_name="deposit"))[0]
        self.assertEqual(node.aliases, [])


class EdgeBuilderTests(unittest.TestCase):
    def test_full_slice_edges(self) -> None:
        cls, vp, asms, gaps = _slice()
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        ekinds = {e.edge_kind for e in g.edges}
        self.assertIn(G.GRAPH_EDGE_FUNCTION_TO_VALUE_PATH, ekinds)
        self.assertIn(G.GRAPH_EDGE_VALUE_PATH_TO_SEGMENT, ekinds)
        self.assertIn(G.GRAPH_EDGE_VALUE_PATH_TO_ASSUMPTION, ekinds)
        self.assertIn(G.GRAPH_EDGE_ASSUMPTION_TO_TEST_GAP, ekinds)

    def test_function_to_test_gap_edge(self) -> None:
        cls = _role_node_with_function("withdraw", "function:w")
        gaps = TG.build_test_gaps_from_roles(["OUTFLOW"], function_id="function:w")
        g = G.build_protocol_intelligence_graph("P", [cls], None, None, gaps)
        self.assertIn(G.GRAPH_EDGE_FUNCTION_TO_TEST_GAP, {e.edge_kind for e in g.edges})

    def test_value_path_to_test_gap_edge(self) -> None:
        cls, vp, _, _ = _slice()
        gaps = TG.build_test_gaps_from_value_path(vp)
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], None, gaps)
        self.assertIn(G.GRAPH_EDGE_VALUE_PATH_TO_TEST_GAP, {e.edge_kind for e in g.edges})

    def test_local_validation_edge_only_with_node(self) -> None:
        gap = TG.correlate_test_gap_with_local_validation(
            TG.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")[0],
            local_validation_ids=["lv1"], tested=True)
        g = G.build_protocol_intelligence_graph("P", test_gaps=[gap], local_validation_ids=["lv1"])
        self.assertIn(G.GRAPH_EDGE_TEST_GAP_TO_LOCAL_VALIDATION, {e.edge_kind for e in g.edges})

    def test_trace_receipt_edge_only_with_node(self) -> None:
        gap = TG.correlate_test_gap_with_local_validation(
            TG.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")[0],
            trace_receipt_ids=["tr1"], trace_bound=True)
        g = G.build_protocol_intelligence_graph("P", test_gaps=[gap], trace_receipt_ids=["tr1"])
        self.assertIn(G.GRAPH_EDGE_TEST_GAP_TO_TRACE_RECEIPT, {e.edge_kind for e in g.edges})

    def test_missing_target_creates_unresolved_check(self) -> None:
        gap = TG.correlate_test_gap_with_local_validation(
            TG.build_test_gaps_from_roles(["OUTFLOW"], function_id="f")[0],
            local_validation_ids=["lv-missing"], tested=True)
        g = G.build_protocol_intelligence_graph("P", test_gaps=[gap])  # lv node not supplied
        self.assertIn(G.GRAPH_CHECK_UNRESOLVED_REFERENCE, {c.check_kind for c in g.checks})

    def test_ambiguous_function_alias_check(self) -> None:
        c1 = _role_node_with_function("withdraw", "function:dup", "VaultA")
        c2 = _role_node_with_function("withdrawAll", "function:dup", "VaultB")
        vp = V.build_value_path_from_role_classification(c1, function_id="function:dup")
        g = G.build_protocol_intelligence_graph("P", [c1, c2], [vp])
        self.assertIn(G.GRAPH_CHECK_AMBIGUOUS_ALIAS, {c.check_kind for c in g.checks})
        self.assertNotIn(G.GRAPH_EDGE_FUNCTION_TO_VALUE_PATH, {e.edge_kind for e in g.edges})

    def test_no_fuzzy_matching(self) -> None:
        # Role node with function:a, value path with function:b -> no edge.
        cls = _role_node_with_function("withdraw", "function:a")
        vp = V.build_value_path_from_role_classification(
            RO.classify_function_role(function_name="withdraw"), function_id="function:b")
        g = G.build_protocol_intelligence_graph("P", [cls], [vp])
        self.assertNotIn(G.GRAPH_EDGE_FUNCTION_TO_VALUE_PATH, {e.edge_kind for e in g.edges})


class GraphBuilderTests(unittest.TestCase):
    def test_empty_graph_deterministic(self) -> None:
        a = G.graph_to_dict(G.build_protocol_intelligence_graph("Empty"))
        b = G.graph_to_dict(G.build_protocol_intelligence_graph("Empty"))
        self.assertEqual(a, b)
        self.assertEqual(a["node_count"], 0)
        self.assertEqual(a["edge_count"], 0)

    def test_builds_all_node_kinds(self) -> None:
        cls, vp, asms, gaps = _slice()
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        kinds = {n.node_kind for n in g.nodes}
        for kind in (G.GRAPH_NODE_FUNCTION_ROLE, G.GRAPH_NODE_VALUE_PATH,
                     G.GRAPH_NODE_VALUE_PATH_SEGMENT, G.GRAPH_NODE_ASSUMPTION, G.GRAPH_NODE_TEST_GAP):
            self.assertIn(kind, kinds)

    def test_local_validation_node_only_when_supplied(self) -> None:
        g = G.build_protocol_intelligence_graph("P", local_validation_ids=["lv1"])
        self.assertIn(G.GRAPH_NODE_LOCAL_VALIDATION, {n.node_kind for n in g.nodes})

    def test_trace_node_only_when_supplied(self) -> None:
        g = G.build_protocol_intelligence_graph("P", trace_receipt_ids=["tr1"])
        self.assertIn(G.GRAPH_NODE_TRACE_RECEIPT, {n.node_kind for n in g.nodes})

    def test_does_not_invent_local_validation(self) -> None:
        cls, vp, asms, gaps = _slice()
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        self.assertNotIn(G.GRAPH_NODE_LOCAL_VALIDATION, {n.node_kind for n in g.nodes})

    def test_does_not_invent_trace(self) -> None:
        cls, vp, asms, gaps = _slice()
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        self.assertNotIn(G.GRAPH_NODE_TRACE_RECEIPT, {n.node_kind for n in g.nodes})

    def test_counts(self) -> None:
        cls, vp, asms, gaps = _slice()
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        self.assertEqual(g.node_count, len(g.nodes))
        self.assertEqual(g.edge_count, len(g.edges))

    def test_rollups(self) -> None:
        cls, vp, asms, gaps = _slice()
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        self.assertIn("function:w", g.linked_function_ids)
        self.assertIn(vp.path_id, g.linked_value_path_ids)
        self.assertEqual(g.linked_assumption_ids, sorted(a.assumption_id for a in asms))
        self.assertEqual(g.linked_test_gap_ids, sorted({x.test_gap_id for x in gaps}))

    def test_local_validation_rollup(self) -> None:
        g = G.build_protocol_intelligence_graph("P", local_validation_ids=["lv1"])
        self.assertEqual(g.linked_local_validation_ids, ["lv1"])

    def test_graph_id_and_ordering_deterministic(self) -> None:
        cls, vp, asms, gaps = _slice()
        g1 = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        g2 = G.build_protocol_intelligence_graph("P", test_gaps=gaps, assumptions=asms, value_paths=[vp], role_classifications=[cls])
        self.assertEqual(g1.graph_id, g2.graph_id)
        self.assertEqual([n.node_id for n in g1.nodes], [n.node_id for n in g2.nodes])
        self.assertEqual([e.edge_id for e in g1.edges], [e.edge_id for e in g2.edges])


class ConsistencyTests(unittest.TestCase):
    def test_duplicate_node_check(self) -> None:
        nodes = G.graph_nodes_from_value_path(_slice()[1])
        _, checks = G.deduplicate_graph_nodes(nodes + nodes)
        self.assertIn(G.GRAPH_CHECK_DUPLICATE_NODE_ID, {c.check_kind for c in checks})

    def test_duplicate_edge_check(self) -> None:
        e = G.ProtocolGraphEdge(edge_id="dup", edge_kind=G.GRAPH_EDGE_UNKNOWN)
        _, checks = G.deduplicate_graph_edges([e, e])
        self.assertIn(G.GRAPH_CHECK_DUPLICATE_EDGE_ID, {c.check_kind for c in checks})

    def test_dangling_source_error(self) -> None:
        n = G.ProtocolGraphNode(node_id="n", node_kind=G.GRAPH_NODE_VALUE_PATH)
        graph = G.ProtocolIntelligenceGraph(nodes=[n], edges=[
            G.ProtocolGraphEdge(edge_id="e", edge_kind=G.GRAPH_EDGE_UNKNOWN, source_node_id="missing", target_node_id="n")])
        checks = G.validate_protocol_graph(graph)
        c = next(c for c in checks if c.check_kind == G.GRAPH_CHECK_DANGLING_EDGE_SOURCE)
        self.assertEqual(c.severity, G.SEVERITY_ERROR)

    def test_dangling_target_error(self) -> None:
        n = G.ProtocolGraphNode(node_id="n", node_kind=G.GRAPH_NODE_VALUE_PATH)
        graph = G.ProtocolIntelligenceGraph(nodes=[n], edges=[
            G.ProtocolGraphEdge(edge_id="e", edge_kind=G.GRAPH_EDGE_UNKNOWN, source_node_id="n", target_node_id="missing")])
        self.assertIn(G.GRAPH_CHECK_DANGLING_EDGE_TARGET, {c.check_kind for c in G.validate_protocol_graph(graph)})

    def test_orphan_warning(self) -> None:
        graph = G.ProtocolIntelligenceGraph(
            nodes=[G.ProtocolGraphNode(node_id="n", node_kind=G.GRAPH_NODE_VALUE_PATH)], edges=[])
        c = next(c for c in G.validate_protocol_graph(graph) if c.check_kind == G.GRAPH_CHECK_ORPHAN_NODE)
        self.assertEqual(c.severity, G.SEVERITY_WARNING)

    def test_unsupported_node_kind_check(self) -> None:
        graph = G.ProtocolIntelligenceGraph(nodes=[G.ProtocolGraphNode(node_id="n", node_kind="WEIRD")])
        self.assertIn(G.GRAPH_CHECK_UNSUPPORTED_NODE_KIND, {c.check_kind for c in G.validate_protocol_graph(graph)})

    def test_unsupported_edge_kind_check(self) -> None:
        n = G.ProtocolGraphNode(node_id="n", node_kind=G.GRAPH_NODE_VALUE_PATH)
        graph = G.ProtocolIntelligenceGraph(nodes=[n], edges=[
            G.ProtocolGraphEdge(edge_id="e", edge_kind="WEIRD", source_node_id="n", target_node_id="n")])
        self.assertIn(G.GRAPH_CHECK_UNSUPPORTED_EDGE_KIND, {c.check_kind for c in G.validate_protocol_graph(graph)})

    def test_ready_for_submission_true_check(self) -> None:
        graph = G.ProtocolIntelligenceGraph(
            nodes=[G.ProtocolGraphNode(node_id="n", node_kind=G.GRAPH_NODE_VALUE_PATH, ready_for_submission=True)])
        self.assertIn(G.GRAPH_CHECK_READY_FOR_SUBMISSION_TRUE, {c.check_kind for c in G.validate_protocol_graph(graph)})

    def test_forbidden_finality_wording_check(self) -> None:
        graph = G.ProtocolIntelligenceGraph(
            nodes=[G.ProtocolGraphNode(node_id="n", node_kind=G.GRAPH_NODE_VALUE_PATH, label="confirmed vulnerability here")])
        self.assertIn(G.GRAPH_CHECK_FORBIDDEN_FINALITY_WORDING, {c.check_kind for c in G.validate_protocol_graph(graph)})

    def test_checks_manual_review_true(self) -> None:
        graph = G.ProtocolIntelligenceGraph(
            nodes=[G.ProtocolGraphNode(node_id="n", node_kind=G.GRAPH_NODE_VALUE_PATH)], edges=[])
        self.assertTrue(all(c.manual_review_required for c in G.validate_protocol_graph(graph)))

    def test_checks_ready_false(self) -> None:
        graph = G.ProtocolIntelligenceGraph(
            nodes=[G.ProtocolGraphNode(node_id="n", node_kind=G.GRAPH_NODE_VALUE_PATH)], edges=[])
        self.assertTrue(all(not c.ready_for_submission for c in G.validate_protocol_graph(graph)))


class DedupSerializationTests(unittest.TestCase):
    def test_deduplicate_nodes_deterministic(self) -> None:
        nodes = G.graph_nodes_from_value_path(_slice()[1])
        a, _ = G.deduplicate_graph_nodes(nodes)
        b, _ = G.deduplicate_graph_nodes(nodes)
        self.assertEqual([n.node_id for n in a], [n.node_id for n in b])

    def test_deduplicate_edges_deterministic(self) -> None:
        cls, vp, asms, gaps = _slice()
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        a, _ = G.deduplicate_graph_edges(g.edges)
        b, _ = G.deduplicate_graph_edges(g.edges)
        self.assertEqual([e.edge_id for e in a], [e.edge_id for e in b])

    def test_graph_to_dict_json_serializable(self) -> None:
        cls, vp, asms, gaps = _slice()
        data = G.graph_to_dict(G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps))
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_graph_to_dict_no_mutation(self) -> None:
        cls, vp, asms, gaps = _slice()
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        before = g.node_count
        G.graph_to_dict(g)
        self.assertEqual(g.node_count, before)

    def test_graph_to_dict_unsupported_raises(self) -> None:
        with self.assertRaises(TypeError):
            G.graph_to_dict(object())

    def test_output_has_no_overclaim_wording(self) -> None:
        cls, vp, asms, gaps = _slice("liquidate", "function:l")
        g = G.build_protocol_intelligence_graph("P", [cls], [vp], asms, gaps)
        blob = json.dumps(G.graph_to_dict(g)).lower()
        for token in ("human_reviewed", "confirmed vulnerability", "final severity", "audit passed",
                      "bounty", "verified safe", "proves safety", "ready_for_submission\": true"):
            self.assertNotIn(token, blob)

    def test_no_overclaim_tokens_in_taxonomy(self) -> None:
        forbidden = {"SAFE", "VERIFIED_SAFE", "CONFIRMED_VULNERABILITY", "AUDIT_PASSED",
                     "FINAL_SEVERITY", "HUMAN_REVIEWED", "BOUNTY"}
        self.assertFalse(forbidden & set(G.GRAPH_NODE_KINDS))
        self.assertFalse(forbidden & set(G.GRAPH_EDGE_KINDS))
        self.assertFalse(forbidden & set(G.GRAPH_CHECK_KINDS))

    def test_taxonomy_counts(self) -> None:
        self.assertEqual(len(G.GRAPH_NODE_KINDS), 10)
        self.assertEqual(len(G.GRAPH_EDGE_KINDS), 15)
        self.assertEqual(len(G.GRAPH_CHECK_KINDS), 12)


class ImportAndExportTests(unittest.TestCase):
    def test_import_has_no_filesystem_side_effects(self) -> None:
        import importlib
        import arkheionx.intelligence.graph as mod
        importlib.reload(mod)
        self.assertTrue(hasattr(mod, "build_protocol_intelligence_graph"))

    def test_package_exports_graph(self) -> None:
        import arkheionx.intelligence as intel
        self.assertTrue(hasattr(intel, "graph"))
        self.assertTrue(hasattr(intel, "ProtocolIntelligenceGraph"))
        self.assertTrue(hasattr(intel, "build_protocol_intelligence_graph"))
        self.assertIn("ProtocolIntelligenceGraph", intel.__all__)


if __name__ == "__main__":
    unittest.main()
