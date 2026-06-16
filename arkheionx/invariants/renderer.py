"""Renderers for the invariant artifacts (07/08 — headline outputs)."""
from __future__ import annotations

from . import classifier


def invariants_json(invset) -> dict:
    payload = invset.to_dict()
    payload["classification"] = classifier.classify(invset)
    return payload


def invariants_md(invset) -> str:
    summary = classifier.classify(invset)
    lines = [
        "# 07 Invariants",
        "",
        f"Generated {summary['total']} candidate invariants; "
        f"{summary['suspicious']} look suspicious on this code.",
        "",
        "An invariant is an actionable, falsifiable economic property. A *suspicious*",
        "invariant is a breakage hypothesis with reasons — it is review context and a",
        "PoC target, never a confirmed finding.",
        "",
    ]
    susp = [i for i in classifier.ordered(invset) if i.suspicious]
    rest = [i for i in classifier.ordered(invset) if not i.suspicious]

    if susp:
        lines.append("## Suspicious here (PoC targets)")
        lines.append("")
        for inv in susp:
            lines += _render_one(inv)
    if rest:
        lines.append("## Other invariants to hold the line on")
        lines.append("")
        for inv in rest:
            lines.append(f"- **{inv.id} {inv.family}** ({inv.testability}) — {inv.description}")
        lines.append("")
    return "\n".join(lines) + "\n"


def _render_one(inv) -> list:
    out = [
        f"### {inv.id} — {inv.title}  `[{inv.family}]`",
        "",
        inv.description,
        "",
        f"- Assertion: `{inv.assertion_form}`",
        f"- Attacker: {inv.attacker_capability}",
        f"- Victim: {inv.victim}",
        f"- Asset: {inv.asset}",
        f"- Functions: {', '.join(inv.related_functions)}",
        f"- Testability: {inv.testability}",
        f"- Severity hint (pre-gate): {inv.severity_hint}",
        f"- Confidence: {inv.confidence}",
    ]
    if inv.suspicion_reasons:
        out.append("- Why suspicious here:")
        out += [f"  - {r}" for r in inv.suspicion_reasons]
    out += [f"- Why it matters: {inv.why_it_matters}", ""]
    return out
