"""Value-flow engine for hunter mode.

Identifies *real value movement*: where assets enter, where they exit, which
accounting and state-machine variables gate the path, whether an external call
happens before or after the state update (a reentrancy-ordering signal), whether the
path is reachable by an unprivileged attacker, and what breaks if the invariant fails.

Local/static and read-only. Heuristic, not a compiler; a value path is a research
lens, not a finding.
"""
from __future__ import annotations

import re

from . import models as M
from . import source_scan

# Value entry signals.
_VALUE_IN = (
    "msg.value", "transferfrom", "safetransferfrom", "deposit", "mint", "stake",
    "supply", "wrap", "donate", "fund", "addliquidity",
)
# Value exit signals.
_VALUE_OUT = (
    ".call{", ".call(", ".transfer(", ".send(", "safetransfer", "withdraw", "redeem",
    "claim", "unstake", "exit", "migrate", "sweep", "rescue", "distribute", "dispatch",
    "pay", "pull", "push", "release", "unwrap", "removeliquidity",
)
# Accounting variables.
_ACCOUNTING_VARS = (
    "shares", "totalsupply", "totalassets", "balance", "liquidity", "principal",
    "rewards", "fees", "commission", "debt", "credit", "coverage", "cursor",
    "checkpoint", "epoch", "round", "rate", "price", "exchangerate", "locked",
    "unlocked", "claimed", "withdrawn", "released", "maturity", "queueindex",
)
# State-machine variables.
_STATE_VARS = (
    "status", "phase", "pending", "queued", "exited", "withdrawn", "claimed",
    "released", "activated", "finalized", "migrated", "locked", "unlocked", "cursor",
    "index", "checkpoint", "round", "epoch", "nonce", "request", "coverage",
    "deficit", "shortfall", "maturity",
)
_EXTERNAL_CALL_RE = re.compile(r"\.(call|delegatecall|staticcall)\s*[{(]|\b[A-Za-z_]\w*\.[a-z]\w*\s*\(")
_STATE_WRITE_RE = re.compile(r"\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*(?:=|\+=|-=)\s")
_ROLE_GUARD_RE = re.compile(
    r"only(Owner|Admin|Role|Governance|Guardian|Operator|Keeper)|"
    r"require\s*\(\s*msg\.sender\s*==|hasRole\s*\(|_checkRole|_checkOwner",
    re.IGNORECASE,
)
_ASSET_RE = re.compile(r"\b(asset|token|underlying|weth|stETH|want|reward[sS]?)\b", re.IGNORECASE)


def _present(body_low: str, terms) -> list:
    return sorted({t for t in terms if t in body_low})


def _reachability(fn) -> tuple[str, bool]:
    vis = (fn.visibility or "").lower()
    role_guarded = bool(_ROLE_GUARD_RE.search(fn.body)) or bool(_ROLE_GUARD_RE.search(fn.raw_signature))
    if vis in ("internal", "private"):
        return "INTERNAL_ONLY", role_guarded
    if role_guarded:
        return "TRUSTED_ROLE", True
    if vis in ("public", "external"):
        return "UNPRIVILEGED_EXTERNAL", False
    return "UNKNOWN", role_guarded


def _ordering(body: str) -> str:
    body_low = body.lower()
    ext = _EXTERNAL_CALL_RE.search(body)
    if not ext:
        return "no-external-call"
    first_ext = ext.start()
    first_write = None
    for m in _STATE_WRITE_RE.finditer(body):
        var = m.group(1).lower()
        if any(v in var for v in _ACCOUNTING_VARS) or any(v in var for v in _STATE_VARS):
            first_write = m.start()
            break
    if first_write is None:
        return "external-call-without-tracked-state-update"
    if first_ext < first_write:
        return "external-call-before-state-update (reentrancy-suspect)"
    return "state-update-before-external-call (CEI-ordered)"


def _entry_asset(body: str) -> str:
    if "msg.value" in body.lower():
        return "native ETH (msg.value)"
    m = _ASSET_RE.search(body)
    return m.group(0) if m else ""


def build_value_paths(review_map, sources: dict) -> list:
    """Build value paths from contract sources (and review-map value paths)."""
    paths: list = []
    counter = 0

    def _next_id() -> str:
        nonlocal counter
        counter += 1
        return f"VP-{counter:03d}"

    for contract, (path, text) in sorted(sources.items()):
        for fn in source_scan.find_functions(text):
            if not fn.body:
                continue
            low = fn.body.lower()
            has_in = any(s in low for s in _VALUE_IN)
            has_out = any(s in low for s in _VALUE_OUT)
            if not (has_in or has_out):
                continue
            accounting = _present(low, _ACCOUNTING_VARS)
            state_vars = _present(low, _STATE_VARS)
            ext_calls = sorted({m.group(0).strip() for m in _EXTERNAL_CALL_RE.finditer(fn.body)})[:8]
            reachability, trusted = _reachability(fn)
            direction = "out" if has_out else "in"
            impact = (
                "Unauthorized value exit / accounting corruption if the guard or ordering is wrong."
                if has_out else
                "Mis-accounted value entry (share/asset accounting) if the deposit math is wrong."
            )
            paths.append(M.ValuePath(
                path_id=_next_id(),
                entry_function=f"{contract}.{fn.name}" if has_in else "",
                entry_asset=_entry_asset(fn.body),
                accounting_variables=accounting,
                state_machine_variables=state_vars,
                external_calls=ext_calls,
                state_update_ordering=_ordering(fn.body),
                exit_function=f"{contract}.{fn.name}" if has_out else "",
                recipient="caller / arbitrary `to`" if has_out else "",
                attacker_reachability=reachability,
                trusted_role_required=trusted,
                impact_if_broken=impact,
                source_lines=[f"{path}:L{fn.line}"],
            ))
    return paths


def value_paths_for_contract(value_paths: list, contract: str) -> list:
    contract = (contract or "").lower()
    out: list = []
    for vp in value_paths:
        surf = (vp.entry_function or vp.exit_function or "").split(".")[0].lower()
        if surf and surf == contract:
            out.append(vp.path_id)
    return out
