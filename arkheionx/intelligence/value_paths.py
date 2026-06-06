"""Internal value-path graph model and deterministic IDs (v3.8, additive).

This module turns the controlled function roles from
:mod:`arkheionx.intelligence.roles` into structured, deterministic value-path
records: a value path (with a controlled kind), its ordered segments (with
controlled segment kinds), and a value-path graph rollup. It is internal
infrastructure: no filesystem, network, subprocess, CLI, or live-chain behavior,
and importing it has no side effects.

A value path is review surface only. It describes structurally how value moves or
how state changes (an inflow path, an oracle-dependent path); it never asserts a
confirmed vulnerability, a final severity, an audit outcome, submission
readiness, or a safe verdict. Every record keeps ``manual_review_required`` true
and ``ready_for_submission`` false, and never emits a human-reviewed status.

Mapping from roles is exact and non-inventive: assets, oracle sources, external
targets, and state variables stay empty unless explicit data is supplied, and an
ambiguous role-to-path mapping adds a warning rather than guessing.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, fields, is_dataclass

from .roles import ROLE_PRIORITY, UNCLASSIFIED

_HASH_LEN = 12

# --- Controlled value-path kinds --------------------------------------------

VALUE_INFLOW = "VALUE_INFLOW"
VALUE_OUTFLOW = "VALUE_OUTFLOW"
ACCOUNTING_MUTATION_PATH = "ACCOUNTING_MUTATION_PATH"
EXTERNAL_CALL_PATH = "EXTERNAL_CALL_PATH"
ORACLE_DEPENDENT_PATH = "ORACLE_DEPENDENT_PATH"
AUTHORITY_PATH = "AUTHORITY_PATH"
EMERGENCY_PATH = "EMERGENCY_PATH"
UPGRADE_PATH = "UPGRADE_PATH"
LIQUIDATION_PATH = "LIQUIDATION_PATH"
SWAP_PATH = "SWAP_PATH"
BRIDGE_PATH = "BRIDGE_PATH"
REWARD_PATH = "REWARD_PATH"
VIEW_ONLY_PATH = "VIEW_ONLY_PATH"
UNCLASSIFIED_PATH = "UNCLASSIFIED_PATH"

VALUE_PATH_KIND_VALUES: tuple[str, ...] = (
    VALUE_INFLOW,
    VALUE_OUTFLOW,
    ACCOUNTING_MUTATION_PATH,
    EXTERNAL_CALL_PATH,
    ORACLE_DEPENDENT_PATH,
    AUTHORITY_PATH,
    EMERGENCY_PATH,
    UPGRADE_PATH,
    LIQUIDATION_PATH,
    SWAP_PATH,
    BRIDGE_PATH,
    REWARD_PATH,
    VIEW_ONLY_PATH,
    UNCLASSIFIED_PATH,
)

VALUE_PATH_KIND_DESCRIPTIONS: dict[str, str] = {
    VALUE_INFLOW: "Value enters the protocol (deposit / supply / stake / add liquidity).",
    VALUE_OUTFLOW: "Value leaves the protocol (withdraw / redeem / unstake).",
    ACCOUNTING_MUTATION_PATH: "Internal accounting state changes (accrue / index / mint / burn).",
    EXTERNAL_CALL_PATH: "An external or batched call is made (multicall / execute / flash loan).",
    ORACLE_DEPENDENT_PATH: "Behavior depends on an oracle/price value (read or update).",
    AUTHORITY_PATH: "A privileged authority / role / parameter is exercised.",
    EMERGENCY_PATH: "A pause / unpause / emergency action.",
    UPGRADE_PATH: "An upgrade / implementation / delegatecall action.",
    LIQUIDATION_PATH: "A liquidation / seize / auction.",
    SWAP_PATH: "A swap / route / exact-input / exact-output.",
    BRIDGE_PATH: "A bridge / cross-chain message / relay.",
    REWARD_PATH: "A reward claim / harvest.",
    VIEW_ONLY_PATH: "A read-only view / pure computation.",
    UNCLASSIFIED_PATH: "No controlled path kind mapped; manual review required.",
}

# --- Controlled segment kinds -----------------------------------------------

FUNCTION_ENTRY = "FUNCTION_ENTRY"
STATE_READ = "STATE_READ"
STATE_WRITE = "STATE_WRITE"
BALANCE_INCREASE = "BALANCE_INCREASE"
BALANCE_DECREASE = "BALANCE_DECREASE"
TOKEN_TRANSFER_IN = "TOKEN_TRANSFER_IN"
TOKEN_TRANSFER_OUT = "TOKEN_TRANSFER_OUT"
EXTERNAL_CALL = "EXTERNAL_CALL"
ORACLE_READ = "ORACLE_READ"
ORACLE_UPDATE = "ORACLE_UPDATE"
AUTHORITY_CHECK = "AUTHORITY_CHECK"
ADMIN_UPDATE = "ADMIN_UPDATE"
PAUSE_CHECK = "PAUSE_CHECK"
EMERGENCY_ACTION = "EMERGENCY_ACTION"
UPGRADE_ACTION = "UPGRADE_ACTION"
DELEGATECALL_ACTION = "DELEGATECALL_ACTION"
ACCOUNTING_UPDATE = "ACCOUNTING_UPDATE"
REWARD_ACCOUNTING = "REWARD_ACCOUNTING"
BRIDGE_MESSAGE = "BRIDGE_MESSAGE"
VIEW_COMPUTATION = "VIEW_COMPUTATION"
UNKNOWN_SEGMENT = "UNKNOWN_SEGMENT"

VALUE_PATH_SEGMENT_KIND_VALUES: tuple[str, ...] = (
    FUNCTION_ENTRY,
    STATE_READ,
    STATE_WRITE,
    BALANCE_INCREASE,
    BALANCE_DECREASE,
    TOKEN_TRANSFER_IN,
    TOKEN_TRANSFER_OUT,
    EXTERNAL_CALL,
    ORACLE_READ,
    ORACLE_UPDATE,
    AUTHORITY_CHECK,
    ADMIN_UPDATE,
    PAUSE_CHECK,
    EMERGENCY_ACTION,
    UPGRADE_ACTION,
    DELEGATECALL_ACTION,
    ACCOUNTING_UPDATE,
    REWARD_ACCOUNTING,
    BRIDGE_MESSAGE,
    VIEW_COMPUTATION,
    UNKNOWN_SEGMENT,
)

VALUE_PATH_SEGMENT_KIND_DESCRIPTIONS: dict[str, str] = {
    FUNCTION_ENTRY: "Entry into the function.",
    STATE_READ: "Reads contract state.",
    STATE_WRITE: "Writes contract state.",
    BALANCE_INCREASE: "Increases an internal balance / share.",
    BALANCE_DECREASE: "Decreases an internal balance / share.",
    TOKEN_TRANSFER_IN: "Pulls tokens into the protocol.",
    TOKEN_TRANSFER_OUT: "Sends tokens out of the protocol.",
    EXTERNAL_CALL: "Calls an external address.",
    ORACLE_READ: "Reads an oracle / price value.",
    ORACLE_UPDATE: "Updates an oracle / price-feed source.",
    AUTHORITY_CHECK: "Checks or changes a role / ownership / operator.",
    ADMIN_UPDATE: "Updates a privileged configuration parameter.",
    PAUSE_CHECK: "Checks or toggles paused state.",
    EMERGENCY_ACTION: "Performs an emergency action.",
    UPGRADE_ACTION: "Performs an upgrade / implementation change.",
    DELEGATECALL_ACTION: "Performs a delegatecall.",
    ACCOUNTING_UPDATE: "Updates internal accounting.",
    REWARD_ACCOUNTING: "Updates reward accounting.",
    BRIDGE_MESSAGE: "Sends or receives a cross-chain message.",
    VIEW_COMPUTATION: "Performs a read-only computation.",
    UNKNOWN_SEGMENT: "Unclassified segment; manual review required.",
}


# --- ID + canonical hashing -------------------------------------------------

def canonical_value_path_seed(value: object) -> str:
    """Canonical JSON seed (sorted keys, compact separators).

    Raises ``TypeError`` for non-JSON-native seeds (for example a set), so an
    unsupported seed never silently stringifies.
    """

    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _short_hash(value: object) -> str:
    return hashlib.sha256(canonical_value_path_seed(value).encode("utf-8")).hexdigest()[:_HASH_LEN]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")


def value_path_id(
    path_kind: str,
    function_id: str = "",
    function_name: str = "",
    contract_name: str = "",
    roles: list[str] | None = None,
) -> str:
    """Deterministic value-path ID. ``roles`` are sorted before hashing."""

    kind = str(path_kind or "").strip()
    if not kind:
        raise ValueError("value_path_id requires a non-empty path_kind")
    seed = {
        "path_kind": kind,
        "function_id": str(function_id or "").strip(),
        "function_name": str(function_name or "").strip(),
        "contract_name": str(contract_name or "").strip(),
        "roles": sorted(str(r) for r in (roles or [])),
    }
    return f"value-path:{_slug(kind)}:{_short_hash(seed)}"


def value_path_segment_id(
    path_id: str,
    segment_kind: str,
    order_index: int = 0,
    role: str = "",
    function_id: str = "",
    source_label: str = "",
    target_label: str = "",
) -> str:
    """Deterministic segment ID (order-sensitive). Requires path_id + kind."""

    pid = str(path_id or "").strip()
    kind = str(segment_kind or "").strip()
    if not pid:
        raise ValueError("value_path_segment_id requires a non-empty path_id")
    if not kind:
        raise ValueError("value_path_segment_id requires a non-empty segment_kind")
    seed = {
        "path_id": pid,
        "segment_kind": kind,
        "order_index": int(order_index),
        "role": str(role or "").strip(),
        "function_id": str(function_id or "").strip(),
        "source_label": str(source_label or "").strip(),
        "target_label": str(target_label or "").strip(),
    }
    return f"value-path-segment:{_slug(kind)}:{_short_hash(seed)}"


def value_path_graph_id(protocol_name: str, value_path_ids: list[str]) -> str:
    """Deterministic graph ID. ``value_path_ids`` are sorted before hashing."""

    name = str(protocol_name or "").strip()
    if not name:
        raise ValueError("value_path_graph_id requires a non-empty protocol_name")
    seed = {"protocol_name": name, "value_path_ids": sorted(str(v) for v in (value_path_ids or []))}
    return f"value-path-graph:{_slug(name)}:{_short_hash(seed)}"


# --- Dataclasses ------------------------------------------------------------

@dataclass
class ValuePathSegment:
    segment_id: str = ""
    path_id: str = ""
    segment_kind: str = UNKNOWN_SEGMENT
    function_id: str = ""
    function_name: str = ""
    contract_name: str = ""
    role: str = ""
    source_label: str = ""
    target_label: str = ""
    asset_symbol: str = ""
    state_variable: str = ""
    external_target: str = ""
    oracle_source: str = ""
    authority_label: str = ""
    order_index: int = 0
    linked_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ValuePath:
    path_id: str = ""
    path_kind: str = UNCLASSIFIED_PATH
    name: str = ""
    contract_name: str = ""
    function_name: str = ""
    function_id: str = ""
    roles: list[str] = field(default_factory=list)
    segments: list[ValuePathSegment] = field(default_factory=list)
    linked_function_ids: list[str] = field(default_factory=list)
    linked_assumption_ids: list[str] = field(default_factory=list)
    linked_test_gap_ids: list[str] = field(default_factory=list)
    support_level: str = "CLASSIFIED"
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ValuePathGraph:
    graph_id: str = ""
    protocol_name: str = ""
    value_paths: list[ValuePath] = field(default_factory=list)
    segments: list[ValuePathSegment] = field(default_factory=list)
    linked_function_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


# --- Role -> path / segment mapping -----------------------------------------

# Primary value-path kind per controlled function role (exact, no fuzzy).
_ROLE_TO_PATH_KIND: dict[str, str] = {
    "INFLOW": VALUE_INFLOW,
    "OUTFLOW": VALUE_OUTFLOW,
    "ACCOUNTING_MUTATION": ACCOUNTING_MUTATION_PATH,
    "EXTERNAL_CALL": EXTERNAL_CALL_PATH,
    "ORACLE_CONSUMER": ORACLE_DEPENDENT_PATH,
    "ORACLE_SETTER": ORACLE_DEPENDENT_PATH,
    "ADMIN_PARAM": AUTHORITY_PATH,
    "ACCESS_CONTROL": AUTHORITY_PATH,
    "PAUSE_EMERGENCY": EMERGENCY_PATH,
    "UPGRADE_PROXY": UPGRADE_PATH,
    "DELEGATECALL": UPGRADE_PATH,
    "BORROW_REPAY": ACCOUNTING_MUTATION_PATH,
    "LIQUIDATION": LIQUIDATION_PATH,
    "SWAP": SWAP_PATH,
    "MINT_BURN": ACCOUNTING_MUTATION_PATH,
    "CLAIM_REWARD": REWARD_PATH,
    "BRIDGE": BRIDGE_PATH,
    "VIEW_PURE": VIEW_ONLY_PATH,
    UNCLASSIFIED: UNCLASSIFIED_PATH,
}

# Role-specific segment kinds (FUNCTION_ENTRY is added by the builder).
_ROLE_TO_SEGMENT_KINDS: dict[str, tuple[str, ...]] = {
    "INFLOW": (TOKEN_TRANSFER_IN, BALANCE_INCREASE),
    "OUTFLOW": (TOKEN_TRANSFER_OUT, BALANCE_DECREASE),
    "ACCOUNTING_MUTATION": (ACCOUNTING_UPDATE, STATE_WRITE),
    "EXTERNAL_CALL": (EXTERNAL_CALL,),
    "ORACLE_CONSUMER": (ORACLE_READ,),
    "ORACLE_SETTER": (ORACLE_UPDATE,),
    "ADMIN_PARAM": (ADMIN_UPDATE,),
    "ACCESS_CONTROL": (AUTHORITY_CHECK,),
    "PAUSE_EMERGENCY": (PAUSE_CHECK, EMERGENCY_ACTION),
    "UPGRADE_PROXY": (UPGRADE_ACTION,),
    "DELEGATECALL": (DELEGATECALL_ACTION,),
    "BORROW_REPAY": (ACCOUNTING_UPDATE,),
    "LIQUIDATION": (BALANCE_DECREASE, TOKEN_TRANSFER_OUT, ACCOUNTING_UPDATE),
    "SWAP": (TOKEN_TRANSFER_IN, TOKEN_TRANSFER_OUT, EXTERNAL_CALL),
    "MINT_BURN": (BALANCE_INCREASE, BALANCE_DECREASE),
    "CLAIM_REWARD": (REWARD_ACCOUNTING, TOKEN_TRANSFER_OUT),
    "BRIDGE": (BRIDGE_MESSAGE, TOKEN_TRANSFER_IN, TOKEN_TRANSFER_OUT),
    "VIEW_PURE": (VIEW_COMPUTATION,),
    UNCLASSIFIED: (UNKNOWN_SEGMENT,),
}

# Roles whose direction is genuinely ambiguous (warn, never guess).
_AMBIGUOUS_ROLE_NOTES: dict[str, str] = {
    "BORROW_REPAY": "BORROW_REPAY is direction-ambiguous (borrow is inflow, repay is outflow); manual review required",
}

_ROLE_PRIORITY_INDEX: dict[str, int] = {r: i for i, r in enumerate(ROLE_PRIORITY)}


def _order_roles(roles: list[str]) -> list[str]:
    return sorted(
        {r for r in roles if r},
        key=lambda r: _ROLE_PRIORITY_INDEX.get(r, len(ROLE_PRIORITY)),
    )


def path_kinds_for_roles(roles: list[str]) -> list[str]:
    """Map controlled roles to value-path kinds (deterministic, priority order).

    Exact mapping only; an unmapped role contributes ``UNCLASSIFIED_PATH``. The
    result is de-duplicated and ordered by role priority.
    """

    out: list[str] = []
    for role in _order_roles(roles):
        kind = _ROLE_TO_PATH_KIND.get(role, UNCLASSIFIED_PATH)
        if kind not in out:
            out.append(kind)
    return out


def segment_kinds_for_role(role: str) -> list[str]:
    """Return the role-specific segment kinds (excludes FUNCTION_ENTRY)."""

    return list(_ROLE_TO_SEGMENT_KINDS.get(str(role or "").strip(), (UNKNOWN_SEGMENT,)))


def build_value_path_from_role_classification(classification: object, function_id: str = "") -> ValuePath:
    """Build one :class:`ValuePath` from a ``FunctionRoleClassification``.

    Exactly one value path per classification: ``path_kind`` is the primary
    (highest-priority) role's path kind, ``roles`` carries every role, and all
    mapped path kinds are recorded in ``metadata['path_kinds']``. Segments are
    ``FUNCTION_ENTRY`` followed by the de-duplicated, deterministically ordered
    segment kinds of every role. Assets, oracle sources, external targets, and
    state variables are never invented (left empty).
    """

    roles = _order_roles(list(getattr(classification, "roles", []) or []))
    function_name = str(getattr(classification, "function_name", "") or "")
    contract_name = str(getattr(classification, "contract_name", "") or "")
    fid = str(function_id or "")
    warnings: list[str] = []

    path_kinds = path_kinds_for_roles(roles)
    primary_kind = path_kinds[0] if path_kinds else UNCLASSIFIED_PATH

    for role in roles:
        note = _AMBIGUOUS_ROLE_NOTES.get(role)
        if note and note not in warnings:
            warnings.append(note)
    if not roles:
        warnings.append("no roles to map; unclassified value path; manual review required")

    pid = value_path_id(primary_kind, fid, function_name, contract_name, roles)

    # De-duplicate segment kinds across roles, preserving first occurrence.
    ordered_segment_kinds: list[tuple[str, str]] = []  # (segment_kind, role)
    seen_kinds: set[str] = set()
    for role in roles:
        for kind in segment_kinds_for_role(role):
            if kind not in seen_kinds:
                seen_kinds.add(kind)
                ordered_segment_kinds.append((kind, role))
    if not ordered_segment_kinds:
        ordered_segment_kinds.append((UNKNOWN_SEGMENT, ""))

    segments: list[ValuePathSegment] = []
    entry = ValuePathSegment(
        path_id=pid, segment_kind=FUNCTION_ENTRY, function_id=fid,
        function_name=function_name, contract_name=contract_name, order_index=0,
    )
    entry.segment_id = value_path_segment_id(pid, FUNCTION_ENTRY, 0, "", fid)
    segments.append(entry)
    for index, (kind, role) in enumerate(ordered_segment_kinds, start=1):
        seg = ValuePathSegment(
            path_id=pid, segment_kind=kind, role=role, function_id=fid,
            function_name=function_name, contract_name=contract_name, order_index=index,
        )
        seg.segment_id = value_path_segment_id(pid, kind, index, role, fid)
        segments.append(seg)

    name = f"{contract_name}.{function_name}" if contract_name and function_name else function_name
    metadata: dict[str, object] = {"path_kinds": path_kinds}
    class_warnings = list(getattr(classification, "warnings", []) or [])
    if class_warnings:
        metadata["classification_warnings"] = class_warnings

    return ValuePath(
        path_id=pid,
        path_kind=primary_kind,
        name=name,
        contract_name=contract_name,
        function_name=function_name,
        function_id=fid,
        roles=roles,
        segments=segments,
        linked_function_ids=[fid] if fid else [],
        support_level="CLASSIFIED",
        warnings=warnings,
        manual_review_required=True,
        ready_for_submission=False,
        metadata=metadata,
    )


def build_value_path_graph(protocol_name: str, paths: list[ValuePath]) -> ValuePathGraph:
    """Roll up value paths into a deterministic :class:`ValuePathGraph`."""

    path_list = list(paths or [])
    graph_id = value_path_graph_id(protocol_name, [p.path_id for p in path_list])
    segments: list[ValuePathSegment] = []
    fids: set[str] = set()
    for path in path_list:
        segments.extend(path.segments)
        for fid in path.linked_function_ids:
            if fid:
                fids.add(fid)
        if path.function_id:
            fids.add(path.function_id)
    return ValuePathGraph(
        graph_id=graph_id,
        protocol_name=str(protocol_name or "").strip(),
        value_paths=path_list,
        segments=segments,
        linked_function_ids=sorted(fids),
        manual_review_required=True,
        ready_for_submission=False,
    )


# --- Serialization ----------------------------------------------------------

def value_path_to_dict(value: object) -> object:
    """Recursively serialize value-path dataclasses to plain JSON-ready data.

    Dataclasses become dicts, lists/tuples become lists, dicts are walked, and
    primitives / ``None`` pass through. Unsupported objects raise ``TypeError``.
    Does not mutate the source.
    """

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: value_path_to_dict(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {key: value_path_to_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [value_path_to_dict(item) for item in value]
    raise TypeError(f"unsupported value for value_path_to_dict: {type(value).__name__}")
