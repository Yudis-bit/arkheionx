"""Numeric severity scoring + impact / cap / proof typing.

Turns a candidate plus its decision-tree label into an explainable
:class:`~arkheionx.severity.models.SeverityScore`, so a reviewer can see *why* a
label landed where it did (e.g. "High impact, but rounding-unit capped and only a
local skeleton, so Low"). The label is still decided by the decision tree in
``classifier``; the score corroborates and explains it. Conservative: caps and weak
proof pull the score down.
"""
from __future__ import annotations

from . import models as S

# family -> (impact_type, base impact score 0-10)
_IMPACT = {
    "SIGNATURE_OPERATION_BINDING": (S.DIRECT_THEFT, 9),
    "THRESHOLD_AUTHORIZATION_BYPASS": (S.DIRECT_THEFT, 10),
    "NONCE_SEQUENCE_REPLAY": (S.DIRECT_THEFT, 8),
    "DELEGATECALL_STORAGE_CONTROL": (S.DIRECT_THEFT, 10),
    "FACTORY_INITIALIZATION_TAKEOVER": (S.DIRECT_THEFT, 9),
    "KEY_REUSE_REPLAY": (S.NO_VALUE_IMPACT, 2),
    "DEBT_REPAYMENT_RECONCILIATION": (S.VICTIM_LOSS, 5),
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": (S.VICTIM_LOSS, 6),
    "BORROW_CONSERVATION": (S.PROTOCOL_INSOLVENCY, 8),
    "DEPOSIT_CONSUMPTION": (S.DIRECT_THEFT, 9),
    "VAULT_SHARE_ASSET_RECONCILIATION": (S.VICTIM_LOSS, 7),
    "COLLATERAL_STATUS_RELEASE": (S.COLLATERAL_RELEASE, 8),
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": (S.ACCOUNTING_OVER_CREDIT, 6),
    "ORACLE_DECIMAL_NORMALIZATION": (S.ORACLE_OVERBORROW, 8),
    "CROSS_CHAIN_SUPPLY_CONSERVATION": (S.CROSS_CHAIN_OVERMINT, 9),
    "ACCESS_CONTROLLED_VALUE_MOVEMENT": (S.NO_VALUE_IMPACT, 0),
}

# family -> (cap_type, cap penalty 0-10)
_CAP = {
    "SIGNATURE_OPERATION_BINDING": (S.POSITION_CAPPED, 2),
    "THRESHOLD_AUTHORIZATION_BYPASS": (S.TVL_CAPPED, 1),
    "NONCE_SEQUENCE_REPLAY": (S.POSITION_CAPPED, 2),
    "DELEGATECALL_STORAGE_CONTROL": (S.TVL_CAPPED, 1),
    "FACTORY_INITIALIZATION_TAKEOVER": (S.POSITION_CAPPED, 2),
    "KEY_REUSE_REPLAY": (S.CONFIG_CAPPED, 8),
    "DEBT_REPAYMENT_RECONCILIATION": (S.ROUNDING_UNIT_CAPPED, 8),
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": (S.DEPOSIT_BUFFER_CAPPED, 5),
    "BORROW_CONSERVATION": (S.UNCAPPED, 1),
    "DEPOSIT_CONSUMPTION": (S.UNCAPPED, 1),
    "VAULT_SHARE_ASSET_RECONCILIATION": (S.POSITION_CAPPED, 3),
    "COLLATERAL_STATUS_RELEASE": (S.POSITION_CAPPED, 3),
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": (S.POOL_CAPPED, 4),
    "ORACLE_DECIMAL_NORMALIZATION": (S.POSITION_CAPPED, 2),
    "CROSS_CHAIN_SUPPLY_CONSERVATION": (S.UNCAPPED, 0),
    "ACCESS_CONTROLLED_VALUE_MOVEMENT": (S.USER_CONSENT_CAPPED, 9),
}

_PROOF_SCORE = {
    S.STATIC_ONLY: 2, S.LOCAL_POC_SKELETON: 4, S.LOCAL_POC_PASSING: 8,
    S.FORK_PLAN_ONLY: 3, S.FORK_POC_PASSING: 9, S.REAL_ASSET_VALIDATED: 10,
    S.MANUAL_REVIEW_REQUIRED: 1,
}

_REPEAT = {
    "SIGNATURE_OPERATION_BINDING": 8,
    "THRESHOLD_AUTHORIZATION_BYPASS": 9,
    "NONCE_SEQUENCE_REPLAY": 9,
    "DELEGATECALL_STORAGE_CONTROL": 9,
    "FACTORY_INITIALIZATION_TAKEOVER": 7,
    "KEY_REUSE_REPLAY": 2,
    "DEPOSIT_CONSUMPTION": 9, "CROSS_CHAIN_SUPPLY_CONSERVATION": 9,
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": 8, "ORACLE_DECIMAL_NORMALIZATION": 7,
    "DEBT_REPAYMENT_RECONCILIATION": 6, "BORROW_CONSERVATION": 6,
    "VAULT_SHARE_ASSET_RECONCILIATION": 5, "COLLATERAL_STATUS_RELEASE": 5,
}


def impact_type(family):
    return _IMPACT.get(family, (S.NO_VALUE_IMPACT, 0))


def cap_type(family):
    return _CAP.get(family, (S.CAP_UNKNOWN, 3))


def proof_quality(candidate):
    """Current evidence strength. Skeletons are not passing PoCs; we never claim
    LOCAL_POC_PASSING / FORK_POC_PASSING from static analysis alone."""
    if candidate.role_gated:
        return S.MANUAL_REVIEW_REQUIRED
    if candidate.fork_requirement or candidate.proof_strategy == "fork":
        return S.FORK_PLAN_ONLY
    if candidate.proof_strategy == "manual":
        return S.MANUAL_REVIEW_REQUIRED
    return S.LOCAL_POC_SKELETON


def _likelihood_score(candidate):
    if candidate.role_gated:
        return 1
    if candidate.fork_requirement:
        return 5
    return 8 if candidate.proof_strategy == "local" else 6


def _realism_score(candidate, cap_penalty):
    base = 1 if candidate.role_gated else (5 if candidate.fork_requirement else 8)
    return max(0, base - cap_penalty // 3)


def _scope_risk(candidate):
    sr = (candidate.scope_risk or "").upper()
    if sr == "OUT_OF_SCOPE":
        return 10
    if "AMBIGUOUS" in sr:
        return 5
    return 0


def _dup_risk(candidate):
    dr = (candidate.duplicate_risk or "").upper()
    if dr == "SAME_ROOT_CAUSE":
        return 10
    if dr == "RELATED_BUT_DISTINCT":
        return 4
    return 0


def build_score(candidate, label) -> S.SeverityScore:
    family = candidate.invariant_family
    itype, iscore = impact_type(family)
    ctype, cpen = cap_type(family)
    pq = proof_quality(candidate)
    pscore = _PROOF_SCORE.get(pq, 2)
    like = _likelihood_score(candidate)
    real = _realism_score(candidate, cpen)
    rep = _REPEAT.get(family, 5)
    scope = _scope_risk(candidate)
    dup = _dup_risk(candidate)

    bits = [f"impact {itype}({iscore})", f"cap {ctype}(-{cpen})",
            f"proof {pq}({pscore})", f"likelihood {like}", f"repeatability {rep}"]
    if scope:
        bits.append(f"scope_risk {scope}")
    if dup:
        bits.append(f"duplicate_risk {dup}")
    explanation = label + " <= " + ", ".join(bits)

    return S.SeverityScore(
        impact_score=iscore, likelihood_score=like, realism_score=real,
        proof_score=pscore, repeatability_score=rep, cap_penalty=cpen,
        scope_risk=scope, duplicate_risk=dup, final_label=label,
        explanation=explanation,
    )
