"""Render authorization analysis artifacts."""
from __future__ import annotations


def auth_json(analysis) -> dict:
    return analysis.to_dict()


def auth_md(analysis) -> str:
    lines = [
        "# Authorization and Signature Analysis",
        "",
        f"- Active: {'yes' if analysis.active else 'no'}",
        f"- Activation signals detected: {'yes' if analysis.activation_signals else 'no'}",
        f"- Signed operations: {len(analysis.signed_operations)}",
        f"- Authorization candidates: {len(analysis.candidates)}",
    ]
    if analysis.activation_signals:
        lines.append(f"- Activation signals: {', '.join(analysis.activation_signals)}")
    if analysis.warnings:
        lines += ["", "## Warnings"] + [f"- {warning}" for warning in analysis.warnings]
    lines += [
        "",
        "| Family | Contract | Function | Severity hint | Key reuse only |",
        "| --- | --- | --- | --- | --- |",
    ]
    for candidate in analysis.candidates:
        lines.append(
            f"| {candidate.family} | {candidate.contract} | {candidate.function} | "
            f"{candidate.severity_hint} | {'yes' if candidate.requires_key_reuse else 'no'} |"
        )
    if not analysis.candidates:
        lines.append("| - | - | - | - | - |")
    return "\n".join(lines) + "\n"
