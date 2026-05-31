"""Detect user journeys from classified functions.

A journey groups related entry and exit functions into a plain-language story
a researcher can follow (e.g. "Stake and claim rewards").
"""
from __future__ import annotations

from .model import HEURISTIC, FunctionRole, UserJourney

# (journey name, entry-name fragments, exit-name fragments)
_JOURNEY_SHAPES = (
    ("Stake and claim rewards", ("stake",), ("unstake", "claim")),
    ("Deposit and withdraw", ("deposit",), ("withdraw", "redeem")),
    ("Supply and borrow", ("supply", "deposit"), ("borrow", "repay", "withdraw")),
    ("Provide and remove liquidity", ("addliquidity",), ("removeliquidity",)),
    ("Swap assets", ("swap",), ("swap",)),
    ("Mint and burn", ("mint",), ("burn", "redeem")),
)


def _matches(froles: list[FunctionRole], fragments: tuple[str, ...]) -> list[str]:
    out = []
    for fr in froles:
        if fr.visibility in {"public", "external"} and any(f in fr.function_name.lower() for f in fragments):
            out.append(fr.function_name)
    return sorted(set(out))


def detect_journeys(function_roles: list[FunctionRole]) -> list[UserJourney]:
    journeys: list[UserJourney] = []
    seen_entries: set[str] = set()
    for name, entry_frags, exit_frags in _JOURNEY_SHAPES:
        entries = _matches(function_roles, entry_frags)
        exits = _matches(function_roles, exit_frags)
        if not entries:
            continue
        # Avoid duplicate journeys that reuse the same primary entry function.
        primary = entries[0]
        if primary in seen_entries:
            continue
        seen_entries.add(primary)
        steps = [f"User calls {entries[0]}() to enter"]
        if exits:
            steps.append(f"Protocol updates accounting/state")
            steps.append(f"User calls {exits[0]}() to exit or claim value")
        assets = _infer_assets(function_roles)
        journeys.append(
            UserJourney(
                name=name,
                actor="User",
                steps=steps,
                entry_functions=entries,
                exit_functions=exits,
                assets_involved=assets,
                evidence_level=HEURISTIC,
            )
        )
    if not journeys:
        journeys.append(
            UserJourney(
                name="No clear user journey detected",
                actor="Unknown",
                steps=["No standard deposit/stake/swap entry points were detected."],
                evidence_level=HEURISTIC,
            )
        )
    return journeys


def _infer_assets(function_roles: list[FunctionRole]) -> list[str]:
    assets: set[str] = set()
    for fr in function_roles:
        if any(c.lower().startswith(("transfer", "safetransfer", "send")) for c in fr.external_calls):
            assets.add("ERC20 token")
    return sorted(assets)
