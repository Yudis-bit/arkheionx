"""Static, local detection helpers for the Protocol Review Map.

No compiler, RPC, Foundry, or network is required. Detection reuses the
workbench analysis (``protocol.detector.analyze``) and adds review-oriented
keyword classification. All groups are explicit constants, kept conservative.
"""
from __future__ import annotations

from arkheionx.protocol.model import FunctionRole

from .model import HIGH, LOW, MEDIUM, ContractSurface, FunctionSurface

# --- Keyword groups (lowercased substrings matched against function names) ---
ENTRY_KEYWORDS = ("deposit", "stake", "mint", "addliquidity", "supply", "lock", "fund", "contribute")
MOVEMENT_KEYWORDS = (
    "transfer", "swap", "rebalance", "update", "accrue", "harvest", "claim",
    "distribute", "borrow", "repay", "liquidate", "sync", "settle",
)
EXIT_KEYWORDS = (
    "withdraw", "redeem", "unstake", "burn", "removeliquidity", "claim",
    "collect", "payout", "sweep", "rescue",
)
ADMIN_KEYWORDS = (
    "set", "configure", "pause", "unpause", "upgrade", "initialize",
    "grantrole", "revokerole", "setoracle", "setfee", "setreward",
)
ORACLE_SIGNALS = ("oracle", "price", "feed", "round", "stale", "heartbeat", "decimals", "chainlink", "twap")
# External-call / reentrancy signals (matched against external_calls + name).
EXTERNAL_CALL_SIGNALS = (
    "call", "delegatecall", "transfer", "send", "safetransfer",
    "safetransferfrom", "onerc721received", "onerc1155received", "callback",
)

# Token movement primitives that pull value in vs push value out.
_VALUE_IN_CALLS = ("transferfrom", "safetransferfrom")
_VALUE_OUT_CALLS = ("transfer", "safetransfer", "send")

# Asset-like state variable name fragments.
_ASSET_FRAGMENTS = (
    "token", "reserve", "collateral", "debt", "balance", "liquidity",
    "staked", "total", "reward", "asset", "share", "vault", "pool", "deposit",
)


def _match(name_lower: str, keywords: tuple[str, ...]) -> list[str]:
    return [kw for kw in keywords if kw in name_lower]


def value_direction(name_lower: str, external_calls: list[str]) -> str:
    """Classify token-value direction as in | out | both | none.

    The underlying parser matches ``transfer`` as a substring of
    ``transferFrom``, so a plain transfer is only treated as value-out when no
    ``transferFrom`` is present or the name itself implies an exit/swap.
    """

    calls = [c.lower() for c in external_calls]
    has_from = any(c in _VALUE_IN_CALLS for c in calls)
    plain_transfer = any(c in ("transfer", "safetransfer", "send") for c in calls)
    name_entry = bool(_match(name_lower, ENTRY_KEYWORDS))
    name_exit = bool(_match(name_lower, EXIT_KEYWORDS))
    name_swap = "swap" in name_lower
    # A plain transfer is only a genuine push-out when not shadowed by a
    # transferFrom substring match. Names disambiguate exchanges (swap) and
    # avoid "unstake" being read as "stake" (entry).
    real_out_call = plain_transfer and not has_from
    has_in = has_from or (name_entry and not name_exit)
    has_out = real_out_call or name_exit or name_swap
    if has_in and has_out:
        return "both"
    if has_out:
        return "out"
    if has_in:
        return "in"
    return "none"


def _oracle_signals(name_lower: str, fr: FunctionRole) -> list[str]:
    signals = set(_match(name_lower, ORACLE_SIGNALS))
    if fr.oracle_calls:
        signals.add("oracle")
    return sorted(signals)


def _risk_signals(name_lower: str, fr: FunctionRole, direction: str, oracle: list[str]) -> list[str]:
    signals: list[str] = []
    if direction in ("out", "both"):
        signals.append("value-out")
    if direction in ("in", "both"):
        signals.append("value-in")
    if oracle:
        signals.append("oracle-dependent")
    if any(c.lower() in EXTERNAL_CALL_SIGNALS for c in fr.external_calls) or any(
        c in ("call", "delegatecall") for c in (x.lower() for x in fr.external_calls)
    ):
        signals.append("external-call")
    if fr.privileged or _match(name_lower, ("grantrole", "revokerole")):
        signals.append("privileged")
    if any(k in name_lower for k in ("borrow", "liquidate")):
        signals.append("debt-or-liquidation")
    return sorted(set(signals))


def _is_admin(name_lower: str, fr: FunctionRole) -> bool:
    if fr.privileged:
        return True
    return any(name_lower.startswith(k) or name_lower == k for k in ADMIN_KEYWORDS)


def _admin_controls_value(name_lower: str) -> bool:
    return any(k in name_lower for k in ("oracle", "fee", "reward", "price", "emission", "rate", "treasury"))


def function_priority(name_lower: str, fr: FunctionRole, direction: str, oracle: list[str], admin: bool) -> str:
    """Review priority. Never a severity; it only orders review attention."""

    external = "external-call" in _risk_signals(name_lower, fr, direction, oracle)
    # High: value-out, borrow/liquidate, oracle+sensitive, external+value-out,
    # admin controlling oracle/fees/rewards.
    if direction in ("out", "both"):
        return HIGH
    if any(k in name_lower for k in ("borrow", "liquidate")):
        return HIGH
    if oracle and any(k in name_lower for k in ("borrow", "liquidate", "withdraw", "redeem")):
        return HIGH
    if external and direction in ("out", "both"):
        return HIGH
    if admin and _admin_controls_value(name_lower):
        return HIGH
    # Medium: value-in/accounting, reward distribution, liquidity management.
    if direction == "in":
        return MEDIUM
    if any(k in name_lower for k in ("claim", "reward", "distribute", "accrue", "harvest", "swap")):
        return MEDIUM
    if any(k in name_lower for k in ("addliquidity", "removeliquidity", "liquidity", "sync")):
        return MEDIUM
    if admin:
        return MEDIUM
    # Low: views / helpers / metadata.
    return LOW


def _mutability(fr: FunctionRole) -> str:
    return "view" if not fr.writes_state else "state-changing"


def build_function_surface(fr: FunctionRole) -> FunctionSurface:
    name_lower = fr.function_name.lower()
    direction = value_direction(name_lower, fr.external_calls)
    oracle = _oracle_signals(name_lower, fr)
    admin = _is_admin(name_lower, fr)
    risk = _risk_signals(name_lower, fr, direction, oracle)
    keywords = sorted(set(
        _match(name_lower, ENTRY_KEYWORDS)
        + _match(name_lower, MOVEMENT_KEYWORDS)
        + _match(name_lower, EXIT_KEYWORDS)
        + (_match(name_lower, ADMIN_KEYWORDS) if admin else [])
    ))
    mutability = _mutability(fr)
    priority = function_priority(name_lower, fr, direction, oracle, admin)
    # View/helper functions are low priority even if name hints at value.
    if mutability == "view" and direction == "none" and not admin:
        priority = LOW
    line = fr.line_range[0] if fr.line_range else 0
    return FunctionSurface(
        contract=fr.contract_name,
        name=fr.function_name,
        signature=fr.signature,
        visibility=fr.visibility,
        mutability=mutability,
        path=fr.file_path,
        line=line,
        value_direction=direction,
        value_keywords=keywords,
        risk_signals=risk,
        review_priority=priority,
    )


def is_value_sensitive(fs: FunctionSurface) -> bool:
    return fs.value_direction != "none" or bool(
        set(fs.risk_signals) & {"value-in", "value-out", "oracle-dependent", "debt-or-liquidation"}
    )


def _contract_assets(functions: list[FunctionRole], declared: list[str]) -> list[str]:
    assets = set(declared or [])
    for fr in functions:
        for var in list(fr.writes_state) + list(fr.reads_state):
            if any(fragment in var.lower() for fragment in _ASSET_FRAGMENTS):
                assets.add(var)
    return sorted(assets)


def build_contract_surface(name: str, path: str, kind: str, roles: list[str], declared_assets: list[str],
                            frs: list[FunctionRole], surfaces: list[FunctionSurface]) -> ContractSurface:
    from .model import priority_rank

    external = sorted({c for fr in frs for c in fr.external_calls})
    oracle_signals = sorted({s for fr in frs for s in _oracle_signals(fr.function_name.lower(), fr)})
    value_sensitive = any(is_value_sensitive(fs) for fs in surfaces)
    priority = LOW
    for fs in surfaces:
        if priority_rank(fs.review_priority) < priority_rank(priority):
            priority = fs.review_priority
    return ContractSurface(
        name=name,
        path=path,
        kind=kind,
        functions=sorted(fr.function_name for fr in frs),
        roles=sorted(set(roles)),
        assets=_contract_assets(frs, declared_assets),
        external_calls=external,
        oracle_signals=oracle_signals,
        value_sensitive=value_sensitive,
        review_priority=priority,
    )
