"""Reviewer outcome memory used as evidence, not as an automatic truth source."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

ACCEPTED = "accepted"
REJECTED = "rejected"
DUPLICATE = "duplicate"
INFORMATIONAL = "informational"
LOW = "low"
PAID = "paid"
UNKNOWN = "unknown"

STATUSES = (ACCEPTED, REJECTED, DUPLICATE, INFORMATIONAL, LOW, PAID, UNKNOWN)

REASON_TAGS = (
    "duplicate",
    "dust",
    "no_profit",
    "victim_opt_in",
    "signed_terms",
    "precision_rounding",
    "out_of_scope",
    "key_reuse",
    "trusted_role",
    "offchain_validation",
    "forced_value_transfer",
    "no_significant_risk",
    "gas_only",
    "carveout",
    "missing_profit_path",
)


@dataclass
class ReviewerOutcome:
    status: str = UNKNOWN
    reason_tags: list = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
