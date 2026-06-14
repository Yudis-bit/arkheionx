"""Renderers for the state-transition artifacts (06 of the war-run)."""
from __future__ import annotations


def transitions_json(tmap) -> dict:
    return tmap.to_dict()


def transitions_md(tmap) -> str:
    lines = [
        "# 06 State Transitions",
        "",
        f"Reconstructed {len(tmap.transitions)} value-affecting transitions",
        "(before / action / after). Heuristic; review context, not a finding.",
        "",
    ]
    for t in tmap.transitions:
        lines += [
            f"## {t.id} {t.function} ({t.lifecycle})",
            "",
            f"- Actor: {t.actor}",
            f"- Before: {t.before_summary}",
            f"- After: {t.after_summary}",
        ]
        if t.external_calls:
            lines.append(f"- External calls: {', '.join(t.external_calls)}")
        if t.flags:
            lines.append(f"- Flags: {', '.join(t.flags)}")
        if t.possible_invariants:
            lines.append(f"- Possible invariants: {', '.join(t.possible_invariants)}")
        lines.append("")
    return "\n".join(lines) + "\n"
