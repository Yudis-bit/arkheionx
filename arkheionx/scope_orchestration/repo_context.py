"""Shared repo-analysis context for the v7 layer.

Reuses the v4 review map and the v5 surface-record engine so v7 stays consistent
with the layers it builds on. No source file is re-scanned here. Leaf module: it
imports only lower layers, so lane/task/scope-map builders can all share it without
an import cycle.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.blind_spots.signals import build_surface_records
from arkheionx.research.surfaces import build_research_surfaces
from arkheionx.review_map.model import ReviewMap


def repo_summary(rm: ReviewMap, source_files: int = 0, test_files: int = 0) -> dict:
    """Return portable repository metadata for generated review packs.

    ``ReviewMap.repo_path`` is local execution provenance and can contain a user
    name, workspace layout, or a private target name. Scope and protocol-lens
    packs can be exported, so retain the legacy field with a stable relative
    marker instead of embedding the host path.
    """
    s = rm.summary
    return {
        "repo_path": ".",
        "mode": rm.mode,
        "protocol_types": list(s.protocol_types),
        "contracts": s.contracts_analyzed,
        "functions": s.functions_mapped,
        "source_files": source_files,
        "test_files": test_files,
        "value_paths": s.value_paths,
        "assumptions": s.assumptions,
        "test_gaps": s.test_gaps,
    }


def build_repo_context(rm: ReviewMap, root: Path | str, *,
                       source_files: int = 0, test_files: int = 0) -> dict:
    """Build the shared context: repo summary + scored surface records.

    Returns ``{"repo_summary": dict, "records": list[SurfaceRecord], "generated_at": str}``.
    """
    surfaces = build_research_surfaces(rm, Path(root))
    records = build_surface_records(rm, surfaces)
    return {
        "repo_summary": repo_summary(rm, source_files, test_files),
        "records": records,
        "generated_at": rm.generated_at,
    }
