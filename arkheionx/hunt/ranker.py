"""Rank bug-hunting surfaces for a solo researcher.

Produces a focused, ranked list (not noisy warning spam). Scoring reuses the
per-function risk score and applies small adjustments for hunt relevance.
"""
from __future__ import annotations

from arkheionx.protocol.model import FunctionRole

from .bug_classes import bug_classes_for
from .model import HunterTarget, ValueHotspot
from .test_suggestions import suggest_tests


def _priority(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def _adjusted_score(fr: FunctionRole) -> int:
    score = fr.risk_score
    # Hunt cares most about user-callable, value-moving surfaces.
    if fr.user_callable and fr.role in {"Money Exit", "Reward Claim"}:
        score += 8
    if fr.oracle_calls and fr.writes_state:
        score += 5
    return max(0, min(100, score))


def rank_hotspots(function_roles: list[FunctionRole], evidence_level: str) -> list[ValueHotspot]:
    hotspots: list[ValueHotspot] = []
    for fr in function_roles:
        score = _adjusted_score(fr)
        if score <= 0:
            continue
        hotspots.append(
            ValueHotspot(
                target_id=fr.function_id,
                target_type="function",
                score=score,
                priority=_priority(score),
                reasons=list(fr.reasons),
                evidence_level=evidence_level,
                suggested_next_command=f"arkheionx prove . --target {fr.display_id or (fr.contract_name + '.' + fr.function_name)}",
            )
        )
    hotspots.sort(key=lambda h: (-h.score, h.target_id))
    return hotspots


def rank_targets(function_roles: list[FunctionRole], evidence_level: str, top: int = 10) -> list[HunterTarget]:
    by_id = {fr.function_id: fr for fr in function_roles}
    hotspots = rank_hotspots(function_roles, evidence_level)
    targets: list[HunterTarget] = []
    for rank, hotspot in enumerate(hotspots[:top], start=1):
        fr = by_id[hotspot.target_id]
        tests, invariants = suggest_tests(fr)
        qualified = fr.display_id or f"{fr.contract_name}.{fr.function_name}"
        targets.append(
            HunterTarget(
                rank=rank,
                target_id=hotspot.target_id,
                score=hotspot.score,
                priority=hotspot.priority,
                bug_classes=bug_classes_for(fr),
                why_it_matters=list(fr.reasons),
                suggested_tests=tests,
                suggested_invariants=invariants,
                evidence_level=evidence_level,
                next_command=f"arkheionx prove . --target {qualified}",
            )
        )
    return targets
