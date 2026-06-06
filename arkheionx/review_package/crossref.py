"""Package-level cross-reference validation (v3.6, additive, internal-only).

Resolves IDs referenced by packaged artifacts (function/contract/value-path/
assumption/test-gap/proof-suggestion/receipt/evidence/report/evidence-link IDs,
plus legacy target aliases) against an included ProtocolModel sidecar -- by
exact ID match or an explicit alias only. No fuzzy or substring matching, and no
invented links: an unresolved or missing reference is a warning, never a
fabricated edge. A missing protocol model is a warning, not an error. Checks are
deterministic, mutate nothing, write nothing, and never echo raw artifact
contents or absolute paths.
"""
from __future__ import annotations

import json
from pathlib import Path

from .model import ReviewPackageManifest

PASS, WARN, FAIL, SKIP = "PASS", "WARN", "FAIL", "SKIP"
INFO, WARNING, ERROR = "info", "warning", "error"

# Reference key (as found in artifact JSON) -> protocol-model ID class.
_REF_KEY_TO_CLASS = {
    "function_id": "function", "target_function_id": "function",
    "entry_function_id": "function", "exit_function_id": "function",
    "linked_target_function_id": "function",
    "contract_id": "contract", "value_path_id": "value_path",
    "assumption_id": "assumption", "test_gap_id": "test_gap",
    "proof_suggestion_id": "proof_suggestion", "proof_receipt_id": "proof_receipt",
    "trace_receipt_id": "trace_receipt", "evidence_package_id": "evidence_package",
    "report_id": "report", "evidence_link_id": "evidence_link",
    "review_map_target": "alias", "target_id": "alias",
    # local-validation linked ID lists (Agent 7, v3.7) -> resolved by exact match.
    "linked_function_ids": "function", "linked_value_path_ids": "value_path",
    "linked_assumption_ids": "assumption", "linked_test_gap_ids": "test_gap",
}
_REF_KEYS = frozenset(_REF_KEY_TO_CLASS)


def _check(name, status, severity, message, path="", kind=""):
    return {"name": name, "status": status, "severity": severity, "message": message,
            "artifact_id": "", "path": path, "kind": kind}


def load_json_artifact(path: str | Path) -> dict | None:
    try:
        data = json.loads(Path(str(path)).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _ids_from(model: dict, section: str, key: str) -> set:
    return {str(n.get(key, "")) for n in model.get(section, []) if isinstance(n, dict) and n.get(key)}


def extract_protocol_model_ids(protocol_model: dict) -> dict[str, set]:
    classes = {
        "protocol": {str(protocol_model.get("protocol_id", ""))} - {""},
        "contract": _ids_from(protocol_model, "contracts", "contract_id"),
        "function": _ids_from(protocol_model, "functions", "function_id"),
        "value_path": _ids_from(protocol_model, "value_paths", "value_path_id"),
        "assumption": _ids_from(protocol_model, "assumptions", "assumption_id"),
        "test_gap": _ids_from(protocol_model, "test_gaps", "test_gap_id"),
        "proof_suggestion": _ids_from(protocol_model, "proof_suggestions", "proof_suggestion_id"),
        "proof_receipt": _ids_from(protocol_model, "proof_receipts", "proof_receipt_id"),
        "trace_receipt": _ids_from(protocol_model, "trace_receipts", "trace_receipt_id"),
        "evidence_package": _ids_from(protocol_model, "evidence_packages", "evidence_package_id"),
        "report": _ids_from(protocol_model, "report_drafts", "report_id"),
        "evidence_link": _ids_from(protocol_model, "evidence_links", "evidence_link_id"),
    }
    # Evidence-link nodes carry exact receipt/package/report IDs even when the
    # model (built from review-map only) has no separate receipt nodes.
    for link in protocol_model.get("evidence_links", []):
        if not isinstance(link, dict):
            continue
        for field, cls in (("proof_receipt_id", "proof_receipt"), ("trace_receipt_id", "trace_receipt"),
                           ("evidence_package_id", "evidence_package"), ("report_id", "report")):
            value = str(link.get(field, "") or "")
            if value:
                classes[cls].add(value)
    aliases: set = set()
    for section in ("contracts", "functions", "value_paths", "assumptions", "test_gaps",
                    "proof_suggestions", "proof_receipts", "trace_receipts", "evidence_packages",
                    "report_drafts", "evidence_links"):
        for node in protocol_model.get(section, []):
            if isinstance(node, dict):
                for value in (node.get("aliases", {}) or {}).values():
                    if isinstance(value, str) and value:
                        aliases.add(value)
    classes["alias"] = aliases
    return classes


def extract_artifact_references(artifact_payload: dict, kind: str = "") -> dict[str, set]:
    refs: dict[str, set] = {}

    def walk(obj: object) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in _REF_KEYS:
                    if isinstance(value, str) and value.strip():
                        refs.setdefault(key, set()).add(value.strip())
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and item.strip():
                                refs.setdefault(key, set()).add(item.strip())
                walk(value)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                walk(item)

    walk(artifact_payload)
    return refs


def _artifact_path(artifact, repo_path, package_root):
    if package_root is not None:
        copied = Path(str(package_root)) / "artifacts" / artifact.relative_path
        if copied.is_file():
            return copied
    if artifact.path:
        source = Path(str(repo_path)) / artifact.path
        if source.is_file():
            return source
    return None


def collect_package_cross_references(manifest: ReviewPackageManifest, repo_path, package_root=None) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for artifact in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        if artifact.kind == "protocol_model":
            continue
        path = _artifact_path(artifact, repo_path, package_root)
        if path is None or path.suffix.lower() != ".json":
            continue
        payload = load_json_artifact(path)
        if payload is None:
            continue
        for ref_key, values in extract_artifact_references(payload, artifact.kind).items():
            cls = _REF_KEY_TO_CLASS[ref_key]
            for value in values:
                out.setdefault(cls, {}).setdefault(value, artifact.relative_path)
    return out


def validate_package_cross_references(manifest, repo_path, package_root=None, protocol_model=None) -> list[dict]:
    if not protocol_model:
        return [_check("crossref.protocol_model.present", WARN, WARNING,
                       "no protocol model included; cross-reference checks skipped")]
    checks = [_check("crossref.protocol_model.present", PASS, INFO, "protocol model included")]
    model_ids = extract_protocol_model_ids(protocol_model)
    for artifact in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        if artifact.kind == "protocol_model":
            continue
        path = _artifact_path(artifact, repo_path, package_root)
        if path is not None and path.suffix.lower() == ".json" and load_json_artifact(path) is None:
            checks.append(_check("crossref.artifact.malformed", WARN, WARNING,
                                 "artifact JSON could not be parsed", path=artifact.relative_path, kind=artifact.kind))
    references = collect_package_cross_references(manifest, repo_path, package_root)
    for cls in sorted(references):
        for value in sorted(references[cls]):
            relpath = references[cls][value]
            resolved = value in model_ids.get(cls, set()) or value in model_ids.get("alias", set())
            checks.append(_check(
                f"crossref.{cls}", PASS if resolved else WARN, INFO if resolved else WARNING,
                f"{cls} reference {'resolved' if resolved else 'unresolved'}: {value}",
                path=relpath, kind=cls,
            ))
    return checks


# --- Protocol intelligence graph cross-references (Agent 9, v3.8) ------------

# Graph artifact kinds that carry resolvable references.
_GRAPH_ARTIFACT_KINDS = frozenset({
    "protocol_graph", "protocol_graph_node", "protocol_graph_edge",
    "protocol_graph_check", "protocol_graph_coverage_summary",
    "protocol_graph_artifacts_index",
})
# Local-validation artifact kinds whose IDs graph artifacts may reference.
_LV_ARTIFACT_KINDS = frozenset({
    "local_validation_summary", "local_validation_run", "local_test_result",
    "local_trace_receipt", "local_validation_artifacts_index",
})
# Local-validation definition keys -> class (used to index resolvable LV IDs).
_LV_DEFINITION_KEYS = {
    "test_result_id": "local_validation", "summary_id": "local_validation",
    "run_id": "local_validation", "test_result_ids": "local_validation",
    "run_ids": "local_validation", "trace_receipt_id": "trace_receipt",
    "trace_receipt_ids": "trace_receipt",
}
# Graph reference key (as found in artifact JSON) -> resolution class. Graph
# internal classes resolve against the packaged graph artifacts; model classes
# resolve against an included protocol model; local-validation classes resolve
# against included local-validation artifacts; ``any`` resolves against the union
# (used for polymorphic source_id/target_id entity references).
_GRAPH_REF_KEY_TO_CLASS = {
    "node_id": "node", "source_node_id": "node", "target_node_id": "node",
    "edge_id": "edge", "check_id": "check", "graph_id": "graph",
    "coverage_id": "coverage", "coverage_summary_id": "coverage",
    "function_id": "function", "target_function_id": "function",
    "linked_function_ids": "function",
    "value_path_id": "value_path", "target_value_path_id": "value_path",
    "linked_value_path_ids": "value_path",
    "assumption_id": "assumption", "target_assumption_id": "assumption",
    "linked_assumption_ids": "assumption",
    "test_gap_id": "test_gap", "target_test_gap_id": "test_gap",
    "linked_test_gap_ids": "test_gap",
    "linked_local_validation_ids": "local_validation",
    "source_local_validation_id": "local_validation",
    "linked_trace_receipt_ids": "trace_receipt",
    "source_trace_receipt_id": "trace_receipt",
    "source_id": "any", "target_id": "any",
}
_GRAPH_REF_KEYS = frozenset(_GRAPH_REF_KEY_TO_CLASS)


def _index_graph_definitions(payload: object, index: dict[str, set]) -> None:
    """Collect defined graph IDs (node/edge/check/graph/coverage) from a payload."""

    if isinstance(payload, dict):
        nid = payload.get("node_id")
        if payload.get("node_kind") and isinstance(nid, str) and nid:
            index["node"].add(nid)
            sid = payload.get("source_id")
            if isinstance(sid, str) and sid:
                index["node_source"].add(sid)
        eid = payload.get("edge_id")
        if payload.get("edge_kind") and isinstance(eid, str) and eid:
            index["edge"].add(eid)
        cid = payload.get("check_id")
        if payload.get("check_kind") and isinstance(cid, str) and cid:
            index["check"].add(cid)
        gid = payload.get("graph_id")
        if isinstance(gid, str) and gid and ("nodes" in payload or "protocol_name" in payload):
            index["graph"].add(gid)
        covid = payload.get("coverage_id")
        if isinstance(covid, str) and covid and "support_level" in payload:
            index["coverage"].add(covid)
        csid = payload.get("coverage_summary_id")
        if isinstance(csid, str) and csid:
            index["coverage"].add(csid)
        for value in payload.values():
            _index_graph_definitions(value, index)
    elif isinstance(payload, (list, tuple)):
        for item in payload:
            _index_graph_definitions(item, index)


def _index_lv_definitions(payload: object, index: dict[str, set]) -> None:
    """Collect resolvable local-validation / trace-receipt IDs from a payload."""

    if isinstance(payload, dict):
        for key, value in payload.items():
            cls = _LV_DEFINITION_KEYS.get(key)
            if cls:
                if isinstance(value, str) and value.strip():
                    index[cls].add(value.strip())
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and item.strip():
                            index[cls].add(item.strip())
            _index_lv_definitions(value, index)
    elif isinstance(payload, (list, tuple)):
        for item in payload:
            _index_lv_definitions(item, index)


def extract_graph_references(artifact_payload: dict) -> dict[str, set]:
    """Extract graph reference values per key (exact strings only, no matching)."""

    refs: dict[str, set] = {}

    def walk(obj: object) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in _GRAPH_REF_KEYS:
                    if isinstance(value, str) and value.strip():
                        refs.setdefault(key, set()).add(value.strip())
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and item.strip():
                                refs.setdefault(key, set()).add(item.strip())
                walk(value)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                walk(item)

    walk(artifact_payload)
    return refs


def collect_protocol_graph_indexes(manifest, repo_path, package_root=None) -> dict[str, dict[str, set]]:
    """Build the internal-graph and local-validation ID indexes from packaged JSON."""

    internal = {"node": set(), "node_source": set(), "edge": set(),
                "check": set(), "graph": set(), "coverage": set()}
    lv_index = {"local_validation": set(), "trace_receipt": set()}
    for artifact in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        path = _artifact_path(artifact, repo_path, package_root)
        if path is None or path.suffix.lower() != ".json":
            continue
        if artifact.kind in _GRAPH_ARTIFACT_KINDS:
            payload = load_json_artifact(path)
            if payload is not None:
                _index_graph_definitions(payload, internal)
        elif artifact.kind in _LV_ARTIFACT_KINDS:
            payload = load_json_artifact(path)
            if payload is not None:
                _index_lv_definitions(payload, lv_index)
    return {"internal": internal, "local_validation": lv_index}


def validate_protocol_graph_cross_references(manifest, repo_path, package_root=None, protocol_model=None) -> list[dict]:
    """Cross-reference protocol-graph artifact IDs by exact ID / explicit alias only.

    Graph-internal IDs (node/edge/check/graph/coverage) resolve against the packaged
    graph artifacts themselves; function/value-path/assumption/test-gap IDs resolve
    against an included protocol model when present; local-validation and
    trace-receipt IDs resolve against included local-validation artifacts. Matching
    is exact only: there is no fuzzy or substring matching and no invented link. An
    unresolved reference is a warning, never a failure, and a missing protocol model
    is a warning, not an error. Returns no checks when no protocol-graph artifacts
    are present. Deterministic, read-only, and mutates nothing.
    """

    graph_arts = [a for a in manifest.included_artifacts if a.kind in _GRAPH_ARTIFACT_KINDS]
    if not graph_arts:
        return []
    checks = [_check("crossref.protocol_graph.present", PASS, INFO, "protocol graph artifacts included")]

    indexes = collect_protocol_graph_indexes(manifest, repo_path, package_root)
    internal = indexes["internal"]
    lv_index = indexes["local_validation"]
    if protocol_model:
        model_ids = extract_protocol_model_ids(protocol_model)
    else:
        model_ids = {}
        checks.append(_check("crossref.protocol_graph.protocol_model.present", WARN, WARNING,
                             "no protocol model included; graph model references resolved as unresolved"))

    any_ids: set = set()
    for bucket in (internal, lv_index):
        for value_set in bucket.values():
            any_ids |= value_set
    for value_set in model_ids.values():
        any_ids |= set(value_set)

    def resolve(cls: str, value: str) -> bool:
        if cls == "any":
            return value in any_ids
        if cls == "node":
            return value in internal["node"] or value in internal["node_source"]
        if cls in ("edge", "check", "graph", "coverage"):
            return value in internal[cls]
        if cls == "local_validation":
            return value in lv_index["local_validation"]
        if cls == "trace_receipt":
            return value in lv_index["trace_receipt"] or value in model_ids.get("trace_receipt", set())
        return value in model_ids.get(cls, set()) or value in model_ids.get("alias", set())

    references: dict[str, dict[str, str]] = {}
    for artifact in sorted(graph_arts, key=lambda a: a.relative_path):
        path = _artifact_path(artifact, repo_path, package_root)
        if path is None or path.suffix.lower() != ".json":
            continue
        payload = load_json_artifact(path)
        if payload is None:
            checks.append(_check("crossref.protocol_graph.malformed", WARN, WARNING,
                                 "protocol graph artifact JSON could not be parsed",
                                 path=artifact.relative_path, kind=artifact.kind))
            continue
        for ref_key, values in extract_graph_references(payload).items():
            cls = _GRAPH_REF_KEY_TO_CLASS[ref_key]
            for value in values:
                references.setdefault(cls, {}).setdefault(value, artifact.relative_path)

    for cls in sorted(references):
        for value in sorted(references[cls]):
            relpath = references[cls][value]
            resolved = resolve(cls, value)
            checks.append(_check(
                f"crossref.protocol_graph.{cls}", PASS if resolved else WARN, INFO if resolved else WARNING,
                f"graph {cls} reference {'resolved' if resolved else 'unresolved'}: {value}",
                path=relpath, kind=cls,
            ))
    return checks
