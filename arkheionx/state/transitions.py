"""State transition models (Layer 3).

A :class:`StateTransition` reconstructs the before/action/after lifecycle of a
value-affecting function: who acts, what must hold first, what storage and assets
move, which external calls fire, and which status changes occur. It also carries
``possible_invariants`` — hints the invariant engine keys on.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

LOW, MEDIUM, HIGH = "LOW", "MEDIUM", "HIGH"

# Lifecycle categories.
LC_DEPOSIT = "deposit"
LC_BORROW = "borrow"
LC_REPAY = "repay"
LC_LIQUIDATION = "liquidation"
LC_VAULT_DEPOSIT = "vault_deposit"
LC_VAULT_WITHDRAW = "vault_withdraw"
LC_REDEMPTION = "redemption"
LC_SWAP = "swap"
LC_ADAPTER = "adapter"
LC_DEPOSIT_CONSUME = "deposit_consume"
LC_CROSS_CHAIN = "cross_chain"
LC_GOVERNANCE = "governance"
LC_GENERIC = "generic"


@dataclass
class StateTransition:
    id: str = ""
    contract: str = ""
    function: str = ""
    actor: str = "anyone"
    lifecycle: str = LC_GENERIC
    preconditions: list = field(default_factory=list)
    state_reads: list = field(default_factory=list)
    state_writes: list = field(default_factory=list)
    assets_in: list = field(default_factory=list)
    assets_out: list = field(default_factory=list)
    external_calls: list = field(default_factory=list)
    status_changes: list = field(default_factory=list)
    before_summary: str = ""
    after_summary: str = ""
    possible_invariants: list = field(default_factory=list)
    flags: list = field(default_factory=list)  # e.g. has_division, calldata_route, ext_before_write
    confidence: str = MEDIUM
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class TransitionMap:
    root: str = ""
    transitions: list = field(default_factory=list)

    def for_function(self, qualified):
        for t in self.transitions:
            if t.function == qualified:
                return t
        return None

    def to_dict(self) -> dict:
        return {
            "schema_version": "v10-state-transitions",
            "root": self.root,
            "transition_count": len(self.transitions),
            "transitions": [t.to_dict() for t in self.transitions],
        }
