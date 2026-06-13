"""Arkheionx v7.5 — Protocol Lens Packs.

A protocol lens turns a generic local Solidity review into a protocol-aware research
workflow. v4 maps value flow, v5 prioritizes blind spots, v6 classifies evidence,
v7 turns scope into lanes/tasks, and v7.5 adds protocol lenses. v7.5 is the package
version; the lens layer additionally carries its own
:data:`~arkheionx.protocol_lens.models.SCHEMA_VERSION` for its JSON artifacts.

The first implemented lens is Fixed Credit Market (``fixed-credit-market``), which models a
fixed-maturity credit market with credit/debt units, settlement-time liquidity,
maker group exposure, multi-collateral solvency, bad-debt/loss-factor accounting,
gates, fees, and periphery bundles.

Local/static and heuristic. No RPC, no live-chain calls, no transaction execution,
no private keys, no exploit automation, and no external AI API calls. A lens is not
a finding. A review lane is not a vulnerability. An evidence score is not
vulnerability validity. A candidate with evidence is not confirmed. Human review is
required.
"""
from __future__ import annotations

from .base import ProtocolLens
from .blindspots import build_blind_spots
from .evidence_judge import judge_evidence, scoring_rubric
from .evidence_map import build_evidence_map
from .extractor import build_lens_context, extract_protocol_model
from .json_output import (
    default_lens_evidence_dir,
    default_lens_lanes_dir,
    default_lens_map_dir,
    default_lens_pack_dir,
    default_lens_report_filter_dir,
    default_lens_tasks_dir,
    write_lens_evidence,
    write_lens_lanes,
    write_lens_map,
    write_lens_report_filter,
    write_lens_tasks,
)
from .lane_builder import build_lens_map, build_review_lanes
from .leak_check import (
    is_public_output_path,
    output_path_warning,
    run_private_leak_check,
)
from .models import (
    EVIDENCE_STATUSES,
    GRADES,
    JUDGE_DECISIONS,
    REPORT_OUTCOMES,
    SCHEMA_VERSION,
    SCOPE_INCOMPLETE_LOCAL_ONLY,
    UNKNOWN_IN_LOCAL_REPO,
)
from .pack_writer import build_lens_pack
from .registry import (
    PLANNED_LENSES,
    available_lenses,
    get_lens,
    is_registered,
    lens_ids,
)
from .report_filter import PRE_SUBMISSION_CHECKLIST, build_report_filter
from .task_builder import build_scope_tasks

__all__ = [
    "SCHEMA_VERSION",
    "SCOPE_INCOMPLETE_LOCAL_ONLY",
    "UNKNOWN_IN_LOCAL_REPO",
    "EVIDENCE_STATUSES",
    "GRADES",
    "JUDGE_DECISIONS",
    "REPORT_OUTCOMES",
    "ProtocolLens",
    "get_lens",
    "is_registered",
    "available_lenses",
    "lens_ids",
    "PLANNED_LENSES",
    "build_lens_context",
    "extract_protocol_model",
    "build_lens_map",
    "build_review_lanes",
    "build_scope_tasks",
    "build_evidence_map",
    "build_blind_spots",
    "judge_evidence",
    "scoring_rubric",
    "build_report_filter",
    "PRE_SUBMISSION_CHECKLIST",
    "build_lens_pack",
    "run_private_leak_check",
    "output_path_warning",
    "is_public_output_path",
    "write_lens_map",
    "write_lens_lanes",
    "write_lens_tasks",
    "write_lens_evidence",
    "write_lens_report_filter",
    "default_lens_map_dir",
    "default_lens_lanes_dir",
    "default_lens_tasks_dir",
    "default_lens_evidence_dir",
    "default_lens_report_filter_dir",
    "default_lens_pack_dir",
]
