"""Economic severity models (Layer 7).

The gate decides whether a technically valid candidate is bounty-worth, and never
overclaims. Labels are deliberately conservative: dust, trusted-role, and
unproven-buffer candidates are capped or killed, not promoted.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

# Severity labels.
SUBMIT_CRITICAL_CANDIDATE = "SUBMIT_CRITICAL_CANDIDATE"
SUBMIT_HIGH_CANDIDATE = "SUBMIT_HIGH_CANDIDATE"
SUBMIT_MEDIUM_CANDIDATE = "SUBMIT_MEDIUM_CANDIDATE"
SUBMIT_LOW_ONLY = "SUBMIT_LOW_ONLY"
VALID_BUT_LOW = "VALID_BUT_LOW"
VALID_BUT_LOW_LIKELIHOOD = "VALID_BUT_LOW_LIKELIHOOD"
NEEDS_LOCAL_POC = "NEEDS_LOCAL_POC"
NEEDS_FORK_PROOF = "NEEDS_FORK_PROOF"
NEEDS_REAL_ASSET_PROOF = "NEEDS_REAL_ASSET_PROOF"
NEEDS_CAPTURE_PROOF = "NEEDS_CAPTURE_PROOF"
PARK_CONTEXT = "PARK_CONTEXT"
PARK_THEORY = "PARK_THEORY"
PARK_REACHABILITY = "PARK_REACHABILITY"
PARK_INCOMPLETE = "PARK_INCOMPLETE"
KILL_DUST = "KILL_DUST"
KILL_SELF_GRIEF = "KILL_SELF_GRIEF"
KILL_TRUSTED_ROLE = "KILL_TRUSTED_ROLE"
KILL_ADMIN_ONLY = "KILL_ADMIN_ONLY"
KILL_OUT_OF_SCOPE = "KILL_OUT_OF_SCOPE"
KILL_DUPLICATE_ROOT_CAUSE = "KILL_DUPLICATE_ROOT_CAUSE"
KILL_NOT_REACHABLE = "KILL_NOT_REACHABLE"
KILL_EXPECTED_DESIGN = "KILL_EXPECTED_DESIGN"

KILL_LABELS = (KILL_DUST, KILL_SELF_GRIEF, KILL_TRUSTED_ROLE, KILL_ADMIN_ONLY,
               KILL_OUT_OF_SCOPE, KILL_DUPLICATE_ROOT_CAUSE, KILL_NOT_REACHABLE,
               KILL_EXPECTED_DESIGN)
SUBMIT_LABELS = (SUBMIT_CRITICAL_CANDIDATE, SUBMIT_HIGH_CANDIDATE,
                 SUBMIT_MEDIUM_CANDIDATE, SUBMIT_LOW_ONLY)
PARK_LABELS = (PARK_CONTEXT, PARK_THEORY, PARK_REACHABILITY, PARK_INCOMPLETE)
NEEDS_PROOF_LABELS = (NEEDS_LOCAL_POC, NEEDS_FORK_PROOF, NEEDS_REAL_ASSET_PROOF,
                      NEEDS_CAPTURE_PROOF)

# Impact taxonomy (what kind of harm, if the invariant truly breaks).
DIRECT_THEFT = "DIRECT_THEFT"
VICTIM_LOSS = "VICTIM_LOSS"
PROTOCOL_INSOLVENCY = "PROTOCOL_INSOLVENCY"
PERMANENT_STUCK_FUNDS = "PERMANENT_STUCK_FUNDS"
TEMPORARY_STUCK_FUNDS = "TEMPORARY_STUCK_FUNDS"
ACCOUNTING_OVER_CREDIT = "ACCOUNTING_OVER_CREDIT"
COLLATERAL_RELEASE = "COLLATERAL_RELEASE"
GOVERNANCE_TAKEOVER = "GOVERNANCE_TAKEOVER"
CROSS_CHAIN_OVERMINT = "CROSS_CHAIN_OVERMINT"
ORACLE_OVERBORROW = "ORACLE_OVERBORROW"
GRIEF_ONLY = "GRIEF_ONLY"
DUST_ONLY = "DUST_ONLY"
NO_VALUE_IMPACT = "NO_VALUE_IMPACT"

# Cap taxonomy (what bounds the loss).
UNCAPPED = "UNCAPPED"
TVL_CAPPED = "TVL_CAPPED"
POSITION_CAPPED = "POSITION_CAPPED"
POOL_CAPPED = "POOL_CAPPED"
DEPOSIT_BUFFER_CAPPED = "DEPOSIT_BUFFER_CAPPED"
ROUNDING_UNIT_CAPPED = "ROUNDING_UNIT_CAPPED"
GAS_CAPPED = "GAS_CAPPED"
USER_CONSENT_CAPPED = "USER_CONSENT_CAPPED"
CONFIG_CAPPED = "CONFIG_CAPPED"
CAP_UNKNOWN = "UNKNOWN"

# Proof-quality ladder (how strong is the evidence right now).
STATIC_ONLY = "STATIC_ONLY"
LOCAL_POC_SKELETON = "LOCAL_POC_SKELETON"
LOCAL_POC_PASSING = "LOCAL_POC_PASSING"
FORK_PLAN_ONLY = "FORK_PLAN_ONLY"
FORK_POC_PASSING = "FORK_POC_PASSING"
REAL_ASSET_VALIDATED = "REAL_ASSET_VALIDATED"
MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


@dataclass
class SeverityScore:
    """Numeric breakdown behind a label. All 0-10 (cap_penalty/scope/dup are penalties).

    This exists so a verdict is explainable ("why is this only Medium?") rather than a
    bare label. The label is still decided by the decision tree; the score corroborates
    and explains it.
    """

    impact_score: int = 0
    likelihood_score: int = 0
    realism_score: int = 0
    proof_score: int = 0
    repeatability_score: int = 0
    cap_penalty: int = 0
    scope_risk: int = 0
    duplicate_risk: int = 0
    final_label: str = ""
    explanation: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class SeverityVerdict:
    candidate_id: str = ""
    label: str = ""
    impact: str = ""
    impact_type: str = ""
    likelihood: str = ""
    cap: str = ""
    cap_type: str = ""
    proof_quality: str = ""
    repeatability: str = ""
    gas: str = ""
    realism: str = ""
    reasons: list = field(default_factory=list)
    score: dict = field(default_factory=dict)
    final_recommendation: str = ""
    confidence: str = "MEDIUM"

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
