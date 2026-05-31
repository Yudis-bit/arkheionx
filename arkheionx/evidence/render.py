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


def render_status(payload: dict, project: str) -> str:
    if payload["status"] == "no-artifacts":
        return (
            "ARKHEIONX EVIDENCE STATUS\n"
            f"Project: {project}\n"
            "Status: no-artifacts\n\n"
            "No proof/evidence/report artifacts found.\n\n"
            "Next\n"
            f"  {payload['next_command']}\n"
        )
    c = payload["counts"]
    out = [
        "ARKHEIONX EVIDENCE STATUS",
        f"Project: {project}",
        f"Status: {payload['status']}",
        "Mode: local",
        "",
        "Targets",
        f"  {c['proof']} proof, {c['trace']} trace, {c['evidence']} evidence, {c['report']} report",
        "",
    ]
    if payload["ready"]:
        out.append("Ready")
        for r in payload["ready"]:
            out.append(f"  {_short(r['target'])}  {r['review_status']}  ({r['evidence_level']})")
        out.append("")
    if payload["needs_work"]:
        out.append("Needs work")
        for r in payload["needs_work"]:
            flags = "".join(k[0].upper() if r[k] else "-" for k in ("proof", "trace", "evidence", "report"))
            out.append(f"  {_short(r['target'])}  {r['review_status']}  [{flags}]")
            if r["malformed"]:
                out.append(f"    invalid: {', '.join(r['malformed'])}")
            out.append(f"    next: {r['next']}")
        out.append("")
    out.append("Artifacts")
    out.append(f"  Root: {payload['artifacts_root']}")
    out.append("")
    out.append("Next")
    out.append(f"  {payload['next_command']}")
    return "\n".join(out) + "\n"


def render_validate(counts: dict, issues: list[str], project: str) -> str:
    out = [
        "ARKHEIONX VALIDATE ARTIFACTS",
        f"Project: {project}",
        f"Status: {'warning' if issues else 'ok'}",
        "",
        "Checked",
    ]
    for name in ("proof.json", "trace.json", "evidence.json", "report.json"):
        out.append(f"  {name}: {counts.get(name, 0)}")
    out.append("")
    out.append("Issues")
    if issues:
        for i in issues:
            out.append(f"  - {i}")
    else:
        out.append("  none")
    out.append("")
    out.append("Next")
    if issues:
        out.append("  Regenerate the affected artifacts (prove --run / trace / evidence / report).")
    else:
        out.append("  Review the drafts manually before any submission.")
    return "\n".join(out) + "\n"


def _short(target: str) -> str:
    return target.split(":")[-1].split("#")[0]
