"""Compact-first rendering for `arkheionx hunt`."""
from __future__ import annotations

from arkheionx.protocol.detector import Analysis
from arkheionx.protocol.render import header, hidden_block


def render_hunt(analysis: Analysis, project: str, top: int, artifacts: dict[str, str], full: bool = False) -> str:
    targets = analysis.hunter_targets
    out = header("hunt", project, analysis)
    total = len(analysis.functions)
    shown = min(top, len(targets))
    out.append(f"{len(targets)} review targets found. Showing top {shown}." if targets else "No review targets in production code.")
    out.append("")
    for t in targets[:top]:
        display = t.target_id.split("#", 1)[0]
        out.append(f"{t.rank}. {display}")
        out.append(f"   Score: {t.score} {t.priority}")
        if t.why_it_matters:
            out.append(f"   Why: {', '.join(t.why_it_matters[:3])}")
        if t.bug_classes:
            out.append(f"   Bugs: {', '.join(bc.replace(' (candidate)', ' candidate') for bc in t.bug_classes)}")
        out.append(f"   Evidence: {t.evidence_level}")
        out.append(f"   Next: {t.next_command.replace('arkheionx prove . ', f'arkheionx prove {project} ')}")
        out.append("")

    hidden = hidden_block(analysis.hidden_counts)
    if hidden and not full:
        out.append("Hidden:")
        for line in hidden:
            out.append(f"  {line}")
        out.append("Use --show-all to include hidden items.")
        out.append("")
    if analysis.snapshot.evidence_level == "HEURISTIC":
        out.append("Upgrade")
        out.append(f"arkheionx hunt {project} --build")
        out.append("")
    if artifacts:
        out.append("Artifacts")
        for name, path in artifacts.items():
            out.append(f"{name}: {path}")
        out.append("")
    out.append("Limits")
    out.append("- Targets are review candidates, not proven bugs. Use `arkheionx prove` to test.")
    return "\n".join(out) + "\n"
