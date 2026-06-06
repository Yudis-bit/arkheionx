"""Protocol Review Map (v3.1.0).

Turns a local DeFi repository into a structured review surface: contracts,
value paths, assumptions, test gaps, proof suggestions, and evidence links.
Local/static and heuristic by default; review guidance, not findings.
"""
from __future__ import annotations

from .artifacts import default_out_dir, write_artifacts
from .assumptions import build_assumptions_payload, render_assumptions_cli
from .build import build_review_map
from .evidence_links import build_evidence_links_payload, render_evidence_links_cli
from .model import ReviewMap
from .proof_plan import build_proof_plan_payload, render_proof_plan_cli
from .render import render_cli, render_markdown, render_summary_md, status_of
from .test_gap_map import build_test_gap_map, render_test_gap_map_cli, render_test_gap_map_md
from .value_paths import build_value_paths_payload, render_value_paths_cli

__all__ = [
    "build_review_map",
    "write_artifacts",
    "default_out_dir",
    "render_cli",
    "render_markdown",
    "render_summary_md",
    "status_of",
    "build_assumptions_payload",
    "render_assumptions_cli",
    "build_proof_plan_payload",
    "render_proof_plan_cli",
    "build_test_gap_map",
    "render_test_gap_map_cli",
    "render_test_gap_map_md",
    "build_value_paths_payload",
    "render_value_paths_cli",
    "build_evidence_links_payload",
    "render_evidence_links_cli",
    "ReviewMap",
]
