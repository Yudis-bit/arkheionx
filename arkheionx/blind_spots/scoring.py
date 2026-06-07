"""Transparent heuristic scoring for the v5 Blind Spot Intelligence layer.

Nothing here is hidden. Every surface accumulates four additive component
scores, and each contribution is reported with a human-readable reason:

    blind_spot_score = impact + review_gap + complexity + assumption

The score is a heuristic review priority. It is never a probability, never a
severity, and never an exploitability estimate.
"""
from __future__ import annotations

from . import models as m

# --- Impact (criticality potential) dimensions ---------------------------
# (point value, dimension label). Order is the reporting/priority order.
IMPACT_VALUE_EXIT = (25, "value exit")
IMPACT_ACCOUNTING = (20, "accounting mutation")
IMPACT_AUTHORIZATION = (20, "authorization control")
IMPACT_LIQUIDATION = (20, "liquidation/seizure")
IMPACT_ORACLE = (18, "oracle dependency")
IMPACT_EXTERNAL_CALL = (15, "external call/callback")
IMPACT_PERIPHERY = (15, "periphery/core boundary")
IMPACT_ADMIN = (12, "admin/emergency control")
IMPACT_CROSS_CONTRACT = (10, "cross-contract dependency")
IMPACT_TOKEN_MUTATION = (10, "token/share/debt/collateral mutation")

# --- Review-gap points by coverage signal --------------------------------
REVIEW_GAP_POINTS = {
    "no direct test observed": 30,
    "unknown": 20,
    "partially tested": 10,
    "tested": 0,
}

# --- Complexity points ----------------------------------------------------
COMPLEXITY_EXTERNAL_CALL = 10
COMPLEXITY_LOOP = 8
COMPLEXITY_TRY_CATCH = 8
COMPLEXITY_AUTH_LOGIC = 10  # Merkle / signature / domain
COMPLEXITY_CROSS_CONTRACT = 8
COMPLEXITY_PERIPHERY = 8

# --- Assumption points ----------------------------------------------------
ASSUMPTION_BASE = 10  # any unverified critical assumption
ASSUMPTION_MULTIPLE = 5  # bonus when two or more stack on one surface

_ADMIN_NAME_PREFIXES = ("set", "configure", "pause", "unpause", "upgrade",
                        "initialize", "init", "migrate", "kill", "shutdown",
                        "rescue", "sweep", "emergency")
_LIQUIDATION_NAMES = ("liquidate", "liquidation", "seize", "borrow", "health",
                      "collateral", "loantovalue", "ltv", "baddebt", "closefactor")
_ORACLE_NAMES = ("oracle", "price", "feed", "aggregator", "twap", "rate", "quote")
_TOKEN_MUTATION_NAMES = ("mint", "burn", "shares", "share", "collateral", "debt",
                         "credit", "supply", "redeem", "stake", "balance", "index")
_ACCOUNTING_NAMES = ("share", "debt", "credit", "collateral", "supply", "balance",
                     "index", "accumulator", "principal", "interest", "totalassets",
                     "totalsupply", "exchangerate", "reserve", "liquidity")


def _name(record: "m.SurfaceRecord") -> str:
    return (record.function or "").lower()


def _has(values, *needles) -> bool:
    blob = " ".join(values).lower()
    return any(n in blob for n in needles)


def compute_impact(record: "m.SurfaceRecord") -> tuple[int, list[dict], list[str]]:
    """Impact (criticality potential) score with per-dimension breakdown."""
    name = _name(record)
    risk = record.risk_signals
    dims: list[tuple[int, str]] = []

    def add(dim, reason):
        dims.append(dim)
        reasons.append(f"+{dim[0]} {dim[1]}: {reason}")

    reasons: list[str] = []

    if _has(risk, "value exit") or _has(risk, "value-out"):
        add(IMPACT_VALUE_EXIT, "value leaves the system on this path")
    if record.review_priority and (_has(risk, "accounting mutation")
                                   or _has(record.risk_signals, "accounting")
                                   or any(k in name for k in _ACCOUNTING_NAMES)):
        add(IMPACT_ACCOUNTING, "mutates protocol accounting state")
    if record.auth_kinds or _has(risk, "authorization") or _has(risk, "admin control"):
        add(IMPACT_AUTHORIZATION, "controls authorization that binds value movement")
    if _has(risk, "liquidation") or any(k in name for k in _LIQUIDATION_NAMES):
        add(IMPACT_LIQUIDATION, "touches liquidation / debt / collateral boundaries")
    if _has(risk, "oracle") or any(k in name for k in _ORACLE_NAMES):
        add(IMPACT_ORACLE, "depends on an external price / oracle value")
    if _has(risk, "external call") or _has(risk, "callback") or "low-level-call" in record.periphery_interactions:
        add(IMPACT_EXTERNAL_CALL, "performs an external call or callback")
    if record.periphery_interactions:
        add(IMPACT_PERIPHERY, "sits on a periphery-to-core boundary")
    if _has(risk, "admin") or any(name.startswith(p) for p in _ADMIN_NAME_PREFIXES):
        add(IMPACT_ADMIN, "admin / emergency / lifecycle control")
    if record.cross_contract_targets or "cross-contract-call" in record.periphery_interactions:
        add(IMPACT_CROSS_CONTRACT, "depends on another contract")
    if _has(risk, "value entry") or _has(risk, "value-in") or any(k in name for k in _TOKEN_MUTATION_NAMES):
        add(IMPACT_TOKEN_MUTATION, "mutates token / share / debt / collateral balances")

    # Deterministic: highest points first, then label.
    dims.sort(key=lambda d: (-d[0], d[1]))
    score = sum(points for points, _ in dims)
    dimensions = [{"dimension": label, "points": points} for points, label in dims]
    return score, dimensions, reasons


def criticality_label(impact_score: int, has_signals: bool) -> str:
    if not has_signals:
        return m.CRIT_UNKNOWN
    if impact_score >= 60:
        return m.CRIT_VERY_HIGH
    if impact_score >= 40:
        return m.CRIT_HIGH
    if impact_score >= 20:
        return m.CRIT_MEDIUM
    if impact_score >= 1:
        return m.CRIT_LOW
    return m.CRIT_UNKNOWN


def compute_review_gap(coverage_signal: str) -> tuple[int, str]:
    points = REVIEW_GAP_POINTS.get(coverage_signal, 20)
    if points >= 30:
        return points, f"+{points} review gap: no direct test observed on this surface"
    if points == 0:
        return points, "+0 review gap: a direct test was observed"
    return points, f"+{points} review gap: coverage is {coverage_signal}"


def review_density_label(coverage_signal: str, test_reference_count: int) -> str:
    if coverage_signal == "tested":
        return m.DENSITY_STRONG if test_reference_count >= 2 else m.DENSITY_MEDIUM
    if coverage_signal == "partially tested":
        return m.DENSITY_WEAK
    if coverage_signal == "no direct test observed":
        return m.DENSITY_NONE
    return m.DENSITY_UNKNOWN


def compute_complexity(record: "m.SurfaceRecord") -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    def add(points, reason):
        nonlocal score
        score += points
        reasons.append(f"+{points} complexity: {reason}")

    risk = record.risk_signals
    if _has(risk, "external call") or _has(risk, "callback") or "low-level-call" in record.periphery_interactions:
        add(COMPLEXITY_EXTERNAL_CALL, "external call / callback")
    if "loop-with-external-call" in record.periphery_interactions or _has(record.behavior_signals, "require-in-loop"):
        add(COMPLEXITY_LOOP, "loop over items")
    if "try-catch" in record.periphery_interactions or _has(record.behavior_signals, "try-catch"):
        add(COMPLEXITY_TRY_CATCH, "try/catch partial-failure handling")
    if record.auth_kinds and (set(record.auth_kinds) & {"signature", "merkle", "domain", "replay"}):
        add(COMPLEXITY_AUTH_LOGIC, "signature / Merkle / domain logic")
    if record.cross_contract_targets or "cross-contract-call" in record.periphery_interactions:
        add(COMPLEXITY_CROSS_CONTRACT, "cross-contract call")
    if record.periphery_interactions:
        add(COMPLEXITY_PERIPHERY, "periphery route")
    return score, reasons


def compute_assumption(record: "m.SurfaceRecord") -> tuple[int, list[str]]:
    n = len(record.assumptions)
    if n == 0:
        return 0, []
    score = ASSUMPTION_BASE
    reasons = [f"+{ASSUMPTION_BASE} assumption: {n} unverified guarding assumption(s) on this surface"]
    if n >= 2:
        score += ASSUMPTION_MULTIPLE
        reasons.append(f"+{ASSUMPTION_MULTIPLE} assumption: multiple assumptions stack here")
    return score, reasons


def blind_spot_priority(score: int) -> str:
    if score >= 85:
        return m.BSP_VERY_HIGH
    if score >= 65:
        return m.BSP_HIGH
    if score >= 40:
        return m.BSP_MEDIUM
    return m.BSP_MONITOR


def score_surface(record: "m.SurfaceRecord") -> "m.SurfaceRecord":
    """Populate all score fields and labels on ``record`` (in place)."""
    impact, dims, impact_reasons = compute_impact(record)
    gap, gap_reason = compute_review_gap(record.coverage_signal)
    complexity, complexity_reasons = compute_complexity(record)
    assumption, assumption_reasons = compute_assumption(record)

    record.impact_score = impact
    record.impact_dimensions = dims
    record.review_gap_score = gap
    record.complexity_score = complexity
    record.assumption_score = assumption
    record.blind_spot_score = impact + gap + complexity + assumption

    has_signals = bool(dims or record.risk_signals or record.auth_kinds
                       or record.periphery_interactions)
    record.criticality_potential = criticality_label(impact, has_signals)
    record.review_density = review_density_label(record.coverage_signal, record.test_reference_count)
    record.blind_spot_priority = blind_spot_priority(record.blind_spot_score)

    if dims:
        record.primary_dimension = dims[0]["dimension"]
        record.secondary_dimensions = [d["dimension"] for d in dims[1:4]]
    record.score_reasons = impact_reasons + [gap_reason] + complexity_reasons + assumption_reasons
    return record
