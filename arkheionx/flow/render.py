"""Compact-first rendering for `arkheionx flow`."""
from __future__ import annotations

from arkheionx.protocol.detector import Analysis
from arkheionx.protocol.render import header, hidden_block

_MAX_TOP_PATHS = 6


def _short(fid: str) -> str:
    return fid.split("#", 1)[0]


def _disp(analysis: Analysis, fid: str) -> str:
    for fr in analysis.functions:
        if fr.function_id == fid:
            return fr.display_id
    return _short(fid)


def render_flow(analysis: Analysis, project: str, artifacts: dict[str, str], full: bool = False) -> str:
    flow = analysis.money_flow
    out = header("flow", project, analysis)
    out.append("Money Flow Summary")
    out.append(f"Entry points:        {len(flow.entrypoints)}")
    out.append(f"Exit points:         {len(flow.exits)}")
    out.append(f"Value holders:       {len(flow.value_holders)}")
    out.append(f"Privileged movers:   {len(flow.privileged_movers)}")
    out.append(f"Oracle dependencies: {len(flow.pricing_dependencies)}")
    out.append(f"Edges:               {len(flow.edges)}")
    out.append("")

    limit = len(flow.edges) if full else _MAX_TOP_PATHS
    out.append("Top Paths")
    for edge in flow.edges[:limit]:
        out.append(f"{_disp(analysis, edge.source)} -> {_disp(analysis, edge.target)}  [{edge.kind}/{edge.confidence}]")
    if not flow.edges:
        out.append("(no value-flow edges detected)")
    out.append("")

    if artifacts:
        out.append("Artifacts")
        for name, path in artifacts.items():
            out.append(f"{name}: {path}")
        out.append("")
    hidden = hidden_block(analysis.hidden_counts)
    if hidden and not full:
        out.append("Hidden: " + ", ".join(hidden) + " (use --show-all)")
        out.append("")
    out.append("Next")
    out.append(f"arkheionx hunt {project} --top 5")
    if not full:
        out.append("Use --full to print all edges. Use --mermaid for the graph.")
    return "\n".join(out) + "\n"
