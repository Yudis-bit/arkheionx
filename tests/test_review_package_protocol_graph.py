"""Tests for review-package integration of protocol-graph artifacts (Agent 9, v3.8).

Protocol-graph artifacts are optional and never required for package readiness.
They are review context only: they never finalize a security conclusion, never
prove protocol safety, and a graph warning never proves a vulnerability. These
tests cover collection/classification, optional manifest kinds, deterministic
export inclusion, JSON / path / checksum / no-overclaim validation, and exact-ID
cross-referencing (internal graph IDs, protocol-model IDs, and local-validation
IDs) with unresolved references kept as warnings.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from arkheionx.review_package import builder, collector, crossref, validate
from arkheionx.review_package.checksums import checksum_manifest_artifacts, sha256_file
from arkheionx.review_package.manifest import build_review_package_manifest

REPO_ROOT = Path(__file__).resolve().parents[1]

_GRAPH_KINDS = {
    "protocol_graph", "protocol_graph_node", "protocol_graph_edge",
    "protocol_graph_check", "protocol_graph_coverage_summary",
    "protocol_graph_artifacts_index", "protocol_graph_checksums",
}

# A protocol model whose IDs the graph artifacts reference by exact ID.
_MODEL = {
    "protocol_id": "p",
    "contracts": [{"contract_id": "c", "aliases": {"name": "Vault"}}],
    "functions": [{"function_id": "function:dep", "aliases": {"display_name": "Vault.deposit"}}],
    "value_paths": [{"value_path_id": "value-path:vp1"}],
    "assumptions": [{"assumption_id": "assumption:a1"}],
    "test_gaps": [{"test_gap_id": "test-gap:g1"}],
}


def _graph_payloads() -> dict[str, dict]:
    """A coherent protocol-graph artifact set matching the serialized graph shape."""

    n1 = {"node_id": "protocol-graph-node:value-path:n1", "node_kind": "GRAPH_NODE_VALUE_PATH",
          "source_id": "value-path:vp1", "label": "Vault.deposit", "aliases": [],
          "linked_ids": ["function:dep"], "manual_review_required": True,
          "ready_for_submission": False, "metadata": {"function_id": "function:dep"}}
    n2 = {"node_id": "protocol-graph-node:assumption:n2", "node_kind": "GRAPH_NODE_ASSUMPTION",
          "source_id": "assumption:a1", "label": "collateral assumption",
          "manual_review_required": True, "ready_for_submission": False, "metadata": {}}
    n3 = {"node_id": "protocol-graph-node:test-gap:n3", "node_kind": "GRAPH_NODE_TEST_GAP",
          "source_id": "test-gap:g1", "label": "missing test",
          "manual_review_required": True, "ready_for_submission": False, "metadata": {}}
    n4 = {"node_id": "protocol-graph-node:local-validation:n4", "node_kind": "GRAPH_NODE_LOCAL_VALIDATION",
          "source_id": "local-test-result:t1", "label": "local-test-result:t1",
          "manual_review_required": True, "ready_for_submission": False, "metadata": {}}
    e1 = {"edge_id": "protocol-graph-edge:vp-asm:e1", "edge_kind": "GRAPH_EDGE_VALUE_PATH_TO_ASSUMPTION",
          "source_node_id": n1["node_id"], "target_node_id": n2["node_id"],
          "source_id": "value-path:vp1", "target_id": "assumption:a1",
          "manual_review_required": True, "ready_for_submission": False}
    c1 = {"check_id": "protocol-graph-check:orphan:c1", "check_kind": "GRAPH_CHECK_ORPHAN_NODE",
          "severity": "warning", "message": "orphan node (no incident edges)",
          "node_id": n3["node_id"], "edge_id": "", "source_id": "", "target_id": "",
          "manual_review_required": True, "ready_for_submission": False}
    graph = {"graph_id": "protocol-intelligence-graph:vault:g1", "protocol_name": "vault",
             "nodes": [n1, n2, n3, n4], "edges": [e1], "checks": [c1],
             "linked_function_ids": ["function:dep"], "linked_value_path_ids": ["value-path:vp1"],
             "linked_assumption_ids": ["assumption:a1"], "linked_test_gap_ids": ["test-gap:g1"],
             "linked_local_validation_ids": ["local-test-result:t1"],
             "linked_trace_receipt_ids": ["local-trace:tr1"],
             "manual_review_required": True, "ready_for_submission": False}
    cov = {"coverage_summary_id": "local-validation-coverage-summary:vault:s1", "protocol_name": "vault",
           "coverage_links": [{"coverage_id": "local-validation-coverage:cl1",
                               "support_level": "COVERAGE_TESTED",
                               "source_local_validation_id": "local-test-result:t1",
                               "target_test_gap_id": "test-gap:g1", "target_function_id": "function:dep"}],
           "linked_local_validation_ids": ["local-test-result:t1"],
           "linked_trace_receipt_ids": ["local-trace:tr1"],
           "manual_review_required": True, "ready_for_submission": False}
    idx = {"graph": "graph.json",
           "nodes": ["nodes/n1.json", "nodes/n2.json", "nodes/n3.json", "nodes/n4.json"],
           "edges": ["edges/e1.json"], "checks": ["checks/c1.json"]}
    return {"graph.json": graph, "nodes/n1.json": n1, "nodes/n2.json": n2,
            "nodes/n3.json": n3, "nodes/n4.json": n4, "edges/e1.json": e1,
            "checks/c1.json": c1, "coverage-summary.json": cov, "artifacts-index.json": idx}


def _write_review_map(repo: Path) -> None:
    out = repo / ".arkheionx" / "out"
    (out / "review-map").mkdir(parents=True, exist_ok=True)
    (out / "review-map" / "review-map.json").write_text(
        json.dumps({"schema_version": "1.0.0"}), encoding="utf-8")
    (out / "review-map" / "evidence-links.json").write_text("{}", encoding="utf-8")
    (out / "artifacts-index.json").write_text(json.dumps({"targets": []}), encoding="utf-8")


def _write_local_validation(repo: Path) -> None:
    d = repo / ".arkheionx" / "out" / "local-validation"
    d.mkdir(parents=True, exist_ok=True)
    (d / "summary.json").write_text(json.dumps({
        "summary_id": "local-validation-summary:s", "test_result_ids": ["local-test-result:t1"],
        "trace_receipt_ids": ["local-trace:tr1"], "manual_review_required": True,
        "ready_for_submission": False}), encoding="utf-8")


def _write_protocol_graph(repo: Path, payloads: dict | None = None, *, checksums: bool = True) -> Path:
    payloads = _graph_payloads() if payloads is None else payloads
    pg = repo / ".arkheionx" / "out" / "protocol-graph"
    for rel, payload in payloads.items():
        path = pg / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if checksums:
        lines = [f"{sha256_file(pg / rel)}  {rel}" for rel in sorted(payloads)]
        cp = pg / "checksums" / "SHA256SUMS"
        cp.parent.mkdir(parents=True, exist_ok=True)
        cp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return pg


class _RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _write_review_map(self.repo)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _graph_json(self) -> Path:
        return self.repo / ".arkheionx" / "out" / "protocol-graph" / "graph.json"

    def _manifest(self):
        return checksum_manifest_artifacts(build_review_package_manifest(str(self.repo)), str(self.repo))

    def _validate(self, model=_MODEL):
        return validate.validate_review_package_manifest(self._manifest(), str(self.repo), protocol_model=model)

    def _kinds(self) -> set[str]:
        return {a.kind for a in collector.collect_review_package_artifacts(str(self.repo))}

    def _kind_by_relpath(self) -> dict[str, str]:
        return {a.relative_path: a.kind for a in collector.collect_review_package_artifacts(str(self.repo))}


# --- Collector (requirements 1-11) ------------------------------------------

class CollectorTests(_RepoCase):
    def test_missing_protocol_graph_folder_ignored(self) -> None:  # 1
        self.assertFalse(self._kinds() & _GRAPH_KINDS)

    def test_collector_discovers_graph_json(self) -> None:  # 2
        _write_protocol_graph(self.repo)
        self.assertEqual(self._kind_by_relpath()["protocol-graph/graph.json"], "protocol_graph")

    def test_collector_discovers_nodes(self) -> None:  # 3
        _write_protocol_graph(self.repo)
        self.assertEqual(self._kind_by_relpath()["protocol-graph/nodes/n1.json"], "protocol_graph_node")

    def test_collector_discovers_edges(self) -> None:  # 4
        _write_protocol_graph(self.repo)
        self.assertEqual(self._kind_by_relpath()["protocol-graph/edges/e1.json"], "protocol_graph_edge")

    def test_collector_discovers_checks(self) -> None:  # 5
        _write_protocol_graph(self.repo)
        self.assertEqual(self._kind_by_relpath()["protocol-graph/checks/c1.json"], "protocol_graph_check")

    def test_collector_discovers_coverage_summary(self) -> None:  # 6
        _write_protocol_graph(self.repo)
        self.assertEqual(self._kind_by_relpath()["protocol-graph/coverage-summary.json"],
                         "protocol_graph_coverage_summary")

    def test_collector_discovers_artifacts_index(self) -> None:  # 7
        _write_protocol_graph(self.repo)
        self.assertEqual(self._kind_by_relpath()["protocol-graph/artifacts-index.json"],
                         "protocol_graph_artifacts_index")

    def test_collector_discovers_checksums(self) -> None:  # 8
        _write_protocol_graph(self.repo)
        self.assertEqual(self._kind_by_relpath()["protocol-graph/checksums/SHA256SUMS"],
                         "protocol_graph_checksums")

    def test_graph_artifacts_index_not_global(self) -> None:  # 9
        _write_protocol_graph(self.repo)
        by_rel = self._kind_by_relpath()
        self.assertEqual(by_rel["protocol-graph/artifacts-index.json"], "protocol_graph_artifacts_index")
        self.assertEqual(by_rel["artifacts-index.json"], "artifacts_index")  # global one unaffected

    def test_graph_kinds_optional(self) -> None:  # 10
        _write_protocol_graph(self.repo)
        graph_arts = [a for a in collector.collect_review_package_artifacts(str(self.repo))
                      if a.kind in _GRAPH_KINDS]
        self.assertTrue(graph_arts)
        self.assertTrue(all(not a.required for a in graph_arts))
        self.assertTrue(all(collector.is_optional_artifact_kind(a.kind) for a in graph_arts))

    def test_required_kinds_unchanged(self) -> None:  # 11
        self.assertEqual(collector._REQUIRED_KINDS, {"review_map", "evidence_links", "artifacts_index"})


# --- Manifest (requirements 12-15) ------------------------------------------

class ManifestTests(_RepoCase):
    def test_manifest_includes_protocol_graph(self) -> None:  # 12
        _write_protocol_graph(self.repo)
        man = build_review_package_manifest(str(self.repo))
        self.assertTrue(_GRAPH_KINDS <= {a.kind for a in man.included_artifacts})
        self.assertTrue(_GRAPH_KINDS <= set(man.optional_artifacts))

    def test_package_id_changes_with_graph_set(self) -> None:  # 13
        without = build_review_package_manifest(str(self.repo)).package_id
        _write_protocol_graph(self.repo)
        with_graph = build_review_package_manifest(str(self.repo)).package_id
        self.assertNotEqual(without, with_graph)
        # Determinism: same set -> same id.
        self.assertEqual(with_graph, build_review_package_manifest(str(self.repo)).package_id)
        # A larger graph set changes the id again.
        (self.repo / ".arkheionx" / "out" / "protocol-graph" / "nodes" / "n5.json").write_text(
            json.dumps({"node_id": "protocol-graph-node:x:n5", "node_kind": "GRAPH_NODE_UNKNOWN",
                        "source_id": "x", "manual_review_required": True, "ready_for_submission": False}),
            encoding="utf-8")
        self.assertNotEqual(with_graph, build_review_package_manifest(str(self.repo)).package_id)

    def test_manifest_manual_review_required_true(self) -> None:  # 14
        _write_protocol_graph(self.repo)
        self.assertIs(build_review_package_manifest(str(self.repo)).manual_review_required, True)

    def test_manifest_ready_for_submission_false(self) -> None:  # 15
        _write_protocol_graph(self.repo)
        self.assertIs(build_review_package_manifest(str(self.repo)).ready_for_submission, False)


# --- Validation (requirements 16-33) ----------------------------------------

class ValidationTests(_RepoCase):
    def test_passes_when_protocol_graph_absent(self) -> None:  # 16
        res = self._validate()
        self.assertFalse([e for e in res.errors if "graph" in e.lower()])
        self.assertFalse(res.safety_failures)

    def test_valid_graph_parses_no_errors(self) -> None:  # 17
        _write_protocol_graph(self.repo)
        res = self._validate()
        self.assertFalse([e for e in res.errors if "graph" in e.lower()], res.errors)
        self.assertFalse(res.safety_failures)
        self.assertTrue(any(c["name"] == "protocol_graph.parseable" and c["status"] == "PASS"
                            for c in res.checks))

    def test_validation_accepts_builder_graph(self) -> None:  # 17 (realistic, shape-drift guard)
        from arkheionx.intelligence.graph import build_protocol_intelligence_graph, graph_to_dict
        graph = build_protocol_intelligence_graph(
            "vault", local_validation_ids=["local-test-result:t1"], trace_receipt_ids=["local-trace:tr1"])
        _write_protocol_graph(self.repo, {"graph.json": graph_to_dict(graph)})
        res = self._validate()
        self.assertFalse([e for e in res.errors if "graph" in e.lower()], res.errors)
        self.assertFalse(res.safety_failures)

    def _tamper(self, rel: str, transform) -> None:
        _write_protocol_graph(self.repo)
        path = self.repo / ".arkheionx" / "out" / "protocol-graph" / rel
        path.write_text(transform(path.read_text(encoding="utf-8")), encoding="utf-8")

    def test_malformed_graph_json_errors(self) -> None:  # 18
        self._tamper("graph.json", lambda _t: "{not valid json")
        self.assertTrue(any("malformed" in e.lower() for e in self._validate().errors))

    def test_malformed_node_json_errors(self) -> None:  # 19
        self._tamper("nodes/n1.json", lambda _t: "{nope")
        self.assertTrue(any("malformed" in e.lower() for e in self._validate().errors))

    def test_malformed_edge_json_errors(self) -> None:  # 20
        self._tamper("edges/e1.json", lambda _t: "{nope")
        self.assertTrue(any("malformed" in e.lower() for e in self._validate().errors))

    def test_malformed_check_json_errors(self) -> None:  # 21
        self._tamper("checks/c1.json", lambda _t: "{nope")
        self.assertTrue(any("malformed" in e.lower() for e in self._validate().errors))

    def test_malformed_coverage_summary_json_errors(self) -> None:  # 22
        self._tamper("coverage-summary.json", lambda _t: "{nope")
        self.assertTrue(any("malformed" in e.lower() for e in self._validate().errors))

    def test_checksum_mismatch_errors(self) -> None:  # 23
        _write_protocol_graph(self.repo)
        cp = self.repo / ".arkheionx" / "out" / "protocol-graph" / "checksums" / "SHA256SUMS"
        cp.write_text(("a" * 64) + "  graph.json\n", encoding="utf-8")
        res = self._validate()
        self.assertTrue(any("checksum" in e.lower() for e in res.errors), res.errors)
        self.assertEqual(res.status, "PACKAGE_INVALID")

    def test_absolute_path_in_content_errors(self) -> None:  # 24
        self._tamper("graph.json", lambda t: _inject(t, "leak", "/etc/passwd"))
        res = self._validate()
        self.assertTrue(any("absolute" in e.lower() for e in res.errors), res.errors)
        self.assertTrue(all("/etc/passwd" not in e for e in res.errors))  # value not echoed

    def test_path_traversal_in_content_errors(self) -> None:  # 25
        self._tamper("graph.json", lambda t: _inject(t, "leak", "../../etc/passwd"))
        self.assertTrue(any("traversal" in e.lower() for e in self._validate().errors))

    def test_backslash_in_content_errors(self) -> None:  # 25 (companion)
        self._tamper("graph.json", lambda t: _inject(t, "leak", "a\\\\b"))
        self.assertTrue(any("backslash" in e.lower() for e in self._validate().errors))

    def test_ready_for_submission_true_errors(self) -> None:  # 26
        self._tamper("graph.json", lambda t: t.replace(
            '"ready_for_submission": false', '"ready_for_submission": true', 1))
        res = self._validate()
        self.assertTrue(res.safety_failures)
        self.assertEqual(res.status, "PACKAGE_INVALID")

    def test_human_reviewed_errors(self) -> None:  # 27
        self._tamper("graph.json", lambda t: _inject(t, "state", "status HUMAN_REVIEWED"))
        self.assertTrue(self._validate().safety_failures)

    def test_overclaim_wording_errors(self) -> None:  # 28-31
        for snippet in ("confirmed vulnerability", "Final severity: High",
                        "audit passed", "bounty eligible"):
            with self.subTest(snippet=snippet):
                self._tamper("graph.json", lambda t, s=snippet: _inject(t, "note", s))
                res = self._validate()
                self.assertTrue(res.safety_failures, snippet)
                self.assertEqual(res.status, "PACKAGE_INVALID")

    def test_graph_proves_safety_wording_errors(self) -> None:  # 32
        self._tamper("graph.json", lambda t: _inject(t, "note", "this graph proves safety"))
        self.assertTrue(self._validate().safety_failures)

    def test_warning_proves_vulnerability_wording_errors(self) -> None:  # 33
        self._tamper("graph.json", lambda t: _inject(t, "note", "graph warning proves vulnerability"))
        self.assertTrue(self._validate().safety_failures)


# --- Cross-reference (requirements 34-45) -----------------------------------

class CrossrefTests(_RepoCase):
    def _graph_checks(self, model=_MODEL):
        return [c for c in self._validate(model).checks if c["name"].startswith("crossref.protocol_graph")]

    def test_internal_node_ids_resolve(self) -> None:  # 34
        _write_protocol_graph(self.repo)
        node = [c for c in self._graph_checks() if c["name"] == "crossref.protocol_graph.node"]
        self.assertTrue(node)
        self.assertTrue(all(c["status"] == "PASS" for c in node), [c["message"] for c in node])

    def test_internal_edge_ids_resolve(self) -> None:  # 35
        _write_protocol_graph(self.repo)
        edge = [c for c in self._graph_checks() if c["name"] == "crossref.protocol_graph.edge"]
        self.assertTrue(edge)
        self.assertTrue(all(c["status"] == "PASS" for c in edge))

    def test_function_ids_resolve_against_model(self) -> None:  # 36
        _write_protocol_graph(self.repo)
        fn = [c for c in self._graph_checks() if c["name"] == "crossref.protocol_graph.function"]
        self.assertTrue(any(c["status"] == "PASS" and "function:dep" in c["message"] for c in fn))

    def test_value_path_ids_resolve_against_model(self) -> None:  # 37
        _write_protocol_graph(self.repo)
        vp = [c for c in self._graph_checks() if c["name"] == "crossref.protocol_graph.value_path"]
        self.assertTrue(any(c["status"] == "PASS" and "value-path:vp1" in c["message"] for c in vp))

    def test_assumption_ids_resolve_against_model(self) -> None:  # 38
        _write_protocol_graph(self.repo)
        asm = [c for c in self._graph_checks() if c["name"] == "crossref.protocol_graph.assumption"]
        self.assertTrue(any(c["status"] == "PASS" and "assumption:a1" in c["message"] for c in asm))

    def test_test_gap_ids_resolve_against_model(self) -> None:  # 39
        _write_protocol_graph(self.repo)
        gap = [c for c in self._graph_checks() if c["name"] == "crossref.protocol_graph.test_gap"]
        self.assertTrue(any(c["status"] == "PASS" and "test-gap:g1" in c["message"] for c in gap))

    def test_local_validation_ids_resolve_when_present(self) -> None:  # 40
        _write_protocol_graph(self.repo)
        _write_local_validation(self.repo)
        lv = [c for c in self._graph_checks() if c["name"] == "crossref.protocol_graph.local_validation"]
        self.assertTrue(lv)
        self.assertTrue(any(c["status"] == "PASS" and "local-test-result:t1" in c["message"] for c in lv))

    def test_unresolved_graph_refs_warn_not_error(self) -> None:  # 41
        payloads = _graph_payloads()
        payloads["edges/e1.json"]["source_node_id"] = "protocol-graph-node:does-not-exist"
        payloads["graph.json"]["edges"][0]["source_node_id"] = "protocol-graph-node:does-not-exist"
        _write_protocol_graph(self.repo, payloads)
        res = self._validate()
        warns = [c for c in res.checks if c["name"].startswith("crossref.protocol_graph")
                 and c["status"] == "WARN"]
        self.assertTrue(warns)
        self.assertFalse([e for e in res.errors if "crossref" in e.lower()])

    def test_missing_protocol_model_warns_not_error(self) -> None:  # 42
        _write_protocol_graph(self.repo)
        res = self._validate(model=None)
        self.assertTrue(any(c["name"] == "crossref.protocol_graph.protocol_model.present"
                            and c["status"] == "WARN" for c in res.checks))
        self.assertFalse([e for e in res.errors if "graph" in e.lower()])

    def test_no_fuzzy_match(self) -> None:  # 43
        _write_protocol_graph(self.repo)
        near = copy.deepcopy(_MODEL)
        near["functions"] = [{"function_id": "function:deposit_v2", "aliases": {}}]  # similar, not equal
        fn = [c for c in self._graph_checks(model=near) if c["name"] == "crossref.protocol_graph.function"]
        self.assertTrue(fn)
        self.assertTrue(any(c["status"] == "WARN" and "function:dep" in c["message"] for c in fn))

    def test_no_substring_match(self) -> None:  # 44
        _write_protocol_graph(self.repo)
        near = copy.deepcopy(_MODEL)
        near["functions"] = [{"function_id": "function:de", "aliases": {}}]  # substring of function:dep
        fn = [c for c in self._graph_checks(model=near) if c["name"] == "crossref.protocol_graph.function"]
        self.assertTrue(any(c["status"] == "WARN" and "function:dep" in c["message"] for c in fn))

    def test_no_invented_links(self) -> None:  # 45
        _write_protocol_graph(self.repo)
        empty = {"protocol_id": "p", "contracts": [], "functions": [],
                 "value_paths": [], "assumptions": [], "test_gaps": []}
        checks = self._graph_checks(model=empty)
        # No local-validation artifacts and an empty model: model/lv refs are all
        # unresolved (warnings), and there are no fabricated PASS resolutions.
        for cls in ("function", "value_path", "assumption", "test_gap", "local_validation"):
            for c in [c for c in checks if c["name"] == f"crossref.protocol_graph.{cls}"]:
                self.assertEqual(c["status"], "WARN", c["message"])

    def test_extract_graph_references_exact_strings(self) -> None:  # 43/44 unit
        refs = crossref.extract_graph_references(
            {"edge": {"source_node_id": "n:1", "linked_function_ids": ["function:a", "function:b"]}})
        self.assertEqual(refs["source_node_id"], {"n:1"})
        self.assertEqual(refs["linked_function_ids"], {"function:a", "function:b"})

    def test_crossref_deterministic_and_no_mutation(self) -> None:
        _write_protocol_graph(self.repo)
        man = self._manifest()
        before = json.dumps(__import__("arkheionx.review_package", fromlist=["manifest_to_dict"])
                            .manifest_to_dict(man))
        a = crossref.validate_protocol_graph_cross_references(man, str(self.repo), None, _MODEL)
        b = crossref.validate_protocol_graph_cross_references(man, str(self.repo), None, _MODEL)
        self.assertEqual(a, b)
        self.assertEqual(json.dumps(__import__("arkheionx.review_package", fromlist=["manifest_to_dict"])
                                    .manifest_to_dict(man)), before)


# --- Export (requirements 46-47) --------------------------------------------

class ExportTests(_RepoCase):
    def test_export_includes_protocol_graph(self) -> None:  # 46
        _write_protocol_graph(self.repo)
        result = builder.build_review_package(str(self.repo), export_format="zip")
        self.assertTrue(result.export_written, result.export_status)
        names = zipfile.ZipFile(self.repo / result.export_path).namelist()
        self.assertTrue(any(n.endswith("protocol-graph/graph.json") for n in names))
        self.assertTrue(any(n.endswith("protocol-graph/nodes/n1.json") for n in names))
        self.assertTrue(any(n.endswith("protocol-graph/checks/c1.json") for n in names))
        self.assertTrue(any(n.endswith("protocol-graph/checksums/SHA256SUMS") for n in names))
        for n in names:
            self.assertFalse(n.startswith("/"))
            self.assertNotIn("\\", n)
            self.assertNotIn("..", n.split("/"))

    def test_repeated_export_deterministic(self) -> None:  # 47
        _write_protocol_graph(self.repo)
        first = builder.build_review_package(str(self.repo), export_format="zip")
        second = builder.build_review_package(str(self.repo), export_format="zip")
        self.assertEqual(first.export_checksum_sha256, second.export_checksum_sha256)
        self.assertEqual(first.export_id, second.export_id)


# --- CLI artifact count (requirements 48-49) --------------------------------

class CliCountTests(_RepoCase):
    def _cli_artifact_count(self) -> int:
        env = dict(os.environ, ARKHEIONX_COLOR="never")
        result = subprocess.run(
            ["python3", "-m", "arkheionx.cli.main", "review-package", str(self.repo), "--json", "--no-write"],
            cwd=REPO_ROOT, text=True, capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["artifact_count"]

    def test_cli_artifact_count_increases_with_graph(self) -> None:  # 48
        before = self._cli_artifact_count()
        _write_protocol_graph(self.repo)
        self.assertGreater(self._cli_artifact_count(), before)

    def test_review_package_works_without_graph(self) -> None:  # 49
        result = builder.build_review_package(str(self.repo), no_write=True)
        self.assertIs(result.manual_review_required, True)
        self.assertIs(result.ready_for_submission, False)
        self.assertNotEqual(result.validation_status, "PACKAGE_INVALID")


# --- Output hygiene (requirement 50) ----------------------------------------

class OutputHygieneTests(_RepoCase):
    def test_no_absolute_paths_backslashes_or_overclaims(self) -> None:  # 50
        _write_protocol_graph(self.repo)
        _write_local_validation(self.repo)
        to_dict = __import__("arkheionx.review_package", fromlist=["to_dict"]).to_dict
        man = self._manifest()
        res = validate.validate_review_package_manifest(man, str(self.repo), protocol_model=_MODEL)
        blob = json.dumps(__import__("arkheionx.review_package", fromlist=["manifest_to_dict"])
                          .manifest_to_dict(man)) + json.dumps(to_dict(res))
        self.assertNotIn(str(self.repo), blob)  # no absolute repo path leaked
        self.assertNotIn("\\", blob)
        for term in ("confirmed vulnerability", "final severity", "audit passed",
                     "bounty eligible", "HUMAN_REVIEWED"):
            self.assertNotIn(term, blob)
        self.assertFalse(res.safety_failures)


def _inject(text: str, key: str, value: str) -> str:
    """Insert a string field into a top-level JSON object (after the opening brace)."""

    return text.replace("{", '{' + json.dumps(key) + ": " + json.dumps(value) + ", ", 1)


if __name__ == "__main__":
    unittest.main()
