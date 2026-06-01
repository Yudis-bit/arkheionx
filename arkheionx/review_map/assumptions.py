"""Assumption mapping for the Review Map.

Assumptions are protective properties a value path appears to rely on. They are
review prompts, not findings. Each is emitted only when a matching signal is
detected locally, and starts at HEURISTIC.
"""
from __future__ import annotations

from collections.abc import Callable

from .model import Assumption, FunctionSurface

# (id, title, description, category, predicate(FunctionSurface) -> bool)
_SPECS: list[tuple[str, str, str, str, Callable[[FunctionSurface], bool]]] = [
    (
        "asm-oracle-fresh", "Oracle price is fresh and trusted",
        "Value paths assume the oracle/price source is current, non-stale, and not manipulable within a block.",
        "oracle", lambda fs: "oracle-dependent" in fs.risk_signals,
    ),
    (
        "asm-standard-erc20", "Tokens behave like standard ERC20",
        "Token transfers are assumed to return true, not take fees, and not re-enter on transfer.",
        "token", lambda fs: fs.value_direction in ("in", "out", "both"),
    ),
    (
        "asm-admin-bounded", "Admin/owner role is trusted and bounded",
        "Privileged configuration is assumed to be controlled by a trusted, bounded role.",
        "access-control", lambda fs: "privileged" in fs.risk_signals,
    ),
    (
        "asm-reward-monotonic", "Reward index is monotonic",
        "Reward accounting assumes the reward index never decreases and is updated before balance changes.",
        "accounting", lambda fs: any(k in fs.name.lower() for k in ("claim", "reward", "accrue", "distribute", "harvest")),
    ),
    (
        "asm-share-proportional", "Share accounting remains proportional",
        "Minted shares / liquidity are assumed to stay proportional to deposited value.",
        "accounting", lambda fs: any(k in fs.name.lower() for k in ("mint", "addliquidity", "share", "deposit", "stake")),
    ),
    (
        "asm-no-reentrancy", "External calls cannot re-enter unsafe state",
        "State is assumed to be settled before external calls, or guarded against re-entry.",
        "reentrancy", lambda fs: "external-call" in fs.risk_signals,
    ),
    (
        "asm-decimals-normalized", "Token and price decimals are normalized",
        "Math assumes consistent decimal scaling between tokens and price feeds.",
        "math", lambda fs: "oracle-dependent" in fs.risk_signals or "decimals" in fs.value_keywords,
    ),
    (
        "asm-fee-bounded", "Fee bounds are enforced",
        "Configurable fees are assumed to be bounded and validated.",
        "config", lambda fs: "fee" in fs.name.lower(),
    ),
    (
        "asm-liquidation-bounded", "Liquidation and health math is bounded",
        "Collateral/debt and liquidation math is assumed to be bounded and free of rounding abuse.",
        "lending", lambda fs: any(k in fs.name.lower() for k in ("borrow", "liquidate", "health", "collateral", "debt")),
    ),
]


def generate_assumptions(surfaces: list[FunctionSurface]) -> list[Assumption]:
    out: list[Assumption] = []
    for aid, title, desc, category, predicate in _SPECS:
        used_by = sorted({fs.display_id for fs in surfaces if predicate(fs)})
        if not used_by:
            continue
        signals = sorted({s for fs in surfaces if predicate(fs) for s in fs.risk_signals})
        out.append(
            Assumption(
                id=aid,
                title=title,
                description=desc,
                category=category,
                used_by=used_by,
                signals=signals,
            )
        )
    return out
