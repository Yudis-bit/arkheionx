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


def build_report(evidence: dict, root: Path, writer: ArtifactWriter, write: bool = True) -> ReportDraft:
    target = evidence["target"]
    display = evidence.get("target_id", target).split(":")[-1].split("#")[0].split("(")[0]
    slug = target_slug(display)
    level = evidence["evidence_level"]
    title = f"Arkheionx review draft: {display}"

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
            "proof_json": evidence["source_artifacts"].get("proof_json", ""),
            "trace_json": evidence["source_artifacts"].get("trace_json", ""),
        },
    }

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
    md += ["", "## Impact Reasoning", "", p["impact_reasoning"], "", "## Assumptions", ""]
    md += [f"- {a}" for a in p["assumptions"]]
    md += ["", "## Limitations", ""]
    md += [f"- {l}" for l in p["limitations"]]
    md += ["", "## Suggested Next Steps", ""]
    md += [f"- {s}" for s in p["recommended_next_steps"]]
    md += ["", "## Safety Notice", "", p["safety_notice"], ""]
    return "\n".join(md) + "\n"
