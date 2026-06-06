"""Tests for the internal local-validation coverage correlation (v3.8, Agent 7).

Review context only: tested coverage never proves safety and missing coverage
never proves a vulnerability. Exact-ID / explicit-alias linking only.
"""
from __future__ import annotations

import json
import unittest

from arkheionx.intelligence import coverage as C
from arkheionx.intelligence import graph as G
from arkheionx.intelligence import test_gaps as TG


def _gap(fid: str = "function:w", roles=("OUTFLOW",)):
    return TG.build_test_gaps_from_roles(list(roles), function_id=fid)[0]


def _tested_gap(fid: str = "function:w", lv="lv1"):
    return TG.correlate_test_gap_with_local_validation(_gap(fid), local_validation_ids=[lv], tested=True)


def _trace_gap(fid: str = "function:w", tr="tr1"):
    return TG.correlate_test_gap_with_local_validation(_gap(fid), trace_receipt_ids=[tr], trace_bound=True)


class CoverageIdTests(unittest.TestCase):
    def test_coverage_id_deterministic(self) -> None:
        self.assertEqual(
            C.local_validation_coverage_id("lv1", "", "gap1"),
            C.local_validation_coverage_id("lv1", "", "gap1"),
        )

    def test_coverage_id_changes_with_test_gap(self) -> None:
        self.assertNotEqual(
            C.local_validation_coverage_id("lv1", "", "gap1"),
            C.local_validation_coverage_id("lv1", "", "gap2"),
        )

    def test_check_id_deterministic(self) -> None:
        self.assertEqual(
            C.coverage_correlation_check_id(C.COVERAGE_CHECK_DUPLICATE_COVERAGE_ID, coverage_id="c"),
            C.coverage_correlation_check_id(C.COVERAGE_CHECK_DUPLICATE_COVERAGE_ID, coverage_id="c"),
        )

    def test_summary_id_deterministic(self) -> None:
        self.assertEqual(C.local_validation_coverage_summary_id("P", ["a"]),
                         C.local_validation_coverage_summary_id("P", ["a"]))

    def test_summary_id_order_stable(self) -> None:
        self.assertEqual(C.local_validation_coverage_summary_id("P", ["a", "b"]),
                         C.local_validation_coverage_summary_id("P", ["b", "a"]))

    def test_id_prefixes(self) -> None:
        self.assertTrue(C.local_validation_coverage_id("lv1", "", "g").startswith("local-validation-coverage:"))
        self.assertTrue(C.coverage_correlation_check_id(C.COVERAGE_CHECK_AMBIGUOUS_ALIAS).startswith("coverage-check:"))
        self.assertTrue(C.local_validation_coverage_summary_id("My P", []).startswith("local-validation-coverage-summary:my-p:"))

    def test_ids_no_spaces(self) -> None:
        self.assertNotIn(" ", C.local_validation_coverage_id("lv 1", "", "g a"))
        self.assertNotIn(" ", C.local_validation_coverage_summary_id("My P", []))

    def test_ids_no_backslashes(self) -> None:
        self.assertNotIn("\\", C.local_validation_coverage_id("lv1", "", "g"))

    def test_empty_required_raises(self) -> None:
        with self.assertRaises(ValueError):
            C.local_validation_coverage_id()
        with self.assertRaises(ValueError):
            C.local_validation_coverage_id("lv1")  # no target
        with self.assertRaises(ValueError):
            C.coverage_correlation_check_id("")
        with self.assertRaises(ValueError):
            C.local_validation_coverage_summary_id("", [])

    def test_unsupported_seed_raises(self) -> None:
        with self.assertRaises(TypeError):
            C.canonical_coverage_seed({"x": {1, 2}})


class DataclassTests(unittest.TestCase):
    def test_link_minimal(self) -> None:
        self.assertEqual(C.LocalValidationCoverageLink().support_level, C.COVERAGE_CONTEXT_ONLY)

    def test_check_minimal(self) -> None:
        self.assertEqual(C.CoverageCorrelationCheck().severity, C.SEVERITY_WARNING)

    def test_summary_minimal(self) -> None:
        self.assertEqual(C.LocalValidationCoverageSummary().coverage_links, [])

    def test_manual_review_default(self) -> None:
        self.assertTrue(C.LocalValidationCoverageLink().manual_review_required)
        self.assertTrue(C.LocalValidationCoverageSummary().manual_review_required)

    def test_ready_false_default(self) -> None:
        self.assertFalse(C.LocalValidationCoverageLink().ready_for_submission)
        self.assertFalse(C.LocalValidationCoverageSummary().ready_for_submission)

    def test_mutable_defaults_independent(self) -> None:
        a, b = C.LocalValidationCoverageLink(), C.LocalValidationCoverageLink()
        a.warnings.append("x")
        self.assertEqual(b.warnings, [])


class IndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = G.build_protocol_intelligence_graph("P", test_gaps=[_tested_gap()], local_validation_ids=["lv1"])

    def test_node_index_by_source_id(self) -> None:
        index = C.build_graph_node_index(self.graph)
        self.assertIn(_tested_gap().test_gap_id, index)

    def test_node_index_by_node_id(self) -> None:
        index = C.build_graph_node_index(self.graph)
        self.assertTrue(all(n.node_id in index for n in self.graph.nodes))

    def test_alias_index_exact(self) -> None:
        node = G.ProtocolGraphNode(node_id="n1", source_id="src1", aliases=["alias1"])
        index, checks = C.build_explicit_alias_index([node])
        self.assertEqual(index.get("alias1"), "src1")
        self.assertEqual(checks, [])

    def test_alias_index_ambiguous_check(self) -> None:
        a = G.ProtocolGraphNode(node_id="n1", source_id="srcA", aliases=["dup"])
        b = G.ProtocolGraphNode(node_id="n2", source_id="srcB", aliases=["dup"])
        index, checks = C.build_explicit_alias_index([a, b])
        self.assertNotIn("dup", index)
        self.assertIn(C.COVERAGE_CHECK_AMBIGUOUS_ALIAS, {c.check_kind for c in checks})

    def test_no_fuzzy_alias(self) -> None:
        node = G.ProtocolGraphNode(node_id="n1", source_id="src1", aliases=["alias1"])
        index, _ = C.build_explicit_alias_index([node])
        self.assertNotIn("alias", index)  # substring must not resolve

    def test_test_gap_index(self) -> None:
        g = _tested_gap()
        self.assertIn(g.test_gap_id, C.build_test_gap_index([g]))


class CoverageLinkTests(unittest.TestCase):
    def test_tested_link(self) -> None:
        links, _ = C.build_coverage_links_for_test_gap(_tested_gap())
        self.assertTrue(any(l.support_level == C.COVERAGE_TESTED for l in links))

    def test_trace_bound_link(self) -> None:
        links, _ = C.build_coverage_links_for_test_gap(_trace_gap())
        self.assertTrue(any(l.support_level == C.COVERAGE_TRACE_BOUND for l in links))

    def test_graph_node_sets_target_node_id(self) -> None:
        gap = _tested_gap()
        graph = G.build_protocol_intelligence_graph("P", test_gaps=[gap], local_validation_ids=["lv1"])
        links, _ = C.build_coverage_links_for_test_gap(gap, graph=graph)
        self.assertTrue(all(l.target_node_id for l in links))

    def test_missing_graph_context_link_with_warning(self) -> None:
        links, _ = C.build_coverage_links_for_test_gap(_tested_gap(), graph=None)
        self.assertTrue(links)
        self.assertTrue(all(l.warnings for l in links))

    def test_missing_target_unresolved_check(self) -> None:
        graph = G.build_protocol_intelligence_graph("P")  # gap node not present
        _, checks = C.build_coverage_links_for_test_gap(_tested_gap(), graph=graph)
        self.assertIn(C.COVERAGE_CHECK_UNRESOLVED_TEST_GAP_ID, {c.check_kind for c in checks})

    def test_explicit_lv_not_referenced_no_invented_link(self) -> None:
        links, _ = C.build_coverage_links_for_test_gap(_tested_gap(lv="lv1"), local_validation_ids=["other"])
        self.assertFalse(any(l.source_local_validation_id == "other" for l in links))
        self.assertFalse(links)  # gap's lv1 not in allowed set -> no link

    def test_explicit_trace_not_referenced_no_invented_link(self) -> None:
        links, _ = C.build_coverage_links_for_test_gap(_trace_gap(tr="tr1"), trace_receipt_ids=["other"])
        self.assertFalse(any(l.source_trace_receipt_id == "other" for l in links))
        self.assertFalse(links)

    def test_no_lv_ids_no_coverage(self) -> None:
        links, _ = C.build_coverage_links_for_test_gap(_gap())
        self.assertEqual(links, [])

    def test_no_trace_ids_no_trace_bound(self) -> None:
        links, _ = C.build_coverage_links_for_test_gap(_gap())
        self.assertFalse(any(l.support_level == C.COVERAGE_TRACE_BOUND for l in links))


class SummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gap = _tested_gap("function:w", "lv1")
        self.tgap = _trace_gap("function:x", "tr1")
        self.graph = G.build_protocol_intelligence_graph(
            "P", test_gaps=[self.gap, self.tgap], local_validation_ids=["lv1"], trace_receipt_ids=["tr1"])
        self.summary = C.correlate_local_validation_coverage(
            "Proto", graph=self.graph, test_gaps=[self.gap, self.tgap],
            local_validation_ids=["lv1"], trace_receipt_ids=["tr1"])

    def test_builds_summary(self) -> None:
        self.assertTrue(self.summary.coverage_links)

    def test_tested_count(self) -> None:
        self.assertEqual(self.summary.tested_count, sum(1 for l in self.summary.coverage_links if l.support_level == C.COVERAGE_TESTED))
        self.assertGreaterEqual(self.summary.tested_count, 1)

    def test_trace_bound_count(self) -> None:
        self.assertGreaterEqual(self.summary.trace_bound_count, 1)

    def test_unresolved_count(self) -> None:
        s = C.correlate_local_validation_coverage("P", graph=G.build_protocol_intelligence_graph("P"),
                                                  test_gaps=[self.gap])
        self.assertEqual(s.unresolved_count, sum(1 for c in s.checks if c.check_kind in C._UNRESOLVED_CHECK_KINDS))
        self.assertGreaterEqual(s.unresolved_count, 1)

    def test_linked_lv_sorted(self) -> None:
        self.assertEqual(self.summary.linked_local_validation_ids, sorted(set(self.summary.linked_local_validation_ids)))

    def test_linked_trace_sorted(self) -> None:
        self.assertEqual(self.summary.linked_trace_receipt_ids, sorted(set(self.summary.linked_trace_receipt_ids)))

    def test_linked_test_gap_sorted(self) -> None:
        self.assertEqual(self.summary.linked_test_gap_ids, sorted(set(self.summary.linked_test_gap_ids)))

    def test_linked_function_sorted(self) -> None:
        self.assertEqual(self.summary.linked_function_ids, sorted(set(self.summary.linked_function_ids)))

    def test_linked_value_path_sorted(self) -> None:
        self.assertEqual(self.summary.linked_value_path_ids, sorted(set(self.summary.linked_value_path_ids)))

    def test_linked_assumption_sorted(self) -> None:
        self.assertEqual(self.summary.linked_assumption_ids, sorted(set(self.summary.linked_assumption_ids)))

    def test_summary_id_deterministic(self) -> None:
        s2 = C.correlate_local_validation_coverage(
            "Proto", graph=self.graph, test_gaps=[self.gap, self.tgap],
            local_validation_ids=["lv1"], trace_receipt_ids=["tr1"])
        self.assertEqual(self.summary.coverage_summary_id, s2.coverage_summary_id)

    def test_ordering_deterministic(self) -> None:
        s2 = C.correlate_local_validation_coverage(
            "Proto", graph=self.graph, test_gaps=[self.tgap, self.gap],
            local_validation_ids=["lv1"], trace_receipt_ids=["tr1"])
        self.assertEqual([l.coverage_id for l in self.summary.coverage_links],
                         [l.coverage_id for l in s2.coverage_links])


class ApplyToTestGapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gap = _tested_gap("function:w", "lv1")
        self.summary = C.correlate_local_validation_coverage("P", test_gaps=[self.gap], local_validation_ids=["lv1"])
        self.tgap = _trace_gap("function:x", "tr1")
        self.tsummary = C.correlate_local_validation_coverage("P", test_gaps=[self.tgap], trace_receipt_ids=["tr1"])

    def test_apply_returns_copy(self) -> None:
        self.assertIsNot(C.apply_coverage_to_test_gap(self.gap, self.summary.coverage_links), self.gap)

    def test_apply_tested_sets_locally_tested(self) -> None:
        self.assertEqual(C.apply_coverage_to_test_gap(self.gap, self.summary.coverage_links).gap_status,
                         TG.TEST_GAP_LOCALLY_TESTED)

    def test_apply_trace_sets_trace_bound(self) -> None:
        self.assertEqual(C.apply_coverage_to_test_gap(self.tgap, self.tsummary.coverage_links).gap_status,
                         TG.TEST_GAP_TRACE_BOUND)

    def test_apply_adds_local_validation_ids(self) -> None:
        self.assertIn("lv1", C.apply_coverage_to_test_gap(self.gap, self.summary.coverage_links).linked_local_validation_ids)

    def test_apply_adds_trace_receipt_ids(self) -> None:
        self.assertIn("tr1", C.apply_coverage_to_test_gap(self.tgap, self.tsummary.coverage_links).linked_trace_receipt_ids)

    def test_apply_adds_coverage_notes(self) -> None:
        self.assertTrue(C.apply_coverage_to_test_gap(self.gap, self.summary.coverage_links).coverage_notes)

    def test_apply_no_mutation(self) -> None:
        before = self.gap.gap_status
        C.apply_coverage_to_test_gap(self.gap, self.summary.coverage_links)
        self.assertEqual(self.gap.gap_status, before)

    def test_apply_keeps_manual_review(self) -> None:
        self.assertTrue(C.apply_coverage_to_test_gap(self.gap, self.summary.coverage_links).manual_review_required)

    def test_apply_keeps_ready_false(self) -> None:
        self.assertFalse(C.apply_coverage_to_test_gap(self.gap, self.summary.coverage_links).ready_for_submission)

    def test_gap_not_marked_resolved(self) -> None:
        applied = C.apply_coverage_to_test_gap(self.gap, self.summary.coverage_links)
        self.assertNotIn(applied.gap_status, ("RESOLVED", "SAFE", "TEST_GAP_RESOLVED"))

    def test_no_safety_or_vulnerability_claim(self) -> None:
        blob = json.dumps(TG.test_gap_to_dict(C.apply_coverage_to_test_gap(self.gap, self.summary.coverage_links))).lower()
        self.assertNotIn("proves safety", blob)
        self.assertNotIn("proves a vulnerability", blob)


class DedupValidationTests(unittest.TestCase):
    def test_deduplicate_deterministic(self) -> None:
        summary = C.correlate_local_validation_coverage("P", test_gaps=[_tested_gap()], local_validation_ids=["lv1"])
        a, _ = C.deduplicate_coverage_links(summary.coverage_links)
        b, _ = C.deduplicate_coverage_links(summary.coverage_links)
        self.assertEqual([l.coverage_id for l in a], [l.coverage_id for l in b])

    def test_duplicate_coverage_check(self) -> None:
        summary = C.correlate_local_validation_coverage("P", test_gaps=[_tested_gap()], local_validation_ids=["lv1"])
        _, checks = C.deduplicate_coverage_links(summary.coverage_links + summary.coverage_links)
        self.assertIn(C.COVERAGE_CHECK_DUPLICATE_COVERAGE_ID, {c.check_kind for c in checks})

    def test_validate_unknown_support_level(self) -> None:
        s = C.LocalValidationCoverageSummary(coverage_links=[
            C.LocalValidationCoverageLink(coverage_id="x", target_test_gap_id="g", support_level="WEIRD")])
        self.assertIn(C.COVERAGE_CHECK_MISSING_EXPLICIT_LINK, {c.check_kind for c in C.validate_coverage_summary(s)})

    def test_validate_ready_for_submission_true(self) -> None:
        s = C.LocalValidationCoverageSummary(coverage_links=[
            C.LocalValidationCoverageLink(coverage_id="x", target_test_gap_id="g", ready_for_submission=True)])
        self.assertIn(C.COVERAGE_CHECK_READY_FOR_SUBMISSION_TRUE, {c.check_kind for c in C.validate_coverage_summary(s)})

    def test_validate_forbidden_finality_wording(self) -> None:
        s = C.LocalValidationCoverageSummary(coverage_links=[
            C.LocalValidationCoverageLink(coverage_id="x", target_test_gap_id="g",
                                          relationship="confirmed vulnerability")])
        self.assertIn(C.COVERAGE_CHECK_FORBIDDEN_FINALITY_WORDING, {c.check_kind for c in C.validate_coverage_summary(s)})

    def test_validate_human_reviewed_token(self) -> None:
        s = C.LocalValidationCoverageSummary(coverage_links=[
            C.LocalValidationCoverageLink(coverage_id="x", target_test_gap_id="g", evidence_support="HUMAN_REVIEWED")])
        self.assertIn(C.COVERAGE_CHECK_FORBIDDEN_FINALITY_WORDING, {c.check_kind for c in C.validate_coverage_summary(s)})

    def test_validate_missing_target(self) -> None:
        s = C.LocalValidationCoverageSummary(coverage_links=[
            C.LocalValidationCoverageLink(coverage_id="x", source_local_validation_id="lv1")])
        self.assertIn(C.COVERAGE_CHECK_MISSING_EXPLICIT_LINK, {c.check_kind for c in C.validate_coverage_summary(s)})


class SerializationNoOverclaimTests(unittest.TestCase):
    def setUp(self) -> None:
        self.summary = C.correlate_local_validation_coverage(
            "P", test_gaps=[_tested_gap("function:w", "lv1")], local_validation_ids=["lv1"])

    def test_to_dict_json_serializable(self) -> None:
        data = C.coverage_to_dict(self.summary)
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_to_dict_no_mutation(self) -> None:
        before = self.summary.coverage_count
        C.coverage_to_dict(self.summary)
        self.assertEqual(self.summary.coverage_count, before)

    def test_to_dict_unsupported_raises(self) -> None:
        with self.assertRaises(TypeError):
            C.coverage_to_dict(object())

    def test_output_no_overclaim(self) -> None:
        blob = json.dumps(C.coverage_to_dict(self.summary)).lower()
        for token in ("human_reviewed", "confirmed vulnerability", "final severity", "audit passed",
                      "bounty", "verified safe", "proves safety", "proves a vulnerability",
                      "ready_for_submission\": true"):
            self.assertNotIn(token, blob)

    def test_no_overclaim_tokens_in_taxonomy(self) -> None:
        forbidden = {"SAFE", "VERIFIED_SAFE", "CONFIRMED_VULNERABILITY", "AUDIT_PASSED",
                     "FINAL_SEVERITY", "HUMAN_REVIEWED", "BOUNTY"}
        self.assertFalse(forbidden & set(C.COVERAGE_SUPPORT_LEVELS))
        self.assertFalse(forbidden & set(C.COVERAGE_CHECK_KINDS))

    def test_taxonomy_counts(self) -> None:
        self.assertEqual(len(C.COVERAGE_SUPPORT_LEVELS), 7)
        self.assertEqual(len(C.COVERAGE_CHECK_KINDS), 11)


class ImportAndExportTests(unittest.TestCase):
    def test_import_has_no_filesystem_side_effects(self) -> None:
        import importlib
        import arkheionx.intelligence.coverage as mod
        importlib.reload(mod)
        self.assertTrue(hasattr(mod, "correlate_local_validation_coverage"))

    def test_package_exports_coverage(self) -> None:
        import arkheionx.intelligence as intel
        self.assertTrue(hasattr(intel, "coverage"))
        self.assertTrue(hasattr(intel, "LocalValidationCoverageSummary"))
        self.assertTrue(hasattr(intel, "correlate_local_validation_coverage"))
        self.assertIn("LocalValidationCoverageSummary", intel.__all__)


if __name__ == "__main__":
    unittest.main()
