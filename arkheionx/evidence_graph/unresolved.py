"""Unresolved Map builder (v6).

Composes the evidence graph and the interaction matrix into a single view of
everything important that local evidence does not yet close: high-impact
unresolved surfaces, high-impact unresolved interactions, and the surfaces that
could only be left unclassified.

Unresolved does not mean vulnerable. Unresolved means local evidence is
insufficient to close the question. Human review is required.
"""
from __future__ import annotations

from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER
from arkheionx.research.surfaces import ResearchSurfaces, build_research_surfaces
from arkheionx.review_map.model import ReviewMap

from . import models as m
from .builder import build_evidence_graph
from .interactions import build_interaction_matrix


def _safety() -> dict:
    return {
        "disclaimer": LOCAL_ONLY_DISCLAIMER,
        "boundary": list(m.BOUNDARY_LINES),
        "do_not_claim": list(m.DO_NOT_CLAIM),
        "human_review_required": True,
    }


def _final_checklist() -> list[str]:
    return [
        "Which unresolved items must be checked before ending the review? (Start with very-high criticality.)",
        "Which items should be handed to a review agent as a scoped task? (See the agent input.)",
        "Which items need manual code reading rather than a test? (Authorization and lifecycle logic.)",
        "Which items need a local Foundry test? (Value movement and accounting deltas.)",
        "Which items need a fuzz or invariant test? (Share math, rounding, and accounting conservation.)",
        "Which items must not be claimed without independent local proof? (All of them.)",
    ]


def build_unresolved_map(rm: ReviewMap, surfaces: ResearchSurfaces, *,
                         source_files: int = 0, test_files: int = 0,
                         memory: dict[str, str] | None = None,
                         package_version: str = "") -> dict:
    graph = build_evidence_graph(rm, surfaces, source_files=source_files,
                                 test_files=test_files, memory=memory, package_version=package_version)
    matrix = build_interaction_matrix(rm, surfaces, source_files=source_files,
                                      test_files=test_files, memory=memory, package_version=package_version)

    unresolved_surfaces = []
    for s in graph["unresolved_surfaces"]:
        unresolved_surfaces.append({
            "id": s["node_id"],
            "surface": s["surface_id"],
            "source": s["source"],
            "why_important": f"{s['surface_type']} surface with {s['criticality_potential']} criticality potential (heuristic blast radius, not severity).",
            "evidence_state": s["evidence_state"],
            "evidence_strength": s["evidence_strength"],
            "missing_evidence": s["missing_evidence"],
            "suggested_test": s["next_test_direction"],
            "priority": s["criticality_potential"],
            "human_review_required": True,
        })

    unresolved_interactions = []
    for ix in matrix["unresolved_interactions"]:
        unresolved_interactions.append({
            "id": ix["interaction_id"],
            "interaction": ix["interaction_class"],
            "surfaces": ix["surfaces"],
            "why_important": ix["why_combination_matters"],
            "evidence_state": ix["evidence_state"],
            "evidence_strength": ix["evidence_strength"],
            "missing_evidence": ix["missing_test_direction"],
            "suggested_test": ix["suggested_invariant"],
            "priority": ix["interaction_priority"],
            "human_review_required": True,
        })

    unclassified = [
        {
            "id": n["node_id"],
            "surface": n["surface_id"],
            "source": (f"{n['source_file']}:{n['source_line']}" if n["source_line"] else n["source_file"]),
            "surface_type": n["surface_type"],
            "why_unclassified": n["unresolved_reason"] or "Detected as a surface, but local signals are insufficient to classify it.",
            "human_review_required": True,
        }
        for n in graph["nodes"] if n["evidence_state"] == m.STATE_UNCLASSIFIED
    ]

    summary = {
        "unresolved_surfaces": len(unresolved_surfaces),
        "unresolved_interactions": len(unresolved_interactions),
        "unclassified_surfaces": len(unclassified),
        "high_impact_surfaces": graph["repo_summary"]["high_impact_surfaces"],
        "evidence_nodes": len(graph["nodes"]),
        "total_interactions": matrix["matrix_summary"]["total_interactions"],
    }

    return {
        "schema_version": m.SCHEMA_VERSION,
        "package_version": package_version,
        "command": "unresolved-map",
        "kind": m.KIND_UNRESOLVED_MAP,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "repo_summary": graph["repo_summary"],
        "summary": summary,
        "unresolved_surfaces": unresolved_surfaces,
        "unresolved_interactions": unresolved_interactions,
        "unclassified_surfaces": unclassified,
        "final_checklist": _final_checklist(),
        "safety": _safety(),
        "human_review_required": True,
    }


def build_unresolved_map_from_review_map(rm: ReviewMap, root, *,
                                         source_files: int = 0, test_files: int = 0,
                                         memory: dict[str, str] | None = None,
                                         package_version: str = "") -> dict:
    surfaces = build_research_surfaces(rm, root)
    return build_unresolved_map(rm, surfaces, source_files=source_files, test_files=test_files,
                                memory=memory, package_version=package_version)
