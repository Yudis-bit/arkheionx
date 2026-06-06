"""Internal assumption engine and deterministic assumption IDs (v3.8, additive).

This module derives controlled protective assumptions for a function from its
Agent 2 roles and its Agent 3 value-path kinds. An assumption is a review prompt
(a protective property a value path appears to rely on), never a finding. It is
internal infrastructure: no filesystem, network, subprocess, CLI, or live-chain
behavior, and importing it has no side effects.

Assumptions are review surface only. They never assert a confirmed
vulnerability, a final severity, an audit outcome, submission readiness, or a
safe verdict. Every record keeps ``manual_review_required`` true and
``ready_for_submission`` false, and never emits a human-reviewed status. Mapping
is exact (no fuzzy or substring matching) and non-inventive: assets, oracle
sources, and external targets are never fabricated.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, fields, is_dataclass

_HASH_LEN = 12

# --- Controlled assumption categories ---------------------------------------

ORACLE_FRESHNESS = "ORACLE_FRESHNESS"
ORACLE_MANIPULATION_RESISTANCE = "ORACLE_MANIPULATION_RESISTANCE"
ACCOUNTING_INVARIANT = "ACCOUNTING_INVARIANT"
BALANCE_CONSERVATION = "BALANCE_CONSERVATION"
ACCESS_CONTROL_CORRECTNESS = "ACCESS_CONTROL_CORRECTNESS"
ROLE_SEPARATION = "ROLE_SEPARATION"
REENTRANCY_PROTECTION = "REENTRANCY_PROTECTION"
EXTERNAL_TOKEN_BEHAVIOR = "EXTERNAL_TOKEN_BEHAVIOR"
PAUSE_EMERGENCY_BEHAVIOR = "PAUSE_EMERGENCY_BEHAVIOR"
UPGRADE_SAFETY = "UPGRADE_SAFETY"
LIQUIDATION_THRESHOLD_CORRECTNESS = "LIQUIDATION_THRESHOLD_CORRECTNESS"
SLIPPAGE_BOUND = "SLIPPAGE_BOUND"
FEE_CORRECTNESS = "FEE_CORRECTNESS"
BRIDGE_FINALITY = "BRIDGE_FINALITY"
SIGNER_QUORUM_INTEGRITY = "SIGNER_QUORUM_INTEGRITY"
REWARD_ACCOUNTING_CORRECTNESS = "REWARD_ACCOUNTING_CORRECTNESS"
DELEGATECALL_TARGET_SAFETY = "DELEGATECALL_TARGET_SAFETY"
VIEW_CALCULATION_CONSISTENCY = "VIEW_CALCULATION_CONSISTENCY"
UNCLASSIFIED_ASSUMPTION = "UNCLASSIFIED_ASSUMPTION"

ASSUMPTION_CATEGORY_VALUES: tuple[str, ...] = (
    ORACLE_FRESHNESS,
    ORACLE_MANIPULATION_RESISTANCE,
    ACCOUNTING_INVARIANT,
    BALANCE_CONSERVATION,
    ACCESS_CONTROL_CORRECTNESS,
    ROLE_SEPARATION,
    REENTRANCY_PROTECTION,
    EXTERNAL_TOKEN_BEHAVIOR,
    PAUSE_EMERGENCY_BEHAVIOR,
    UPGRADE_SAFETY,
    LIQUIDATION_THRESHOLD_CORRECTNESS,
    SLIPPAGE_BOUND,
    FEE_CORRECTNESS,
    BRIDGE_FINALITY,
    SIGNER_QUORUM_INTEGRITY,
    REWARD_ACCOUNTING_CORRECTNESS,
    DELEGATECALL_TARGET_SAFETY,
    VIEW_CALCULATION_CONSISTENCY,
    UNCLASSIFIED_ASSUMPTION,
)

ASSUMPTION_CATEGORY_DESCRIPTIONS: dict[str, str] = {
    ORACLE_FRESHNESS: "The oracle / price source is assumed current, non-stale, and trusted.",
    ORACLE_MANIPULATION_RESISTANCE: "The oracle / price is assumed not manipulable within a block or via spot reserves.",
    ACCOUNTING_INVARIANT: "Internal accounting invariants are assumed to hold across the operation.",
    BALANCE_CONSERVATION: "Value is assumed conserved: balances change consistently with transfers.",
    ACCESS_CONTROL_CORRECTNESS: "Privileged entry points are assumed correctly access-controlled.",
    ROLE_SEPARATION: "Privileged roles are assumed separated and bounded, not over-powered.",
    REENTRANCY_PROTECTION: "State is assumed settled before external calls, or guarded against re-entry.",
    EXTERNAL_TOKEN_BEHAVIOR: "External tokens are assumed standard (return value, no fee-on-transfer surprise, no callback abuse).",
    PAUSE_EMERGENCY_BEHAVIOR: "Pause / emergency behavior is assumed correct and access-controlled.",
    UPGRADE_SAFETY: "Upgrades are assumed storage-compatible and correctly authorized.",
    LIQUIDATION_THRESHOLD_CORRECTNESS: "Liquidation / health thresholds are assumed correct and free of rounding abuse.",
    SLIPPAGE_BOUND: "Slippage / output is assumed bounded by an enforced minimum.",
    FEE_CORRECTNESS: "Fee math is assumed correct and bounded.",
    BRIDGE_FINALITY: "Cross-chain messages are assumed final and replay-protected before value release.",
    SIGNER_QUORUM_INTEGRITY: "Signer set / quorum is assumed honest, sufficient, and replay-protected.",
    REWARD_ACCOUNTING_CORRECTNESS: "Reward accounting is assumed monotonic and updated before balance changes.",
    DELEGATECALL_TARGET_SAFETY: "Delegatecall targets are assumed trusted and storage-compatible.",
    VIEW_CALCULATION_CONSISTENCY: "View / pure computations are assumed consistent with state-changing paths.",
    UNCLASSIFIED_ASSUMPTION: "No controlled assumption category mapped; manual review required.",
}

_CATEGORY_TITLES: dict[str, str] = {
    ORACLE_FRESHNESS: "Oracle price is fresh and trusted",
    ORACLE_MANIPULATION_RESISTANCE: "Oracle is resistant to manipulation",
    ACCOUNTING_INVARIANT: "Accounting invariants hold",
    BALANCE_CONSERVATION: "Value is conserved",
    ACCESS_CONTROL_CORRECTNESS: "Access control is correct",
    ROLE_SEPARATION: "Roles are separated and bounded",
    REENTRANCY_PROTECTION: "External calls cannot re-enter unsafe state",
    EXTERNAL_TOKEN_BEHAVIOR: "External tokens behave as standard",
    PAUSE_EMERGENCY_BEHAVIOR: "Pause/emergency behavior is correct",
    UPGRADE_SAFETY: "Upgrades are safe and authorized",
    LIQUIDATION_THRESHOLD_CORRECTNESS: "Liquidation thresholds are correct",
    SLIPPAGE_BOUND: "Slippage is bounded",
    FEE_CORRECTNESS: "Fee math is correct",
    BRIDGE_FINALITY: "Bridge messages are final and replay-protected",
    SIGNER_QUORUM_INTEGRITY: "Signer quorum is intact",
    REWARD_ACCOUNTING_CORRECTNESS: "Reward accounting is correct",
    DELEGATECALL_TARGET_SAFETY: "Delegatecall target is trusted",
    VIEW_CALCULATION_CONSISTENCY: "View calculations are consistent",
    UNCLASSIFIED_ASSUMPTION: "Unclassified assumption",
}

# --- Support levels (non-overclaim) -----------------------------------------

ASSUMPTION_OBSERVED = "ASSUMPTION_OBSERVED"
ASSUMPTION_CLASSIFIED = "ASSUMPTION_CLASSIFIED"
ASSUMPTION_LINKED = "ASSUMPTION_LINKED"
ASSUMPTION_TESTED = "ASSUMPTION_TESTED"
ASSUMPTION_TRACE_BOUND = "ASSUMPTION_TRACE_BOUND"
ASSUMPTION_NEEDS_HUMAN_REVIEW = "ASSUMPTION_NEEDS_HUMAN_REVIEW"

ASSUMPTION_SUPPORT_LEVELS: tuple[str, ...] = (
    ASSUMPTION_OBSERVED,
    ASSUMPTION_CLASSIFIED,
    ASSUMPTION_LINKED,
    ASSUMPTION_TESTED,
    ASSUMPTION_TRACE_BOUND,
    ASSUMPTION_NEEDS_HUMAN_REVIEW,
)

# --- Impact areas (structural context only, never final severity) -----------

IMPACT_UNKNOWN = "IMPACT_UNKNOWN"
IMPACT_VALUE_FLOW = "IMPACT_VALUE_FLOW"
IMPACT_AUTHORITY = "IMPACT_AUTHORITY"
IMPACT_ACCOUNTING = "IMPACT_ACCOUNTING"
IMPACT_ORACLE = "IMPACT_ORACLE"
IMPACT_LIVENESS = "IMPACT_LIVENESS"
IMPACT_UPGRADE = "IMPACT_UPGRADE"
IMPACT_EXTERNAL_DEPENDENCY = "IMPACT_EXTERNAL_DEPENDENCY"

ASSUMPTION_IMPACT_AREAS: tuple[str, ...] = (
    IMPACT_UNKNOWN,
    IMPACT_VALUE_FLOW,
    IMPACT_AUTHORITY,
    IMPACT_ACCOUNTING,
    IMPACT_ORACLE,
    IMPACT_LIVENESS,
    IMPACT_UPGRADE,
    IMPACT_EXTERNAL_DEPENDENCY,
)

_CATEGORY_TO_IMPACT_AREAS: dict[str, tuple[str, ...]] = {
    ORACLE_FRESHNESS: (IMPACT_ORACLE, IMPACT_VALUE_FLOW),
    ORACLE_MANIPULATION_RESISTANCE: (IMPACT_ORACLE, IMPACT_VALUE_FLOW),
    ACCOUNTING_INVARIANT: (IMPACT_ACCOUNTING, IMPACT_VALUE_FLOW),
    BALANCE_CONSERVATION: (IMPACT_ACCOUNTING, IMPACT_VALUE_FLOW),
    ACCESS_CONTROL_CORRECTNESS: (IMPACT_AUTHORITY,),
    ROLE_SEPARATION: (IMPACT_AUTHORITY,),
    REENTRANCY_PROTECTION: (IMPACT_VALUE_FLOW, IMPACT_EXTERNAL_DEPENDENCY),
    EXTERNAL_TOKEN_BEHAVIOR: (IMPACT_EXTERNAL_DEPENDENCY, IMPACT_VALUE_FLOW),
    PAUSE_EMERGENCY_BEHAVIOR: (IMPACT_LIVENESS, IMPACT_AUTHORITY),
    UPGRADE_SAFETY: (IMPACT_UPGRADE, IMPACT_AUTHORITY),
    LIQUIDATION_THRESHOLD_CORRECTNESS: (IMPACT_ACCOUNTING, IMPACT_ORACLE, IMPACT_VALUE_FLOW),
    SLIPPAGE_BOUND: (IMPACT_VALUE_FLOW, IMPACT_ORACLE),
    FEE_CORRECTNESS: (IMPACT_ACCOUNTING, IMPACT_VALUE_FLOW),
    BRIDGE_FINALITY: (IMPACT_EXTERNAL_DEPENDENCY, IMPACT_VALUE_FLOW),
    SIGNER_QUORUM_INTEGRITY: (IMPACT_AUTHORITY, IMPACT_EXTERNAL_DEPENDENCY),
    REWARD_ACCOUNTING_CORRECTNESS: (IMPACT_ACCOUNTING, IMPACT_VALUE_FLOW),
    DELEGATECALL_TARGET_SAFETY: (IMPACT_UPGRADE, IMPACT_EXTERNAL_DEPENDENCY),
    VIEW_CALCULATION_CONSISTENCY: (IMPACT_ACCOUNTING,),
    UNCLASSIFIED_ASSUMPTION: (IMPACT_UNKNOWN,),
}

_CATEGORY_PRIORITY_INDEX: dict[str, int] = {c: i for i, c in enumerate(ASSUMPTION_CATEGORY_VALUES)}


# --- ID + canonical hashing -------------------------------------------------

def canonical_assumption_seed(value: object) -> str:
    """Canonical JSON seed; raises ``TypeError`` for non-JSON-native seeds."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _short_hash(value: object) -> str:
    return hashlib.sha256(canonical_assumption_seed(value).encode("utf-8")).hexdigest()[:_HASH_LEN]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")


def protocol_assumption_id(
    category: str,
    function_id: str = "",
    value_path_ids: list[str] | None = None,
    title: str = "",
    contract_name: str = "",
    function_name: str = "",
) -> str:
    """Deterministic assumption ID. ``value_path_ids`` sorted before hashing."""

    cat = str(category or "").strip()
    if not cat:
        raise ValueError("protocol_assumption_id requires a non-empty category")
    seed = {
        "category": cat,
        "function_id": str(function_id or "").strip(),
        "value_path_ids": sorted(str(v) for v in (value_path_ids or [])),
        "title": str(title or "").strip(),
        "contract_name": str(contract_name or "").strip(),
        "function_name": str(function_name or "").strip(),
    }
    return f"protocol-assumption:{_slug(cat)}:{_short_hash(seed)}"


def assumption_set_id(protocol_name: str, assumption_ids: list[str]) -> str:
    """Deterministic assumption-set ID. ``assumption_ids`` sorted before hashing."""

    name = str(protocol_name or "").strip()
    if not name:
        raise ValueError("assumption_set_id requires a non-empty protocol_name")
    seed = {"protocol_name": name, "assumption_ids": sorted(str(a) for a in (assumption_ids or []))}
    return f"assumption-set:{_slug(name)}:{_short_hash(seed)}"


# --- Dataclasses ------------------------------------------------------------

@dataclass
class ProtocolAssumption:
    assumption_id: str = ""
    category: str = UNCLASSIFIED_ASSUMPTION
    title: str = ""
    description: str = ""
    support_level: str = ASSUMPTION_CLASSIFIED
    impact_area: str = IMPACT_UNKNOWN
    function_id: str = ""
    function_name: str = ""
    contract_name: str = ""
    function_roles: list[str] = field(default_factory=list)
    value_path_ids: list[str] = field(default_factory=list)
    value_path_kinds: list[str] = field(default_factory=list)
    segment_ids: list[str] = field(default_factory=list)
    linked_function_ids: list[str] = field(default_factory=list)
    linked_value_path_ids: list[str] = field(default_factory=list)
    linked_test_gap_ids: list[str] = field(default_factory=list)
    linked_local_validation_ids: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class AssumptionSet:
    assumption_set_id: str = ""
    protocol_name: str = ""
    assumptions: list[ProtocolAssumption] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    linked_function_ids: list[str] = field(default_factory=list)
    linked_value_path_ids: list[str] = field(default_factory=list)
    linked_test_gap_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


# --- Role / value-path -> assumption-category mapping -----------------------

_ROLE_TO_CATEGORIES: dict[str, tuple[str, ...]] = {
    "ORACLE_CONSUMER": (ORACLE_FRESHNESS, ORACLE_MANIPULATION_RESISTANCE),
    "ORACLE_SETTER": (ORACLE_FRESHNESS, ACCESS_CONTROL_CORRECTNESS, ROLE_SEPARATION),
    "ACCOUNTING_MUTATION": (ACCOUNTING_INVARIANT, BALANCE_CONSERVATION),
    "INFLOW": (EXTERNAL_TOKEN_BEHAVIOR, BALANCE_CONSERVATION),
    "OUTFLOW": (BALANCE_CONSERVATION, REENTRANCY_PROTECTION, EXTERNAL_TOKEN_BEHAVIOR),
    "EXTERNAL_CALL": (REENTRANCY_PROTECTION, EXTERNAL_TOKEN_BEHAVIOR),
    "ADMIN_PARAM": (ACCESS_CONTROL_CORRECTNESS, ROLE_SEPARATION),
    "ACCESS_CONTROL": (ACCESS_CONTROL_CORRECTNESS, ROLE_SEPARATION),
    "PAUSE_EMERGENCY": (PAUSE_EMERGENCY_BEHAVIOR, ACCESS_CONTROL_CORRECTNESS),
    "UPGRADE_PROXY": (UPGRADE_SAFETY, ACCESS_CONTROL_CORRECTNESS),
    "DELEGATECALL": (DELEGATECALL_TARGET_SAFETY, UPGRADE_SAFETY),
    "BORROW_REPAY": (ACCOUNTING_INVARIANT, BALANCE_CONSERVATION),
    "LIQUIDATION": (LIQUIDATION_THRESHOLD_CORRECTNESS, ORACLE_FRESHNESS, ACCOUNTING_INVARIANT),
    "SWAP": (SLIPPAGE_BOUND, ORACLE_MANIPULATION_RESISTANCE, EXTERNAL_TOKEN_BEHAVIOR),
    "MINT_BURN": (ACCOUNTING_INVARIANT, BALANCE_CONSERVATION),
    "CLAIM_REWARD": (REWARD_ACCOUNTING_CORRECTNESS, BALANCE_CONSERVATION),
    "BRIDGE": (BRIDGE_FINALITY, SIGNER_QUORUM_INTEGRITY, EXTERNAL_TOKEN_BEHAVIOR),
    "VIEW_PURE": (VIEW_CALCULATION_CONSISTENCY,),
    "UNCLASSIFIED": (UNCLASSIFIED_ASSUMPTION,),
}

_PATH_KIND_TO_CATEGORIES: dict[str, tuple[str, ...]] = {
    "VALUE_INFLOW": (EXTERNAL_TOKEN_BEHAVIOR, BALANCE_CONSERVATION),
    "VALUE_OUTFLOW": (BALANCE_CONSERVATION, REENTRANCY_PROTECTION, EXTERNAL_TOKEN_BEHAVIOR),
    "ACCOUNTING_MUTATION_PATH": (ACCOUNTING_INVARIANT, BALANCE_CONSERVATION),
    "EXTERNAL_CALL_PATH": (REENTRANCY_PROTECTION, EXTERNAL_TOKEN_BEHAVIOR),
    "ORACLE_DEPENDENT_PATH": (ORACLE_FRESHNESS, ORACLE_MANIPULATION_RESISTANCE),
    "AUTHORITY_PATH": (ACCESS_CONTROL_CORRECTNESS, ROLE_SEPARATION),
    "EMERGENCY_PATH": (PAUSE_EMERGENCY_BEHAVIOR, ACCESS_CONTROL_CORRECTNESS),
    "UPGRADE_PATH": (UPGRADE_SAFETY, DELEGATECALL_TARGET_SAFETY),
    "LIQUIDATION_PATH": (LIQUIDATION_THRESHOLD_CORRECTNESS, ORACLE_FRESHNESS, ACCOUNTING_INVARIANT),
    "SWAP_PATH": (SLIPPAGE_BOUND, ORACLE_MANIPULATION_RESISTANCE),
    "BRIDGE_PATH": (BRIDGE_FINALITY, SIGNER_QUORUM_INTEGRITY),
    "REWARD_PATH": (REWARD_ACCOUNTING_CORRECTNESS, BALANCE_CONSERVATION),
    "VIEW_ONLY_PATH": (VIEW_CALCULATION_CONSISTENCY,),
    "UNCLASSIFIED_PATH": (UNCLASSIFIED_ASSUMPTION,),
}


def _order_categories(categories) -> list[str]:
    return sorted(
        {c for c in categories if c},
        key=lambda c: _CATEGORY_PRIORITY_INDEX.get(c, len(ASSUMPTION_CATEGORY_VALUES)),
    )


def impact_areas_for_assumption_category(category: str) -> list[str]:
    """Return the structural impact areas for a category (never final severity)."""

    return list(_CATEGORY_TO_IMPACT_AREAS.get(str(category or "").strip(), (IMPACT_UNKNOWN,)))


def assumption_categories_for_roles(roles: list[str]) -> list[str]:
    """Map controlled roles to assumption categories (exact, priority-ordered)."""

    collected: list[str] = []
    for role in roles or []:
        collected.extend(_ROLE_TO_CATEGORIES.get(str(role or "").strip(), (UNCLASSIFIED_ASSUMPTION,)))
    return _order_categories(collected)


def assumption_categories_for_value_path_kinds(path_kinds: list[str]) -> list[str]:
    """Map controlled value-path kinds to assumption categories (exact, ordered)."""

    collected: list[str] = []
    for kind in path_kinds or []:
        collected.extend(_PATH_KIND_TO_CATEGORIES.get(str(kind or "").strip(), (UNCLASSIFIED_ASSUMPTION,)))
    return _order_categories(collected)


def _make_assumption(
    category: str,
    *,
    function_id: str = "",
    function_name: str = "",
    contract_name: str = "",
    function_roles: list[str] | None = None,
    value_path_ids: list[str] | None = None,
    value_path_kinds: list[str] | None = None,
    warnings: list[str] | None = None,
) -> ProtocolAssumption:
    impacts = impact_areas_for_assumption_category(category)
    vpids = list(value_path_ids or [])
    warn = list(warnings or [])
    if category == UNCLASSIFIED_ASSUMPTION:
        warn.append("unclassified assumption (no controlled category mapped); manual review required")
    return ProtocolAssumption(
        assumption_id=protocol_assumption_id(
            category, function_id, vpids, _CATEGORY_TITLES.get(category, ""), contract_name, function_name),
        category=category,
        title=_CATEGORY_TITLES.get(category, ""),
        description=ASSUMPTION_CATEGORY_DESCRIPTIONS.get(category, ""),
        support_level=ASSUMPTION_CLASSIFIED,
        impact_area=impacts[0],
        function_id=str(function_id or ""),
        function_name=str(function_name or ""),
        contract_name=str(contract_name or ""),
        function_roles=list(function_roles or []),
        value_path_ids=vpids,
        value_path_kinds=list(value_path_kinds or []),
        linked_function_ids=[function_id] if function_id else [],
        linked_value_path_ids=list(vpids),
        warnings=warn,
        manual_review_required=True,
        ready_for_submission=False,
        metadata={"impact_areas": impacts},
    )


def build_assumptions_from_roles(
    function_roles: list[str],
    function_id: str = "",
    function_name: str = "",
    contract_name: str = "",
) -> list[ProtocolAssumption]:
    """Build one assumption per mapped category for a function's roles."""

    roles = list(function_roles or [])
    unknown = [r for r in roles if r and r not in _ROLE_TO_CATEGORIES]
    categories = assumption_categories_for_roles(roles)
    if not categories:
        categories = [UNCLASSIFIED_ASSUMPTION]
    out: list[ProtocolAssumption] = []
    for category in categories:
        warn = []
        if unknown and category == UNCLASSIFIED_ASSUMPTION:
            warn.append("unknown role(s) mapped to unclassified assumption: " + ", ".join(sorted(unknown)))
        out.append(_make_assumption(
            category, function_id=function_id, function_name=function_name,
            contract_name=contract_name, function_roles=roles, warnings=warn))
    return out


def build_assumptions_from_value_path(value_path: object) -> list[ProtocolAssumption]:
    """Build assumptions for a :class:`ValuePath`, preserving its exact links."""

    path_kinds = list((getattr(value_path, "metadata", {}) or {}).get("path_kinds", []) or [])
    if not path_kinds:
        primary = str(getattr(value_path, "path_kind", "") or "")
        path_kinds = [primary] if primary else []
    unknown = [k for k in path_kinds if k and k not in _PATH_KIND_TO_CATEGORIES]
    categories = assumption_categories_for_value_path_kinds(path_kinds)
    if not categories:
        categories = [UNCLASSIFIED_ASSUMPTION]
    pid = str(getattr(value_path, "path_id", "") or "")
    fid = str(getattr(value_path, "function_id", "") or "")
    fname = str(getattr(value_path, "function_name", "") or "")
    cname = str(getattr(value_path, "contract_name", "") or "")
    roles = list(getattr(value_path, "roles", []) or [])
    out: list[ProtocolAssumption] = []
    for category in categories:
        warn = []
        if unknown and category == UNCLASSIFIED_ASSUMPTION:
            warn.append("unknown value-path kind(s) mapped to unclassified assumption: " + ", ".join(sorted(unknown)))
        out.append(_make_assumption(
            category, function_id=fid, function_name=fname, contract_name=cname,
            function_roles=roles, value_path_ids=[pid] if pid else [],
            value_path_kinds=path_kinds, warnings=warn))
    return out


def build_assumption_set(protocol_name: str, assumptions: list[ProtocolAssumption]) -> AssumptionSet:
    """Roll up assumptions into a deterministic :class:`AssumptionSet`."""

    items = list(assumptions or [])
    categories = _order_categories(a.category for a in items)
    fids: set[str] = set()
    vpids: set[str] = set()
    gaps: set[str] = set()
    for a in items:
        fids.update(x for x in ([a.function_id] + list(a.linked_function_ids)) if x)
        vpids.update(x for x in (list(a.value_path_ids) + list(a.linked_value_path_ids)) if x)
        gaps.update(x for x in a.linked_test_gap_ids if x)
    return AssumptionSet(
        assumption_set_id=assumption_set_id(protocol_name, [a.assumption_id for a in items]),
        protocol_name=str(protocol_name or "").strip(),
        assumptions=items,
        categories=categories,
        linked_function_ids=sorted(fids),
        linked_value_path_ids=sorted(vpids),
        linked_test_gap_ids=sorted(gaps),
        manual_review_required=True,
        ready_for_submission=False,
    )


def _merge_lists(*lists) -> list[str]:
    return sorted({str(x) for lst in lists for x in (lst or []) if x})


def deduplicate_assumptions(assumptions: list[ProtocolAssumption]) -> list[ProtocolAssumption]:
    """Merge assumptions sharing (category, function_id, value_path_ids).

    Linked IDs and warnings are merged deterministically; distinct categories are
    never merged; ``manual_review_required`` stays true and
    ``ready_for_submission`` stays false. No resolution is claimed.
    """

    merged: dict[tuple, ProtocolAssumption] = {}
    order: list[tuple] = []
    for a in assumptions or []:
        key = (a.category, a.function_id, tuple(sorted(a.value_path_ids)))
        if key not in merged:
            merged[key] = ProtocolAssumption(
                assumption_id=a.assumption_id, category=a.category, title=a.title,
                description=a.description, support_level=a.support_level, impact_area=a.impact_area,
                function_id=a.function_id, function_name=a.function_name, contract_name=a.contract_name,
                function_roles=list(a.function_roles), value_path_ids=list(a.value_path_ids),
                value_path_kinds=list(a.value_path_kinds), segment_ids=list(a.segment_ids),
                linked_function_ids=list(a.linked_function_ids), linked_value_path_ids=list(a.linked_value_path_ids),
                linked_test_gap_ids=list(a.linked_test_gap_ids),
                linked_local_validation_ids=list(a.linked_local_validation_ids),
                evidence_refs=list(a.evidence_refs), warnings=list(a.warnings),
                manual_review_required=True, ready_for_submission=False, metadata=dict(a.metadata))
            order.append(key)
        else:
            tgt = merged[key]
            tgt.function_roles = _merge_lists(tgt.function_roles, a.function_roles)
            tgt.value_path_kinds = _merge_lists(tgt.value_path_kinds, a.value_path_kinds)
            tgt.segment_ids = _merge_lists(tgt.segment_ids, a.segment_ids)
            tgt.linked_function_ids = _merge_lists(tgt.linked_function_ids, a.linked_function_ids)
            tgt.linked_value_path_ids = _merge_lists(tgt.linked_value_path_ids, a.linked_value_path_ids)
            tgt.linked_test_gap_ids = _merge_lists(tgt.linked_test_gap_ids, a.linked_test_gap_ids)
            tgt.linked_local_validation_ids = _merge_lists(tgt.linked_local_validation_ids, a.linked_local_validation_ids)
            tgt.evidence_refs = _merge_lists(tgt.evidence_refs, a.evidence_refs)
            tgt.warnings = _merge_lists(tgt.warnings, a.warnings)
            tgt.manual_review_required = True
            tgt.ready_for_submission = False
    return [
        merged[key]
        for key in sorted(order, key=lambda k: (_CATEGORY_PRIORITY_INDEX.get(k[0], 99), k[1], k[2]))
    ]


# --- Serialization ----------------------------------------------------------

def assumption_to_dict(value: object) -> object:
    """Recursively serialize assumption dataclasses to plain JSON-ready data.

    Dataclasses become dicts, lists/tuples become lists, dicts are walked, and
    primitives / ``None`` pass through. Unsupported objects raise ``TypeError``.
    Does not mutate the source.
    """

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: assumption_to_dict(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {key: assumption_to_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [assumption_to_dict(item) for item in value]
    raise TypeError(f"unsupported value for assumption_to_dict: {type(value).__name__}")
