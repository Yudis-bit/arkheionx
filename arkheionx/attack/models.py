"""Attack candidate models (Layer 5).

An :class:`AttackCandidate` turns a suspicious invariant (or a role-gated value
path) into a concrete, rankable hypothesis: attacker, victim, asset, entry point,
call sequence, broken invariant, proof strategy, and fork need. Severity and
dedup verdicts are filled by later layers. A candidate is a research direction,
never a confirmed exploit.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

LOW, MEDIUM, HIGH = "LOW", "MEDIUM", "HIGH"

# Source of the candidate.
SRC_INVARIANT = "suspicious_invariant"
SRC_ROLE_VALUE = "role_gated_value_path"


@dataclass
class AttackCandidate:
    id: str = ""
    title: str = ""
    root_cause: str = ""
    broken_invariant: str = ""
    invariant_id: str = ""
    invariant_family: str = ""
    attacker: str = ""
    attacker_capability: str = ""
    victim: str = ""
    asset: str = ""
    entry_function: str = ""
    call_sequence: list = field(default_factory=list)
    state_transition: str = ""
    exploit_hypothesis: str = ""
    required_conditions: list = field(default_factory=list)
    evidence: list = field(default_factory=list)            # file:line / signals
    proof_strategy: str = "local"                            # local | fork | manual
    fork_requirement: bool = False
    role_gated: bool = False
    role_gates: list = field(default_factory=list)
    # Filled by later layers:
    economic_severity: str = ""
    severity_hint: str = ""        # pre-gate hint from the invariant
    severity_detail: dict = field(default_factory=dict)
    duplicate_risk: str = "UNKNOWN"
    scope_risk: str = "UNKNOWN"
    root_cause_hash: str = ""
    recommendation: str = "NEEDS_POC"
    poc_skeleton: str = ""
    rank_score: float = 0.0
    rank_reasons: list = field(default_factory=list)
    confidence: str = MEDIUM

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class AttackGraph:
    root: str = ""
    candidates: list = field(default_factory=list)

    def top(self, n):
        return self.candidates[:n]

    def to_dict(self) -> dict:
        return {
            "schema_version": "v10-attack-graph",
            "root": self.root,
            "candidate_count": len(self.candidates),
            "candidates": [c.to_dict() for c in self.candidates],
        }
