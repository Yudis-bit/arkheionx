"""Protocol Review Map (v3.1.0).

Turns a local DeFi repository into a structured review surface: contracts,
value paths, assumptions, test gaps, proof suggestions, and evidence links.
Local/static and heuristic by default; review guidance, not findings.
"""
from __future__ import annotations

from .artifacts import default_out_dir, write_artifacts
from .build import build_review_map
from .model import ReviewMap
from .render import render_cli, render_markdown, render_summary_md, status_of

__all__ = [
    "build_review_map",
    "write_artifacts",
    "default_out_dir",
    "render_cli",
    "render_markdown",
    "render_summary_md",
    "status_of",
    "ReviewMap",
]
