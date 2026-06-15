"""Models for authorization-heavy Solidity analysis."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field as dc_field

BOUND = "BOUND"
UNBOUND_CRITICAL = "UNBOUND_CRITICAL"
UNBOUND_VALUE_FIELD = "UNBOUND_VALUE_FIELD"
UNBOUND_CONTROL_FIELD = "UNBOUND_CONTROL_FIELD"
UNBOUND_BUT_NON_VALUE = "UNBOUND_BUT_NON_VALUE"
OUT_OF_SCOPE_POLICY = "OUT_OF_SCOPE_POLICY"
TRUSTED_ONLY = "TRUSTED_ONLY"
UNKNOWN = "UNKNOWN"

MATRIX_FIELDS = (
    "destination",
    "value",
    "calldata",
    "operation_type",
    "nonce_or_sequence",
    "chain_id",
    "wallet_address",
    "expiry",
    "gas_payment",
    "refund_receiver",
    "token",
    "asset",
    "batch_contents",
    "signer_set",
    "threshold",
    "receiver",
    "implementation",
    "init_data",
)


@dataclass
class HashBindingField:
    field: str = ""
    executed: bool = False
    signed: bool = False
    affects_value: bool = False
    affects_control: bool = False
    bound_elsewhere: bool = False
    verdict: str = UNKNOWN
    evidence: list = dc_field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class HashBindingMatrix:
    fields: dict = dc_field(default_factory=dict)

    def field(self, name: str) -> HashBindingField:
        return self.fields[name]

    def to_dict(self) -> dict:
        return {name: value.to_dict() for name, value in self.fields.items()}


@dataclass
class SignedOperation:
    contract: str = ""
    function: str = ""
    hash_expression: str = ""
    hash_inputs: list = dc_field(default_factory=list)
    execution_inputs: list = dc_field(default_factory=list)
    signer_source: str = ""
    threshold_source: str = ""
    nonce_source: str = ""
    chain_binding: bool = False
    wallet_binding: bool = False
    value_fields_bound: list = dc_field(default_factory=list)
    value_fields_unbound: list = dc_field(default_factory=list)
    control_fields_bound: list = dc_field(default_factory=list)
    control_fields_unbound: list = dc_field(default_factory=list)
    replay_protection: str = ""
    evidence: list = dc_field(default_factory=list)
    confidence: str = "MEDIUM"
    binding_matrix: HashBindingMatrix = dc_field(default_factory=HashBindingMatrix)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class ThresholdAnalysis:
    contract: str = ""
    function: str = ""
    required_threshold: str = ""
    signer_membership_check: bool = False
    duplicate_signer_check: bool = False
    sorted_order_check: bool = False
    zero_address_rejection: bool = False
    ecrecover_failure_handling: bool = False
    low_s_check: bool = False
    v_normalization: bool = False
    malleability_impact: str = ""
    unique_signer_count: str = ""
    verdict: str = UNKNOWN
    evidence: list = dc_field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class ReplayAnalysis:
    contract: str = ""
    function: str = ""
    nonce_present: bool = False
    sequence_present: bool = False
    consumed_before_external_call: bool = False
    chain_id_bound: bool = False
    wallet_address_bound: bool = False
    expiry_bound: bool = False
    replay_same_wallet: bool = False
    replay_cross_wallet: bool = False
    replay_cross_chain: bool = False
    requires_key_reuse: bool = False
    program_policy_carveout: bool = False
    verdict: str = UNKNOWN
    evidence: list = dc_field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class DelegatecallAnalysis:
    contract: str = ""
    function: str = ""
    delegatecall_present: bool = False
    operation_type_bound: bool = False
    target_bound: bool = False
    calldata_bound: bool = False
    storage_control_risk: bool = False
    threshold_required: bool = False
    verdict: str = UNKNOWN
    evidence: list = dc_field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class FactoryInitAnalysis:
    contract: str = ""
    function: str = ""
    initializer_callable: bool = False
    initializer_guard: bool = False
    create2_salt_fields: list = dc_field(default_factory=list)
    signer_or_owner_bound_in_salt: bool = False
    parent_or_controller_bound_in_salt: bool = False
    atomic_init: bool = False
    proxy_implementation: str = ""
    takeover_risk: bool = False
    verdict: str = UNKNOWN
    evidence: list = dc_field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class AuthCandidate:
    family: str = ""
    contract: str = ""
    function: str = ""
    title: str = ""
    severity_hint: str = ""
    requires_key_reuse: bool = False
    proof_quality: str = "STATIC_ONLY"
    evidence: list = dc_field(default_factory=list)
    confidence: str = "MEDIUM"

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class AuthorizationAnalysis:
    active: bool = False
    activation_signals: list = dc_field(default_factory=list)
    signed_operations: list = dc_field(default_factory=list)
    threshold_analyses: list = dc_field(default_factory=list)
    replay_analyses: list = dc_field(default_factory=list)
    delegatecall_analyses: list = dc_field(default_factory=list)
    factory_init_analyses: list = dc_field(default_factory=list)
    candidates: list = dc_field(default_factory=list)
    warnings: list = dc_field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "schema_version": "v10.1-auth-signature-analysis",
            "artifact_type": "auth_signature_analysis",
            "active": self.active,
            "activation_signals_detected": bool(self.activation_signals),
            "signed_operations_detected": bool(self.signed_operations),
            "auth_candidates_detected": bool(self.candidates),
            "activation_signals": list(self.activation_signals),
            "signed_operations": [item.to_dict() for item in self.signed_operations],
            "threshold_analyses": [item.to_dict() for item in self.threshold_analyses],
            "replay_analyses": [item.to_dict() for item in self.replay_analyses],
            "delegatecall_analyses": [item.to_dict() for item in self.delegatecall_analyses],
            "factory_init_analyses": [item.to_dict() for item in self.factory_init_analyses],
            "candidates": [item.to_dict() for item in self.candidates],
            "warnings": list(self.warnings),
        }
