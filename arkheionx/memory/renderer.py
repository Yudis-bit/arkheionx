"""Renderer for the dedup/scope risk artifact (14)."""
from __future__ import annotations


def dedup_scope_md(graph) -> str:
    lines = [
        "# 14 Dedup / Scope Risk",
        "",
        "Semantic root-cause dedup (family + function role + attacker category) and",
        "scope risk. UNKNOWN means no memory corpus was provided, so 'not a duplicate'",
        "is unverified.",
        "",
        "| Candidate | Family | Root-cause hash | Duplicate risk | Scope risk |",
        "| --- | --- | --- | --- | --- |",
    ]
    for c in graph.candidates:
        lines.append(f"| {c.id} | {c.invariant_family} | `{c.root_cause_hash}` | "
                     f"{c.duplicate_risk} | {c.scope_risk} |")
    return "\n".join(lines) + "\n"
