"""Compact rendering for the report command."""
from __future__ import annotations

from .model import ReportDraft


def _mode(level: str) -> str:
    return {
        "EVIDENCE_READY": "evidence-ready",
        "EXECUTION_CONFIRMED": "execution-confirmed",
        "COMPILER_CONFIRMED": "compiler-confirmed",
    }.get(level, "heuristic")


def render_report(draft: ReportDraft, project: str) -> str:
    out = [
        "ARKHEIONX REPORT",
        f"Project: {project}",
        f"Target: {draft.target}",
        "Status: draft-created",
        f"Mode: {_mode(draft.evidence_level)}",
        "",
        "Draft",
        f"  Markdown: {draft.md_path}",
        f"  JSON: {draft.json_path}",
        "",
        "Evidence",
        f"  Level: {draft.evidence_level}",
        f"  Proof: {draft.proof_path or 'n/a'}",
        f"  Trace: {draft.trace_path or 'n/a'}",
        "",
        "Limits",
        "  Draft only. No auto-submit. No final severity claim.",
        "",
        "Next",
        "  Review the draft manually before submission.",
    ]
    return "\n".join(out) + "\n"
