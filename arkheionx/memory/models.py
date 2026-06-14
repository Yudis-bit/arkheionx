"""Root-cause memory models (Layer 9)."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

# Statuses.
SUBMITTED = "submitted"
KILLED = "killed"
PARKED = "parked"
ACCEPTED = "accepted"
REJECTED = "rejected"
DUPLICATE = "duplicate"
UNKNOWN = "unknown"

STATUSES = (SUBMITTED, ACCEPTED, REJECTED, DUPLICATE, KILLED, PARKED, UNKNOWN)

# Duplicate classifications.
SAME_ROOT_CAUSE = "SAME_ROOT_CAUSE"
RELATED_BUT_DISTINCT = "RELATED_BUT_DISTINCT"
DISTINCT = "DISTINCT"
DUP_UNKNOWN = "UNKNOWN"


@dataclass
class MemoryEntry:
    target: str = ""
    program: str = ""
    repo: str = ""
    commit: str = ""
    root_cause: str = ""
    root_cause_hash: str = ""
    invariant_family: str = ""
    function_role: str = ""
    attacker_category: str = ""
    affected_contracts: list = field(default_factory=list)
    status: str = UNKNOWN
    finding_id: str = ""
    severity: str = ""
    reason: str = ""
    do_not_resubmit: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict):
        fields = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in fields})
