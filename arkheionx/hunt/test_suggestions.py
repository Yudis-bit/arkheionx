"""Suggested tests and invariants per hunter target."""
from __future__ import annotations

from arkheionx.protocol.model import FunctionRole


def suggest_tests(fr: FunctionRole) -> tuple[list[str], list[str]]:
    """Return ``(suggested_tests, suggested_invariants)`` for a function."""

    tests: list[str] = []
    invariants: list[str] = []
    token_out = any(c.lower().startswith(("transfer", "safetransfer", "send")) and "from" not in c.lower() for c in fr.external_calls)

    if token_out and fr.writes_state:
        tests.append(f"Reentrant receiver during {fr.function_name}(); assert no double payout")
        invariants.append("Contract token balance >= sum of user claimable")
    if fr.role == "Reward Claim":
        tests.append(f"Call {fr.function_name}() twice in one block; assert second yields zero")
        invariants.append("Sum of claimed rewards <= funded/emitted rewards")
    if fr.oracle_calls:
        tests.append(f"Feed stale/zero/negative price into {fr.function_name}(); assert revert or bounds")
        invariants.append("Price used is fresh and within configured bounds")
    if fr.role in {"Money Entry"}:
        tests.append(f"Deposit/withdraw roundtrip through {fr.function_name}(); assert no value created")
        invariants.append("totalAssets/totalStaked == sum of user balances")
    if fr.role in {"Share Mint", "Share Burn"}:
        tests.append(f"Mint/burn boundary around {fr.function_name}(); assert share<->asset conversion")
        invariants.append("totalSupply of shares is fully backed by assets")
    if fr.privileged:
        tests.append(f"Call {fr.function_name}() from non-owner; assert revert (blast-radius review)")
    if not tests:
        tests.append(f"Exercise {fr.function_name}() happy path and edge cases; assert state deltas")
    return tests, invariants
