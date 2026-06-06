"""Compact terminal rendering for `arkheionx trace`."""
from __future__ import annotations

from arkheionx.protocol.render import _MODE


def _mode(evidence: str) -> str:
    return _MODE.get(evidence, "heuristic")


def render_trace(target_display: str, project: str, status: str, evidence: str, foundry: str, trace: dict, artifacts: dict[str, str], next_command: str) -> str:
    out = [
        "ARKHEIONX TRACE",
        f"Project: {project}",
        f"Target: {target_display}",
        f"Status: {'ok' if evidence == 'EXECUTION_CONFIRMED' else 'warning'}",
        f"Mode: {_mode(evidence)}",
        f"Foundry: {foundry}",
        "",
    ]
    if not trace:
        out.append("No proof artifact found.")
        out.append("")
        out.append("Next")
        out.append(f"  {next_command}")
        return "\n".join(out) + "\n"

    out.append("Result")
    out.append(f"  Tests: {trace.get('tests_run', 0)} run, {trace.get('passed', 0)} passed, {trace.get('failed', 0)} failed, {trace.get('skipped', 0)} skipped")
    out.append(f"  Reverts: {len(trace.get('reverts', []))}")
    out.append(f"  Trace lines summarized: {len(trace.get('call_sequence', []))}")
    out.append("")
    out.append("Trace")
    for line in trace.get("call_sequence", [])[:8]:
        out.append(f"  - {line}")
    for fail in trace.get("assertion_failures", [])[:3]:
        out.append(f"  - {fail}")
    if not trace.get("call_sequence") and not trace.get("assertion_failures"):
        out.append("  (no call lines parsed; see raw artifact)")
    out.append("")
    if artifacts:
        out.append("Artifacts")
        for name, path in artifacts.items():
            out.append(f"  {name}: {path}")
        out.append("")
    out.append("Limits")
    for lim in trace.get("limitations", [])[:3]:
        out.append(f"  - {lim}")
    out.append("")
    out.append("Next")
    out.append(f"  {next_command}")
    return "\n".join(out) + "\n"
