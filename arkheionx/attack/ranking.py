"""Candidate ranking (Layer 5).

Ranks candidates by realistic research value. Uses the economic-severity verdict
when present (post-gate); otherwise a family base plus pre-gate adjustments
(fork dependency, role-gating, dust/rounding caps, duplicate/scope risk).
"""
from __future__ import annotations

_FAMILY_BASE = {
    "THRESHOLD_AUTHORIZATION_BYPASS": 90,
    "SIGNATURE_OPERATION_BINDING": 88,
    "DELEGATECALL_STORAGE_CONTROL": 90,
    "FACTORY_INITIALIZATION_TAKEOVER": 85,
    "NONCE_SEQUENCE_REPLAY": 78,
    "KEY_REUSE_REPLAY": 20,
    "DEPOSIT_CONSUMPTION": 70,
    "VAULT_SHARE_ASSET_RECONCILIATION": 65,
    "CROSS_CHAIN_SUPPLY_CONSERVATION": 62,
    "COLLATERAL_STATUS_RELEASE": 60,
    "BORROW_CONSERVATION": 55,
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": 50,
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": 48,
    "ORACLE_DECIMAL_NORMALIZATION": 45,
    "DEBT_REPAYMENT_RECONCILIATION": 30,
    "ACCESS_CONTROLLED_VALUE_MOVEMENT": 5,
}

_SEV_SCORE = {
    "SUBMIT_CRITICAL_CANDIDATE": 100, "SUBMIT_HIGH_CANDIDATE": 95,
    "SUBMIT_MEDIUM_CANDIDATE": 80, "SUBMIT_LOW_ONLY": 45,
    "NEEDS_FORK_PROOF": 55, "NEEDS_REAL_ASSET_PROOF": 50,
    "VALID_BUT_LOW": 28, "VALID_BUT_LOW_LIKELIHOOD": 26,
    "PARK_CONTEXT": 20, "PARK_THEORY": 18, "PARK_REACHABILITY": 16,
    "KILL_DUST": 3, "KILL_SELF_GRIEF": 3, "KILL_TRUSTED_ROLE": 2,
    "KILL_OUT_OF_SCOPE": 1, "KILL_DUPLICATE_ROOT_CAUSE": 2,
}

_DUST_HINT = ("low", "dust", "rounding", "capped")


def _score(c) -> tuple:
    reasons = []
    if c.economic_severity and c.economic_severity in _SEV_SCORE:
        score = float(_SEV_SCORE[c.economic_severity])
        reasons.append(f"economic gate: {c.economic_severity}")
    else:
        score = float(_FAMILY_BASE.get(c.invariant_family, 35))
        if c.role_gated:
            score = min(score, 5.0)
            reasons.append("role-gated: unprivileged reachability absent (kill candidate)")
        if c.fork_requirement:
            score -= 10.0
            reasons.append("fork dependency lowers local certainty")
        hint = (c.severity_hint or "").lower()
        if any(w in hint for w in _DUST_HINT):
            score -= 15.0
            reasons.append("severity hint indicates rounding/dust/low cap")
        if c.confidence == "LOW":
            score -= 5.0
    if c.duplicate_risk == "SAME_ROOT_CAUSE":
        score -= 25.0
        reasons.append("likely duplicate of a known root cause")
    if c.scope_risk == "OUT_OF_SCOPE":
        score -= 30.0
        reasons.append("out-of-scope risk")
    return max(0.0, score), reasons


def rank(graph):
    for c in graph.candidates:
        c.rank_score, c.rank_reasons = _score(c)
    graph.candidates.sort(key=lambda c: (-c.rank_score, c.invariant_family, c.id))
    return graph
