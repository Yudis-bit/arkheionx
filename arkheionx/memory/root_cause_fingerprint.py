"""Semantic root-cause classification and deterministic fingerprinting."""
from __future__ import annotations

import dataclasses
import hashlib
import re
from dataclasses import dataclass, field

from . import families as F
from .normalizer import normalize_field, normalize_text

ROUNDING_UNIT_CAPPED = "ROUNDING_UNIT_CAPPED"
DEPOSIT_BUFFER_CAPPED = "DEPOSIT_BUFFER_CAPPED"
KEY_REUSE_OR_DOMAIN_CAPPED = "KEY_REUSE_OR_DOMAIN_CAPPED"
CAP_UNKNOWN = "UNKNOWN"


@dataclass
class RootCauseFingerprint:
    raw_text: str = ""
    normalized_text: str = ""
    family: str = F.UNKNOWN
    subfamily: str = "unknown"
    lifecycle: str = "unknown"
    affected_function: str = "unknown"
    affected_asset_type: str = "unknown"
    attacker_capability: str = "unknown"
    victim_type: str = "unknown"
    impact_path: str = "unknown"
    cap_type: str = CAP_UNKNOWN
    proof_status: str = "unknown"
    program_outcome: str = "unknown"
    fingerprint_hash: str = ""
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _contains(text: str, *patterns: str) -> bool:
    return all(re.search(pattern, text) for pattern in patterns)


def _classify(text: str, explicit_family: str = "") -> tuple[str, str, str, str, str, float]:
    explicit = F.canonical(explicit_family)
    if explicit != F.UNKNOWN:
        return explicit, "explicit_family", _lifecycle(text), "unknown", CAP_UNKNOWN, 0.98

    if _contains(text, r"\brepay", r"round") and re.search(r"tranche|lender|distribution|aggregate|loan", text):
        if re.search(r"close|closed|zero", text):
            sub = "debt_closes_before_lender_distribution_reconciles"
        elif re.search(r"round up|rounding up", text) and re.search(r"round down|rounding down", text):
            sub = "aggregate_round_up_per_tranche_round_down"
        else:
            sub = "aggregate_repayment_per_tranche_distribution_mismatch"
        return F.ROUNDING_REPAYMENT_RECONCILIATION, sub, "repay", \
            "lender_repayment_shortfall", ROUNDING_UNIT_CAPPED, 0.96

    if re.search(r"share", text) and re.search(r"asset|vault", text) and re.search(r"round|reconcil|inflation", text):
        return F.ROUNDING_SHARE_ASSET_RECONCILIATION, "share_asset_rounding_mismatch", \
            _lifecycle(text), "share_asset_accounting", ROUNDING_UNIT_CAPPED, 0.91

    if re.search(r"refund|buffer|predeposit|deposit buffer", text) and \
            re.search(r"route|swap data|cross-token|borrower.controlled|counterparty.controlled", text):
        return F.LENDER_CONSENT_VALUE_FIELD_BINDING, \
            "counterparty_controlled_route_affects_refund", "borrow_or_origination", \
            "lender_refund_buffer", DEPOSIT_BUFFER_CAPPED, 0.96

    if re.search(r"operation hash|transaction hash|signed hash|signature", text) and \
            re.search(r"chain id|wallet address|domain|cross.chain|cross.wallet", text) and \
            re.search(r"omit|missing|not bound|without", text):
        return F.SIGNATURE_REPLAY_DOMAIN, "domain_not_bound", "execute", \
            "signed_operation_replay", KEY_REUSE_OR_DOMAIN_CAPPED, 0.97

    if re.search(r"key reuse|same key|same signer", text) and re.search(r"replay", text):
        return F.KEY_REUSE_REPLAY, "replay_requires_reused_signing_authority", "execute", \
            "signed_operation_replay", KEY_REUSE_OR_DOMAIN_CAPPED, 0.94

    if re.search(r"duplicate signer|same signature|threshold", text) and \
            re.search(r"bypass|counted twice|duplicate", text):
        return F.THRESHOLD_AUTHORIZATION_BYPASS, "duplicate_signer_counted_toward_threshold", \
            "execute", "unauthorized_execution", "UNCAPPED", 0.95

    if re.search(r"nonce|sequence", text) and re.search(r"replay|not consumed|reuse", text):
        return F.NONCE_SEQUENCE_REPLAY, "nonce_or_sequence_not_consumed", "execute", \
            "signed_operation_replay", "POSITION_CAPPED", 0.93

    if re.search(r"delegatecall", text) and re.search(r"unbound|storage|operation type|target", text):
        return F.DELEGATECALL_STORAGE_CONTROL, "delegatecall_control_field_not_bound", \
            "execute", "wallet_storage_control", "TVL_CAPPED", 0.94

    if re.search(r"hash|signature|signed", text) and re.search(r"omit|missing|unbound|not bound", text):
        return F.SIGNATURE_OPERATION_BINDING, "executed_field_not_signed", "execute", \
            "unauthorized_signed_operation_mutation", "POSITION_CAPPED", 0.88

    if re.search(r"forced value|force value|forced ether|selfdestruct", text) and \
            re.search(r"no logic flaw|without logic|balance", text):
        return F.FORCED_VALUE_TRANSFER_NO_LOGIC_FLAW, "forced_balance_without_logic_dependency", \
            "receive", "balance_only", "NO_LOGIC_IMPACT", 0.98

    if re.search(r"trusted signer|trusted role|admin|owner", text) and \
            re.search(r"grief|emergency|malicious|assumption", text):
        return F.TRUSTED_ROLE_ASSUMPTION, "trusted_actor_behavior", _lifecycle(text), \
            "trusted_role_action", "TRUSTED_ROLE_CAPPED", 0.94

    if re.search(r"zero address|validation missing|missing validation|off.chain", text) and \
            re.search(r"signer|owner|input|configuration|validation", text):
        return F.OFFCHAIN_VALIDATION_OMISSION, "deployment_or_input_validation_omitted", \
            _lifecycle(text), "configuration_validation", "POLICY_CAPPED", 0.91

    rules = (
        (F.ACTUAL_RECEIVED_VS_CREDITED, r"actual received|fee.on.transfer", r"credit"),
        (F.ORACLE_DECIMAL_NORMALIZATION, r"oracle|price feed", r"decimal|scale"),
        (F.ORACLE_STALENESS_VALIDATION, r"oracle|price feed", r"stale|freshness"),
        (F.CROSS_CHAIN_SUPPLY_CONSERVATION, r"cross.chain|bridge", r"supply|mint|burn"),
        (F.DEPOSIT_CONTEXT_COMPLETENESS, r"deposit", r"context|recipient|asset"),
        (F.DEPOSIT_DOUBLE_CONSUMPTION, r"deposit", r"double|twice|replay|consume"),
        (F.COLLATERAL_STATUS_RELEASE, r"collateral", r"release|status|settle"),
        (F.BORROW_CONSERVATION, r"borrow", r"conservation|accounting|debt"),
        (F.VAULT_SHARE_INFLATION, r"vault|share", r"inflat|donation|first depositor"),
        (F.RECEIVER_AUTHORIZATION, r"receiver|recipient", r"authoriz|signed|consent"),
        (F.FACTORY_INITIALIZATION_TAKEOVER, r"factory|proxy|create2", r"initializ|takeover|owner"),
        (F.GAS_ONLY, r"gas", r"only|cost|optimization"),
        (F.PRECISION_DUST_ONLY, r"precision|rounding|dust", r"dust|tiny|base unit"),
        (F.NO_ATTACKER_PROFIT, r"no attacker profit|attacker cannot profit", r"profit"),
        (F.VICTIM_OPT_IN_TERMS, r"victim opt.in|signed terms|consent", r"terms|consent|opt"),
    )
    for family, left, right in rules:
        if re.search(left, text) and re.search(right, text):
            return family, normalize_field(family), _lifecycle(text), \
                normalize_field(family), CAP_UNKNOWN, 0.82
    return F.UNKNOWN, "unknown", _lifecycle(text), "unknown", CAP_UNKNOWN, 0.25


def _lifecycle(text: str) -> str:
    for pattern, lifecycle in (
        (r"repay|settle", "repay"),
        (r"borrow|originat", "borrow_or_origination"),
        (r"deposit|mint", "deposit"),
        (r"withdraw|redeem", "withdraw"),
        (r"execute|operation|transaction|signature|signer", "execute"),
        (r"initializ|factory|create2", "initialize"),
        (r"bridge|cross.chain", "cross_chain"),
    ):
        if re.search(pattern, text):
            return lifecycle
    return "unknown"


def fingerprint_hash(fp: RootCauseFingerprint) -> str:
    fields = (
        fp.family,
        fp.subfamily,
        fp.lifecycle,
        fp.affected_function,
        fp.impact_path,
        fp.cap_type,
        fp.attacker_capability,
        fp.victim_type,
    )
    seed = "|".join(normalize_field(v) for v in fields)
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def build_fingerprint(
    raw_text: str,
    *,
    explicit_family: str = "",
    affected_function: str = "",
    affected_asset_type: str = "",
    attacker_capability: str = "",
    victim_type: str = "",
    impact_path: str = "",
    cap_type: str = "",
    proof_status: str = "",
    program_outcome: str = "",
) -> RootCauseFingerprint:
    normalized = normalize_text(raw_text)
    family, subfamily, lifecycle, inferred_impact, inferred_cap, confidence = \
        _classify(normalized, explicit_family)
    warnings: list[str] = []
    if family == F.UNKNOWN or confidence < 0.5:
        warnings.append("low confidence")
    fp = RootCauseFingerprint(
        raw_text=raw_text or "",
        normalized_text=normalized,
        family=family,
        subfamily=subfamily,
        lifecycle=lifecycle,
        affected_function=normalize_field(affected_function),
        affected_asset_type=normalize_field(affected_asset_type),
        attacker_capability=normalize_field(attacker_capability),
        victim_type=normalize_field(victim_type),
        impact_path=normalize_field(impact_path or inferred_impact),
        cap_type=cap_type or inferred_cap,
        proof_status=normalize_field(proof_status),
        program_outcome=normalize_field(program_outcome),
        confidence=confidence,
        warnings=warnings,
    )
    fp.fingerprint_hash = fingerprint_hash(fp)
    return fp
