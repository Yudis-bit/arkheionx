"""Compact rendering for the evidence command."""
from __future__ import annotations

from .model import EvidencePackage


def _mode(level: str) -> str:
    return {
        "EVIDENCE_READY": "evidence-ready",
        "EXECUTION_CONFIRMED": "execution-confirmed",
        "COMPILER_CONFIRMED": "compiler-confirmed",
    }.get(level, "heuristic")


def render_evidence(pkg: EvidencePackage, project: str) -> str:
    if pkg.status == "no_proof":
        return (
            "ARKHEIONX EVIDENCE\n"
            f"Project: {project}\n"
            f"Target: {pkg.target}\n"
            "Status: no-proof\n"
            "Mode: heuristic\n\n"
            "No proof artifact found.\n\n"
            "Next\n"
            f"  {pkg.next_command}\n"
        )
    out = [
        "ARKHEIONX EVIDENCE",
        f"Project: {project}",
        f"Target: {pkg.target}",
        "Status: ready" if pkg.evidence_level == "EVIDENCE_READY" else f"Status: {pkg.status}",
        f"Mode: {_mode(pkg.evidence_level)}",
        "",
        "Evidence",
        f"  Proof: {'found' if pkg.proof_found else 'missing'}",
        f"  Trace: {'found' if pkg.trace_found else 'missing'}",
        f"  Tests: {pkg.tests_run} run, {pkg.passed} passed, {pkg.failed} failed, {pkg.skipped} skipped",
        f"  Evidence level: {pkg.evidence_level}",
        "",
        "Package",
        f"  JSON: {pkg.json_path}",
        f"  Text: {pkg.text_path}",
        "",
        "Limits",
        "  Severity is not final. Human review required.",
        "",
        "Next",
        f"  {pkg.next_command}",
    ]
    return "\n".join(out) + "\n"


def evidence_text(payload: dict) -> str:
    p = payload["proof_summary"]
    lines = [
        f"Arkheionx Evidence: {payload['target']}",
        f"Evidence level: {payload['evidence_level']}  (status: {payload['status']})",
        f"Generated: {payload['generated_at']}",
        "",
        f"Proof status: {p['status']}",
        f"Tests: {p['tests_run']} run, {p['passed']} passed, {p['failed']} failed, {p['skipped']} skipped",
        f"Foundry command: {p['foundry_command']}",
        "",
        "Candidate impact: " + payload["impact_notes"]["candidate_impact"],
        "Affected: " + ", ".join(payload["impact_notes"]["affected_components"]),
        "",
        "Limitations:",
    ]
    lines += [f"- {x}" for x in payload["impact_notes"]["limitations"]]
    lines += ["", "Source artifacts:"]
    lines += [f"- {k}: {v}" for k, v in payload["source_artifacts"].items() if v]
    return "\n".join(lines) + "\n"
