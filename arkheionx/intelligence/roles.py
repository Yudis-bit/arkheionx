"""Internal function-role taxonomy and deterministic role IDs (v3.8, additive).

This module assigns controlled, descriptive review roles to a Solidity function
from its name / signature alone, using boundary-aware token matching (never
substring or fuzzy matching). It is internal infrastructure: it has no
filesystem, network, subprocess, CLI, or live-chain behavior, and importing it
has no side effects.

Roles are review surface only. A role describes what a function structurally does
(for example it moves value in, or it sets an oracle); it never asserts a
confirmed vulnerability, a final severity, an audit outcome, submission
readiness, or a safe verdict. Every classification keeps ``manual_review_required``
true and ``ready_for_submission`` false, and never emits a human-reviewed status.

Classification ``confidence`` reports that the engine produced a structural
classification (``CLASSIFIED``); it is never security confidence.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

_HASH_LEN = 12

# --- Controlled role taxonomy -----------------------------------------------

INFLOW = "INFLOW"
OUTFLOW = "OUTFLOW"
ACCOUNTING_MUTATION = "ACCOUNTING_MUTATION"
EXTERNAL_CALL = "EXTERNAL_CALL"
ORACLE_CONSUMER = "ORACLE_CONSUMER"
ORACLE_SETTER = "ORACLE_SETTER"
ADMIN_PARAM = "ADMIN_PARAM"
ACCESS_CONTROL = "ACCESS_CONTROL"
PAUSE_EMERGENCY = "PAUSE_EMERGENCY"
UPGRADE_PROXY = "UPGRADE_PROXY"
DELEGATECALL = "DELEGATECALL"
BORROW_REPAY = "BORROW_REPAY"
LIQUIDATION = "LIQUIDATION"
SWAP = "SWAP"
MINT_BURN = "MINT_BURN"
CLAIM_REWARD = "CLAIM_REWARD"
BRIDGE = "BRIDGE"
VIEW_PURE = "VIEW_PURE"

# Sentinel for "no controlled role matched". Never implies safety.
UNCLASSIFIED = "UNCLASSIFIED"

# Stable priority order (low index = higher precedence in the output ordering).
# This is review ordering only; it is never a severity.
ROLE_PRIORITY: tuple[str, ...] = (
    UPGRADE_PROXY,
    DELEGATECALL,
    PAUSE_EMERGENCY,
    ACCESS_CONTROL,
    ADMIN_PARAM,
    ORACLE_SETTER,
    LIQUIDATION,
    BORROW_REPAY,
    BRIDGE,
    SWAP,
    MINT_BURN,
    CLAIM_REWARD,
    INFLOW,
    OUTFLOW,
    ACCOUNTING_MUTATION,
    EXTERNAL_CALL,
    ORACLE_CONSUMER,
    VIEW_PURE,
)

FUNCTION_ROLE_VALUES: tuple[str, ...] = ROLE_PRIORITY

FUNCTION_ROLE_DESCRIPTIONS: dict[str, str] = {
    INFLOW: "Pulls value into the protocol (deposit / supply / stake / add liquidity).",
    OUTFLOW: "Sends value out of the protocol (withdraw / redeem / unstake).",
    ACCOUNTING_MUTATION: "Mutates internal accounting state (accrue / index / settle / sync).",
    EXTERNAL_CALL: "Makes or batches external calls (multicall / execute / flash loan / sweep).",
    ORACLE_CONSUMER: "Reads a price / oracle value (price / latest answer / quote / exchange rate).",
    ORACLE_SETTER: "Sets or updates an oracle / price-feed source.",
    ADMIN_PARAM: "Sets a privileged configuration parameter (fee / limit / treasury / guardian).",
    ACCESS_CONTROL: "Changes roles, ownership, or operators (grant / revoke / transfer ownership).",
    PAUSE_EMERGENCY: "Pause, unpause, or emergency action.",
    UPGRADE_PROXY: "Upgrade / implementation / proxy-admin action.",
    DELEGATECALL: "Uses delegatecall.",
    BORROW_REPAY: "Borrow / repay / refinance debt.",
    LIQUIDATION: "Liquidation / seize / auction.",
    SWAP: "Swap / exact-input / exact-output / route.",
    MINT_BURN: "Mint / burn / issue tokens or shares.",
    CLAIM_REWARD: "Claim / harvest rewards.",
    BRIDGE: "Bridge / cross-chain message / relay / finalize withdrawal.",
    VIEW_PURE: "Read-only view / pure / preview / get / calculate function.",
    UNCLASSIFIED: "No controlled role matched; manual review required.",
}

# Roles that imply a state change (suppressed for view/pure/preview/get/etc.).
_STATE_MUTATING_ROLES: frozenset[str] = frozenset(
    FUNCTION_ROLE_VALUES
) - frozenset({ORACLE_CONSUMER, VIEW_PURE})

_VIEW_PREFIXES: frozenset[str] = frozenset(
    {"get", "preview", "quote", "calculate", "compute", "view", "is", "simulate"}
)
_ROLE_PRIORITY_INDEX: dict[str, int] = {role: i for i, role in enumerate(ROLE_PRIORITY)}


# --- ID + canonical hashing -------------------------------------------------

def canonical_role_seed(value: object) -> str:
    """Return a canonical JSON seed (sorted keys, compact separators).

    Raises ``TypeError`` for objects that are not JSON-native (for example a set
    or an arbitrary object), so an unsupported seed never silently stringifies.
    """

    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _short_hash(value: object) -> str:
    return hashlib.sha256(canonical_role_seed(value).encode("utf-8")).hexdigest()[:_HASH_LEN]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")


def function_role_classification_id(
    function_name: str,
    signature: str = "",
    selector: str = "",
    contract_name: str = "",
    roles: list[str] | None = None,
) -> str:
    """Deterministic classification ID. ``roles`` are sorted before hashing, so
    classification identity does not depend on role output order."""

    name = str(function_name or "").strip()
    sig = normalize_signature(signature)
    if not name and not sig:
        raise ValueError("function_role_classification_id requires function_name or signature")
    seed = {
        "function_name": name,
        "signature": sig,
        "selector": normalize_selector(selector),
        "contract_name": str(contract_name or "").strip(),
        "roles": sorted(str(r) for r in (roles or [])),
    }
    return f"function-role-classification:{_short_hash(seed)}"


def function_role_id(
    role: str,
    function_name: str = "",
    signature: str = "",
    selector: str = "",
    contract_name: str = "",
) -> str:
    """Deterministic per-(role, function) ID. Requires a non-empty ``role``."""

    role_text = str(role or "").strip()
    if not role_text:
        raise ValueError("function_role_id requires a non-empty role")
    seed = {
        "role": role_text,
        "function_name": str(function_name or "").strip(),
        "signature": normalize_signature(signature),
        "selector": normalize_selector(selector),
        "contract_name": str(contract_name or "").strip(),
    }
    return f"function-role:{_slug(role_text)}:{_short_hash(seed)}"


# --- Tokenization + normalization -------------------------------------------

_TOKEN_RE = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z0-9]+|[A-Z]+")
_SELECTOR_RE = re.compile(r"^(?:0x)?[0-9a-fA-F]{8}$")


def split_identifier_tokens(value: str) -> list[str]:
    """Split a Solidity identifier into lowercase tokens (boundary-aware).

    Handles camelCase (``withdrawAll`` -> ``withdraw``, ``all``), snake_case and
    kebab-case (``set_oracle`` -> ``set``, ``oracle``), leading/trailing
    underscores, embedded numbers, and uppercase acronyms. Empty input -> ``[]``.
    A whole, separator-free lowercase word stays one token (``unstake`` ->
    ``unstake``), which is what prevents ``unstake`` reading as ``stake``.
    """

    text = str(value or "").strip()
    if not text:
        return []
    # Drop any signature/argument tail and qualifier before tokenizing.
    text = extract_function_name_from_signature(text)
    text = text.replace("-", " ").replace("_", " ")
    return [tok.lower() for tok in _TOKEN_RE.findall(text) if tok]


def normalize_selector(value: str) -> str:
    """Normalize a 4-byte selector to ``0x`` + 8 lowercase hex, or ``""``.

    Accepts an optionally ``0x``-prefixed 8-hex string. Any other non-empty value
    is rejected (returns ``""``), never guessed.
    """

    text = str(value or "").strip()
    if not text:
        return ""
    if not _SELECTOR_RE.match(text):
        return ""
    hex_part = text[2:] if text.lower().startswith("0x") else text
    return "0x" + hex_part.lower()


def normalize_signature(signature: str) -> str:
    """Collapse redundant whitespace while preserving argument order and types."""

    return re.sub(r"\s+", " ", str(signature or "").strip())


def extract_function_name_from_signature(signature: str) -> str:
    """Return the function name from a signature or qualified display name.

    ``withdraw(uint256)`` -> ``withdraw``; ``Vault.withdraw(uint256)`` ->
    ``withdraw``; a bare name is returned unchanged (whitespace-trimmed).
    """

    text = str(signature or "").strip()
    if not text:
        return ""
    text = text.split("(", 1)[0].strip()
    if "." in text:
        text = text.rsplit(".", 1)[-1].strip()
    return text


# --- Classification ----------------------------------------------------------

@dataclass
class FunctionRoleClassification:
    """A pure, local/static structural role classification for one function.

    Review surface only: roles describe structure, never a vulnerability,
    severity, audit outcome, or submission readiness.
    """

    classification_id: str = ""
    function_name: str = ""
    signature: str = ""
    selector: str = ""
    contract_name: str = ""
    roles: list[str] = field(default_factory=list)
    matched_tokens: list[str] = field(default_factory=list)
    unmatched_tokens: list[str] = field(default_factory=list)
    confidence: str = "CLASSIFIED"
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return asdict(self)


def _has(token_set: set[str], *tokens: str) -> bool:
    return any(t in token_set for t in tokens)


def _pair(token_set: set[str], a: str, b: str) -> bool:
    return a in token_set and b in token_set


def _raw_role_matches(tokens: list[str], full: str) -> dict[str, list[str]]:
    """Return {role: [matched tokens]} from boundary-aware token rules only.

    No substring matching: every test is against whole tokens, explicit token
    pairs, or the separator-free full name (an exact whole-name match).
    """

    ts = set(tokens)
    matched: dict[str, list[str]] = {}

    def add(role: str, *toks: str) -> None:
        bucket = matched.setdefault(role, [])
        for tok in toks:
            if tok and tok not in bucket:
                bucket.append(tok)

    # INFLOW
    for tok in ("deposit", "supply", "fund", "contribute", "stake"):
        if tok in ts:
            add(INFLOW, tok)
    if _pair(ts, "add", "liquidity"):
        add(INFLOW, "add", "liquidity")
    if full == "transferfrom":  # pulls value in; never a plain-transfer outflow
        add(INFLOW, "transfer", "from")

    # OUTFLOW
    for tok in ("withdraw", "redeem", "unstake", "payout", "collect"):
        if tok in ts:
            add(OUTFLOW, tok)
    if _pair(ts, "remove", "liquidity"):
        add(OUTFLOW, "remove", "liquidity")

    # ACCOUNTING_MUTATION
    for tok in ("accrue", "settle", "sync", "rebalance", "checkpoint", "harvest"):
        if tok in ts:
            add(ACCOUNTING_MUTATION, tok)
    if _pair(ts, "update", "index"):
        add(ACCOUNTING_MUTATION, "update", "index")
    if _pair(ts, "update", "accounting"):
        add(ACCOUNTING_MUTATION, "update", "accounting")

    # EXTERNAL_CALL
    for tok in ("multicall", "execute", "sweep", "rescue"):
        if tok in ts:
            add(EXTERNAL_CALL, tok)
    if _pair(ts, "flash", "loan"):
        add(EXTERNAL_CALL, "flash", "loan")
    if _pair(ts, "transfer", "out"):
        add(EXTERNAL_CALL, "transfer", "out")

    # ORACLE_SETTER (checked so it can suppress ORACLE_CONSUMER below)
    if _has(ts, "set", "update") and _has(ts, "oracle", "aggregator", "pricefeed"):
        add(ORACLE_SETTER, *[t for t in ("set", "update", "oracle", "aggregator", "pricefeed") if t in ts])
    if _has(ts, "set", "update") and _pair(ts, "price", "feed"):
        add(ORACLE_SETTER, *[t for t in ("set", "update", "price", "feed") if t in ts])

    # ORACLE_CONSUMER
    for tok in ("price", "consult", "quote", "exchangerate", "latestanswer"):
        if tok in ts:
            add(ORACLE_CONSUMER, tok)
    if _pair(ts, "latest", "answer"):
        add(ORACLE_CONSUMER, "latest", "answer")
    if _pair(ts, "exchange", "rate"):
        add(ORACLE_CONSUMER, "exchange", "rate")

    # ADMIN_PARAM
    if "set" in ts and _has(
        ts, "fee", "config", "limit", "parameter", "param", "treasury",
        "guardian", "rate", "cap", "threshold", "ratio", "factor",
    ):
        add(ADMIN_PARAM, *[t for t in (
            "set", "fee", "config", "limit", "parameter", "param", "treasury",
            "guardian", "rate", "cap", "threshold", "ratio", "factor") if t in ts])

    # ACCESS_CONTROL
    if "ownership" in ts:
        add(ACCESS_CONTROL, "ownership")
    if "role" in ts and _has(ts, "grant", "revoke", "renounce", "set", "has"):
        add(ACCESS_CONTROL, "role", *[t for t in ("grant", "revoke", "renounce", "set", "has") if t in ts])
    if "set" in ts and _has(ts, "admin", "operator", "manager"):
        add(ACCESS_CONTROL, "set", *[t for t in ("admin", "operator", "manager") if t in ts])

    # PAUSE_EMERGENCY
    for tok in ("pause", "unpause", "emergency"):
        if tok in ts:
            add(PAUSE_EMERGENCY, tok)
    if "shutdown" in ts:
        add(PAUSE_EMERGENCY, "shutdown")

    # UPGRADE_PROXY
    for tok in ("upgrade", "implementation", "proxyadmin"):
        if tok in ts:
            add(UPGRADE_PROXY, tok)
    if _pair(ts, "set", "implementation"):
        add(UPGRADE_PROXY, "set", "implementation")
    if _pair(ts, "proxy", "admin"):
        add(UPGRADE_PROXY, "proxy", "admin")

    # DELEGATECALL
    if "delegatecall" in ts:
        add(DELEGATECALL, "delegatecall")
    if _pair(ts, "delegate", "call"):
        add(DELEGATECALL, "delegate", "call")

    # BORROW_REPAY
    for tok in ("borrow", "repay", "refinance"):
        if tok in ts:
            add(BORROW_REPAY, tok)

    # LIQUIDATION
    for tok in ("liquidate", "liquidation", "seize", "auction"):
        if tok in ts:
            add(LIQUIDATION, tok)

    # SWAP
    if "swap" in ts:
        add(SWAP, "swap")
    if "route" in ts:
        add(SWAP, "route")
    if _pair(ts, "exact", "input") or _pair(ts, "exact", "output"):
        add(SWAP, "exact", *[t for t in ("input", "output") if t in ts])

    # MINT_BURN
    for tok in ("mint", "burn", "issue"):
        if tok in ts:
            add(MINT_BURN, tok)

    # CLAIM_REWARD
    for tok in ("claim", "reward", "rewards"):
        if tok in ts:
            add(CLAIM_REWARD, tok)

    # BRIDGE
    for tok in ("bridge", "relay"):
        if tok in ts:
            add(BRIDGE, tok)
    if "message" in ts and _has(ts, "send", "receive"):
        add(BRIDGE, "message", *[t for t in ("send", "receive") if t in ts])
    if _pair(ts, "finalize", "withdrawal"):
        add(BRIDGE, "finalize", "withdrawal")

    return matched


def _order_roles(roles: set[str]) -> list[str]:
    return sorted(roles, key=lambda r: _ROLE_PRIORITY_INDEX.get(r, len(ROLE_PRIORITY)))


def classify_function_role(
    function_name: str = "",
    signature: str = "",
    selector: str = "",
    contract_name: str = "",
    mutability: str = "",
    visibility: str = "",
    modifiers: list[str] | None = None,
    metadata: dict[str, object] | None = None,
) -> FunctionRoleClassification:
    """Classify a function into controlled roles by boundary-aware tokens only.

    Multi-label, deterministic, and exact: roles never come from substring or
    fuzzy matching, and an ambiguous case adds a warning rather than inventing
    certainty. Returns a :class:`FunctionRoleClassification` (review surface only;
    no security finality).
    """

    name = str(function_name or "").strip() or extract_function_name_from_signature(signature)
    sig = normalize_signature(signature)
    sel = normalize_selector(selector)
    tokens = split_identifier_tokens(name) if name else split_identifier_tokens(sig)
    full = "".join(tokens)
    mut = str(mutability or "").strip().lower()
    warnings: list[str] = []
    meta: dict[str, object] = dict(metadata or {})

    result = FunctionRoleClassification(
        function_name=name,
        signature=sig,
        selector=sel,
        contract_name=str(contract_name or "").strip(),
        confidence="CLASSIFIED",
        manual_review_required=True,
        ready_for_submission=False,
        warnings=warnings,
        metadata=meta,
    )

    if not tokens:
        warnings.append("empty function identifier; no role classified; manual review required")
        result.unmatched_tokens = []
        result.roles = []
        return result

    raw = _raw_role_matches(tokens, full)
    roles = set(raw)

    # An oracle setter consumes nothing; drop a coincidental consumer signal.
    if ORACLE_SETTER in roles and ORACLE_CONSUMER in roles:
        roles.discard(ORACLE_CONSUMER)
        raw.pop(ORACLE_CONSUMER, None)

    # updateOracle is genuinely ambiguous (sets vs reads the oracle).
    if "update" in set(tokens) and "oracle" in set(tokens):
        warnings.append("updateOracle is ambiguous (may set or consume the oracle); manual review required")

    # View-like detection: explicit view/pure mutability or a read-only prefix.
    view_by_mutability = mut in ("view", "pure")
    view_by_prefix = bool(tokens) and tokens[0] in _VIEW_PREFIXES
    view_like = view_by_mutability or view_by_prefix

    if view_like:
        state_roles = roles & _STATE_MUTATING_ROLES
        if state_roles:
            if view_by_mutability:
                warnings.append(
                    "contradiction: name suggests state change ("
                    + ", ".join(_order_roles(state_roles))
                    + f") but mutability is '{mut}'; suppressed; manual review required"
                )
            else:
                meta["view_like_prefix_suppressed"] = _order_roles(state_roles)
            for role in state_roles:
                roles.discard(role)
                raw.pop(role, None)
        roles.add(VIEW_PURE)
        meta["view_like"] = True

    matched_tokens: set[str] = set()
    for role in roles:
        for tok in raw.get(role, []):
            matched_tokens.add(tok)

    if not roles:
        warnings.append("no controlled role matched; manual review required")
        meta["status"] = UNCLASSIFIED

    result.roles = _order_roles(roles)
    result.matched_tokens = sorted(matched_tokens)
    result.unmatched_tokens = sorted(t for t in set(tokens) if t not in matched_tokens)
    result.classification_id = function_role_classification_id(
        name, signature=sig, selector=sel, contract_name=contract_name, roles=result.roles
    )
    return result
