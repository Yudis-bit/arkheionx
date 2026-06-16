"""Invariant models (Layer 4).

An :class:`Invariant` is an actionable, falsifiable economic property tied to a
state transition. Bad: "potential accounting mismatch." Good: "debt reduction in
repay() must reconcile with lender repayment credit; suspicious if debt is reduced
before per-tranche flooring."

Invariants carry whether they look *suspicious here* (a breakage hypothesis with
reasons) — this is what later layers turn into candidates. An invariant alone is
review context, never a finding.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

LOW, MEDIUM, HIGH = "LOW", "MEDIUM", "HIGH"

# Testability ladder.
T_STATIC = "static"
T_LOCAL = "local"
T_FORK = "fork"
T_MANUAL = "manual"


@dataclass
class Invariant:
    id: str = ""
    family: str = ""          # template id
    title: str = ""
    description: str = ""
    related_entities: list = field(default_factory=list)
    related_functions: list = field(default_factory=list)
    state_transition: str = ""
    assertion_form: str = ""
    attacker_capability: str = ""
    victim: str = ""
    asset: str = ""
    why_it_matters: str = ""
    testability: str = T_LOCAL
    severity_hint: str = ""
    suspicious: bool = False
    suspicion_reasons: list = field(default_factory=list)
    confidence: str = MEDIUM
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class InvariantSet:
    root: str = ""
    invariants: list = field(default_factory=list)

    def suspicious(self):
        return [i for i in self.invariants if i.suspicious]

    def families(self):
        return {i.family for i in self.invariants}

    def to_dict(self) -> dict:
        return {
            "schema_version": "v10-invariants",
            "root": self.root,
            "invariant_count": len(self.invariants),
            "suspicious_count": len(self.suspicious()),
            "invariants": [i.to_dict() for i in self.invariants],
        }
