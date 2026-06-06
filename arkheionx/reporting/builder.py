"""Build a responsible report draft from an evidence package.

The draft never auto-submits, never claims final severity, and never includes
live-chain exploitation instructions.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.proof.payloads import target_slug
from arkheionx.version import __version__

from .model import ReportDraft

_SAFETY_NOTICE = (
    "Local defensive security research only. Not a formal audit and not a "
    "severity guarantee. Do not submit automatically; review manually first."
)


def _impact_reasoning(evidence: dict) -> str:
    level = evidence["evidence_level"]
    proof = evidence["proof_summary"]
    impact = evidence["impact_notes"]["candidate_impact"]
    if proof.get("failed", 0) > 0:
        observed = "Observed a failing local test. Human review is required to determine whether this represents a valid vulnerability."
    elif proof.get("passed", 0) > 0:
        observed = "Observed a passing local test. This does not prove absence of bugs."
    else:
        observed = "No relevant local test executed for this target yet."
    return (
        f"Candidate impact (review surface): {impact}. "
        f"{observed} Evidence level: {level}. This is not a final severity claim."
    )


def _reproduction_steps(evidence: dict) -> list[str]:
    cmd = evidence["proof_summary"].get("foundry_command", "")
    steps = [
        "Clone/checkout the authorized local repository.",
        "Run `forge build` to confirm the project compiles.",
    ]
    if cmd:
        steps.append(f"Run the targeted local test: `{cmd}` (local only; no network).")
    steps.append("Inspect the generated proof/trace artifacts listed below.")
    steps.append("Local-only reproduction; no live-chain, no broadcast, no private keys.")
    return steps


def _what_is_proven(evidence: dict) -> list[str]:
    level = evidence.get("evidence_level", "HEURISTIC")
    proof = evidence.get("proof_summary", {})
    items: list[str] = []
    if level in {"EXECUTION_CONFIRMED", "EVIDENCE_READY"}:
        items.append(
            f"A relevant local Foundry test executed "
            f"({proof.get('passed', 0)} passed, {proof.get('failed', 0)} failed)."
        )
    if level in {"COMPILER_CONFIRMED", "EXECUTION_CONFIRMED", "EVIDENCE_READY"}:
        items.append("`forge build` compiled the target locally.")
    if not items:
        items.append("Static heuristic classification only; nothing is execution-confirmed.")
    return items


def _readiness(level: str) -> str:
    return {
        "EVIDENCE_READY": "evidence_ready",
        "EXECUTION_CONFIRMED": "execution_confirmed",
        "COMPILER_CONFIRMED": "compiler_confirmed",
    }.get(level, "heuristic")


def _manifest_source(evidence: dict, kind: str) -> dict:
    sources = ((evidence.get("manifest", {}) or {}).get("sources", []) or [])
    return next(
        (source for source in sources if isinstance(source, dict) and source.get("kind") == kind),
        {},
    )


def _manifest_checks(evidence: dict) -> dict:
    return dict(((evidence.get("manifest", {}) or {}).get("checks", {}) or {}))


def _evidence_context(evidence: dict, evidence_source_path: str, report_json_path: str) -> dict:
    src = evidence.get("source_artifacts", {}) or {}
    manifest = evidence.get("manifest", {}) or {}
    level = evidence.get("evidence_level", "HEURISTIC")
    return {
        "evidence_package_id": evidence.get("evidence_package_id", ""),
        "evidence_level": level,
        "readiness": manifest.get("readiness") or _readiness(level),
        "review_status": "NEEDS_HUMAN_REVIEW",
        "human_review_required": True,
        "source_artifacts": {
            "evidence_json": evidence_source_path,
            "proof_json": src.get("proof_json", ""),
            "trace_json": src.get("trace_json", ""),
            "report_json": report_json_path,
        },
        "manifest_checks": {
            "proof_linked": bool(_manifest_checks(evidence).get("proof_linked", bool(src.get("proof_json", "")))),
            "trace_linked": bool(_manifest_checks(evidence).get("trace_linked", bool(src.get("trace_json", "")))),
            "trace_required_for_evidence_ready": bool(
                _manifest_checks(evidence).get("trace_required_for_evidence_ready", True)
            ),
            "source_paths_recorded": bool(_manifest_checks(evidence).get("source_paths_recorded", bool(src))),
            "human_review_required": bool(_manifest_checks(evidence).get("human_review_required", True)),
        },
    }


def _receipt_references(evidence: dict, evidence_source_path: str) -> dict:
    proof_source = _manifest_source(evidence, "proof")
    trace_source = _manifest_source(evidence, "trace")
    src = evidence.get("source_artifacts", {}) or {}
    return {
        "proof_receipt_id": proof_source.get("receipt_id", ""),
        "trace_receipt_id": trace_source.get("receipt_id", ""),
        "evidence_package_id": evidence.get("evidence_package_id", ""),
        "proof_source": proof_source.get("path") or src.get("proof_json", ""),
        "trace_source": trace_source.get("path") or src.get("trace_json", ""),
        "evidence_source": evidence_source_path,
    }


def _report_readiness(evidence: dict) -> dict:
    level = evidence.get("evidence_level", "HEURISTIC")
    checks = _manifest_checks(evidence)
    src = evidence.get("source_artifacts", {}) or {}
    trace_linked = bool(checks.get("trace_linked", bool(src.get("trace_json", ""))))
    evidence_ready = level == "EVIDENCE_READY" and trace_linked
    missing: list[str] = []
    warnings: list[str] = []
    if not evidence_ready:
        missing.append("EVIDENCE_READY evidence package")
        warnings.append(f"Evidence level is {level}; keep this draft in manual review.")
    if level in {"EXECUTION_CONFIRMED", "EVIDENCE_READY"} and not trace_linked:
        missing.append("linked trace artifact")
        warnings.append("Trace is missing or not linked; do not treat this report as evidence-ready.")
    return {
        "status": "draft",
        "ready_for_human_review": True,
        "ready_for_submission": False,
        "requires_manual_review": True,
        "evidence_ready": evidence_ready,
        "missing_items": missing,
        "warnings": warnings,
    }


def _claim_references(evidence: dict, receipts: dict, readiness: dict) -> list[dict]:
    supported_by = [
        key
        for key in ("proof_receipt_id", "trace_receipt_id", "evidence_package_id")
        if receipts.get(key)
    ]
    if readiness["evidence_ready"]:
        claim = "Local proof and trace evidence are linked for this target."
        limitations = [
            "Does not prove exploitability.",
            "Does not assign final severity.",
            "Requires manual review before any submission decision.",
        ]
    else:
        claim = "Local evidence exists for this target, but evidence readiness is incomplete."
        limitations = [
            "Missing or lower-level evidence must be resolved manually.",
            "Does not prove exploitability.",
            "Does not assign final severity.",
        ]
    return [
        {
            "claim_id": "claim:local-evidence-linked",
            "claim": claim,
            "supported_by": supported_by,
            "status": "needs_human_review",
            "limitations": limitations,
        }
    ]


_LV_REPORT_NOTE = (
    "Local validation support observed: passing local tests were recorded as supporting "
    "context; failing local tests require manual review. This does not finalize any security "
    "conclusion; manual review is required and the draft is not ready for submission."
)


def _local_validation_report_support(evidence: dict) -> dict | None:
    """Summarize local-validation support from an evidence package, if present.

    Supporting context only: it never promotes a finding, assigns severity, marks
    a report ready, or emits a human-reviewed status.
    """

    support = evidence.get("local_validation_support")
    if not isinstance(support, dict):
        return None
    return {
        "observed": True,
        "tested_support": int(support.get("tested_count", 0) or 0),
        "trace_bound_support": int(support.get("trace_bound_count", 0) or 0),
        "tests_needing_review": int(support.get("needs_review_count", 0) or 0),
        "summary_id": str(support.get("summary_id", "")),
        "note": _LV_REPORT_NOTE,
        "manual_review_required": True,
        "ready_for_submission": False,
    }


def _protocol_graph_report_context(evidence: dict) -> dict | None:
    """Summarize an evidence ``protocol_graph_context`` block into a report
    context block (supporting review context only).

    The report stays a draft requiring manual review: this introduces no finding,
    no severity, and no claim. A graph warning is reviewer orientation only and
    never a confirmed vulnerability; ``ready_for_submission`` stays false.
    """

    ctx = evidence.get("protocol_graph_context")
    if not isinstance(ctx, dict):
        return None
    return {
        "observed": True,
        "graph_id": str(ctx.get("graph_id", "")),
        "function_role_count": int(ctx.get("function_role_count", 0) or 0),
        "value_path_count": int(ctx.get("value_path_count", 0) or 0),
        "assumption_count": int(ctx.get("assumption_count", 0) or 0),
        "test_gap_count": int(ctx.get("test_gap_count", 0) or 0),
        "coverage_count": int(ctx.get("coverage_count", 0) or 0),
        "tested_count": int(ctx.get("tested_count", 0) or 0),
        "trace_bound_count": int(ctx.get("trace_bound_count", 0) or 0),
        "warning_count": int(ctx.get("warning_count", 0) or 0),
        "review_note": (
            "Protocol graph context (function roles, value paths, assumptions, and test gaps) "
            "is included for reviewer orientation as supporting context only; it does not finalize "
            "any security conclusion. Manual review is required."
        ),
        "manual_review_required": True,
        "ready_for_submission": False,
    }


def build_report(
    evidence: dict,
    root: Path,
    writer: ArtifactWriter,
    write: bool = True,
    evidence_source_path: str = "",
) -> ReportDraft:
    target = evidence["target"]
    display = evidence.get("target_id", target).split(":")[-1].split("#")[0].split("(")[0]
    slug = target_slug(display)
    level = evidence["evidence_level"]
    title = f"Arkheionx review draft: {display}"
    report_json_path = str(writer.path_for(f"reports/{slug}/report.json"))
    evidence_context = _evidence_context(evidence, evidence_source_path, report_json_path)
    receipt_references = _receipt_references(evidence, evidence_source_path)
    report_readiness = _report_readiness(evidence)
    claim_references = _claim_references(evidence, receipt_references, report_readiness)
    local_validation_support = _local_validation_report_support(evidence)

    payload = {
        "schema_version": "1.0.0",
        "arkheionx_version": __version__,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "target": target,
        "title": title,
        "evidence_level": level,
        "status": "draft-created",
        "summary": (
            f"Local workbench review of {display}. "
            f"{evidence['impact_notes']['candidate_impact']} (candidate, requires human validation)."
        ),
        "affected_components": evidence["impact_notes"]["affected_components"],
        "proof": evidence["source_artifacts"],
        "trace_summary": evidence["trace_summary"],
        "impact_reasoning": _impact_reasoning(evidence),
        "review_status": "NEEDS_HUMAN_REVIEW",
        "what_is_proven": _what_is_proven(evidence),
        "what_is_not_proven": [
            "exploitability",
            "final severity",
            "absence of other bugs",
            "live-chain impact",
            "bounty eligibility",
        ],
        "required_human_checks": [
            "validate the target context",
            "review the trace manually",
            "confirm the affected components",
            "add project-specific impact analysis",
            "decide if this is reportable",
        ],
        "assumptions": evidence["impact_notes"]["assumptions"],
        "limitations": evidence["impact_notes"]["limitations"],
        "reproduction_steps": _reproduction_steps(evidence),
        "recommended_next_steps": [
            "Manually review the proof and trace before any submission.",
            "Confirm the tested property reflects a real protocol invariant.",
            "Add or refine tests to strengthen the evidence.",
        ],
        "safety_notice": _SAFETY_NOTICE,
        "artifact_paths": {
            "evidence_json": evidence_source_path,
            "proof_json": evidence["source_artifacts"].get("proof_json", ""),
            "trace_json": evidence["source_artifacts"].get("trace_json", ""),
            "report_json": report_json_path,
        },
        "evidence_context": evidence_context,
        "receipt_references": receipt_references,
        "report_readiness": report_readiness,
        "claim_references": claim_references,
    }
    if local_validation_support is not None:
        payload["local_validation_support"] = local_validation_support
    protocol_graph_context = _protocol_graph_report_context(evidence)
    if protocol_graph_context is not None:
        payload["protocol_graph_context"] = protocol_graph_context

    draft = ReportDraft(
        target=target,
        title=title,
        evidence_level=level,
        proof_path=payload["artifact_paths"]["proof_json"],
        trace_path=payload["artifact_paths"]["trace_json"],
        next_command="Review the draft manually before submission.",
        payload=payload,
    )
    if write:
        draft.json_path = str(writer.write_text(f"reports/{slug}/report.json", json.dumps(payload, indent=2)))
        payload["artifact_paths"]["report_json"] = draft.json_path
        payload["evidence_context"]["source_artifacts"]["report_json"] = draft.json_path
        draft.md_path = str(writer.write_text(f"reports/{slug}/report.md", report_markdown(payload)))
    return draft


def report_markdown(p: dict) -> str:
    md = [
        f"# {p['title']}",
        "",
        "## Review Status",
        "",
        p.get("review_status", "NEEDS_HUMAN_REVIEW"),
        "",
        "## Summary",
        "",
        p["summary"],
        "",
        "## Evidence Level",
        "",
        p["evidence_level"],
        "",
        "## What Is Proven",
        "",
    ]
    md += [f"- {x}" for x in p.get("what_is_proven", [])]
    md += ["", "## What Is Not Proven", ""]
    md += [f"- {x}" for x in p.get("what_is_not_proven", [])]
    md += ["", "## Required Human Checks", ""]
    md += [f"- {x}" for x in p.get("required_human_checks", [])]
    md += ["", "## Affected Components", ""]
    md += [f"- {c}" for c in p["affected_components"]] or ["- (none recorded)"]
    md += ["", "## Proof Artifacts", ""]
    md += [f"- {k}: `{v}`" for k, v in p["proof"].items() if v] or ["- (none)"]
    md += ["", "## Reproduction", ""]
    md += [f"{i}. {s}" for i, s in enumerate(p["reproduction_steps"], 1)]
    md += ["", "## Trace Summary", ""]
    ts = p["trace_summary"]
    md.append(f"- Reverts: {len(ts.get('reverts', []))}")
    md.append(f"- Assertion failures: {len(ts.get('assertion_failures', []))}")
    md.append(f"- Call lines summarized: {len(ts.get('call_sequence', []))}")
    ctx = p.get("evidence_context", {}) or {}
    receipts = p.get("receipt_references", {}) or {}
    readiness = p.get("report_readiness", {}) or {}
    md += ["", "## Evidence Context", ""]
    md.append(f"- Evidence package: `{ctx.get('evidence_package_id', '') or 'n/a'}`")
    md.append(f"- Evidence readiness: {ctx.get('readiness', 'unknown')}")
    md.append(f"- Manual review required: {ctx.get('human_review_required', True)}")
    md += ["", "## Receipt References", ""]
    md.append(f"- Proof receipt: `{receipts.get('proof_receipt_id', '') or 'n/a'}`")
    md.append(f"- Trace receipt: `{receipts.get('trace_receipt_id', '') or 'n/a'}`")
    md.append(f"- Evidence source: `{receipts.get('evidence_source', '') or 'n/a'}`")
    md += ["", "## Report Readiness", ""]
    md.append(f"- Status: {readiness.get('status', 'draft')}")
    md.append(f"- Requires manual review: {readiness.get('requires_manual_review', True)}")
    md.append(f"- Ready for submission: {readiness.get('ready_for_submission', False)}")
    for warning in readiness.get("warnings", []):
        md.append(f"- Warning: {warning}")
    if p.get("claim_references"):
        md += ["", "## Claim References", ""]
        for claim in p["claim_references"]:
            md.append(f"- `{claim.get('claim_id', '')}`: {claim.get('claim', '')} ({claim.get('status', '')})")
    md += ["", "## Impact Reasoning", "", p["impact_reasoning"], "", "## Assumptions", ""]
    md += [f"- {a}" for a in p["assumptions"]]
    md += ["", "## Limitations", ""]
    md += [f"- {l}" for l in p["limitations"]]
    md += ["", "## Suggested Next Steps", ""]
    md += [f"- {s}" for s in p["recommended_next_steps"]]
    if p.get("local_validation_support"):
        lvs = p["local_validation_support"]
        md += [
            "", "## Local Validation Context", "",
            f"- Tested support: {lvs.get('tested_support', 0)}",
            f"- Trace-bound support: {lvs.get('trace_bound_support', 0)}",
            f"- Local tests needing manual review: {lvs.get('tests_needing_review', 0)}",
            f"- Manual review required: {lvs.get('manual_review_required', True)}",
            f"- Ready for submission: {lvs.get('ready_for_submission', False)}",
            f"- {lvs.get('note', '')}",
        ]
    md += ["", "## Safety Notice", "", p["safety_notice"], ""]
    return "\n".join(md) + "\n"
