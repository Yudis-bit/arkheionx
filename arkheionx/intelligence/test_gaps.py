"""Internal test-gap engine and deterministic test-gap IDs (v3.8, additive).

This module derives controlled test gaps for a function from its Agent 2 roles,
its Agent 3 value-path kinds, and its Agent 4 assumption categories. A test gap
is a review suggestion to add or strengthen a local test, never a claim that a
bug exists. It is internal infrastructure: no filesystem, network, subprocess,
CLI, or live-chain behavior, and importing it has no side effects.

Test gaps are review surface only. A missing test never proves a vulnerability,
and a passing local test never proves safety. Local-validation correlation is
context only and is applied solely when explicit IDs are supplied. Every record
keeps ``manual_review_required`` true and ``ready_for_submission`` false, never
emits a human-reviewed status, and never asserts a confirmed vulnerability, a
final severity, an audit outcome, or bounty eligibility. Mapping is exact (no
fuzzy or substring matching) and invents no coverage.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass, field, fields, is_dataclass

_HASH_LEN = 12

# --- Controlled test-gap categories -----------------------------------------

MISSING_POSITIVE_PATH_TEST = "MISSING_POSITIVE_PATH_TEST"
MISSING_NEGATIVE_PATH_TEST = "MISSING_NEGATIVE_PATH_TEST"
MISSING_ACCESS_CONTROL_TEST = "MISSING_ACCESS_CONTROL_TEST"
MISSING_REENTRANCY_TEST = "MISSING_REENTRANCY_TEST"
MISSING_ORACLE_STALE_TEST = "MISSING_ORACLE_STALE_TEST"
MISSING_ORACLE_MANIPULATION_TEST = "MISSING_ORACLE_MANIPULATION_TEST"
MISSING_PAUSE_EMERGENCY_TEST = "MISSING_PAUSE_EMERGENCY_TEST"
MISSING_INVARIANT_TEST = "MISSING_INVARIANT_TEST"
MISSING_VALUE_CONSERVATION_TEST = "MISSING_VALUE_CONSERVATION_TEST"
MISSING_LIQUIDATION_EDGE_CASE_TEST = "MISSING_LIQUIDATION_EDGE_CASE_TEST"
MISSING_EXTERNAL_CALL_FAILURE_TEST = "MISSING_EXTERNAL_CALL_FAILURE_TEST"
MISSING_UPGRADE_PROXY_TEST = "MISSING_UPGRADE_PROXY_TEST"
MISSING_ROLE_QUORUM_TEST = "MISSING_ROLE_QUORUM_TEST"
MISSING_SLIPPAGE_BOUNDS_TEST = "MISSING_SLIPPAGE_BOUNDS_TEST"
MISSING_FEE_CALCULATION_TEST = "MISSING_FEE_CALCULATION_TEST"
MISSING_BRIDGE_FINALITY_TEST = "MISSING_BRIDGE_FINALITY_TEST"
MISSING_REWARD_ACCOUNTING_TEST = "MISSING_REWARD_ACCOUNTING_TEST"
MISSING_DELEGATECALL_TARGET_TEST = "MISSING_DELEGATECALL_TARGET_TEST"
MISSING_VIEW_CALCULATION_TEST = "MISSING_VIEW_CALCULATION_TEST"
UNCLASSIFIED_TEST_GAP = "UNCLASSIFIED_TEST_GAP"

TEST_GAP_CATEGORY_VALUES: tuple[str, ...] = (
    MISSING_ACCESS_CONTROL_TEST,
    MISSING_UPGRADE_PROXY_TEST,
    MISSING_DELEGATECALL_TARGET_TEST,
    MISSING_ROLE_QUORUM_TEST,
    MISSING_ORACLE_MANIPULATION_TEST,
    MISSING_ORACLE_STALE_TEST,
    MISSING_LIQUIDATION_EDGE_CASE_TEST,
    MISSING_REENTRANCY_TEST,
    MISSING_VALUE_CONSERVATION_TEST,
    MISSING_BRIDGE_FINALITY_TEST,
    MISSING_PAUSE_EMERGENCY_TEST,
    MISSING_INVARIANT_TEST,
    MISSING_EXTERNAL_CALL_FAILURE_TEST,
    MISSING_SLIPPAGE_BOUNDS_TEST,
    MISSING_FEE_CALCULATION_TEST,
    MISSING_REWARD_ACCOUNTING_TEST,
    MISSING_NEGATIVE_PATH_TEST,
    MISSING_POSITIVE_PATH_TEST,
    MISSING_VIEW_CALCULATION_TEST,
    UNCLASSIFIED_TEST_GAP,
)

TEST_GAP_CATEGORY_DESCRIPTIONS: dict[str, str] = {
    MISSING_POSITIVE_PATH_TEST: "A happy-path test of the intended behavior appears missing.",
    MISSING_NEGATIVE_PATH_TEST: "A negative / revert-path test (bad input, bounds) appears missing.",
    MISSING_ACCESS_CONTROL_TEST: "A test that unauthorized callers are rejected appears missing.",
    MISSING_REENTRANCY_TEST: "A re-entrancy / reentrant-callback test appears missing.",
    MISSING_ORACLE_STALE_TEST: "A stale / outdated oracle rejection test appears missing.",
    MISSING_ORACLE_MANIPULATION_TEST: "An oracle / spot-price manipulation test appears missing.",
    MISSING_PAUSE_EMERGENCY_TEST: "A pause / unpause / emergency behavior test appears missing.",
    MISSING_INVARIANT_TEST: "An accounting / protocol invariant test appears missing.",
    MISSING_VALUE_CONSERVATION_TEST: "A value-conservation (balances vs transfers) test appears missing.",
    MISSING_LIQUIDATION_EDGE_CASE_TEST: "A liquidation / health-threshold edge-case test appears missing.",
    MISSING_EXTERNAL_CALL_FAILURE_TEST: "A failed / reverting external-call handling test appears missing.",
    MISSING_UPGRADE_PROXY_TEST: "An upgrade / proxy storage-compatibility test appears missing.",
    MISSING_ROLE_QUORUM_TEST: "A role-separation / signer-quorum test appears missing.",
    MISSING_SLIPPAGE_BOUNDS_TEST: "A slippage / minimum-output bound test appears missing.",
    MISSING_FEE_CALCULATION_TEST: "A fee-calculation / fee-bound test appears missing.",
    MISSING_BRIDGE_FINALITY_TEST: "A bridge finality / replay-protection test appears missing.",
    MISSING_REWARD_ACCOUNTING_TEST: "A reward-accounting (double-claim, monotonicity) test appears missing.",
    MISSING_DELEGATECALL_TARGET_TEST: "A delegatecall target / storage-safety test appears missing.",
    MISSING_VIEW_CALCULATION_TEST: "A view / pure calculation-consistency test appears missing.",
    UNCLASSIFIED_TEST_GAP: "No controlled test-gap category mapped; manual review required.",
}

_CATEGORY_TITLES: dict[str, str] = {
    MISSING_POSITIVE_PATH_TEST: "Add a positive-path test",
    MISSING_NEGATIVE_PATH_TEST: "Add a negative-path test",
    MISSING_ACCESS_CONTROL_TEST: "Add an access-control test",
    MISSING_REENTRANCY_TEST: "Add a reentrancy test",
    MISSING_ORACLE_STALE_TEST: "Add a stale-oracle test",
    MISSING_ORACLE_MANIPULATION_TEST: "Add an oracle-manipulation test",
    MISSING_PAUSE_EMERGENCY_TEST: "Add a pause/emergency test",
    MISSING_INVARIANT_TEST: "Add an invariant test",
    MISSING_VALUE_CONSERVATION_TEST: "Add a value-conservation test",
    MISSING_LIQUIDATION_EDGE_CASE_TEST: "Add a liquidation edge-case test",
    MISSING_EXTERNAL_CALL_FAILURE_TEST: "Add an external-call-failure test",
    MISSING_UPGRADE_PROXY_TEST: "Add an upgrade/proxy test",
    MISSING_ROLE_QUORUM_TEST: "Add a role/quorum test",
    MISSING_SLIPPAGE_BOUNDS_TEST: "Add a slippage-bounds test",
    MISSING_FEE_CALCULATION_TEST: "Add a fee-calculation test",
    MISSING_BRIDGE_FINALITY_TEST: "Add a bridge-finality test",
    MISSING_REWARD_ACCOUNTING_TEST: "Add a reward-accounting test",
    MISSING_DELEGATECALL_TARGET_TEST: "Add a delegatecall-target test",
    MISSING_VIEW_CALCULATION_TEST: "Add a view-calculation test",
    UNCLASSIFIED_TEST_GAP: "Unclassified test gap",
}

# --- Gap status (non-overclaim) ---------------------------------------------

TEST_GAP_OPEN = "TEST_GAP_OPEN"
TEST_GAP_PARTIALLY_COVERED = "TEST_GAP_PARTIALLY_COVERED"
TEST_GAP_LOCALLY_TESTED = "TEST_GAP_LOCALLY_TESTED"
TEST_GAP_TRACE_BOUND = "TEST_GAP_TRACE_BOUND"
TEST_GAP_NEEDS_HUMAN_REVIEW = "TEST_GAP_NEEDS_HUMAN_REVIEW"
TEST_GAP_UNCLASSIFIED = "TEST_GAP_UNCLASSIFIED"

TEST_GAP_STATUS_VALUES: tuple[str, ...] = (
    TEST_GAP_OPEN,
    TEST_GAP_PARTIALLY_COVERED,
    TEST_GAP_LOCALLY_TESTED,
    TEST_GAP_TRACE_BOUND,
    TEST_GAP_NEEDS_HUMAN_REVIEW,
    TEST_GAP_UNCLASSIFIED,
)

# Coverage strength order (higher = stronger local context, never safety proof).
_STATUS_RANK: dict[str, int] = {
    TEST_GAP_UNCLASSIFIED: 0,
    TEST_GAP_NEEDS_HUMAN_REVIEW: 0,
    TEST_GAP_OPEN: 0,
    TEST_GAP_PARTIALLY_COVERED: 1,
    TEST_GAP_LOCALLY_TESTED: 2,
    TEST_GAP_TRACE_BOUND: 3,
}

# --- Structural review priority (never final severity) ----------------------

GAP_PRIORITY_UNKNOWN = "GAP_PRIORITY_UNKNOWN"
GAP_PRIORITY_LOW = "GAP_PRIORITY_LOW"
GAP_PRIORITY_MEDIUM = "GAP_PRIORITY_MEDIUM"
GAP_PRIORITY_HIGH = "GAP_PRIORITY_HIGH"
GAP_PRIORITY_CRITICAL_REVIEW = "GAP_PRIORITY_CRITICAL_REVIEW"

GAP_PRIORITY_VALUES: tuple[str, ...] = (
    GAP_PRIORITY_UNKNOWN,
    GAP_PRIORITY_LOW,
    GAP_PRIORITY_MEDIUM,
    GAP_PRIORITY_HIGH,
    GAP_PRIORITY_CRITICAL_REVIEW,
)

_PRIORITY_RANK: dict[str, int] = {p: i for i, p in enumerate(GAP_PRIORITY_VALUES)}

_CATEGORY_PRIORITY: dict[str, str] = {
    MISSING_ACCESS_CONTROL_TEST: GAP_PRIORITY_CRITICAL_REVIEW,
    MISSING_UPGRADE_PROXY_TEST: GAP_PRIORITY_CRITICAL_REVIEW,
    MISSING_DELEGATECALL_TARGET_TEST: GAP_PRIORITY_CRITICAL_REVIEW,
    MISSING_ROLE_QUORUM_TEST: GAP_PRIORITY_HIGH,
    MISSING_ORACLE_MANIPULATION_TEST: GAP_PRIORITY_HIGH,
    MISSING_ORACLE_STALE_TEST: GAP_PRIORITY_HIGH,
    MISSING_LIQUIDATION_EDGE_CASE_TEST: GAP_PRIORITY_HIGH,
    MISSING_REENTRANCY_TEST: GAP_PRIORITY_HIGH,
    MISSING_VALUE_CONSERVATION_TEST: GAP_PRIORITY_HIGH,
    MISSING_BRIDGE_FINALITY_TEST: GAP_PRIORITY_HIGH,
    MISSING_PAUSE_EMERGENCY_TEST: GAP_PRIORITY_MEDIUM,
    MISSING_INVARIANT_TEST: GAP_PRIORITY_MEDIUM,
    MISSING_EXTERNAL_CALL_FAILURE_TEST: GAP_PRIORITY_MEDIUM,
    MISSING_SLIPPAGE_BOUNDS_TEST: GAP_PRIORITY_MEDIUM,
    MISSING_FEE_CALCULATION_TEST: GAP_PRIORITY_MEDIUM,
    MISSING_REWARD_ACCOUNTING_TEST: GAP_PRIORITY_MEDIUM,
    MISSING_NEGATIVE_PATH_TEST: GAP_PRIORITY_MEDIUM,
    MISSING_POSITIVE_PATH_TEST: GAP_PRIORITY_LOW,
    MISSING_VIEW_CALCULATION_TEST: GAP_PRIORITY_LOW,
    UNCLASSIFIED_TEST_GAP: GAP_PRIORITY_UNKNOWN,
}

_CATEGORY_PRIORITY_INDEX: dict[str, int] = {c: i for i, c in enumerate(TEST_GAP_CATEGORY_VALUES)}


# --- ID + canonical hashing -------------------------------------------------

def canonical_test_gap_seed(value: object) -> str:
    """Canonical JSON seed; raises ``TypeError`` for non-JSON-native seeds."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _short_hash(value: object) -> str:
    return hashlib.sha256(canonical_test_gap_seed(value).encode("utf-8")).hexdigest()[:_HASH_LEN]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")


def protocol_test_gap_id(
    category: str,
    function_id: str = "",
    value_path_ids: list[str] | None = None,
    assumption_ids: list[str] | None = None,
    title: str = "",
    contract_name: str = "",
    function_name: str = "",
) -> str:
    """Deterministic test-gap ID. ``value_path_ids`` / ``assumption_ids`` sorted."""

    cat = str(category or "").strip()
    if not cat:
        raise ValueError("protocol_test_gap_id requires a non-empty category")
    seed = {
        "category": cat,
        "function_id": str(function_id or "").strip(),
        "value_path_ids": sorted(str(v) for v in (value_path_ids or [])),
        "assumption_ids": sorted(str(a) for a in (assumption_ids or [])),
        "title": str(title or "").strip(),
        "contract_name": str(contract_name or "").strip(),
        "function_name": str(function_name or "").strip(),
    }
    return f"protocol-test-gap:{_slug(cat)}:{_short_hash(seed)}"


def test_gap_set_id(protocol_name: str, test_gap_ids: list[str]) -> str:
    """Deterministic test-gap-set ID. ``test_gap_ids`` sorted before hashing."""

    name = str(protocol_name or "").strip()
    if not name:
        raise ValueError("test_gap_set_id requires a non-empty protocol_name")
    seed = {"protocol_name": name, "test_gap_ids": sorted(str(t) for t in (test_gap_ids or []))}
    return f"test-gap-set:{_slug(name)}:{_short_hash(seed)}"


# --- Dataclasses ------------------------------------------------------------

@dataclass
class ProtocolTestGap:
    test_gap_id: str = ""
    category: str = UNCLASSIFIED_TEST_GAP
    title: str = ""
    description: str = ""
    gap_status: str = TEST_GAP_OPEN
    priority: str = GAP_PRIORITY_UNKNOWN
    function_id: str = ""
    function_name: str = ""
    contract_name: str = ""
    function_roles: list[str] = field(default_factory=list)
    value_path_ids: list[str] = field(default_factory=list)
    value_path_kinds: list[str] = field(default_factory=list)
    assumption_ids: list[str] = field(default_factory=list)
    assumption_categories: list[str] = field(default_factory=list)
    linked_function_ids: list[str] = field(default_factory=list)
    linked_value_path_ids: list[str] = field(default_factory=list)
    linked_assumption_ids: list[str] = field(default_factory=list)
    linked_local_validation_ids: list[str] = field(default_factory=list)
    linked_trace_receipt_ids: list[str] = field(default_factory=list)
    coverage_notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class TestGapSet:
    test_gap_set_id: str = ""
    protocol_name: str = ""
    test_gaps: list[ProtocolTestGap] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    open_gap_count: int = 0
    locally_tested_gap_count: int = 0
    trace_bound_gap_count: int = 0
    linked_function_ids: list[str] = field(default_factory=list)
    linked_value_path_ids: list[str] = field(default_factory=list)
    linked_assumption_ids: list[str] = field(default_factory=list)
    linked_local_validation_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


# --- Mapping tables ---------------------------------------------------------

_ROLE_TO_CATEGORIES: dict[str, tuple[str, ...]] = {
    "INFLOW": (MISSING_POSITIVE_PATH_TEST, MISSING_VALUE_CONSERVATION_TEST),
    "OUTFLOW": (MISSING_NEGATIVE_PATH_TEST, MISSING_VALUE_CONSERVATION_TEST, MISSING_REENTRANCY_TEST),
    "ACCOUNTING_MUTATION": (MISSING_INVARIANT_TEST, MISSING_VALUE_CONSERVATION_TEST),
    "EXTERNAL_CALL": (MISSING_EXTERNAL_CALL_FAILURE_TEST, MISSING_REENTRANCY_TEST),
    "ORACLE_CONSUMER": (MISSING_ORACLE_STALE_TEST, MISSING_ORACLE_MANIPULATION_TEST),
    "ORACLE_SETTER": (MISSING_ACCESS_CONTROL_TEST, MISSING_ORACLE_STALE_TEST),
    "ADMIN_PARAM": (MISSING_ACCESS_CONTROL_TEST, MISSING_NEGATIVE_PATH_TEST),
    "ACCESS_CONTROL": (MISSING_ACCESS_CONTROL_TEST, MISSING_ROLE_QUORUM_TEST),
    "PAUSE_EMERGENCY": (MISSING_PAUSE_EMERGENCY_TEST, MISSING_ACCESS_CONTROL_TEST),
    "UPGRADE_PROXY": (MISSING_UPGRADE_PROXY_TEST, MISSING_ACCESS_CONTROL_TEST),
    "DELEGATECALL": (MISSING_DELEGATECALL_TARGET_TEST, MISSING_UPGRADE_PROXY_TEST),
    "BORROW_REPAY": (MISSING_POSITIVE_PATH_TEST, MISSING_NEGATIVE_PATH_TEST, MISSING_INVARIANT_TEST),
    "LIQUIDATION": (MISSING_LIQUIDATION_EDGE_CASE_TEST, MISSING_ORACLE_STALE_TEST, MISSING_INVARIANT_TEST),
    "SWAP": (MISSING_SLIPPAGE_BOUNDS_TEST, MISSING_EXTERNAL_CALL_FAILURE_TEST),
    "MINT_BURN": (MISSING_INVARIANT_TEST, MISSING_VALUE_CONSERVATION_TEST),
    "CLAIM_REWARD": (MISSING_REWARD_ACCOUNTING_TEST, MISSING_VALUE_CONSERVATION_TEST),
    "BRIDGE": (MISSING_BRIDGE_FINALITY_TEST, MISSING_ROLE_QUORUM_TEST),
    "VIEW_PURE": (MISSING_VIEW_CALCULATION_TEST,),
    "UNCLASSIFIED": (UNCLASSIFIED_TEST_GAP,),
}

_PATH_KIND_TO_CATEGORIES: dict[str, tuple[str, ...]] = {
    "VALUE_INFLOW": (MISSING_POSITIVE_PATH_TEST, MISSING_VALUE_CONSERVATION_TEST),
    "VALUE_OUTFLOW": (MISSING_NEGATIVE_PATH_TEST, MISSING_VALUE_CONSERVATION_TEST, MISSING_REENTRANCY_TEST),
    "ACCOUNTING_MUTATION_PATH": (MISSING_INVARIANT_TEST, MISSING_VALUE_CONSERVATION_TEST),
    "EXTERNAL_CALL_PATH": (MISSING_EXTERNAL_CALL_FAILURE_TEST, MISSING_REENTRANCY_TEST),
    "ORACLE_DEPENDENT_PATH": (MISSING_ORACLE_STALE_TEST, MISSING_ORACLE_MANIPULATION_TEST),
    "AUTHORITY_PATH": (MISSING_ACCESS_CONTROL_TEST, MISSING_ROLE_QUORUM_TEST),
    "EMERGENCY_PATH": (MISSING_PAUSE_EMERGENCY_TEST, MISSING_ACCESS_CONTROL_TEST),
    "UPGRADE_PATH": (MISSING_UPGRADE_PROXY_TEST, MISSING_DELEGATECALL_TARGET_TEST),
    "LIQUIDATION_PATH": (MISSING_LIQUIDATION_EDGE_CASE_TEST, MISSING_ORACLE_STALE_TEST),
    "SWAP_PATH": (MISSING_SLIPPAGE_BOUNDS_TEST, MISSING_EXTERNAL_CALL_FAILURE_TEST),
    "BRIDGE_PATH": (MISSING_BRIDGE_FINALITY_TEST, MISSING_ROLE_QUORUM_TEST),
    "REWARD_PATH": (MISSING_REWARD_ACCOUNTING_TEST, MISSING_VALUE_CONSERVATION_TEST),
    "VIEW_ONLY_PATH": (MISSING_VIEW_CALCULATION_TEST,),
    "UNCLASSIFIED_PATH": (UNCLASSIFIED_TEST_GAP,),
}

_ASSUMPTION_CATEGORY_TO_GAP: dict[str, str] = {
    "ORACLE_FRESHNESS": MISSING_ORACLE_STALE_TEST,
    "ORACLE_MANIPULATION_RESISTANCE": MISSING_ORACLE_MANIPULATION_TEST,
    "ACCOUNTING_INVARIANT": MISSING_INVARIANT_TEST,
    "BALANCE_CONSERVATION": MISSING_VALUE_CONSERVATION_TEST,
    "ACCESS_CONTROL_CORRECTNESS": MISSING_ACCESS_CONTROL_TEST,
    "ROLE_SEPARATION": MISSING_ROLE_QUORUM_TEST,
    "REENTRANCY_PROTECTION": MISSING_REENTRANCY_TEST,
    "EXTERNAL_TOKEN_BEHAVIOR": MISSING_EXTERNAL_CALL_FAILURE_TEST,
    "PAUSE_EMERGENCY_BEHAVIOR": MISSING_PAUSE_EMERGENCY_TEST,
    "UPGRADE_SAFETY": MISSING_UPGRADE_PROXY_TEST,
    "LIQUIDATION_THRESHOLD_CORRECTNESS": MISSING_LIQUIDATION_EDGE_CASE_TEST,
    "SLIPPAGE_BOUND": MISSING_SLIPPAGE_BOUNDS_TEST,
    "FEE_CORRECTNESS": MISSING_FEE_CALCULATION_TEST,
    "BRIDGE_FINALITY": MISSING_BRIDGE_FINALITY_TEST,
    "SIGNER_QUORUM_INTEGRITY": MISSING_ROLE_QUORUM_TEST,
    "REWARD_ACCOUNTING_CORRECTNESS": MISSING_REWARD_ACCOUNTING_TEST,
    "DELEGATECALL_TARGET_SAFETY": MISSING_DELEGATECALL_TARGET_TEST,
    "VIEW_CALCULATION_CONSISTENCY": MISSING_VIEW_CALCULATION_TEST,
    "UNCLASSIFIED_ASSUMPTION": UNCLASSIFIED_TEST_GAP,
}


def _order_categories(categories) -> list[str]:
    return sorted(
        {c for c in categories if c},
        key=lambda c: _CATEGORY_PRIORITY_INDEX.get(c, len(TEST_GAP_CATEGORY_VALUES)),
    )


def priority_for_test_gap_category(category: str) -> str:
    """Return the structural review priority for a category (never final severity)."""

    return _CATEGORY_PRIORITY.get(str(category or "").strip(), GAP_PRIORITY_UNKNOWN)


def test_gap_categories_for_roles(roles: list[str]) -> list[str]:
    """Map controlled roles to test-gap categories (exact, priority-ordered)."""

    collected: list[str] = []
    for role in roles or []:
        collected.extend(_ROLE_TO_CATEGORIES.get(str(role or "").strip(), (UNCLASSIFIED_TEST_GAP,)))
    return _order_categories(collected)


def test_gap_categories_for_value_path_kinds(path_kinds: list[str]) -> list[str]:
    """Map controlled value-path kinds to test-gap categories (exact, ordered)."""

    collected: list[str] = []
    for kind in path_kinds or []:
        collected.extend(_PATH_KIND_TO_CATEGORIES.get(str(kind or "").strip(), (UNCLASSIFIED_TEST_GAP,)))
    return _order_categories(collected)


def test_gap_categories_for_assumption_categories(categories: list[str]) -> list[str]:
    """Map controlled assumption categories to test-gap categories (exact)."""

    collected: list[str] = []
    for cat in categories or []:
        collected.append(_ASSUMPTION_CATEGORY_TO_GAP.get(str(cat or "").strip(), UNCLASSIFIED_TEST_GAP))
    return _order_categories(collected)


def _make_gap(
    category: str,
    *,
    function_id: str = "",
    function_name: str = "",
    contract_name: str = "",
    function_roles: list[str] | None = None,
    value_path_ids: list[str] | None = None,
    value_path_kinds: list[str] | None = None,
    assumption_ids: list[str] | None = None,
    assumption_categories: list[str] | None = None,
    warnings: list[str] | None = None,
) -> ProtocolTestGap:
    vpids = list(value_path_ids or [])
    aids = list(assumption_ids or [])
    warn = list(warnings or [])
    status = TEST_GAP_UNCLASSIFIED if category == UNCLASSIFIED_TEST_GAP else TEST_GAP_OPEN
    if category == UNCLASSIFIED_TEST_GAP:
        warn.append("unclassified test gap (no controlled category mapped); manual review required")
    return ProtocolTestGap(
        test_gap_id=protocol_test_gap_id(
            category, function_id, vpids, aids, _CATEGORY_TITLES.get(category, ""), contract_name, function_name),
        category=category,
        title=_CATEGORY_TITLES.get(category, ""),
        description=TEST_GAP_CATEGORY_DESCRIPTIONS.get(category, ""),
        gap_status=status,
        priority=priority_for_test_gap_category(category),
        function_id=str(function_id or ""),
        function_name=str(function_name or ""),
        contract_name=str(contract_name or ""),
        function_roles=list(function_roles or []),
        value_path_ids=vpids,
        value_path_kinds=list(value_path_kinds or []),
        assumption_ids=aids,
        assumption_categories=list(assumption_categories or []),
        linked_function_ids=[function_id] if function_id else [],
        linked_value_path_ids=list(vpids),
        linked_assumption_ids=list(aids),
        coverage_notes=[],
        warnings=warn,
        manual_review_required=True,
        ready_for_submission=False,
        metadata={},
    )


def build_test_gaps_from_roles(
    function_roles: list[str],
    function_id: str = "",
    function_name: str = "",
    contract_name: str = "",
) -> list[ProtocolTestGap]:
    """Build one test gap per mapped category for a function's roles."""

    roles = list(function_roles or [])
    unknown = [r for r in roles if r and r not in _ROLE_TO_CATEGORIES]
    categories = test_gap_categories_for_roles(roles) or [UNCLASSIFIED_TEST_GAP]
    out: list[ProtocolTestGap] = []
    for category in categories:
        warn = []
        if unknown and category == UNCLASSIFIED_TEST_GAP:
            warn.append("unknown role(s) mapped to unclassified test gap: " + ", ".join(sorted(unknown)))
        out.append(_make_gap(
            category, function_id=function_id, function_name=function_name,
            contract_name=contract_name, function_roles=roles, warnings=warn))
    return out


def build_test_gaps_from_value_path(value_path: object) -> list[ProtocolTestGap]:
    """Build test gaps for a :class:`ValuePath`, preserving its exact links."""

    path_kinds = list((getattr(value_path, "metadata", {}) or {}).get("path_kinds", []) or [])
    if not path_kinds:
        primary = str(getattr(value_path, "path_kind", "") or "")
        path_kinds = [primary] if primary else []
    unknown = [k for k in path_kinds if k and k not in _PATH_KIND_TO_CATEGORIES]
    categories = test_gap_categories_for_value_path_kinds(path_kinds) or [UNCLASSIFIED_TEST_GAP]
    pid = str(getattr(value_path, "path_id", "") or "")
    fid = str(getattr(value_path, "function_id", "") or "")
    fname = str(getattr(value_path, "function_name", "") or "")
    cname = str(getattr(value_path, "contract_name", "") or "")
    roles = list(getattr(value_path, "roles", []) or [])
    out: list[ProtocolTestGap] = []
    for category in categories:
        warn = []
        if unknown and category == UNCLASSIFIED_TEST_GAP:
            warn.append("unknown value-path kind(s) mapped to unclassified test gap: " + ", ".join(sorted(unknown)))
        out.append(_make_gap(
            category, function_id=fid, function_name=fname, contract_name=cname,
            function_roles=roles, value_path_ids=[pid] if pid else [],
            value_path_kinds=path_kinds, warnings=warn))
    return out


def build_test_gaps_from_assumption(assumption: object) -> list[ProtocolTestGap]:
    """Build test gaps for a :class:`ProtocolAssumption`, preserving its links."""

    category_in = str(getattr(assumption, "category", "") or "")
    unknown = bool(category_in) and category_in not in _ASSUMPTION_CATEGORY_TO_GAP
    gap_categories = test_gap_categories_for_assumption_categories([category_in]) or [UNCLASSIFIED_TEST_GAP]
    aid = str(getattr(assumption, "assumption_id", "") or "")
    fid = str(getattr(assumption, "function_id", "") or "")
    fname = str(getattr(assumption, "function_name", "") or "")
    cname = str(getattr(assumption, "contract_name", "") or "")
    roles = list(getattr(assumption, "function_roles", []) or [])
    vpids = list(getattr(assumption, "value_path_ids", []) or [])
    out: list[ProtocolTestGap] = []
    for category in gap_categories:
        warn = []
        if unknown and category == UNCLASSIFIED_TEST_GAP:
            warn.append(f"unknown assumption category mapped to unclassified test gap: {category_in}")
        out.append(_make_gap(
            category, function_id=fid, function_name=fname, contract_name=cname,
            function_roles=roles, value_path_ids=vpids,
            assumption_ids=[aid] if aid else [],
            assumption_categories=[category_in] if category_in else [], warnings=warn))
    return out


# --- Local-validation correlation (context only) ----------------------------

def correlate_test_gap_with_local_validation(
    test_gap: ProtocolTestGap,
    local_validation_ids: list[str] | None = None,
    trace_receipt_ids: list[str] | None = None,
    tested: bool = False,
    trace_bound: bool = False,
) -> ProtocolTestGap:
    """Return a copy of ``test_gap`` updated with local-validation context only.

    Local validation is context, never proof: a passing local test does not prove
    safety and a missing test does not prove a vulnerability. Status is only
    upgraded when explicit IDs are supplied; otherwise no coverage is claimed.
    ``manual_review_required`` stays true and ``ready_for_submission`` stays false.
    """

    gap = copy.deepcopy(test_gap)
    lv_ids = [str(x) for x in (local_validation_ids or []) if x]
    tr_ids = [str(x) for x in (trace_receipt_ids or []) if x]

    if tested and lv_ids:
        gap.linked_local_validation_ids = sorted(set(gap.linked_local_validation_ids) | set(lv_ids))
        gap.gap_status = TEST_GAP_LOCALLY_TESTED
        note = "local validation evidence referenced as context (passing local tests do not prove safety)"
        if note not in gap.coverage_notes:
            gap.coverage_notes.append(note)
    elif tested and not lv_ids:
        warn = "tested requested without local_validation_ids; no local coverage claimed; manual review required"
        if warn not in gap.warnings:
            gap.warnings.append(warn)

    if trace_bound and tr_ids:
        gap.linked_trace_receipt_ids = sorted(set(gap.linked_trace_receipt_ids) | set(tr_ids))
        gap.gap_status = TEST_GAP_TRACE_BOUND
        note = "trace receipt referenced as context (not final proof)"
        if note not in gap.coverage_notes:
            gap.coverage_notes.append(note)
    elif trace_bound and not tr_ids:
        warn = "trace_bound requested without trace_receipt_ids; no trace coverage claimed; manual review required"
        if warn not in gap.warnings:
            gap.warnings.append(warn)

    gap.manual_review_required = True
    gap.ready_for_submission = False
    return gap


# --- Deduplication ----------------------------------------------------------

def _merge_lists(*lists) -> list[str]:
    return sorted({str(x) for lst in lists for x in (lst or []) if x})


def deduplicate_test_gaps(test_gaps: list[ProtocolTestGap]) -> list[ProtocolTestGap]:
    """Merge gaps sharing (category, function_id, value_path_ids, assumption_ids).

    Linked IDs, coverage notes, and warnings merge deterministically; the highest
    structural priority and strongest coverage status are kept; distinct
    categories are never merged; ``manual_review_required`` stays true and
    ``ready_for_submission`` stays false. No resolution is claimed.
    """

    merged: dict[tuple, ProtocolTestGap] = {}
    order: list[tuple] = []
    for g in test_gaps or []:
        key = (g.category, g.function_id, tuple(sorted(g.value_path_ids)), tuple(sorted(g.assumption_ids)))
        if key not in merged:
            merged[key] = copy.deepcopy(g)
            merged[key].manual_review_required = True
            merged[key].ready_for_submission = False
            order.append(key)
            continue
        tgt = merged[key]
        tgt.function_roles = _merge_lists(tgt.function_roles, g.function_roles)
        tgt.value_path_kinds = _merge_lists(tgt.value_path_kinds, g.value_path_kinds)
        tgt.assumption_categories = _merge_lists(tgt.assumption_categories, g.assumption_categories)
        tgt.linked_function_ids = _merge_lists(tgt.linked_function_ids, g.linked_function_ids)
        tgt.linked_value_path_ids = _merge_lists(tgt.linked_value_path_ids, g.linked_value_path_ids)
        tgt.linked_assumption_ids = _merge_lists(tgt.linked_assumption_ids, g.linked_assumption_ids)
        tgt.linked_local_validation_ids = _merge_lists(tgt.linked_local_validation_ids, g.linked_local_validation_ids)
        tgt.linked_trace_receipt_ids = _merge_lists(tgt.linked_trace_receipt_ids, g.linked_trace_receipt_ids)
        tgt.coverage_notes = _merge_lists(tgt.coverage_notes, g.coverage_notes)
        tgt.warnings = _merge_lists(tgt.warnings, g.warnings)
        if _PRIORITY_RANK.get(g.priority, 0) > _PRIORITY_RANK.get(tgt.priority, 0):
            tgt.priority = g.priority
        if _STATUS_RANK.get(g.gap_status, 0) > _STATUS_RANK.get(tgt.gap_status, 0):
            tgt.gap_status = g.gap_status
        tgt.manual_review_required = True
        tgt.ready_for_submission = False
    return [
        merged[key]
        for key in sorted(order, key=lambda k: (_CATEGORY_PRIORITY_INDEX.get(k[0], 99), k[1], k[2], k[3]))
    ]


def build_test_gap_set(protocol_name: str, test_gaps: list[ProtocolTestGap]) -> TestGapSet:
    """Deduplicate and roll up test gaps into a deterministic :class:`TestGapSet`."""

    items = deduplicate_test_gaps(list(test_gaps or []))
    categories = _order_categories(g.category for g in items)
    fids: set[str] = set()
    vpids: set[str] = set()
    aids: set[str] = set()
    lvids: set[str] = set()
    for g in items:
        fids.update(x for x in ([g.function_id] + list(g.linked_function_ids)) if x)
        vpids.update(x for x in (list(g.value_path_ids) + list(g.linked_value_path_ids)) if x)
        aids.update(x for x in (list(g.assumption_ids) + list(g.linked_assumption_ids)) if x)
        lvids.update(x for x in g.linked_local_validation_ids if x)
    return TestGapSet(
        test_gap_set_id=test_gap_set_id(protocol_name, [g.test_gap_id for g in items]),
        protocol_name=str(protocol_name or "").strip(),
        test_gaps=items,
        categories=categories,
        open_gap_count=sum(1 for g in items if g.gap_status == TEST_GAP_OPEN),
        locally_tested_gap_count=sum(1 for g in items if g.gap_status == TEST_GAP_LOCALLY_TESTED),
        trace_bound_gap_count=sum(1 for g in items if g.gap_status == TEST_GAP_TRACE_BOUND),
        linked_function_ids=sorted(fids),
        linked_value_path_ids=sorted(vpids),
        linked_assumption_ids=sorted(aids),
        linked_local_validation_ids=sorted(lvids),
        manual_review_required=True,
        ready_for_submission=False,
    )


# --- Serialization ----------------------------------------------------------

def test_gap_to_dict(value: object) -> object:
    """Recursively serialize test-gap dataclasses to plain JSON-ready data.

    Dataclasses become dicts, lists/tuples become lists, dicts are walked, and
    primitives / ``None`` pass through. Unsupported objects raise ``TypeError``.
    Does not mutate the source.
    """

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: test_gap_to_dict(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {key: test_gap_to_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [test_gap_to_dict(item) for item in value]
    raise TypeError(f"unsupported value for test_gap_to_dict: {type(value).__name__}")
