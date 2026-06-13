"""Transparent blind-spot scoring for lens output (section 13).

Six dimensions, each 1-5:

    Importance, Evidence weakness, Cross-surface complexity,
    Exploitability plausibility, Potential severity, Duplicate risk

    BlindSpotScore = Importance * Evidence weakness * Cross-surface complexity
                     * Exploitability plausibility * Potential severity
                     - Duplicate risk

Every dimension is a heuristic review signal, never a probability or a severity.
A blind spot is a place to look, not a vulnerability.
"""
from __future__ import annotations

from . import models as m

_PRIORITY_IMPORTANCE = {
    m.PRIORITY_VERY_HIGH: 5,
    m.PRIORITY_HIGH: 4,
    m.PRIORITY_MEDIUM: 3,
    m.PRIORITY_MONITOR: 2,
}

# Evidence weakness by status: weaker (less) evidence -> higher weakness score.
_EVIDENCE_WEAKNESS = {
    m.EV_UNKNOWN: 5,
    m.EV_UNTESTED: 5,
    m.EV_COMMENT_ONLY: 5,
    m.EV_HAPPY_PATH_ONLY: 4,
    m.EV_INDIRECTLY_TESTED: 4,
    m.EV_FUZZED_BUT_NOT_TARGETED: 3,
    m.EV_DIRECTLY_TESTED_WEAK: 2,
    m.EV_DIRECTLY_TESTED_STRONG: 1,
    m.EV_FORMALLY_PROVEN: 1,
}

# Per-lane potential severity and duplicate-risk bases (heuristic, review-only).
# Severity = blast radius if a bug existed; duplicate = how picked-over the family is.
_LANE_SEVERITY = {
    "LANE-01": 5, "LANE-02": 5, "LANE-03": 5, "LANE-04": 4, "LANE-05": 5,
    "LANE-06": 4, "LANE-07": 3, "LANE-08": 4, "LANE-09": 3, "LANE-10": 4,
}
_LANE_DUPLICATE = {
    "LANE-01": 3, "LANE-02": 3, "LANE-03": 4, "LANE-04": 2, "LANE-05": 3,
    "LANE-06": 4, "LANE-07": 2, "LANE-08": 3, "LANE-09": 3, "LANE-10": 4,
}


def _clamp(v: int, lo: int = 1, hi: int = 5) -> int:
    return max(lo, min(hi, v))


def evidence_weakness(status: str) -> int:
    return _EVIDENCE_WEAKNESS.get(status, 5)


def score_dimensions(*, lane_id: str, priority: str, status: str,
                     matched_count: int, cross_count: int,
                     value_out: bool) -> dict:
    importance = _PRIORITY_IMPORTANCE.get(priority, 3)
    weakness = evidence_weakness(status)
    complexity = _clamp(1 + matched_count // 2 + min(cross_count, 3))
    base_exploit = {5: 4, 4: 3, 3: 2, 2: 2}.get(importance, 2)
    exploitability = _clamp(base_exploit + (1 if value_out else 0))
    severity = _clamp(_LANE_SEVERITY.get(lane_id, 3))
    duplicate = _clamp(_LANE_DUPLICATE.get(lane_id, 3))
    return {
        "importance": importance,
        "evidence_weakness": weakness,
        "cross_surface_complexity": complexity,
        "exploitability_plausibility": exploitability,
        "potential_severity": severity,
        "duplicate_risk": duplicate,
    }


def blind_spot_score(dims: dict) -> int:
    product = (
        dims["importance"]
        * dims["evidence_weakness"]
        * dims["cross_surface_complexity"]
        * dims["exploitability_plausibility"]
        * dims["potential_severity"]
    )
    return int(product - dims["duplicate_risk"])
