"""Arkheionx v7 — Scope-Aware Orchestration + Evidence Judge.

v4 maps value flow. v5 prioritizes likely blind spots. v6 classifies evidence and
unresolved interactions. v7 turns an audit/contest/program scope note into review
lanes, scope tasks, evidence requirements, and report filters so AI-assisted
security review starts from rules and evidence instead of vague prompts.

Local/static and heuristic. No RPC, no live-chain calls, no transaction execution,
no private keys, no exploit automation, and no external AI API calls. A scope task
is a research instruction, not an exploit instruction. Evidence quality is not
vulnerability validity. Candidate-with-evidence is not a confirmed vulnerability.
Task priority is not severity. Human review is required.
"""
from __future__ import annotations

from .evidence_judge import judge_evidence, scoring_rubric
from .json_output import (
    default_evidence_judge_dir,
    default_report_filter_dir,
    default_scope_lanes_dir,
    default_scope_map_dir,
    default_scope_pack_dir,
    default_scope_tasks_dir,
    write_evidence_judge,
    write_report_filter,
    write_scope_lanes,
    write_scope_map,
    write_scope_tasks,
)
from .lane_builder import build_scope_lanes, build_scope_map
from .leak_check import (
    default_private_dir,
    default_private_terms_path,
    load_private_terms,
    run_private_leak_check,
    scan_text_for_terms,
)
from .models import (
    CLASSIFICATIONS,
    EVIDENCE_QUALITIES,
    JUDGMENTS,
    LANE_DEFS,
    SCHEMA_VERSION,
    ScopeData,
)
from .pack_writer import build_scope_pack
from .render import (
    render_evidence_judge_cli,
    render_evidence_judge_md,
    render_report_filter_cli,
    render_report_filter_md,
    render_scope_lanes_cli,
    render_scope_lanes_md,
    render_scope_map_cli,
    render_scope_map_md,
    render_scope_tasks_cli,
    render_scope_tasks_md,
)
from .report_filter import PRE_SUBMISSION_CHECKLIST, filter_report_candidates
from .scope_parser import parse_scope_file, parse_scope_text, requires_medium_high
from .task_builder import build_scope_tasks

__all__ = [
    "SCHEMA_VERSION",
    "ScopeData",
    "LANE_DEFS",
    "CLASSIFICATIONS",
    "EVIDENCE_QUALITIES",
    "JUDGMENTS",
    "build_scope_map",
    "build_scope_lanes",
    "build_scope_tasks",
    "build_scope_pack",
    "judge_evidence",
    "filter_report_candidates",
    "scoring_rubric",
    "parse_scope_file",
    "parse_scope_text",
    "requires_medium_high",
    "run_private_leak_check",
    "load_private_terms",
    "scan_text_for_terms",
    "default_private_dir",
    "default_private_terms_path",
    "PRE_SUBMISSION_CHECKLIST",
    "render_scope_map_md",
    "render_scope_map_cli",
    "render_scope_lanes_md",
    "render_scope_lanes_cli",
    "render_scope_tasks_md",
    "render_scope_tasks_cli",
    "render_evidence_judge_md",
    "render_evidence_judge_cli",
    "render_report_filter_md",
    "render_report_filter_cli",
    "write_scope_map",
    "write_scope_lanes",
    "write_scope_tasks",
    "write_evidence_judge",
    "write_report_filter",
    "default_scope_map_dir",
    "default_scope_lanes_dir",
    "default_scope_tasks_dir",
    "default_scope_pack_dir",
    "default_evidence_judge_dir",
    "default_report_filter_dir",
]
