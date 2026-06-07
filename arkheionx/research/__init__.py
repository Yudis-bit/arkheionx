"""Research memory engine (v4.1).

Extends the local/static review-map workflow into an AI-assisted research
memory: an agent brief, a hypothesis log (rejected-finding memory), and a
case-study generator, plus the surface engine that backs them (coverage
weakness ranking, authorization surfaces, periphery/core flows, and
behavior-mismatch heuristics).

Local/static and heuristic. Hypotheses are review prompts, not findings. Human
review is required for every conclusion.
"""
from __future__ import annotations

from .agent_brief import (
    build_agent_brief,
    build_agent_brief_from_review_map,
    render_agent_brief_cli,
    render_agent_brief_md,
)
from .case_study import (
    build_case_study,
    build_case_study_from_review_map,
    render_case_study_cli,
    render_case_study_md,
)
from .hypotheses import generate_hypotheses
from .hypothesis_log import (
    build_hypothesis_log,
    build_hypothesis_log_from_review_map,
    render_hypothesis_log_cli,
    render_hypothesis_log_md,
)
from .surfaces import ResearchSurfaces, build_research_surfaces
from .artifacts import (
    default_research_dir,
    write_agent_brief,
    write_case_study,
    write_hypothesis_log,
)

__all__ = [
    "build_research_surfaces",
    "ResearchSurfaces",
    "generate_hypotheses",
    "build_agent_brief",
    "build_agent_brief_from_review_map",
    "render_agent_brief_md",
    "render_agent_brief_cli",
    "build_hypothesis_log",
    "build_hypothesis_log_from_review_map",
    "render_hypothesis_log_md",
    "render_hypothesis_log_cli",
    "build_case_study",
    "build_case_study_from_review_map",
    "render_case_study_md",
    "render_case_study_cli",
    "default_research_dir",
    "write_agent_brief",
    "write_hypothesis_log",
    "write_case_study",
]
