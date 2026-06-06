"""Foundry-style compact rendering for the workbench output standard.

Terminal output is compact by default; `--full` adds tables; `--json` emits a
deterministic machine-readable document. Markdown is not the primary product.
"""
from __future__ import annotations

from arkheionx.protocol.model import to_dict
from arkheionx.version import __version__

from . import foundry as foundry_mod
from .detector import Analysis
from .source_kind import category_label

_MODE = {
    "HEURISTIC": "heuristic",
    "COMPILER_CONFIRMED": "compiler-confirmed",
    "EXECUTION_CONFIRMED": "execution-confirmed",
    "REPORT_READY": "report-ready",
}


def mode_header(evidence_level: str) -> str:
    return _MODE.get(evidence_level, "heuristic")


def foundry_header(status) -> str:
    s = status.status
    if s == foundry_mod.BUILD_PASSED:
        return "build-passed"
    if s == foundry_mod.BUILD_FAILED:
        return "build-failed"
    if s == foundry_mod.AVAILABLE_NOT_BUILT:
        return "ready"
    if status.has_foundry_toml:
        return "missing"  # foundry.toml present, forge not installed
    return "not-a-foundry-project"


def status_for(analysis: Analysis) -> str:
    if not analysis.contracts:
        return "warning"
    if analysis.snapshot.evidence_level == "HEURISTIC":
        return "warning"
    return "ok"


def header(command: str, project: str, analysis: Analysis, status: str | None = None) -> list[str]:
    return [
        f"ARKHEIONX {command.upper()}",
        f"Project: {project}",
        f"Status: {status or status_for(analysis)}",
        f"Mode: {mode_header(analysis.snapshot.evidence_level)}",
        f"Foundry: {foundry_header(analysis.foundry)}",
        "",
    ]


def hidden_block(hidden_counts: dict[str, int]) -> list[str]:
    lines = []
    for category in ("interfaces", "tests_invariants", "mocks_fixtures", "archive", "scripts", "generated"):
        count = hidden_counts.get(category, 0)
        if count:
            lines.append(f"{count} {category_label(category)}")
    return lines


def _disp(fid: str) -> str:
    return fid.split("#", 1)[0]


def _short_fn(display_id: str) -> str:
    return display_id.split(".")[-1]


def render_map(analysis: Analysis, project: str, artifacts: dict[str, str], full: bool = False) -> str:
    snap = analysis.snapshot
    flow = analysis.money_flow
    out = header("map", project, analysis)

    out.append("Protocol")
    out.append(f"Type: {' + '.join(snap.protocol_types)}")
    out.append(f"Active contracts: {snap.contracts_analyzed}")
    out.append(f"Hidden support files: {sum(analysis.hidden_counts.values())}")
    out.append(f"Evidence: {snap.evidence_level}")
    out.append("")

    out.append("User Journey")
    for i, j in enumerate(analysis.journeys[:3], 1):
        entry = j.entry_functions[0] if j.entry_functions else "?"
        exits = " / ".join(j.exit_functions[:2]) or "?"
        out.append(f"{i}. {entry} -> {exits}")
    out.append("")

    out.append("Money")
    out.append(f"In:      {', '.join(self_disp(analysis, flow.entrypoints))[:120] or '-'}")
    out.append(f"Store:   {', '.join(flow.value_holders[:3]) or '-'}")
    out.append(f"Out:     {', '.join(self_disp(analysis, flow.exits))[:120] or '-'}")
    out.append(f"Control: {', '.join(sorted({_short_fn(_disp_id(analysis, e)) for e in flow.privileged_movers}))[:120] or '-'}")
    out.append("")

    out.append("Top Contracts")
    for i, c in enumerate(_top_contracts(analysis)[:5], 1):
        out.append(f"{i}. {c.contract_name:<24} {c.role}")
    out.append("")

    out.append("Top Functions")
    for i, t in enumerate(analysis.hunter_targets[:3], 1):
        out.append(f"{i}. {t.target_id.split('#')[0]:<36} {t.score}")
    out.append("")

    hidden = hidden_block(analysis.hidden_counts)
    if hidden and not full:
        out.append("Hidden")
        out.extend(hidden)
        out.append("Use --show-all to include hidden items.")
        out.append("")

    if full:
        out.extend(_full_tables(analysis))

    out.append("Next")
    out.append(f"arkheionx hunt {project} --top 5")
    out.append("")
    if artifacts:
        out.append("Artifacts")
        for name, path in artifacts.items():
            out.append(f"{name}: {path}")
        out.append("")
    out.append("Limits")
    for lim in snap.limitations[:3]:
        out.append(f"- {lim}")
    return "\n".join(out) + "\n"


def render_open(analysis: Analysis, project: str) -> str:
    snap = analysis.snapshot
    out = header("open", project, analysis)
    out.append(snap.summary)
    out.append("")
    out.append("Top Surfaces")
    for i, t in enumerate(analysis.hunter_targets[:3], 1):
        reason = t.why_it_matters[0] if t.why_it_matters else ""
        out.append(f"{i}. {t.target_id.split('#')[0]:<36} {t.score:>3}  {reason}")
    if not analysis.hunter_targets:
        out.append("- No value-moving functions detected in production code.")
    out.append("")
    flow = analysis.money_flow
    out.append("Money Flow")
    out.append(f"In:      {', '.join(self_disp(analysis, flow.entrypoints))[:90] or '-'}")
    out.append(f"Stored:  {', '.join(flow.value_holders[:3]) or '-'}")
    out.append(f"Out:     {', '.join(self_disp(analysis, flow.exits))[:90] or '-'}")
    out.append(f"Control: {', '.join(sorted({_short_fn(_disp_id(analysis, e)) for e in flow.privileged_movers}))[:90] or '-'}")
    out.append("")
    hidden = hidden_block(analysis.hidden_counts)
    if hidden:
        out.append("Hidden: " + ", ".join(hidden) + " (use --show-all)")
        out.append("")
    out.append("Next")
    out.append(f"arkheionx map {project}")
    return "\n".join(out) + "\n"


def _disp_id(analysis: Analysis, function_id: str) -> str:
    for fr in analysis.functions:
        if fr.function_id == function_id:
            return fr.display_id
    return function_id.split("#", 1)[0]


def self_disp(analysis: Analysis, function_ids: list[str]) -> list[str]:
    return [_disp_id(analysis, fid) for fid in function_ids[:3]]


def _top_contracts(analysis: Analysis):
    priority = {"Value Holder": 0, "Reward Distributor": 1, "Share Token": 2, "Pricing / Oracle": 3}
    return sorted(analysis.contracts, key=lambda c: (priority.get(c.role, 9), c.contract_name))


def _full_tables(analysis: Analysis) -> list[str]:
    out = ["Contract Roles"]
    for c in analysis.contracts:
        out.append(f"  {c.contract_name:<26} {c.role:<20} [{c.source_kind}]")
    out.append("")
    out.append("Function Risk Map")
    for fr in sorted(analysis.functions, key=lambda f: -f.risk_score):
        out.append(f"  {fr.display_id:<36} {fr.role:<18} {fr.risk_score:>3} {fr.evidence_level}")
    out.append("")
    return out


def build_json(analysis: Analysis, artifacts: dict[str, str], next_commands: list[str]) -> dict:
    snap = analysis.snapshot
    return {
        "meta": {"tool": "Arkheionx Workbench", "version": __version__, "schema": "protocol-map/1.1.0"},
        "protocol_snapshot": to_dict(snap),
        "foundry_display": foundry_header(analysis.foundry),
        "hidden_counts": analysis.hidden_counts,
        "user_journeys": to_dict(analysis.journeys),
        "money_flow": to_dict(analysis.money_flow),
        "contracts": to_dict(analysis.contracts),
        "functions": to_dict(analysis.functions),
        "all_contracts": to_dict(analysis.all_contracts),
        "value_hotspots": to_dict(analysis.hotspots),
        "hunter_targets": to_dict(analysis.hunter_targets),
        "suggested_tests": [t for tgt in analysis.hunter_targets for t in tgt.suggested_tests],
        "invariants": sorted({i for tgt in analysis.hunter_targets for i in tgt.suggested_invariants}),
        "foundry": to_dict(analysis.foundry),
        "artifacts": artifacts,
        "limitations": snap.limitations,
        "next_commands": next_commands,
    }
