"""Markdown and CLI renderers for the v6 Evidence Graph artifacts.

All renderers are deterministic and emit plain text (no ANSI). They restate the
safety boundary and never claim a vulnerability or a severity.
"""
from __future__ import annotations

from . import models as m


def _boundary_block(safety: dict) -> list[str]:
    return [f"- {line}" for line in safety.get("boundary", m.BOUNDARY_LINES)]


def _repo_lines(repo: dict) -> list[str]:
    return [
        f"- Path: `{repo['repo_path']}`",
        f"- Mode: {repo['mode']} (heuristic)",
        f"- Contracts: {repo['contracts']} · Functions: {repo['functions']} · "
        f"Source files: {repo['source_files']} · Test files: {repo['test_files']}",
        f"- Value paths: {repo['value_paths']} · Assumptions: {repo['assumptions']} · "
        f"Test gaps: {repo['test_gaps']} · Counterfactuals: {repo['counterfactuals']}",
        f"- Authorization surfaces: {repo['authorization_surfaces']} · "
        f"Periphery surfaces: {repo['periphery_surfaces']} · "
        f"Behavior-mismatch surfaces: {repo['behavior_mismatch_surfaces']}",
        f"- Evidence nodes: {repo['evidence_nodes']} · High-impact surfaces: {repo['high_impact_surfaces']} · "
        f"Unresolved surfaces: {repo['unresolved_surfaces']}",
    ]


# ==========================================================================
# evidence-graph
# ==========================================================================
def render_evidence_graph_md(data: dict) -> str:
    repo = data["repo_summary"]
    summary = data["evidence_state_summary"]
    out = [
        "# Arkheionx Evidence Graph",
        "",
        "> Local/static review artifact. Evidence state is not a vulnerability claim.",
        "> Confirmed-candidate is not a confirmed vulnerability. Unresolved does not mean",
        "> vulnerable. Human review required.",
        "",
        "## Boundary",
        "",
    ]
    out += _boundary_block(data["safety"])
    out += ["", "## Repository Summary", ""]
    out += _repo_lines(repo)
    out += ["", "## Evidence State Summary", "",
            "_Counts across classified surfaces. None of these states is a vulnerability claim._", ""]
    for state in m.EVIDENCE_STATE_ORDER:
        out.append(f"- {state}: {summary.get(state, 0)}")
    out += ["", "## Evidence Nodes", ""]
    if not data["nodes"]:
        out.append("_No reviewable surfaces surfaced._")
    for n in data["nodes"]:
        src = f"{n['source_file']}:{n['source_line']}" if n["source_line"] else (n["source_file"] or "—")
        out += [
            f"### {n['node_id']} — {n['surface_id']}",
            "",
            f"- Surface: {n['surface_name']}",
            f"- Contract: {n['contract'] or '—'} · Function: {n['function'] or '—'}",
            f"- Source: {src}",
            f"- Surface type: {n['surface_type']}",
            f"- Criticality potential: **{n['criticality_potential']}** (heuristic blast radius, not severity)",
            f"- Review density: **{n['review_density']}** · Blind spot priority: {n['blind_spot_priority']}",
            f"- Evidence state: **{n['evidence_state']}** · Evidence strength: **{n['evidence_strength']}** · Confidence: {n['confidence']}",
            f"- Tests detected: {n['tests_detected']} · Invariants detected: {str(n['invariants_detected']).lower()} · Fuzz evidence: {str(n['fuzz_detected']).lower()}",
            f"- Assumptions: {', '.join(n['assumptions']) or '—'}",
            f"- Counterfactuals: {', '.join(n['counterfactuals']) or '—'}",
            f"- Proof-plan links: {', '.join(n['proof_plan_links']) or '—'}",
            f"- Why this state: {n['why_state']}",
            f"- Missing evidence: {', '.join(n['missing_evidence']) or '—'}",
            f"- Next local test direction: {n['next_test_direction'] or '—'}",
            "- Human review required: yes",
            "",
        ]
    out += ["## High-Impact Unresolved Surfaces", "",
            "_Criticality potential high/very-high with an open evidence state. Unresolved is not vulnerable._", ""]
    if data["unresolved_surfaces"]:
        for s in data["unresolved_surfaces"]:
            out.append(f"- `{s['surface_id']}` ({s['surface_type']}) — state {s['evidence_state']}, "
                       f"strength {s['evidence_strength']} — {s['unresolved_reason']}")
    else:
        out.append("_None: no high-impact surface is left in an open evidence state._")
    out += ["", "## Evidence Gaps", "",
            "_Categories of local evidence not observed across surfaces._", ""]
    if data["evidence_gaps"]:
        for g in data["evidence_gaps"]:
            out.append(f"- {g['gap']} — {g['count']} surface(s)")
    else:
        out.append("_No evidence gaps surfaced._")
    out += ["", "## Human Review Checklist", ""]
    for item in data["human_review_checklist"]:
        out.append(f"- [ ] {item}")
    out += ["", "---", "", data["safety"]["disclaimer"], ""]
    return "\n".join(out) + "\n"


def render_evidence_graph_cli(data: dict, repo: str) -> str:
    summary = data["evidence_state_summary"]
    r = data["repo_summary"]
    lines = [
        "ARKHEIONX EVIDENCE GRAPH",
        "View: Evidence Graph (v6)",
        "Local/static review artifact. Evidence state is not a vulnerability claim.",
        "Confirmed-candidate is not a confirmed vulnerability. Unresolved does not mean vulnerable.",
        "Human review required.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {data['mode']}",
        "",
        "Evidence state summary",
    ]
    for state in m.EVIDENCE_STATE_ORDER:
        lines.append(f"  {state}: {summary.get(state, 0)}")
    lines += [
        "",
        f"Nodes: {len(data['nodes'])} · High-impact unresolved surfaces: {len(data['unresolved_surfaces'])} · "
        f"Evidence-gap categories: {len(data['evidence_gaps'])}",
        "",
        "Top high-impact unresolved surfaces",
    ]
    if data["unresolved_surfaces"]:
        for s in data["unresolved_surfaces"][:6]:
            lines.append(f"  {s['node_id']} {s['surface_id']} [{s['surface_type']}; "
                         f"crit {s['criticality_potential']}; state {s['evidence_state']}]")
    else:
        lines.append("  - none surfaced")
    lines += ["", "Next",
              f"  Full graph (Markdown): arkheionx evidence-graph {repo} --out .arkheionx/evidence-graph",
              f"  Interactions:          arkheionx interaction-matrix {repo}",
              f"  Unresolved map:        arkheionx unresolved-map {repo}",
              f"  Machine readable:      arkheionx evidence-graph {repo} --json",
              "",
              "Boundary",
              "  Local/static only. No RPC, no exploit automation, no severity, no bug claims.",
              "  Evidence state is not a vulnerability claim. Human review required."]
    return "\n".join(lines) + "\n"


# ==========================================================================
# interaction-matrix
# ==========================================================================
def render_interaction_matrix_md(data: dict) -> str:
    s = data["matrix_summary"]
    out = [
        "# Arkheionx Interaction Matrix",
        "",
        "> Interaction candidates are not vulnerabilities. Interaction priority is not",
        "> severity. This is a local/static review artifact. Human review required.",
        "",
        "## Boundary",
        "",
    ]
    out += _boundary_block(data["safety"])
    out += ["", "## Matrix Summary", "",
            f"- Total interactions: {s['total_interactions']}",
            f"- High-impact interactions: {s['high_impact_interactions']}",
            f"- Unresolved interactions: {s['unresolved_interactions']}",
            f"- Tested interactions: {s['tested_interactions']}",
            f"- Weak-evidence interactions: {s['weak_evidence_interactions']}",
            f"- Interaction classes detected: {len(s['interaction_classes'])}",
            ""]
    out += ["## Top Interactions", ""]
    if not data["interactions"]:
        out.append("_No meaningful interactions surfaced._")
    for ix in data["interactions"]:
        out += [
            f"### {ix['interaction_id']} — {ix['interaction_class']}",
            "",
            f"- Surfaces: {', '.join(ix['surfaces'])}",
            f"- Contracts: {', '.join(ix['contracts']) or '—'} · Functions: {', '.join(ix['functions']) or '—'}",
            f"- Source refs: {', '.join(ix['source_refs']) or '—'}",
            f"- Criticality potential: **{ix['criticality_potential']}** (not severity)",
            f"- Review evidence: density {ix['review_density']} · state {ix['evidence_state']} · strength {ix['evidence_strength']}",
            f"- Interaction priority: **{ix['interaction_priority']}** "
            f"(impact {ix['impact_score']} + review-gap {ix['review_gap_score']} + complexity {ix['interaction_complexity_score']})",
            f"- Why this combination matters: {ix['why_combination_matters']}",
            f"- Missing test direction: {ix['missing_test_direction']}",
            f"- Suggested local invariant: {ix['suggested_invariant']}",
            f"- Suggested counterfactual: {ix['suggested_counterfactual']}",
            f"- Stop condition: {ix['stop_condition']}",
            "- Human review required: yes",
            "",
        ]
    out += ["## Untested High-Impact Interactions", "",
            "_High/very-high interaction priority with weak or no evidence — inspect first._", ""]
    if data["unresolved_interactions"]:
        for ix in data["unresolved_interactions"]:
            out.append(f"- `{ix['interaction_id']}` {ix['interaction_class']} "
                       f"[priority {ix['interaction_priority']}; strength {ix['evidence_strength']}] — "
                       f"{', '.join(ix['surfaces'])}")
    else:
        out.append("_None: no high-impact interaction is left without evidence._")
    out += ["", "## Interaction Test Plan", "",
            "_For each high-priority unresolved interaction: pre-state, action, assertion, evidence, rejection._", ""]
    plan_items = data["unresolved_interactions"] or data["interactions"][:6]
    for ix in plan_items[:10]:
        out += [
            f"### {ix['interaction_id']} — {ix['interaction_class']}",
            "",
            "- Pre-state: set up the two surfaces in a realistic combined state.",
            f"- Action: exercise the combination ({', '.join(ix['functions']) or 'the surfaces above'}).",
            f"- Assertion: {ix['suggested_invariant']}",
            "- Evidence needed: a local Foundry test that drives the combination and asserts the invariant.",
            f"- Rejection condition: {ix['stop_condition']}",
            "- Human review note: this is a review candidate, not a finding. Human review required.",
            "",
        ]
    out += ["---", "", data["safety"]["disclaimer"], ""]
    return "\n".join(out) + "\n"


def render_interaction_matrix_cli(data: dict, repo: str) -> str:
    s = data["matrix_summary"]
    lines = [
        "ARKHEIONX INTERACTION MATRIX",
        "View: Interaction Matrix (v6)",
        "Interaction candidates are not vulnerabilities. Interaction priority is not severity.",
        "Local/static review artifact. Human review required.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {data['mode']}",
        "",
        "Summary",
        f"  Total interactions: {s['total_interactions']} · High-impact: {s['high_impact_interactions']} · "
        f"Unresolved: {s['unresolved_interactions']}",
        f"  Tested: {s['tested_interactions']} · Weak-evidence: {s['weak_evidence_interactions']} · "
        f"Classes: {len(s['interaction_classes'])}",
        "",
        "Top interactions (interaction priority, not severity)",
    ]
    if data["interactions"]:
        for ix in data["interactions"][:6]:
            lines.append(f"  {ix['interaction_id']} {ix['interaction_class']} "
                         f"[priority {ix['interaction_priority']}; crit {ix['criticality_potential']}; "
                         f"state {ix['evidence_state']}]")
    else:
        lines.append("  - none surfaced")
    lines += ["", "Next",
              f"  Full matrix (Markdown): arkheionx interaction-matrix {repo} --out .arkheionx/interaction-matrix",
              f"  Evidence graph:         arkheionx evidence-graph {repo}",
              f"  Unresolved map:         arkheionx unresolved-map {repo}",
              f"  Machine readable:       arkheionx interaction-matrix {repo} --json",
              "",
              "Boundary",
              "  Local/static only. Interaction priority is not severity. No bug claims.",
              "  Human review required."]
    return "\n".join(lines) + "\n"


# ==========================================================================
# unresolved-map
# ==========================================================================
def render_unresolved_map_md(data: dict) -> str:
    out = [
        "# Arkheionx Unresolved Map",
        "",
        "> Unresolved does not mean vulnerable. Unresolved means local evidence is",
        "> insufficient to close the question. Human review required.",
        "",
        "## Boundary",
        "",
    ]
    out += _boundary_block(data["safety"])
    out += ["", "## High-Impact Unresolved Surfaces", ""]
    if data["unresolved_surfaces"]:
        for u in data["unresolved_surfaces"]:
            out += [
                f"### {u['id']} — {u['surface']}",
                "",
                f"- Source: {u['source'] or '—'}",
                f"- Why important: {u['why_important']}",
                f"- Evidence state: {u['evidence_state']} · Evidence strength: {u['evidence_strength']}",
                f"- Missing evidence: {', '.join(u['missing_evidence']) or '—'}",
                f"- Suggested test: {u['suggested_test'] or '—'}",
                f"- Priority: {u['priority']}",
                "- Human review required: yes",
                "",
            ]
    else:
        out.append("_None: no high-impact surface is left in an open evidence state._")
        out.append("")
    out += ["## High-Impact Unresolved Interactions", ""]
    if data["unresolved_interactions"]:
        for u in data["unresolved_interactions"]:
            out += [
                f"### {u['id']} — {u['interaction']}",
                "",
                f"- Surfaces: {', '.join(u['surfaces'])}",
                f"- Why important: {u['why_important']}",
                f"- Missing evidence: {u['missing_evidence']}",
                f"- Suggested test: {u['suggested_test']}",
                f"- Priority: {u['priority']}",
                "- Human review required: yes",
                "",
            ]
    else:
        out.append("_None: no high-impact interaction is left without evidence._")
        out.append("")
    out += ["## Unclassified Surfaces", "",
            "_Important surfaces detected but not classifiable from local signals. Not a verdict._", ""]
    if data["unclassified_surfaces"]:
        for u in data["unclassified_surfaces"]:
            out.append(f"- `{u['surface']}` ({u['surface_type']}) — {u['why_unclassified']}")
    else:
        out.append("_None: every detected surface could be classified._")
    out += ["", "## Final Review Checklist", ""]
    for item in data["final_checklist"]:
        out.append(f"- [ ] {item}")
    out += ["", "---", "", data["safety"]["disclaimer"], ""]
    return "\n".join(out) + "\n"


def render_unresolved_map_cli(data: dict, repo: str) -> str:
    s = data["summary"]
    lines = [
        "ARKHEIONX UNRESOLVED MAP",
        "View: Unresolved Map (v6)",
        "Unresolved does not mean vulnerable. Unresolved means local evidence is insufficient.",
        "Human review required.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {data['mode']}",
        "",
        "Summary",
        f"  Unresolved surfaces: {s['unresolved_surfaces']} · Unresolved interactions: {s['unresolved_interactions']}",
        f"  Unclassified surfaces: {s['unclassified_surfaces']} · High-impact surfaces: {s['high_impact_surfaces']}",
        "",
        "Top high-impact unresolved surfaces",
    ]
    if data["unresolved_surfaces"]:
        for u in data["unresolved_surfaces"][:6]:
            lines.append(f"  {u['id']} {u['surface']} [state {u['evidence_state']}; priority {u['priority']}]")
    else:
        lines.append("  - none surfaced")
    lines += ["", "Top high-impact unresolved interactions"]
    if data["unresolved_interactions"]:
        for u in data["unresolved_interactions"][:6]:
            lines.append(f"  {u['id']} {u['interaction']} [priority {u['priority']}]")
    else:
        lines.append("  - none surfaced")
    lines += ["", "Next",
              f"  Full map (Markdown): arkheionx unresolved-map {repo} --out .arkheionx/unresolved-map",
              f"  Complete review:     arkheionx complete-review {repo} --out .arkheionx/complete-review",
              f"  Machine readable:    arkheionx unresolved-map {repo} --json",
              "",
              "Boundary",
              "  Local/static only. Unresolved does not mean vulnerable. No bug claims.",
              "  Human review required."]
    return "\n".join(lines) + "\n"
