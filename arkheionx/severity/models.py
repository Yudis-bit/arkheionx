"""Economic severity models (Layer 7).

The gate decides whether a technically valid candidate is bounty-worth, and never
overclaims. Labels are deliberately conservative: dust, trusted-role, and
unproven-buffer candidates are capped or killed, not promoted.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

# Severity labels.
SUBMIT_HIGH_CANDIDATE = "SUBMIT_HIGH_CANDIDATE"
SUBMIT_MEDIUM_CANDIDATE = "SUBMIT_MEDIUM_CANDIDATE"
SUBMIT_LOW_ONLY = "SUBMIT_LOW_ONLY"
VALID_BUT_LOW = "VALID_BUT_LOW"
VALID_BUT_LOW_LIKELIHOOD = "VALID_BUT_LOW_LIKELIHOOD"
NEEDS_FORK_PROOF = "NEEDS_FORK_PROOF"
NEEDS_REAL_ASSET_PROOF = "NEEDS_REAL_ASSET_PROOF"
PARK_CONTEXT = "PARK_CONTEXT"
PARK_THEORY = "PARK_THEORY"
PARK_REACHABILITY = "PARK_REACHABILITY"
KILL_DUST = "KILL_DUST"
KILL_SELF_GRIEF = "KILL_SELF_GRIEF"
KILL_TRUSTED_ROLE = "KILL_TRUSTED_ROLE"
KILL_OUT_OF_SCOPE = "KILL_OUT_OF_SCOPE"
KILL_DUPLICATE_ROOT_CAUSE = "KILL_DUPLICATE_ROOT_CAUSE"

KILL_LABELS = (KILL_DUST, KILL_SELF_GRIEF, KILL_TRUSTED_ROLE, KILL_OUT_OF_SCOPE,
               KILL_DUPLICATE_ROOT_CAUSE)
SUBMIT_LABELS = (SUBMIT_HIGH_CANDIDATE, SUBMIT_MEDIUM_CANDIDATE, SUBMIT_LOW_ONLY)


@dataclass
class SeverityVerdict:
    candidate_id: str = ""
    label: str = ""
    impact: str = ""
    likelihood: str = ""
    cap: str = ""
    repeatability: str = ""
    gas: str = ""
    realism: str = ""
    reasons: list = field(default_factory=list)
    final_recommendation: str = ""
    confidence: str = "MEDIUM"

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
