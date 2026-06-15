"""Models for separating code validity from bounty relevance."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field


class BountyRealityVerdict:
    SUBMITTABLE = "SUBMITTABLE"
    NEEDS_MORE_PROOF = "NEEDS_MORE_PROOF"
    VALID_CODE_BUG_BUT_NOT_BOUNTY_WORTHY = "VALID_CODE_BUG_BUT_NOT_BOUNTY_WORTHY"
    DO_NOT_SUBMIT_AS_MEDIUM = "DO_NOT_SUBMIT_AS_MEDIUM"
    DO_NOT_SUBMIT_DUPLICATE = "DO_NOT_SUBMIT_DUPLICATE"
    DO_NOT_SUBMIT_PREVIOUSLY_REJECTED = "DO_NOT_SUBMIT_PREVIOUSLY_REJECTED"
    DO_NOT_SUBMIT_DUST = "DO_NOT_SUBMIT_DUST"
    DO_NOT_SUBMIT_PRECISION_ONLY = "DO_NOT_SUBMIT_PRECISION_ONLY"
    DO_NOT_SUBMIT_NO_PROFIT = "DO_NOT_SUBMIT_NO_PROFIT"
    DO_NOT_SUBMIT_VICTIM_OPT_IN = "DO_NOT_SUBMIT_VICTIM_OPT_IN"
    DO_NOT_SUBMIT_TRUSTED_ROLE = "DO_NOT_SUBMIT_TRUSTED_ROLE"
    DO_NOT_SUBMIT_OFFCHAIN_VALIDATION = "DO_NOT_SUBMIT_OFFCHAIN_VALIDATION"
    DO_NOT_SUBMIT_KEY_REUSE = "DO_NOT_SUBMIT_KEY_REUSE"
    DO_NOT_SUBMIT_FORCED_VALUE_TRANSFER_ONLY = "DO_NOT_SUBMIT_FORCED_VALUE_TRANSFER_ONLY"
    DO_NOT_SUBMIT_GAS_ONLY = "DO_NOT_SUBMIT_GAS_ONLY"
    DO_NOT_SUBMIT_PROGRAM_CARVEOUT = "DO_NOT_SUBMIT_PROGRAM_CARVEOUT"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"


@dataclass
class BountyRealityInput:
    attack_candidate: object | None = None
    severity_result: object | None = None
    memory_match: object | None = None
    scope_policy: object | None = None
    proof_quality: str = ""
    cap_type: str = ""
    attacker_profit: bool | None = None
    victim_loss: bool | None = None
    victim_opt_in: bool | None = None
    duplicate_status: str = ""
    program_history: list = field(default_factory=list)
    reviewer_outcome_memory: list = field(default_factory=list)
    carveout_tags: list = field(default_factory=list)
    family: str = ""
    asset_decimals: int = 0
    official_buffer_small: bool | None = None
    capture_proven: bool | None = None
    safe_mode_exists: bool | None = None
    requires_key_reuse: bool | None = None
    no_contract_logic_flaw: bool | None = None
    unprivileged: bool | None = None
    not_duplicate: bool | None = None
    not_oos: bool | None = None
    malicious_asset_required: bool | None = None
    low_decimal_asset_required: bool | None = None
    cap_tiny: bool | None = None
    gas_only: bool | None = None
    style_only: bool | None = None
    low_impact_grief_only: bool | None = None


@dataclass
class BountyRealityResult:
    candidate_id: str = ""
    family: str = ""
    verdict: str = BountyRealityVerdict.HUMAN_REVIEW_REQUIRED
    final_verdict: str = BountyRealityVerdict.HUMAN_REVIEW_REQUIRED
    secondary_verdicts: list = field(default_factory=list)
    reason_tags: list = field(default_factory=list)
    reviewer_risk: str = "MEDIUM"
    submit_recommendation: str = "HUMAN_REVIEW"
    blocked: bool = False
    explanation: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
