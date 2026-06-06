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
    payload = draft.payload or {}
    evidence_context = payload.get("evidence_context", {}) or {}
    package_id = str(evidence_context.get("evidence_package_id", ""))
    readiness = str((payload.get("report_readiness", {}) or {}).get("status", "draft"))
    out = [
        "ARKHEIONX REPORT",
        f"Project: {project}",
        f"Target: {draft.target}",
        "Status: draft-created",
        f"Review status: {draft.review_status}",
        f"Mode: {_mode(draft.evidence_level)}",
        "",
        "Draft",
        f"  Markdown: {draft.md_path}",
        f"  JSON: {draft.json_path}",
        "",
        "Evidence",
        f"  Level: {draft.evidence_level}",
        f"  Package: {package_id or 'n/a'}",
        f"  Proof: {draft.proof_path or 'n/a'}",
        f"  Trace: {draft.trace_path or 'n/a'}",
        f"  Report readiness: {readiness} (manual review required)",
        "",
        "Limits",
        "  Draft only. No auto-submit. No final severity claim.",
        "",
        "Next",
        "  Review the draft manually before submission.",
    ]
    lvs = payload.get("local_validation_support")
    if isinstance(lvs, dict):
        insert = [
            "",
            "Local Validation Context",
            f"  Tested: {lvs.get('tested_support', 0)}  Trace-bound: {lvs.get('trace_bound_support', 0)}  "
            f"Needs review: {lvs.get('tests_needing_review', 0)}",
            "  Supporting context only; manual review required; not ready for submission.",
        ]
        limits_at = out.index("Limits") - 1
        out[limits_at:limits_at] = insert
    pgc = payload.get("protocol_graph_context")
    if isinstance(pgc, dict):
        insert = [
            "",
            "Protocol Graph Context",
            "  Protocol graph context was included for reviewer orientation.",
            f"  Function roles: {pgc.get('function_role_count', 0)}  Value paths: {pgc.get('value_path_count', 0)}  "
            f"Assumptions: {pgc.get('assumption_count', 0)}  Test gaps: {pgc.get('test_gap_count', 0)}",
            "  Function roles, value paths, assumptions, and test gaps are supporting context only.",
            "  Manual review required. Ready for submission: False.",
        ]
        limits_at = out.index("Limits") - 1
        out[limits_at:limits_at] = insert
    return "\n".join(out) + "\n"
