"""Internal protocol intelligence graph builder (v3.8, additive).

This module composes the v3.8 intelligence layers -- function-role
classifications (Agent 2), value paths and segments (Agent 3), assumptions
(Agent 4), and test gaps (Agent 5) -- into a single deterministic protocol graph
of nodes and edges, plus a deterministic consistency check layer. It is internal
infrastructure: no filesystem, network, subprocess, CLI, or live-chain behavior,
and importing it has no side effects.

The graph is review surface only. Edges connect concepts by exact ID / explicit
alias only; there is no fuzzy or substring matching and no invented edge. A
missing target is an unresolved-reference warning, never a fabricated link. Graph
consistency never proves protocol safety and a graph warning never proves a
vulnerability. Every record keeps ``manual_review_required`` true and
``ready_for_submission`` false, and never emits a human-reviewed status.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, fields, is_dataclass

_HASH_LEN = 12

# --- Controlled graph node kinds --------------------------------------------

GRAPH_NODE_FUNCTION_ROLE = "GRAPH_NODE_FUNCTION_ROLE"
GRAPH_NODE_VALUE_PATH = "GRAPH_NODE_VALUE_PATH"
GRAPH_NODE_VALUE_PATH_SEGMENT = "GRAPH_NODE_VALUE_PATH_SEGMENT"
GRAPH_NODE_ASSUMPTION = "GRAPH_NODE_ASSUMPTION"
GRAPH_NODE_TEST_GAP = "GRAPH_NODE_TEST_GAP"
GRAPH_NODE_LOCAL_VALIDATION = "GRAPH_NODE_LOCAL_VALIDATION"
GRAPH_NODE_TRACE_RECEIPT = "GRAPH_NODE_TRACE_RECEIPT"
GRAPH_NODE_EVIDENCE_REF = "GRAPH_NODE_EVIDENCE_REF"
GRAPH_NODE_REPORT_REF = "GRAPH_NODE_REPORT_REF"
GRAPH_NODE_UNKNOWN = "GRAPH_NODE_UNKNOWN"

GRAPH_NODE_KINDS: tuple[str, ...] = (
    GRAPH_NODE_FUNCTION_ROLE,
    GRAPH_NODE_VALUE_PATH,
    GRAPH_NODE_VALUE_PATH_SEGMENT,
    GRAPH_NODE_ASSUMPTION,
    GRAPH_NODE_TEST_GAP,
    GRAPH_NODE_LOCAL_VALIDATION,
    GRAPH_NODE_TRACE_RECEIPT,
    GRAPH_NODE_EVIDENCE_REF,
    GRAPH_NODE_REPORT_REF,
    GRAPH_NODE_UNKNOWN,
)

# --- Controlled graph edge kinds --------------------------------------------

GRAPH_EDGE_CLASSIFIES_FUNCTION = "GRAPH_EDGE_CLASSIFIES_FUNCTION"
GRAPH_EDGE_FUNCTION_TO_VALUE_PATH = "GRAPH_EDGE_FUNCTION_TO_VALUE_PATH"
GRAPH_EDGE_VALUE_PATH_TO_SEGMENT = "GRAPH_EDGE_VALUE_PATH_TO_SEGMENT"
GRAPH_EDGE_FUNCTION_TO_ASSUMPTION = "GRAPH_EDGE_FUNCTION_TO_ASSUMPTION"
GRAPH_EDGE_VALUE_PATH_TO_ASSUMPTION = "GRAPH_EDGE_VALUE_PATH_TO_ASSUMPTION"
GRAPH_EDGE_ASSUMPTION_TO_TEST_GAP = "GRAPH_EDGE_ASSUMPTION_TO_TEST_GAP"
GRAPH_EDGE_VALUE_PATH_TO_TEST_GAP = "GRAPH_EDGE_VALUE_PATH_TO_TEST_GAP"
GRAPH_EDGE_FUNCTION_TO_TEST_GAP = "GRAPH_EDGE_FUNCTION_TO_TEST_GAP"
GRAPH_EDGE_TEST_GAP_TO_LOCAL_VALIDATION = "GRAPH_EDGE_TEST_GAP_TO_LOCAL_VALIDATION"
GRAPH_EDGE_TEST_GAP_TO_TRACE_RECEIPT = "GRAPH_EDGE_TEST_GAP_TO_TRACE_RECEIPT"
GRAPH_EDGE_ASSUMPTION_TO_EVIDENCE = "GRAPH_EDGE_ASSUMPTION_TO_EVIDENCE"
GRAPH_EDGE_TEST_GAP_TO_EVIDENCE = "GRAPH_EDGE_TEST_GAP_TO_EVIDENCE"
GRAPH_EDGE_EVIDENCE_TO_REPORT = "GRAPH_EDGE_EVIDENCE_TO_REPORT"
GRAPH_EDGE_EXPLICIT_ALIAS = "GRAPH_EDGE_EXPLICIT_ALIAS"
GRAPH_EDGE_UNKNOWN = "GRAPH_EDGE_UNKNOWN"

GRAPH_EDGE_KINDS: tuple[str, ...] = (
    GRAPH_EDGE_CLASSIFIES_FUNCTION,
    GRAPH_EDGE_FUNCTION_TO_VALUE_PATH,
    GRAPH_EDGE_VALUE_PATH_TO_SEGMENT,
    GRAPH_EDGE_FUNCTION_TO_ASSUMPTION,
    GRAPH_EDGE_VALUE_PATH_TO_ASSUMPTION,
    GRAPH_EDGE_ASSUMPTION_TO_TEST_GAP,
    GRAPH_EDGE_VALUE_PATH_TO_TEST_GAP,
    GRAPH_EDGE_FUNCTION_TO_TEST_GAP,
    GRAPH_EDGE_TEST_GAP_TO_LOCAL_VALIDATION,
    GRAPH_EDGE_TEST_GAP_TO_TRACE_RECEIPT,
    GRAPH_EDGE_ASSUMPTION_TO_EVIDENCE,
    GRAPH_EDGE_TEST_GAP_TO_EVIDENCE,
    GRAPH_EDGE_EVIDENCE_TO_REPORT,
    GRAPH_EDGE_EXPLICIT_ALIAS,
    GRAPH_EDGE_UNKNOWN,
)

# --- Controlled graph check kinds -------------------------------------------

GRAPH_CHECK_DUPLICATE_NODE_ID = "GRAPH_CHECK_DUPLICATE_NODE_ID"
GRAPH_CHECK_DUPLICATE_EDGE_ID = "GRAPH_CHECK_DUPLICATE_EDGE_ID"
GRAPH_CHECK_DANGLING_EDGE_SOURCE = "GRAPH_CHECK_DANGLING_EDGE_SOURCE"
GRAPH_CHECK_DANGLING_EDGE_TARGET = "GRAPH_CHECK_DANGLING_EDGE_TARGET"
GRAPH_CHECK_ORPHAN_NODE = "GRAPH_CHECK_ORPHAN_NODE"
GRAPH_CHECK_AMBIGUOUS_ALIAS = "GRAPH_CHECK_AMBIGUOUS_ALIAS"
GRAPH_CHECK_UNRESOLVED_REFERENCE = "GRAPH_CHECK_UNRESOLVED_REFERENCE"
GRAPH_CHECK_UNSUPPORTED_NODE_KIND = "GRAPH_CHECK_UNSUPPORTED_NODE_KIND"
GRAPH_CHECK_UNSUPPORTED_EDGE_KIND = "GRAPH_CHECK_UNSUPPORTED_EDGE_KIND"
GRAPH_CHECK_READY_FOR_SUBMISSION_TRUE = "GRAPH_CHECK_READY_FOR_SUBMISSION_TRUE"
GRAPH_CHECK_HUMAN_REVIEWED_PRESENT = "GRAPH_CHECK_HUMAN_REVIEWED_PRESENT"
GRAPH_CHECK_FORBIDDEN_FINALITY_WORDING = "GRAPH_CHECK_FORBIDDEN_FINALITY_WORDING"

GRAPH_CHECK_KINDS: tuple[str, ...] = (
    GRAPH_CHECK_DUPLICATE_NODE_ID,
    GRAPH_CHECK_DUPLICATE_EDGE_ID,
    GRAPH_CHECK_DANGLING_EDGE_SOURCE,
    GRAPH_CHECK_DANGLING_EDGE_TARGET,
    GRAPH_CHECK_ORPHAN_NODE,
    GRAPH_CHECK_AMBIGUOUS_ALIAS,
    GRAPH_CHECK_UNRESOLVED_REFERENCE,
    GRAPH_CHECK_UNSUPPORTED_NODE_KIND,
    GRAPH_CHECK_UNSUPPORTED_EDGE_KIND,
    GRAPH_CHECK_READY_FOR_SUBMISSION_TRUE,
    GRAPH_CHECK_HUMAN_REVIEWED_PRESENT,
    GRAPH_CHECK_FORBIDDEN_FINALITY_WORDING,
)

SEVERITY_WARNING = "warning"
SEVERITY_ERROR = "error"

# Forbidden finality wording (positive claims only; checked against labels/values).
_FORBIDDEN_WORDING = (
    "confirmed vulnerability", "final severity", "audit passed",
    "verified safe", "proven safe", "bounty eligible", "ready for submission",
)


# --- ID + canonical hashing -------------------------------------------------

def canonical_graph_seed(value: object) -> str:
    """Canonical JSON seed; raises ``TypeError`` for non-JSON-native seeds."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _short_hash(value: object) -> str:
    return hashlib.sha256(canonical_graph_seed(value).encode("utf-8")).hexdigest()[:_HASH_LEN]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")


def protocol_graph_node_id(
    node_kind: str,
    source_id: str = "",
    label: str = "",
    category: str = "",
    role: str = "",
    path_kind: str = "",
) -> str:
    """Deterministic graph-node ID. Requires a non-empty ``node_kind``."""

    kind = str(node_kind or "").strip()
    if not kind:
        raise ValueError("protocol_graph_node_id requires a non-empty node_kind")
    seed = {
        "node_kind": kind,
        "source_id": str(source_id or "").strip(),
        "label": str(label or "").strip(),
        "category": str(category or "").strip(),
        "role": str(role or "").strip(),
        "path_kind": str(path_kind or "").strip(),
    }
    return f"protocol-graph-node:{_slug(kind)}:{_short_hash(seed)}"


def protocol_graph_edge_id(
    edge_kind: str,
    source_node_id: str,
    target_node_id: str,
    relationship: str = "",
) -> str:
    """Deterministic graph-edge ID. Requires edge_kind + source + target."""

    kind = str(edge_kind or "").strip()
    src = str(source_node_id or "").strip()
    tgt = str(target_node_id or "").strip()
    if not kind:
        raise ValueError("protocol_graph_edge_id requires a non-empty edge_kind")
    if not src:
        raise ValueError("protocol_graph_edge_id requires a non-empty source_node_id")
    if not tgt:
        raise ValueError("protocol_graph_edge_id requires a non-empty target_node_id")
    seed = {"edge_kind": kind, "source_node_id": src, "target_node_id": tgt,
            "relationship": str(relationship or "").strip()}
    return f"protocol-graph-edge:{_slug(kind)}:{_short_hash(seed)}"


def protocol_graph_check_id(
    check_kind: str,
    source_id: str = "",
    target_id: str = "",
    node_id: str = "",
    edge_id: str = "",
) -> str:
    """Deterministic graph-check ID. Requires a non-empty ``check_kind``."""

    kind = str(check_kind or "").strip()
    if not kind:
        raise ValueError("protocol_graph_check_id requires a non-empty check_kind")
    seed = {"check_kind": kind, "source_id": str(source_id or "").strip(),
            "target_id": str(target_id or "").strip(), "node_id": str(node_id or "").strip(),
            "edge_id": str(edge_id or "").strip()}
    return f"protocol-graph-check:{_slug(kind)}:{_short_hash(seed)}"


def protocol_intelligence_graph_id(protocol_name: str, node_ids: list[str], edge_ids: list[str]) -> str:
    """Deterministic graph ID. ``node_ids`` / ``edge_ids`` sorted before hashing."""

    name = str(protocol_name or "").strip()
    if not name:
        raise ValueError("protocol_intelligence_graph_id requires a non-empty protocol_name")
    seed = {"protocol_name": name,
            "node_ids": sorted(str(n) for n in (node_ids or [])),
            "edge_ids": sorted(str(e) for e in (edge_ids or []))}
    return f"protocol-intelligence-graph:{_slug(name)}:{_short_hash(seed)}"


# --- Dataclasses ------------------------------------------------------------

@dataclass
class ProtocolGraphNode:
    node_id: str = ""
    node_kind: str = GRAPH_NODE_UNKNOWN
    source_id: str = ""
    label: str = ""
    contract_name: str = ""
    function_name: str = ""
    category: str = ""
    role: str = ""
    path_kind: str = ""
    status: str = ""
    aliases: list[str] = field(default_factory=list)
    linked_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ProtocolGraphEdge:
    edge_id: str = ""
    edge_kind: str = GRAPH_EDGE_UNKNOWN
    source_node_id: str = ""
    target_node_id: str = ""
    source_id: str = ""
    target_id: str = ""
    relationship: str = ""
    confidence: str = "LINKED"
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ProtocolGraphCheck:
    check_id: str = ""
    check_kind: str = ""
    severity: str = SEVERITY_WARNING
    message: str = ""
    node_id: str = ""
    edge_id: str = ""
    source_id: str = ""
    target_id: str = ""
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ProtocolIntelligenceGraph:
    graph_id: str = ""
    protocol_name: str = ""
    nodes: list[ProtocolGraphNode] = field(default_factory=list)
    edges: list[ProtocolGraphEdge] = field(default_factory=list)
    checks: list[ProtocolGraphCheck] = field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    linked_function_ids: list[str] = field(default_factory=list)
    linked_value_path_ids: list[str] = field(default_factory=list)
    linked_assumption_ids: list[str] = field(default_factory=list)
    linked_test_gap_ids: list[str] = field(default_factory=list)
    linked_local_validation_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


def _check(check_kind: str, severity: str, message: str, *, node_id: str = "",
           edge_id: str = "", source_id: str = "", target_id: str = "") -> ProtocolGraphCheck:
    return ProtocolGraphCheck(
        check_id=protocol_graph_check_id(check_kind, source_id, target_id, node_id, edge_id),
        check_kind=check_kind, severity=severity, message=message,
        node_id=node_id, edge_id=edge_id, source_id=source_id, target_id=target_id,
        manual_review_required=True, ready_for_submission=False,
    )


# --- Node builders ----------------------------------------------------------

def _function_id_of(obj: object) -> str:
    fid = str(getattr(obj, "function_id", "") or "")
    if fid:
        return fid
    meta = getattr(obj, "metadata", {}) or {}
    return str(meta.get("function_id", "") or "")


def graph_node_from_role_classification(classification: object) -> list[ProtocolGraphNode]:
    """Build one FUNCTION_ROLE node per classification (roles in metadata).

    The function anchor is ``function_id`` read from the classification or its
    metadata when present; standard role classifications carry none, so
    function-level edges form only when a caller supplies it. No alias is
    invented.
    """

    roles = list(getattr(classification, "roles", []) or [])
    source_id = str(getattr(classification, "classification_id", "") or "")
    fid = _function_id_of(classification)
    function_name = str(getattr(classification, "function_name", "") or "")
    contract_name = str(getattr(classification, "contract_name", "") or "")
    primary_role = roles[0] if roles else ""
    label = f"{contract_name}.{function_name}" if contract_name and function_name else function_name
    node = ProtocolGraphNode(
        node_id=protocol_graph_node_id(GRAPH_NODE_FUNCTION_ROLE, source_id, label, "", primary_role, ""),
        node_kind=GRAPH_NODE_FUNCTION_ROLE,
        source_id=source_id,
        label=label,
        contract_name=contract_name,
        function_name=function_name,
        role=primary_role,
        status=str(getattr(classification, "confidence", "") or ""),
        aliases=[],
        linked_ids=[fid] if fid else [],
        manual_review_required=True,
        ready_for_submission=False,
        metadata={"roles": roles, "function_id": fid},
    )
    return [node]


def graph_nodes_from_value_path(value_path: object) -> list[ProtocolGraphNode]:
    """Build one VALUE_PATH node plus one VALUE_PATH_SEGMENT node per segment."""

    pid = str(getattr(value_path, "path_id", "") or "")
    fid = str(getattr(value_path, "function_id", "") or "")
    path_kind = str(getattr(value_path, "path_kind", "") or "")
    label = str(getattr(value_path, "name", "") or "")
    contract_name = str(getattr(value_path, "contract_name", "") or "")
    function_name = str(getattr(value_path, "function_name", "") or "")
    nodes: list[ProtocolGraphNode] = [ProtocolGraphNode(
        node_id=protocol_graph_node_id(GRAPH_NODE_VALUE_PATH, pid, label, "", "", path_kind),
        node_kind=GRAPH_NODE_VALUE_PATH, source_id=pid, label=label,
        contract_name=contract_name, function_name=function_name, path_kind=path_kind,
        status=str(getattr(value_path, "support_level", "") or ""),
        linked_ids=[fid] if fid else [], manual_review_required=True, ready_for_submission=False,
        metadata={"function_id": fid},
    )]
    for seg in list(getattr(value_path, "segments", []) or []):
        sid = str(getattr(seg, "segment_id", "") or "")
        kind = str(getattr(seg, "segment_kind", "") or "")
        nodes.append(ProtocolGraphNode(
            node_id=protocol_graph_node_id(GRAPH_NODE_VALUE_PATH_SEGMENT, sid, kind, kind, "", ""),
            node_kind=GRAPH_NODE_VALUE_PATH_SEGMENT, source_id=sid, label=kind, category=kind,
            contract_name=contract_name, function_name=function_name,
            linked_ids=[pid] if pid else [], manual_review_required=True, ready_for_submission=False,
            metadata={"path_id": pid, "order_index": int(getattr(seg, "order_index", 0) or 0)},
        ))
    return nodes


def graph_nodes_from_assumption(assumption: object) -> list[ProtocolGraphNode]:
    """Build one ASSUMPTION node."""

    aid = str(getattr(assumption, "assumption_id", "") or "")
    fid = str(getattr(assumption, "function_id", "") or "")
    category = str(getattr(assumption, "category", "") or "")
    vpids = list(getattr(assumption, "value_path_ids", []) or [])
    return [ProtocolGraphNode(
        node_id=protocol_graph_node_id(GRAPH_NODE_ASSUMPTION, aid, str(getattr(assumption, "title", "") or ""), category),
        node_kind=GRAPH_NODE_ASSUMPTION, source_id=aid,
        label=str(getattr(assumption, "title", "") or ""), category=category,
        contract_name=str(getattr(assumption, "contract_name", "") or ""),
        function_name=str(getattr(assumption, "function_name", "") or ""),
        status=str(getattr(assumption, "support_level", "") or ""),
        linked_ids=sorted({x for x in ([fid] + vpids) if x}),
        manual_review_required=True, ready_for_submission=False,
        metadata={"function_id": fid, "value_path_ids": vpids},
    )]


def graph_nodes_from_test_gap(test_gap: object) -> list[ProtocolGraphNode]:
    """Build one TEST_GAP node."""

    tid = str(getattr(test_gap, "test_gap_id", "") or "")
    fid = str(getattr(test_gap, "function_id", "") or "")
    category = str(getattr(test_gap, "category", "") or "")
    vpids = list(getattr(test_gap, "value_path_ids", []) or [])
    aids = list(getattr(test_gap, "assumption_ids", []) or [])
    lvids = list(getattr(test_gap, "linked_local_validation_ids", []) or [])
    trids = list(getattr(test_gap, "linked_trace_receipt_ids", []) or [])
    return [ProtocolGraphNode(
        node_id=protocol_graph_node_id(GRAPH_NODE_TEST_GAP, tid, str(getattr(test_gap, "title", "") or ""), category),
        node_kind=GRAPH_NODE_TEST_GAP, source_id=tid,
        label=str(getattr(test_gap, "title", "") or ""), category=category,
        contract_name=str(getattr(test_gap, "contract_name", "") or ""),
        function_name=str(getattr(test_gap, "function_name", "") or ""),
        status=str(getattr(test_gap, "gap_status", "") or ""),
        linked_ids=sorted({x for x in ([fid] + vpids + aids + lvids + trids) if x}),
        manual_review_required=True, ready_for_submission=False,
        metadata={"function_id": fid, "value_path_ids": vpids, "assumption_ids": aids,
                  "linked_local_validation_ids": lvids, "linked_trace_receipt_ids": trids},
    )]


def _ref_node(node_kind: str, source_id: str) -> ProtocolGraphNode:
    return ProtocolGraphNode(
        node_id=protocol_graph_node_id(node_kind, source_id, source_id),
        node_kind=node_kind, source_id=source_id, label=source_id,
        manual_review_required=True, ready_for_submission=False,
    )


# --- Edge builders ----------------------------------------------------------

def _edge(edge_kind: str, src: ProtocolGraphNode, tgt: ProtocolGraphNode, relationship: str) -> ProtocolGraphEdge:
    return ProtocolGraphEdge(
        edge_id=protocol_graph_edge_id(edge_kind, src.node_id, tgt.node_id, relationship),
        edge_kind=edge_kind, source_node_id=src.node_id, target_node_id=tgt.node_id,
        source_id=src.source_id, target_id=tgt.source_id, relationship=relationship,
        confidence="LINKED", manual_review_required=True, ready_for_submission=False,
    )


class _NodeIndex:
    """Resolve nodes by source_id (1:1) and FUNCTION_ROLE nodes by function_id."""

    def __init__(self, nodes: list[ProtocolGraphNode]) -> None:
        self.by_source: dict[str, ProtocolGraphNode] = {}
        self._function_nodes: dict[str, list[ProtocolGraphNode]] = {}
        for node in nodes:
            if node.source_id and node.source_id not in self.by_source:
                self.by_source[node.source_id] = node
            if node.node_kind == GRAPH_NODE_FUNCTION_ROLE:
                fid = str((node.metadata or {}).get("function_id", "") or "")
                if fid:
                    self._function_nodes.setdefault(fid, []).append(node)

    def node(self, source_id: str) -> ProtocolGraphNode | None:
        return self.by_source.get(str(source_id or ""))

    def function_node(self, function_id: str) -> tuple[ProtocolGraphNode | None, bool]:
        """Return (unique function-role node, ambiguous?) for a function_id."""

        hits = self._function_nodes.get(str(function_id or ""), [])
        if len(hits) == 1:
            return hits[0], False
        return None, len(hits) > 1


def build_edges_for_value_path(value_path: object, node_index: _NodeIndex) -> tuple[list[ProtocolGraphEdge], list[ProtocolGraphCheck]]:
    edges: list[ProtocolGraphEdge] = []
    checks: list[ProtocolGraphCheck] = []
    pid = str(getattr(value_path, "path_id", "") or "")
    vp_node = node_index.node(pid)
    if vp_node is None:
        return edges, checks
    for seg in list(getattr(value_path, "segments", []) or []):
        seg_node = node_index.node(str(getattr(seg, "segment_id", "") or ""))
        if seg_node is not None:
            edges.append(_edge(GRAPH_EDGE_VALUE_PATH_TO_SEGMENT, vp_node, seg_node, "contains-segment"))
    fid = str(getattr(value_path, "function_id", "") or "")
    if fid:
        fn_node, ambiguous = node_index.function_node(fid)
        if ambiguous:
            checks.append(_check(GRAPH_CHECK_AMBIGUOUS_ALIAS, SEVERITY_WARNING,
                                 f"ambiguous function_id for value path: {fid}", source_id=fid, node_id=vp_node.node_id))
        elif fn_node is not None:
            edges.append(_edge(GRAPH_EDGE_FUNCTION_TO_VALUE_PATH, fn_node, vp_node, "function-has-value-path"))
    return edges, checks


def build_edges_for_assumption(assumption: object, node_index: _NodeIndex) -> tuple[list[ProtocolGraphEdge], list[ProtocolGraphCheck]]:
    edges: list[ProtocolGraphEdge] = []
    checks: list[ProtocolGraphCheck] = []
    aid = str(getattr(assumption, "assumption_id", "") or "")
    asm_node = node_index.node(aid)
    if asm_node is None:
        return edges, checks
    for vpid in sorted({x for x in (list(getattr(assumption, "value_path_ids", []) or [])
                                    + list(getattr(assumption, "linked_value_path_ids", []) or [])) if x}):
        vp_node = node_index.node(vpid)
        if vp_node is not None:
            edges.append(_edge(GRAPH_EDGE_VALUE_PATH_TO_ASSUMPTION, vp_node, asm_node, "value-path-relies-on-assumption"))
        else:
            checks.append(_check(GRAPH_CHECK_UNRESOLVED_REFERENCE, SEVERITY_WARNING,
                                 f"assumption references unknown value path: {vpid}", source_id=aid, target_id=vpid))
    fid = str(getattr(assumption, "function_id", "") or "")
    if fid:
        fn_node, ambiguous = node_index.function_node(fid)
        if ambiguous:
            checks.append(_check(GRAPH_CHECK_AMBIGUOUS_ALIAS, SEVERITY_WARNING,
                                 f"ambiguous function_id for assumption: {fid}", source_id=fid, node_id=asm_node.node_id))
        elif fn_node is not None:
            edges.append(_edge(GRAPH_EDGE_FUNCTION_TO_ASSUMPTION, fn_node, asm_node, "function-has-assumption"))
    return edges, checks


def build_edges_for_test_gap(test_gap: object, node_index: _NodeIndex) -> tuple[list[ProtocolGraphEdge], list[ProtocolGraphCheck]]:
    edges: list[ProtocolGraphEdge] = []
    checks: list[ProtocolGraphCheck] = []
    tid = str(getattr(test_gap, "test_gap_id", "") or "")
    gap_node = node_index.node(tid)
    if gap_node is None:
        return edges, checks
    for aid in sorted({x for x in (list(getattr(test_gap, "assumption_ids", []) or [])
                                   + list(getattr(test_gap, "linked_assumption_ids", []) or [])) if x}):
        asm_node = node_index.node(aid)
        if asm_node is not None:
            edges.append(_edge(GRAPH_EDGE_ASSUMPTION_TO_TEST_GAP, asm_node, gap_node, "assumption-needs-test"))
        else:
            checks.append(_check(GRAPH_CHECK_UNRESOLVED_REFERENCE, SEVERITY_WARNING,
                                 f"test gap references unknown assumption: {aid}", source_id=tid, target_id=aid))
    for vpid in sorted({x for x in (list(getattr(test_gap, "value_path_ids", []) or [])
                                    + list(getattr(test_gap, "linked_value_path_ids", []) or [])) if x}):
        vp_node = node_index.node(vpid)
        if vp_node is not None:
            edges.append(_edge(GRAPH_EDGE_VALUE_PATH_TO_TEST_GAP, vp_node, gap_node, "value-path-needs-test"))
    fid = str(getattr(test_gap, "function_id", "") or "")
    if fid:
        fn_node, ambiguous = node_index.function_node(fid)
        if ambiguous:
            checks.append(_check(GRAPH_CHECK_AMBIGUOUS_ALIAS, SEVERITY_WARNING,
                                 f"ambiguous function_id for test gap: {fid}", source_id=fid, node_id=gap_node.node_id))
        elif fn_node is not None:
            edges.append(_edge(GRAPH_EDGE_FUNCTION_TO_TEST_GAP, fn_node, gap_node, "function-needs-test"))
    for lvid in sorted({x for x in (getattr(test_gap, "linked_local_validation_ids", []) or []) if x}):
        lv_node = node_index.node(lvid)
        if lv_node is not None:
            edges.append(_edge(GRAPH_EDGE_TEST_GAP_TO_LOCAL_VALIDATION, gap_node, lv_node, "tested-context-only"))
        else:
            checks.append(_check(GRAPH_CHECK_UNRESOLVED_REFERENCE, SEVERITY_WARNING,
                                 f"test gap references unknown local validation: {lvid}", source_id=tid, target_id=lvid))
    for trid in sorted({x for x in (getattr(test_gap, "linked_trace_receipt_ids", []) or []) if x}):
        tr_node = node_index.node(trid)
        if tr_node is not None:
            edges.append(_edge(GRAPH_EDGE_TEST_GAP_TO_TRACE_RECEIPT, gap_node, tr_node, "trace-bound-context-only"))
        else:
            checks.append(_check(GRAPH_CHECK_UNRESOLVED_REFERENCE, SEVERITY_WARNING,
                                 f"test gap references unknown trace receipt: {trid}", source_id=tid, target_id=trid))
    return edges, checks


def build_explicit_alias_edges(nodes: list[ProtocolGraphNode]) -> tuple[list[ProtocolGraphEdge], list[ProtocolGraphCheck]]:
    """Build EXPLICIT_ALIAS edges only when a node alias exactly matches another
    node's source_id (1:1). Ambiguous matches produce a check and no edge."""

    edges: list[ProtocolGraphEdge] = []
    checks: list[ProtocolGraphCheck] = []
    by_source: dict[str, list[ProtocolGraphNode]] = {}
    for node in nodes:
        if node.source_id:
            by_source.setdefault(node.source_id, []).append(node)
    for node in nodes:
        for alias in list(node.aliases or []):
            hits = by_source.get(str(alias), [])
            hits = [h for h in hits if h.node_id != node.node_id]
            if len(hits) == 1:
                edges.append(_edge(GRAPH_EDGE_EXPLICIT_ALIAS, node, hits[0], "explicit-alias"))
            elif len(hits) > 1:
                checks.append(_check(GRAPH_CHECK_AMBIGUOUS_ALIAS, SEVERITY_WARNING,
                                     f"ambiguous explicit alias: {alias}", node_id=node.node_id, source_id=str(alias)))
    return edges, checks


# --- Dedup + sorting --------------------------------------------------------

def deduplicate_graph_nodes(nodes: list[ProtocolGraphNode]) -> tuple[list[ProtocolGraphNode], list[ProtocolGraphCheck]]:
    seen: dict[str, ProtocolGraphNode] = {}
    checks: list[ProtocolGraphCheck] = []
    for node in nodes or []:
        if node.node_id in seen:
            checks.append(_check(GRAPH_CHECK_DUPLICATE_NODE_ID, SEVERITY_ERROR,
                                 f"duplicate node id: {node.node_id}", node_id=node.node_id))
            continue
        seen[node.node_id] = node
    ordered = sorted(seen.values(), key=lambda n: (n.node_kind, n.node_id))
    return ordered, checks


def deduplicate_graph_edges(edges: list[ProtocolGraphEdge]) -> tuple[list[ProtocolGraphEdge], list[ProtocolGraphCheck]]:
    seen: dict[str, ProtocolGraphEdge] = {}
    checks: list[ProtocolGraphCheck] = []
    for edge in edges or []:
        if edge.edge_id in seen:
            checks.append(_check(GRAPH_CHECK_DUPLICATE_EDGE_ID, SEVERITY_ERROR,
                                 f"duplicate edge id: {edge.edge_id}", edge_id=edge.edge_id))
            continue
        seen[edge.edge_id] = edge
    ordered = sorted(seen.values(), key=lambda e: (e.edge_kind, e.source_node_id, e.target_node_id, e.edge_id))
    return ordered, checks


# --- Consistency checks -----------------------------------------------------

def validate_protocol_graph(graph: ProtocolIntelligenceGraph) -> list[ProtocolGraphCheck]:
    """Deterministic structural checks over a graph (review context only).

    Duplicate IDs and dangling edges are errors; orphan nodes, unsupported kinds,
    ambiguous aliases, and unresolved references are warnings. A
    ``ready_for_submission`` true flag, a ``HUMAN_REVIEWED`` token, or forbidden
    finality wording is a safety error. No check proves safety or a vulnerability.
    """

    checks: list[ProtocolGraphCheck] = []
    nodes = list(graph.nodes or [])
    edges = list(graph.edges or [])

    node_ids: set[str] = set()
    for node in nodes:
        if node.node_id in node_ids:
            checks.append(_check(GRAPH_CHECK_DUPLICATE_NODE_ID, SEVERITY_ERROR,
                                 f"duplicate node id: {node.node_id}", node_id=node.node_id))
        node_ids.add(node.node_id)
        if node.node_kind not in GRAPH_NODE_KINDS:
            checks.append(_check(GRAPH_CHECK_UNSUPPORTED_NODE_KIND, SEVERITY_WARNING,
                                 f"unsupported node kind: {node.node_kind}", node_id=node.node_id))

    edge_ids: set[str] = set()
    incident: set[str] = set()
    for edge in edges:
        if edge.edge_id in edge_ids:
            checks.append(_check(GRAPH_CHECK_DUPLICATE_EDGE_ID, SEVERITY_ERROR,
                                 f"duplicate edge id: {edge.edge_id}", edge_id=edge.edge_id))
        edge_ids.add(edge.edge_id)
        if edge.edge_kind not in GRAPH_EDGE_KINDS:
            checks.append(_check(GRAPH_CHECK_UNSUPPORTED_EDGE_KIND, SEVERITY_WARNING,
                                 f"unsupported edge kind: {edge.edge_kind}", edge_id=edge.edge_id))
        if edge.source_node_id not in node_ids:
            checks.append(_check(GRAPH_CHECK_DANGLING_EDGE_SOURCE, SEVERITY_ERROR,
                                 f"edge source not in graph: {edge.source_node_id}",
                                 edge_id=edge.edge_id, source_id=edge.source_node_id))
        if edge.target_node_id not in node_ids:
            checks.append(_check(GRAPH_CHECK_DANGLING_EDGE_TARGET, SEVERITY_ERROR,
                                 f"edge target not in graph: {edge.target_node_id}",
                                 edge_id=edge.edge_id, target_id=edge.target_node_id))
        incident.add(edge.source_node_id)
        incident.add(edge.target_node_id)

    for node in nodes:
        if node.node_id not in incident:
            checks.append(_check(GRAPH_CHECK_ORPHAN_NODE, SEVERITY_WARNING,
                                 f"orphan node (no incident edges): {node.node_id}", node_id=node.node_id))

    # Safety scans over the serialized graph content.
    blob = json.dumps(graph_to_dict(graph), sort_keys=True).lower()
    if '"ready_for_submission": true' in blob or '"ready_for_submission":true' in blob:
        checks.append(_check(GRAPH_CHECK_READY_FOR_SUBMISSION_TRUE, SEVERITY_ERROR,
                             "ready_for_submission is true somewhere in the graph"))
    if "human_reviewed" in blob:
        checks.append(_check(GRAPH_CHECK_HUMAN_REVIEWED_PRESENT, SEVERITY_ERROR,
                             "a human-reviewed status is present in the graph"))
    for token in _FORBIDDEN_WORDING:
        if token in blob:
            checks.append(_check(GRAPH_CHECK_FORBIDDEN_FINALITY_WORDING, SEVERITY_ERROR,
                                 f"forbidden finality wording present: {token}"))
    return checks


def _sort_checks(checks: list[ProtocolGraphCheck]) -> list[ProtocolGraphCheck]:
    severity_rank = {SEVERITY_ERROR: 0, SEVERITY_WARNING: 1}
    seen: dict[str, ProtocolGraphCheck] = {}
    for c in checks:
        seen.setdefault(c.check_id, c)
    return sorted(seen.values(), key=lambda c: (severity_rank.get(c.severity, 9), c.check_kind, c.check_id))


# --- Graph builder ----------------------------------------------------------

def build_protocol_intelligence_graph(
    protocol_name: str,
    role_classifications: list[object] | None = None,
    value_paths: list[object] | None = None,
    assumptions: list[object] | None = None,
    test_gaps: list[object] | None = None,
    local_validation_ids: list[str] | None = None,
    trace_receipt_ids: list[str] | None = None,
) -> ProtocolIntelligenceGraph:
    """Compose the v3.8 intelligence layers into a deterministic protocol graph.

    All edges are exact-ID / explicit-alias only. Local-validation and
    trace-receipt nodes are created only from explicitly supplied IDs (never
    invented). Consistency checks are run and counts rolled up. Review context
    only: ``manual_review_required`` stays true and ``ready_for_submission`` stays
    false.
    """

    raw_nodes: list[ProtocolGraphNode] = []
    for cls in role_classifications or []:
        raw_nodes.extend(graph_node_from_role_classification(cls))
    for vp in value_paths or []:
        raw_nodes.extend(graph_nodes_from_value_path(vp))
    for asm in assumptions or []:
        raw_nodes.extend(graph_nodes_from_assumption(asm))
    for gap in test_gaps or []:
        raw_nodes.extend(graph_nodes_from_test_gap(gap))
    for lvid in (local_validation_ids or []):
        if lvid:
            raw_nodes.append(_ref_node(GRAPH_NODE_LOCAL_VALIDATION, str(lvid)))
    for trid in (trace_receipt_ids or []):
        if trid:
            raw_nodes.append(_ref_node(GRAPH_NODE_TRACE_RECEIPT, str(trid)))

    nodes, node_checks = deduplicate_graph_nodes(raw_nodes)
    index = _NodeIndex(nodes)

    raw_edges: list[ProtocolGraphEdge] = []
    edge_checks: list[ProtocolGraphCheck] = []
    for vp in value_paths or []:
        e, c = build_edges_for_value_path(vp, index)
        raw_edges.extend(e); edge_checks.extend(c)
    for asm in assumptions or []:
        e, c = build_edges_for_assumption(asm, index)
        raw_edges.extend(e); edge_checks.extend(c)
    for gap in test_gaps or []:
        e, c = build_edges_for_test_gap(gap, index)
        raw_edges.extend(e); edge_checks.extend(c)
    alias_edges, alias_checks = build_explicit_alias_edges(nodes)
    raw_edges.extend(alias_edges); edge_checks.extend(alias_checks)

    edges, edge_dupe_checks = deduplicate_graph_edges(raw_edges)

    graph = ProtocolIntelligenceGraph(
        protocol_name=str(protocol_name or "").strip(),
        nodes=nodes,
        edges=edges,
        node_count=len(nodes),
        edge_count=len(edges),
        manual_review_required=True,
        ready_for_submission=False,
    )
    structural_checks = validate_protocol_graph(graph)
    graph.checks = _sort_checks(node_checks + edge_checks + edge_dupe_checks + structural_checks)
    graph.warning_count = sum(1 for c in graph.checks if c.severity == SEVERITY_WARNING)
    graph.error_count = sum(1 for c in graph.checks if c.severity == SEVERITY_ERROR)

    fids: set[str] = set()
    vpids: set[str] = set()
    aids: set[str] = set()
    tids: set[str] = set()
    lvids: set[str] = set()
    for node in nodes:
        meta = node.metadata or {}
        if node.node_kind == GRAPH_NODE_VALUE_PATH:
            vpids.add(node.source_id)
        elif node.node_kind == GRAPH_NODE_ASSUMPTION:
            aids.add(node.source_id)
        elif node.node_kind == GRAPH_NODE_TEST_GAP:
            tids.add(node.source_id)
        elif node.node_kind == GRAPH_NODE_LOCAL_VALIDATION:
            lvids.add(node.source_id)
        fid = str(meta.get("function_id", "") or "")
        if fid:
            fids.add(fid)
    graph.linked_function_ids = sorted(fids)
    graph.linked_value_path_ids = sorted(vpids)
    graph.linked_assumption_ids = sorted(aids)
    graph.linked_test_gap_ids = sorted(tids)
    graph.linked_local_validation_ids = sorted(lvids)
    graph.graph_id = protocol_intelligence_graph_id(
        protocol_name, [n.node_id for n in nodes], [e.edge_id for e in edges])
    return graph


# --- Serialization ----------------------------------------------------------

def graph_to_dict(value: object) -> object:
    """Recursively serialize graph dataclasses to plain JSON-ready data.

    Dataclasses become dicts, lists/tuples become lists, dicts are walked, and
    primitives / ``None`` pass through. Unsupported objects raise ``TypeError``.
    Does not mutate the source.
    """

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: graph_to_dict(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {key: graph_to_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [graph_to_dict(item) for item in value]
    raise TypeError(f"unsupported value for graph_to_dict: {type(value).__name__}")
