"""Internal local-validation coverage correlation (v3.8, additive).

This module correlates explicitly-linked local-validation result IDs and
trace-receipt IDs with protocol-graph test gaps (and, through them, function
roles, value paths, and assumptions) as supporting review context only. It is
internal infrastructure: no filesystem, network, subprocess, CLI, or live-chain
behavior; it never reads ``.arkheionx/out`` and never parses local-validation
artifacts -- it consumes already-loaded IDs and objects. Importing it has no side
effects.

Core rule: local-validation coverage can support review context; it can never
finalize a security conclusion. ``COVERAGE_TESTED`` means a local-validation
result ID was explicitly linked, and ``COVERAGE_TRACE_BOUND`` means a trace
receipt ID was explicitly linked -- never that anything is safe, proven,
confirmed, final, or audit-passed. A passing local test never proves safety and
missing coverage never proves a vulnerability. Correlation is exact-ID /
explicit-alias only (no fuzzy or substring matching) and invents no coverage, no
local-validation ID, and no trace-receipt ID. Every record keeps
``manual_review_required`` true and ``ready_for_submission`` false.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass, field, fields, is_dataclass

from .test_gaps import TEST_GAP_LOCALLY_TESTED, TEST_GAP_TRACE_BOUND

_HASH_LEN = 12

# --- Controlled coverage support levels -------------------------------------

COVERAGE_NONE = "COVERAGE_NONE"
COVERAGE_CONTEXT_ONLY = "COVERAGE_CONTEXT_ONLY"
COVERAGE_TESTED = "COVERAGE_TESTED"
COVERAGE_TRACE_BOUND = "COVERAGE_TRACE_BOUND"
COVERAGE_PARTIAL = "COVERAGE_PARTIAL"
COVERAGE_UNRESOLVED = "COVERAGE_UNRESOLVED"
COVERAGE_NEEDS_HUMAN_REVIEW = "COVERAGE_NEEDS_HUMAN_REVIEW"

COVERAGE_SUPPORT_LEVELS: tuple[str, ...] = (
    COVERAGE_NONE,
    COVERAGE_CONTEXT_ONLY,
    COVERAGE_TESTED,
    COVERAGE_TRACE_BOUND,
    COVERAGE_PARTIAL,
    COVERAGE_UNRESOLVED,
    COVERAGE_NEEDS_HUMAN_REVIEW,
)

# --- Controlled coverage check kinds ----------------------------------------

COVERAGE_CHECK_UNRESOLVED_FUNCTION_ID = "COVERAGE_CHECK_UNRESOLVED_FUNCTION_ID"
COVERAGE_CHECK_UNRESOLVED_VALUE_PATH_ID = "COVERAGE_CHECK_UNRESOLVED_VALUE_PATH_ID"
COVERAGE_CHECK_UNRESOLVED_ASSUMPTION_ID = "COVERAGE_CHECK_UNRESOLVED_ASSUMPTION_ID"
COVERAGE_CHECK_UNRESOLVED_TEST_GAP_ID = "COVERAGE_CHECK_UNRESOLVED_TEST_GAP_ID"
COVERAGE_CHECK_UNRESOLVED_LOCAL_VALIDATION_ID = "COVERAGE_CHECK_UNRESOLVED_LOCAL_VALIDATION_ID"
COVERAGE_CHECK_UNRESOLVED_TRACE_RECEIPT_ID = "COVERAGE_CHECK_UNRESOLVED_TRACE_RECEIPT_ID"
COVERAGE_CHECK_MISSING_EXPLICIT_LINK = "COVERAGE_CHECK_MISSING_EXPLICIT_LINK"
COVERAGE_CHECK_AMBIGUOUS_ALIAS = "COVERAGE_CHECK_AMBIGUOUS_ALIAS"
COVERAGE_CHECK_DUPLICATE_COVERAGE_ID = "COVERAGE_CHECK_DUPLICATE_COVERAGE_ID"
COVERAGE_CHECK_READY_FOR_SUBMISSION_TRUE = "COVERAGE_CHECK_READY_FOR_SUBMISSION_TRUE"
COVERAGE_CHECK_FORBIDDEN_FINALITY_WORDING = "COVERAGE_CHECK_FORBIDDEN_FINALITY_WORDING"

COVERAGE_CHECK_KINDS: tuple[str, ...] = (
    COVERAGE_CHECK_UNRESOLVED_FUNCTION_ID,
    COVERAGE_CHECK_UNRESOLVED_VALUE_PATH_ID,
    COVERAGE_CHECK_UNRESOLVED_ASSUMPTION_ID,
    COVERAGE_CHECK_UNRESOLVED_TEST_GAP_ID,
    COVERAGE_CHECK_UNRESOLVED_LOCAL_VALIDATION_ID,
    COVERAGE_CHECK_UNRESOLVED_TRACE_RECEIPT_ID,
    COVERAGE_CHECK_MISSING_EXPLICIT_LINK,
    COVERAGE_CHECK_AMBIGUOUS_ALIAS,
    COVERAGE_CHECK_DUPLICATE_COVERAGE_ID,
    COVERAGE_CHECK_READY_FOR_SUBMISSION_TRUE,
    COVERAGE_CHECK_FORBIDDEN_FINALITY_WORDING,
)

SEVERITY_WARNING = "warning"
SEVERITY_ERROR = "error"

_UNRESOLVED_CHECK_KINDS = frozenset({
    COVERAGE_CHECK_UNRESOLVED_FUNCTION_ID,
    COVERAGE_CHECK_UNRESOLVED_VALUE_PATH_ID,
    COVERAGE_CHECK_UNRESOLVED_ASSUMPTION_ID,
    COVERAGE_CHECK_UNRESOLVED_TEST_GAP_ID,
    COVERAGE_CHECK_UNRESOLVED_LOCAL_VALIDATION_ID,
    COVERAGE_CHECK_UNRESOLVED_TRACE_RECEIPT_ID,
})

_FORBIDDEN_WORDING = (
    "confirmed vulnerability", "final severity", "audit passed",
    "verified safe", "proven safe", "bounty eligible", "ready for submission",
    "tested means safe", "proves safety", "proves a vulnerability",
)


# --- ID + canonical hashing -------------------------------------------------

def canonical_coverage_seed(value: object) -> str:
    """Canonical JSON seed; raises ``TypeError`` for non-JSON-native seeds."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _short_hash(value: object) -> str:
    return hashlib.sha256(canonical_coverage_seed(value).encode("utf-8")).hexdigest()[:_HASH_LEN]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")


def local_validation_coverage_id(
    source_local_validation_id: str = "",
    source_trace_receipt_id: str = "",
    target_test_gap_id: str = "",
    target_function_id: str = "",
    target_value_path_id: str = "",
    target_assumption_id: str = "",
    relationship: str = "",
) -> str:
    """Deterministic coverage-link ID. Requires at least one source + one target."""

    src = str(source_local_validation_id or "").strip()
    trc = str(source_trace_receipt_id or "").strip()
    tgt_gap = str(target_test_gap_id or "").strip()
    tgt_fn = str(target_function_id or "").strip()
    tgt_vp = str(target_value_path_id or "").strip()
    tgt_asm = str(target_assumption_id or "").strip()
    if not (src or trc):
        raise ValueError("local_validation_coverage_id requires a local-validation or trace-receipt source id")
    if not (tgt_gap or tgt_fn or tgt_vp or tgt_asm):
        raise ValueError("local_validation_coverage_id requires at least one target id")
    seed = {
        "source_local_validation_id": src, "source_trace_receipt_id": trc,
        "target_test_gap_id": tgt_gap, "target_function_id": tgt_fn,
        "target_value_path_id": tgt_vp, "target_assumption_id": tgt_asm,
        "relationship": str(relationship or "").strip(),
    }
    return f"local-validation-coverage:{_short_hash(seed)}"


def coverage_correlation_check_id(check_kind: str, source_id: str = "", target_id: str = "", coverage_id: str = "") -> str:
    """Deterministic coverage-check ID. Requires a non-empty ``check_kind``."""

    kind = str(check_kind or "").strip()
    if not kind:
        raise ValueError("coverage_correlation_check_id requires a non-empty check_kind")
    seed = {"check_kind": kind, "source_id": str(source_id or "").strip(),
            "target_id": str(target_id or "").strip(), "coverage_id": str(coverage_id or "").strip()}
    return f"coverage-check:{_slug(kind)}:{_short_hash(seed)}"


def local_validation_coverage_summary_id(protocol_name: str, coverage_ids: list[str]) -> str:
    """Deterministic coverage-summary ID. ``coverage_ids`` sorted before hashing."""

    name = str(protocol_name or "").strip()
    if not name:
        raise ValueError("local_validation_coverage_summary_id requires a non-empty protocol_name")
    seed = {"protocol_name": name, "coverage_ids": sorted(str(c) for c in (coverage_ids or []))}
    return f"local-validation-coverage-summary:{_slug(name)}:{_short_hash(seed)}"


# --- Dataclasses ------------------------------------------------------------

@dataclass
class LocalValidationCoverageLink:
    coverage_id: str = ""
    support_level: str = COVERAGE_CONTEXT_ONLY
    source_local_validation_id: str = ""
    source_trace_receipt_id: str = ""
    target_node_id: str = ""
    target_test_gap_id: str = ""
    target_function_id: str = ""
    target_value_path_id: str = ""
    target_assumption_id: str = ""
    relationship: str = ""
    evidence_support: str = ""
    test_status: str = ""
    test_name: str = ""
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class CoverageCorrelationCheck:
    check_id: str = ""
    check_kind: str = ""
    severity: str = SEVERITY_WARNING
    message: str = ""
    source_id: str = ""
    target_id: str = ""
    coverage_id: str = ""
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class LocalValidationCoverageSummary:
    coverage_summary_id: str = ""
    protocol_name: str = ""
    coverage_links: list[LocalValidationCoverageLink] = field(default_factory=list)
    checks: list[CoverageCorrelationCheck] = field(default_factory=list)
    coverage_count: int = 0
    tested_count: int = 0
    trace_bound_count: int = 0
    unresolved_count: int = 0
    linked_local_validation_ids: list[str] = field(default_factory=list)
    linked_trace_receipt_ids: list[str] = field(default_factory=list)
    linked_test_gap_ids: list[str] = field(default_factory=list)
    linked_function_ids: list[str] = field(default_factory=list)
    linked_value_path_ids: list[str] = field(default_factory=list)
    linked_assumption_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


def _check(check_kind: str, severity: str, message: str, *, source_id: str = "",
           target_id: str = "", coverage_id: str = "") -> CoverageCorrelationCheck:
    return CoverageCorrelationCheck(
        check_id=coverage_correlation_check_id(check_kind, source_id, target_id, coverage_id),
        check_kind=check_kind, severity=severity, message=message,
        source_id=source_id, target_id=target_id, coverage_id=coverage_id,
        manual_review_required=True, ready_for_submission=False,
    )


# --- Index helpers ----------------------------------------------------------

def build_graph_node_index(graph: object) -> dict[str, object]:
    """Index graph nodes by both ``source_id`` and ``node_id`` (exact only)."""

    index: dict[str, object] = {}
    for node in list(getattr(graph, "nodes", []) or []):
        sid = str(getattr(node, "source_id", "") or "")
        nid = str(getattr(node, "node_id", "") or "")
        if sid and sid not in index:
            index[sid] = node
        if nid and nid not in index:
            index[nid] = node
    return index


def build_test_gap_index(test_gaps: object) -> dict[str, object]:
    """Index test gaps by ``test_gap_id`` (accepts a list or a TestGapSet)."""

    items = getattr(test_gaps, "test_gaps", None)
    if items is None:
        items = test_gaps if isinstance(test_gaps, (list, tuple)) else []
    out: dict[str, object] = {}
    for gap in items or []:
        tid = str(getattr(gap, "test_gap_id", "") or "")
        if tid and tid not in out:
            out[tid] = gap
    return out


def build_explicit_alias_index(nodes: list[object]) -> tuple[dict[str, str], list[CoverageCorrelationCheck]]:
    """Map an explicit node alias to a single node source_id (exact, 1:1).

    Ambiguous aliases produce a check and no mapping; no fuzzy or substring
    matching.
    """

    candidates: dict[str, list[str]] = {}
    for node in nodes or []:
        sid = str(getattr(node, "source_id", "") or "")
        for alias in list(getattr(node, "aliases", []) or []):
            alias = str(alias)
            if alias and sid:
                candidates.setdefault(alias, [])
                if sid not in candidates[alias]:
                    candidates[alias].append(sid)
    index: dict[str, str] = {}
    checks: list[CoverageCorrelationCheck] = []
    for alias, sids in candidates.items():
        if len(sids) == 1:
            index[alias] = sids[0]
        else:
            checks.append(_check(COVERAGE_CHECK_AMBIGUOUS_ALIAS, SEVERITY_WARNING,
                                 f"ambiguous explicit alias: {alias}", source_id=alias))
    return index, checks


# --- Coverage link builders -------------------------------------------------

def build_coverage_links_for_test_gap(
    test_gap: object,
    graph: object | None = None,
    local_validation_ids: list[str] | None = None,
    trace_receipt_ids: list[str] | None = None,
) -> tuple[list[LocalValidationCoverageLink], list[CoverageCorrelationCheck]]:
    """Build coverage links for one test gap from its explicit linked IDs only.

    Only the test gap's own ``linked_local_validation_ids`` /
    ``linked_trace_receipt_ids`` create links; supplied explicit IDs are used as a
    strict filter (an explicit ID not already referenced by the gap never invents
    a link). Resolves the gap's graph node when a graph is supplied.
    """

    links: list[LocalValidationCoverageLink] = []
    checks: list[CoverageCorrelationCheck] = []
    tgid = str(getattr(test_gap, "test_gap_id", "") or "")
    fid = str(getattr(test_gap, "function_id", "") or "")
    vpids = list(getattr(test_gap, "value_path_ids", []) or [])
    aids = list(getattr(test_gap, "assumption_ids", []) or [])
    tgt_vp = vpids[0] if vpids else ""
    tgt_asm = aids[0] if aids else ""

    target_node_id = ""
    graph_missing = graph is None
    if not graph_missing:
        node = build_graph_node_index(graph).get(tgid)
        if node is not None:
            target_node_id = str(getattr(node, "node_id", "") or "")
        elif tgid:
            checks.append(_check(COVERAGE_CHECK_UNRESOLVED_TEST_GAP_ID, SEVERITY_WARNING,
                                 f"test gap not found in graph: {tgid}", target_id=tgid))

    gap_lv = [x for x in (getattr(test_gap, "linked_local_validation_ids", []) or []) if x]
    gap_tr = [x for x in (getattr(test_gap, "linked_trace_receipt_ids", []) or []) if x]
    if local_validation_ids is not None:
        allowed = set(str(x) for x in local_validation_ids)
        gap_lv = [x for x in gap_lv if x in allowed]
    if trace_receipt_ids is not None:
        allowed_tr = set(str(x) for x in trace_receipt_ids)
        gap_tr = [x for x in gap_tr if x in allowed_tr]

    def _make(level: str, lv: str, tr: str, relationship: str) -> LocalValidationCoverageLink:
        link = LocalValidationCoverageLink(
            coverage_id=local_validation_coverage_id(lv, tr, tgid, fid, tgt_vp, tgt_asm, relationship),
            support_level=level, source_local_validation_id=lv, source_trace_receipt_id=tr,
            target_node_id=target_node_id, target_test_gap_id=tgid, target_function_id=fid,
            target_value_path_id=tgt_vp, target_assumption_id=tgt_asm, relationship=relationship,
            manual_review_required=True, ready_for_submission=False,
            metadata={"value_path_ids": list(vpids), "assumption_ids": list(aids)},
        )
        if graph_missing:
            link.warnings.append("no protocol graph supplied; target_node_id unresolved; context only")
        return link

    for lvid in sorted(set(gap_lv)):
        links.append(_make(COVERAGE_TESTED, str(lvid), "", "test-gap-tested-context-only"))
    for trid in sorted(set(gap_tr)):
        links.append(_make(COVERAGE_TRACE_BOUND, "", str(trid), "test-gap-trace-bound-context-only"))
    return links, checks


def _normalize_gaps(test_gaps: object) -> list[object]:
    items = getattr(test_gaps, "test_gaps", None)
    if items is None:
        items = test_gaps if isinstance(test_gaps, (list, tuple)) else []
    return list(items or [])


def correlate_local_validation_coverage(
    protocol_name: str,
    graph: object | None = None,
    test_gaps: object | None = None,
    local_validation_ids: list[str] | None = None,
    trace_receipt_ids: list[str] | None = None,
) -> LocalValidationCoverageSummary:
    """Correlate explicit local-validation/trace IDs with test gaps as context.

    Builds coverage links from each test gap's own explicit linked IDs (filtered
    by any supplied explicit IDs), records unresolved-reference checks, dedups and
    sorts, rolls up counts and linked IDs, and validates. Review context only:
    ``manual_review_required`` stays true and ``ready_for_submission`` stays false.
    """

    gaps = _normalize_gaps(test_gaps)
    all_links: list[LocalValidationCoverageLink] = []
    all_checks: list[CoverageCorrelationCheck] = []
    for gap in gaps:
        links, checks = build_coverage_links_for_test_gap(gap, graph, local_validation_ids, trace_receipt_ids)
        all_links.extend(links)
        all_checks.extend(checks)

    # Explicit IDs supplied but never referenced by any gap -> a single bounded
    # missing-explicit-link check (non-invention: no link is fabricated).
    if local_validation_ids:
        linked_lv = {l.source_local_validation_id for l in all_links if l.source_local_validation_id}
        for lvid in sorted(set(str(x) for x in local_validation_ids) - linked_lv):
            all_checks.append(_check(COVERAGE_CHECK_MISSING_EXPLICIT_LINK, SEVERITY_WARNING,
                                     f"supplied local-validation id has no explicit test-gap link: {lvid}",
                                     source_id=lvid))
    if trace_receipt_ids:
        linked_tr = {l.source_trace_receipt_id for l in all_links if l.source_trace_receipt_id}
        for trid in sorted(set(str(x) for x in trace_receipt_ids) - linked_tr):
            all_checks.append(_check(COVERAGE_CHECK_MISSING_EXPLICIT_LINK, SEVERITY_WARNING,
                                     f"supplied trace-receipt id has no explicit test-gap link: {trid}",
                                     source_id=trid))

    links, dup_checks = deduplicate_coverage_links(all_links)
    all_checks.extend(dup_checks)

    lv_ids = sorted({l.source_local_validation_id for l in links if l.source_local_validation_id})
    tr_ids = sorted({l.source_trace_receipt_id for l in links if l.source_trace_receipt_id})
    gap_ids = sorted({l.target_test_gap_id for l in links if l.target_test_gap_id})
    fn_ids = sorted({l.target_function_id for l in links if l.target_function_id})
    vp_ids = sorted({l.target_value_path_id for l in links if l.target_value_path_id})
    asm_ids = sorted({l.target_assumption_id for l in links if l.target_assumption_id})

    summary = LocalValidationCoverageSummary(
        protocol_name=str(protocol_name or "").strip(),
        coverage_links=links,
        coverage_count=len(links),
        tested_count=sum(1 for l in links if l.support_level == COVERAGE_TESTED),
        trace_bound_count=sum(1 for l in links if l.support_level == COVERAGE_TRACE_BOUND),
        linked_local_validation_ids=lv_ids,
        linked_trace_receipt_ids=tr_ids,
        linked_test_gap_ids=gap_ids,
        linked_function_ids=fn_ids,
        linked_value_path_ids=vp_ids,
        linked_assumption_ids=asm_ids,
        manual_review_required=True,
        ready_for_submission=False,
    )
    summary.coverage_summary_id = local_validation_coverage_summary_id(
        protocol_name, [l.coverage_id for l in links])
    structural = validate_coverage_summary(summary)
    summary.checks = _sort_checks(all_checks + structural)
    summary.unresolved_count = sum(1 for c in summary.checks if c.check_kind in _UNRESOLVED_CHECK_KINDS)
    return summary


# --- Apply coverage to a test gap (pure copy) -------------------------------

def apply_coverage_to_test_gap(test_gap: object, coverage_links: list[LocalValidationCoverageLink]) -> object:
    """Return a copy of ``test_gap`` with coverage context applied (no mutation).

    Trace-bound coverage may set ``TEST_GAP_TRACE_BOUND``; otherwise tested
    coverage may set ``TEST_GAP_LOCALLY_TESTED``. Linked IDs and coverage notes
    are added. The gap is never marked resolved: a passing local test does not
    prove safety and missing coverage does not prove a vulnerability.
    ``manual_review_required`` stays true and ``ready_for_submission`` stays false.
    """

    gap = copy.deepcopy(test_gap)
    tgid = str(getattr(gap, "test_gap_id", "") or "")
    relevant = [l for l in (coverage_links or []) if l.target_test_gap_id == tgid]
    lv_ids = sorted({l.source_local_validation_id for l in relevant if l.source_local_validation_id})
    tr_ids = sorted({l.source_trace_receipt_id for l in relevant if l.source_trace_receipt_id})
    has_tested = any(l.support_level == COVERAGE_TESTED for l in relevant)
    has_trace = any(l.support_level == COVERAGE_TRACE_BOUND for l in relevant)

    if lv_ids:
        gap.linked_local_validation_ids = sorted(set(getattr(gap, "linked_local_validation_ids", []) or []) | set(lv_ids))
    if tr_ids:
        gap.linked_trace_receipt_ids = sorted(set(getattr(gap, "linked_trace_receipt_ids", []) or []) | set(tr_ids))

    if has_trace:
        gap.gap_status = TEST_GAP_TRACE_BOUND
        note = "trace-receipt coverage referenced as context (not final proof; manual review required)"
        if note not in gap.coverage_notes:
            gap.coverage_notes.append(note)
    elif has_tested:
        gap.gap_status = TEST_GAP_LOCALLY_TESTED
        note = "local-validation coverage referenced as context (passing local tests do not prove safety; manual review required)"
        if note not in gap.coverage_notes:
            gap.coverage_notes.append(note)

    gap.manual_review_required = True
    gap.ready_for_submission = False
    return gap


# --- Dedup + validation -----------------------------------------------------

def deduplicate_coverage_links(links: list[LocalValidationCoverageLink]) -> tuple[list[LocalValidationCoverageLink], list[CoverageCorrelationCheck]]:
    """Keep the first link per coverage_id (deterministic), checking duplicates."""

    seen: dict[str, LocalValidationCoverageLink] = {}
    checks: list[CoverageCorrelationCheck] = []
    for link in links or []:
        if link.coverage_id in seen:
            checks.append(_check(COVERAGE_CHECK_DUPLICATE_COVERAGE_ID, SEVERITY_WARNING,
                                 f"duplicate coverage id: {link.coverage_id}", coverage_id=link.coverage_id))
            continue
        seen[link.coverage_id] = link
    ordered = sorted(seen.values(), key=lambda l: (l.support_level, l.target_test_gap_id,
                                                    l.source_local_validation_id, l.source_trace_receipt_id, l.coverage_id))
    return ordered, checks


def _sort_checks(checks: list[CoverageCorrelationCheck]) -> list[CoverageCorrelationCheck]:
    rank = {SEVERITY_ERROR: 0, SEVERITY_WARNING: 1}
    seen: dict[str, CoverageCorrelationCheck] = {}
    for c in checks:
        seen.setdefault(c.check_id, c)
    return sorted(seen.values(), key=lambda c: (rank.get(c.severity, 9), c.check_kind, c.check_id))


def validate_coverage_summary(summary: LocalValidationCoverageSummary) -> list[CoverageCorrelationCheck]:
    """Deterministic structural checks over a coverage summary (review context).

    Duplicate coverage IDs, unknown support levels, and missing targets are
    warnings; a ``ready_for_submission`` true flag, a ``HUMAN_REVIEWED`` token, or
    forbidden finality wording is a safety error. No check proves safety or a
    vulnerability.
    """

    checks: list[CoverageCorrelationCheck] = []
    seen_ids: set[str] = set()
    for link in list(summary.coverage_links or []):
        if link.coverage_id in seen_ids:
            checks.append(_check(COVERAGE_CHECK_DUPLICATE_COVERAGE_ID, SEVERITY_WARNING,
                                 f"duplicate coverage id: {link.coverage_id}", coverage_id=link.coverage_id))
        seen_ids.add(link.coverage_id)
        if link.support_level not in COVERAGE_SUPPORT_LEVELS:
            checks.append(_check(COVERAGE_CHECK_MISSING_EXPLICIT_LINK, SEVERITY_WARNING,
                                 f"unknown coverage support level: {link.support_level}", coverage_id=link.coverage_id))
        if not (link.target_test_gap_id or link.target_node_id or link.target_function_id
                or link.target_value_path_id or link.target_assumption_id):
            checks.append(_check(COVERAGE_CHECK_MISSING_EXPLICIT_LINK, SEVERITY_WARNING,
                                 "coverage link has no resolvable target", coverage_id=link.coverage_id))

    blob = json.dumps(coverage_to_dict(summary), sort_keys=True).lower()
    if '"ready_for_submission": true' in blob or '"ready_for_submission":true' in blob:
        checks.append(_check(COVERAGE_CHECK_READY_FOR_SUBMISSION_TRUE, SEVERITY_ERROR,
                             "ready_for_submission is true somewhere in the coverage summary"))
    if "human_reviewed" in blob:
        checks.append(_check(COVERAGE_CHECK_FORBIDDEN_FINALITY_WORDING, SEVERITY_ERROR,
                             "a human-reviewed status is present in the coverage summary"))
    for token in _FORBIDDEN_WORDING:
        if token in blob:
            checks.append(_check(COVERAGE_CHECK_FORBIDDEN_FINALITY_WORDING, SEVERITY_ERROR,
                                 f"forbidden finality wording present: {token}"))
    return checks


# --- Serialization ----------------------------------------------------------

def coverage_to_dict(value: object) -> object:
    """Recursively serialize coverage dataclasses to plain JSON-ready data.

    Dataclasses become dicts, lists/tuples become lists, dicts are walked, and
    primitives / ``None`` pass through. Unsupported objects raise ``TypeError``.
    Does not mutate the source.
    """

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: coverage_to_dict(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {key: coverage_to_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [coverage_to_dict(item) for item in value]
    raise TypeError(f"unsupported value for coverage_to_dict: {type(value).__name__}")
