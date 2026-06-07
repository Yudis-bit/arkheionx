"""Orchestration for the v5 Blind Spot Intelligence layer.

Builds three deterministic, JSON-ready payloads from a review map and the v4.1
research surfaces:

- ``build_blind_spot_map`` — likely blind-spot candidates, scoring, unknown
  surfaces, notable non-blind-spots, and linked counterfactuals.
- ``build_criticality_map`` — criticality potential across every surface.
- ``build_counterfactual_plan`` — counterfactual research prompts + matrix.

Everything is heuristic and local/static. Human review is required.
"""
from __future__ import annotations

from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER
from arkheionx.review_map.model import ReviewMap
from arkheionx.research.surfaces import ResearchSurfaces, build_research_surfaces

from . import models as m
from . import scoring
from .counterfactuals import build_counterfactuals
from .signals import build_surface_records

# Human-readable description of the scoring model (mirrors scoring.py constants).
SCORING_MODEL = {
    "formula": "blind_spot_score = impact_score + review_gap_score + complexity_score + assumption_score",
    "note": "Heuristic review priority. Not a probability, not a severity, not an exploitability estimate.",
    "impact_points": {
        "value exit": scoring.IMPACT_VALUE_EXIT[0],
        "accounting mutation": scoring.IMPACT_ACCOUNTING[0],
        "authorization control": scoring.IMPACT_AUTHORIZATION[0],
        "liquidation/seizure": scoring.IMPACT_LIQUIDATION[0],
        "oracle dependency": scoring.IMPACT_ORACLE[0],
        "external call/callback": scoring.IMPACT_EXTERNAL_CALL[0],
        "periphery/core boundary": scoring.IMPACT_PERIPHERY[0],
        "admin/emergency control": scoring.IMPACT_ADMIN[0],
        "cross-contract dependency": scoring.IMPACT_CROSS_CONTRACT[0],
        "token/share/debt/collateral mutation": scoring.IMPACT_TOKEN_MUTATION[0],
    },
    "review_gap_points": dict(scoring.REVIEW_GAP_POINTS),
    "complexity_points": {
        "external call": scoring.COMPLEXITY_EXTERNAL_CALL,
        "loop": scoring.COMPLEXITY_LOOP,
        "try/catch": scoring.COMPLEXITY_TRY_CATCH,
        "signature/Merkle/domain": scoring.COMPLEXITY_AUTH_LOGIC,
        "cross-contract call": scoring.COMPLEXITY_CROSS_CONTRACT,
        "periphery route": scoring.COMPLEXITY_PERIPHERY,
    },
    "assumption_points": {
        "any unverified assumption": scoring.ASSUMPTION_BASE,
        "multiple assumptions": scoring.ASSUMPTION_MULTIPLE,
    },
    "blind_spot_priority_thresholds": {"very-high": 85, "high": 65, "medium": 40, "monitor": 0},
    "criticality_thresholds": {"very-high": 60, "high": 40, "medium": 20, "low": 1, "unknown": 0},
}

CRITICALITY_DIMENSIONS = [
    {"dimension": label, "points": points} for points, label in sorted(
        [scoring.IMPACT_VALUE_EXIT, scoring.IMPACT_ACCOUNTING, scoring.IMPACT_AUTHORIZATION,
         scoring.IMPACT_LIQUIDATION, scoring.IMPACT_ORACLE, scoring.IMPACT_EXTERNAL_CALL,
         scoring.IMPACT_PERIPHERY, scoring.IMPACT_ADMIN, scoring.IMPACT_CROSS_CONTRACT,
         scoring.IMPACT_TOKEN_MUTATION],
        key=lambda d: (-d[0], d[1]))
]


def _safety() -> dict:
    return {
        "disclaimer": LOCAL_ONLY_DISCLAIMER,
        "boundary": list(m.BOUNDARY_LINES),
        "do_not_claim": list(m.DO_NOT_CLAIM),
        "human_review_required": True,
    }


def _repository_summary(rm: ReviewMap, surfaces: ResearchSurfaces,
                        source_files: int, test_files: int) -> dict:
    s = rm.summary
    return {
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "protocol_types": list(s.protocol_types),
        "contracts": s.contracts_analyzed,
        "functions": s.functions_mapped,
        "source_files": source_files,
        "test_files": test_files,
        "value_paths": s.value_paths,
        "assumptions": s.assumptions,
        "test_gaps": s.test_gaps,
        "authorization_surfaces": len(surfaces.authorization_surfaces),
        "periphery_surfaces": len(surfaces.periphery_surfaces),
        "behavior_mismatch_surfaces": len(surfaces.behavior_mismatch_surfaces),
    }


def _is_candidate(r: m.SurfaceRecord) -> bool:
    """A blind spot candidate: high-impact, weakly-reviewed surface."""
    return m.is_weak_density(r.review_density) and r.criticality_potential in (
        m.CRIT_VERY_HIGH, m.CRIT_HIGH, m.CRIT_MEDIUM)


def _candidate_dict(r: m.SurfaceRecord, cf_by_target: dict[str, dict]) -> dict:
    cf = cf_by_target.get(r.target)
    return {
        "surface": _surface_label(r),
        "contract": r.contract,
        "function": r.function,
        "target": r.target,
        "source": r.source,
        "criticality_potential": r.criticality_potential,
        "review_density": r.review_density,
        "coverage_signal": r.coverage_signal,
        "blind_spot_score": r.blind_spot_score,
        "score_components": {
            "impact": r.impact_score,
            "review_gap": r.review_gap_score,
            "complexity": r.complexity_score,
            "assumption": r.assumption_score,
        },
        "blind_spot_priority": r.blind_spot_priority,
        "risk_signals": r.risk_signals,
        "review_density_signals": _density_signals(r),
        "primary_dimension": r.primary_dimension,
        "secondary_dimensions": r.secondary_dimensions,
        "score_reasons": r.score_reasons,
        "why_it_may_be_skipped": r.why_it_may_be_skipped,
        "why_it_may_matter": r.why_it_may_matter,
        "suggested_counterfactual": cf["what_if_false"] if cf else "",
        "suggested_counterfactual_id": cf["id"] if cf else "",
        "suggested_local_test": r.suggested_local_test,
        "evidence_needed": r.evidence_needed,
        "do_not_claim": ("This is a blind spot candidate, not a vulnerability. "
                         "Do not submit it as a finding without independent local proof."),
        "status": m.STATUS_OPEN,
        "manual_review_required": True,
    }


def _surface_label(r: m.SurfaceRecord) -> str:
    if "value exit" in r.risk_signals:
        return "value-exit surface"
    if r.auth_kinds:
        return "authorization surface"
    if r.periphery_interactions:
        return "periphery surface"
    if "oracle" in " ".join(r.risk_signals):
        return "oracle surface"
    if "liquidation" in r.risk_signals:
        return "liquidation surface"
    if "value entry" in r.risk_signals:
        return "value-entry surface"
    return "review surface"


def _density_signals(r: m.SurfaceRecord) -> list[str]:
    out = [f"coverage: {r.coverage_signal}", f"direct test references: {r.test_reference_count}"]
    if r.assumptions:
        out.append(f"unverified assumptions: {len(r.assumptions)}")
    return out


def _unknown_surfaces(records: list[m.SurfaceRecord]) -> list[dict]:
    out = []
    for r in records:
        if r.review_density in (m.DENSITY_NONE, m.DENSITY_UNKNOWN):
            out.append({
                "target": r.target,
                "source": r.source,
                "why_unknown": "No direct local test was observed for this surface.",
                "missing_evidence": "A local test exercising this surface and asserting its guarding invariant.",
                "criticality_potential": r.criticality_potential,
                "suggested_local_test": r.suggested_local_test,
                "priority": r.blind_spot_priority,
            })
    return out


def _notable_non_blind_spots(records: list[m.SurfaceRecord]) -> list[dict]:
    """High-value surfaces that DO have stronger test signals — avoid wasting time."""
    out = []
    for r in records:
        if r.criticality_potential in (m.CRIT_VERY_HIGH, m.CRIT_HIGH) and not m.is_weak_density(r.review_density):
            out.append({
                "target": r.target,
                "source": r.source,
                "criticality_potential": r.criticality_potential,
                "review_density": r.review_density,
                "note": "High criticality potential with a direct test observed — lower immediate review priority.",
            })
    return out


def build_blind_spot_map(rm: ReviewMap, surfaces: ResearchSurfaces, *,
                         source_files: int = 0, test_files: int = 0, limit: int = 12) -> dict:
    records = build_surface_records(rm, surfaces)
    counterfactuals = build_counterfactuals(rm, surfaces, records)
    cf_by_target: dict[str, dict] = {}
    for cf in counterfactuals:
        cf_by_target.setdefault(cf["target"], cf)

    candidates = [r for r in records if _is_candidate(r)][:max(1, limit)]
    candidate_dicts = []
    for i, r in enumerate(candidates, 1):
        d = _candidate_dict(r, cf_by_target)
        candidate_dicts.append({"id": f"BSP-{i:03d}", **d})

    return {
        "schema_version": m.SCHEMA_VERSION,
        "kind": m.KIND_BLIND_SPOTS,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "repository": _repository_summary(rm, surfaces, source_files, test_files),
        "candidates": candidate_dicts,
        "scoring": SCORING_MODEL,
        "unknown_surfaces": _unknown_surfaces(records),
        "notable_non_blind_spots": _notable_non_blind_spots(records),
        "counterfactuals": counterfactuals[:8],
        "safety": _safety(),
    }


def build_blind_spot_map_from_review_map(rm: ReviewMap, root, *,
                                         source_files: int = 0, test_files: int = 0,
                                         limit: int = 12) -> dict:
    surfaces = build_research_surfaces(rm, root)
    return build_blind_spot_map(rm, surfaces, source_files=source_files, test_files=test_files, limit=limit)


def build_criticality_map(rm: ReviewMap, surfaces: ResearchSurfaces, *,
                          source_files: int = 0, test_files: int = 0) -> dict:
    records = build_surface_records(rm, surfaces)
    by_impact = sorted(records, key=lambda r: (-r.impact_score, m.criticality_rank(r.criticality_potential), r.target))
    surface_rows = []
    for r in by_impact:
        surface_rows.append({
            "target": r.target,
            "contract": r.contract,
            "function": r.function,
            "source": r.source,
            "criticality_potential": r.criticality_potential,
            "impact_score": r.impact_score,
            "primary_dimension": r.primary_dimension or "—",
            "secondary_dimensions": r.secondary_dimensions,
            "dimensions": r.impact_dimensions,
            "review_density": r.review_density,
            "why_it_could_matter": r.why_it_may_matter,
            "human_review_prompt": (
                f"Confirm the worst-case impact of a bug in `{r.target}` and whether local "
                f"tests cover it. Criticality potential is heuristic blast radius, not severity."),
            "manual_review_required": True,
        })
    highest = [row for row in surface_rows
               if row["criticality_potential"] in (m.CRIT_VERY_HIGH, m.CRIT_HIGH)][:10]
    crit_vs_density = [
        {"target": r.target, "source": r.source, "criticality_potential": r.criticality_potential,
         "review_density": r.review_density, "blind_spot_priority": r.blind_spot_priority}
        for r in by_impact
        if r.criticality_potential in (m.CRIT_VERY_HIGH, m.CRIT_HIGH, m.CRIT_MEDIUM)
        and m.is_weak_density(r.review_density)
    ]
    return {
        "schema_version": m.SCHEMA_VERSION,
        "kind": m.KIND_CRITICALITY_MAP,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "repository": _repository_summary(rm, surfaces, source_files, test_files),
        "dimensions": CRITICALITY_DIMENSIONS,
        "surfaces": surface_rows,
        "highest_blast_radius": highest,
        "criticality_vs_review_density": crit_vs_density,
        "safety": _safety(),
    }


def build_criticality_map_from_review_map(rm: ReviewMap, root, *,
                                          source_files: int = 0, test_files: int = 0) -> dict:
    surfaces = build_research_surfaces(rm, root)
    return build_criticality_map(rm, surfaces, source_files=source_files, test_files=test_files)


def build_counterfactual_plan(rm: ReviewMap, surfaces: ResearchSurfaces, *,
                              source_files: int = 0, test_files: int = 0, limit: int = 24) -> dict:
    records = build_surface_records(rm, surfaces)
    counterfactuals = build_counterfactuals(rm, surfaces, records, limit=limit)
    matrix = [{
        "id": cf["id"],
        "assumption": cf["assumption"],
        "false_world_scenario": cf["what_if_false"],
        "impact_potential": cf["impact_potential"],
        "testability": cf["testability"],
        "priority": cf["priority"],
        "evidence_required": cf["evidence_needed"],
    } for cf in counterfactuals]
    used_assumptions = [
        {"id": a.id, "title": a.title, "category": a.category, "status": a.status}
        for a in sorted(rm.assumptions, key=lambda a: a.id)
    ]
    return {
        "schema_version": m.SCHEMA_VERSION,
        "kind": m.KIND_COUNTERFACTUALS,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "repository": _repository_summary(rm, surfaces, source_files, test_files),
        "counterfactuals": counterfactuals,
        "counterfactual_matrix": matrix,
        "assumptions": used_assumptions,
        "safety": _safety(),
    }


def build_counterfactual_plan_from_review_map(rm: ReviewMap, root, *,
                                              source_files: int = 0, test_files: int = 0,
                                              limit: int = 24) -> dict:
    surfaces = build_research_surfaces(rm, root)
    return build_counterfactual_plan(rm, surfaces, source_files=source_files, test_files=test_files, limit=limit)
