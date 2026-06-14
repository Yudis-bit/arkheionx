"""Renderers for the economic severity artifacts (13)."""
from __future__ import annotations


def severity_json(verdicts) -> dict:
    return {
        "schema_version": "v10-economic-severity",
        "verdict_count": len(verdicts),
        "verdicts": [v.to_dict() for v in verdicts],
    }


def severity_md(verdicts) -> str:
    lines = [
        "# 13 Economic Severity",
        "",
        "Whether each technically valid candidate is bounty-worth. Conservative by",
        "design: dust, trusted-role, and unproven-buffer candidates are capped or",
        "killed. This is review context; a human makes the final call.",
        "",
    ]
    for v in verdicts:
        lines += [
            f"## {v.candidate_id} — {v.label}",
            f"- Impact: {v.impact}",
            f"- Likelihood: {v.likelihood}",
            f"- Cap: {v.cap}",
            f"- Repeatability: {v.repeatability}",
            f"- Gas/profit: {v.gas}",
            f"- Realism: {v.realism}",
        ]
        if v.reasons:
            lines.append("- Reasoning:")
            lines += [f"  - {r}" for r in v.reasons]
        lines.append("")
    return "\n".join(lines) + "\n"
