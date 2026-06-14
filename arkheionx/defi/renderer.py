"""Renderers for the DeFi entity artifacts (05 of the war-run)."""
from __future__ import annotations


def entities_json(emap) -> dict:
    return emap.to_dict()


def entities_md(emap) -> str:
    lines = [
        "# 05 DeFi Entities",
        "",
        f"Detected {len(emap.entities)} economic entities. Detection is name/shape",
        "driven and heuristic; this is review context, not a finding.",
        "",
        "| Entity | Direction | Confidence | Contracts | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for e in emap.entities:
        ev = ", ".join(e.evidence_lines[:3])
        if len(e.evidence_lines) > 3:
            ev += f" (+{len(e.evidence_lines) - 3})"
        lines.append(f"| {e.entity_type} | {e.value_direction} | {e.confidence} | "
                     f"{', '.join(e.related_contracts)} | {ev} |")
    return "\n".join(lines) + "\n"
