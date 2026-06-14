"""Renderers for the state-transition artifacts (06 of the war-run)."""
from __future__ import annotations


def transitions_json(tmap) -> dict:
    return tmap.to_dict()


def contradictions_json(cset) -> dict:
    return cset.to_dict()


def contradictions_md(cset) -> str:
    lines = [
        "# 16 State-Machine Contradictions",
        "",
        f"Reconstructed {len(cset.contradictions)} lifecycle contradiction(s): states that",
        "cannot consistently hold together (e.g. Repaid while lenders unsettled, deposit",
        "consumed yet withdrawable). Heuristic; review context, not a finding.",
        "",
    ]
    if not cset.contradictions:
        lines.append("_No state-machine contradictions detected on this target._")
        return "\n".join(lines) + "\n"
    for c in cset.contradictions:
        lines += [
            f"## {c.id} {c.family}",
            f"- Transition: `{c.transition}` ({c.contract})",
            f"- Likely invariant: {c.likely_invariant}",
            f"- PoC family: {c.poc_family}",
            f"- Severity hint: {c.severity_hint}",
        ]
        if c.evidence:
            lines.append(f"- Evidence: {'; '.join(c.evidence)}")
        lines.append(f"- Note: {c.warning}")
        lines.append("")
    return "\n".join(lines) + "\n"


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
