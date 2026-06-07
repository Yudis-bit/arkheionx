"""Blind Spot Intelligence engine (v5).

Extends the v4 review-map and v4.1 research-memory workflow into an attention
allocation layer for Web3 security research: it identifies likely blind-spot
surfaces (high impact, weak review evidence), maps criticality potential (blast
radius), negates assumptions into counterfactual research prompts, and packages
the result into a local, vendor-agnostic research pack.

Local/static and heuristic. Blind spot candidates are not vulnerabilities;
criticality potential is not severity; counterfactuals are research prompts, not
findings. Human review is required for every conclusion.
"""
from __future__ import annotations

from .counterfactuals import build_counterfactuals
from .engine import (
    SCORING_MODEL,
    build_blind_spot_map,
    build_blind_spot_map_from_review_map,
    build_counterfactual_plan,
    build_counterfactual_plan_from_review_map,
    build_criticality_map,
    build_criticality_map_from_review_map,
)
from .json_output import (
    default_blind_spots_dir,
    default_counterfactuals_dir,
    default_criticality_dir,
    default_research_pack_dir,
    write_blind_spots,
    write_counterfactuals,
    write_criticality_map,
)
from .models import SurfaceRecord
from .pack import build_research_pack
from .render import (
    render_blind_spots_cli,
    render_blind_spots_md,
    render_counterfactuals_cli,
    render_counterfactuals_md,
    render_criticality_map_cli,
    render_criticality_map_md,
)
from .signals import build_surface_records

__all__ = [
    "SurfaceRecord",
    "SCORING_MODEL",
    "build_surface_records",
    "build_blind_spot_map",
    "build_blind_spot_map_from_review_map",
    "build_criticality_map",
    "build_criticality_map_from_review_map",
    "build_counterfactual_plan",
    "build_counterfactual_plan_from_review_map",
    "build_counterfactuals",
    "build_research_pack",
    "render_blind_spots_md",
    "render_blind_spots_cli",
    "render_criticality_map_md",
    "render_criticality_map_cli",
    "render_counterfactuals_md",
    "render_counterfactuals_cli",
    "write_blind_spots",
    "write_criticality_map",
    "write_counterfactuals",
    "default_blind_spots_dir",
    "default_criticality_dir",
    "default_counterfactuals_dir",
    "default_research_pack_dir",
]
