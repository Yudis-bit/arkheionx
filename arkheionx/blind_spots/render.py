"""Markdown and CLI renderers for the v5 Blind Spot Intelligence artifacts.

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
        f"Test gaps: {repo['test_gaps']}",
        f"- Authorization surfaces: {repo['authorization_surfaces']} · "
        f"Periphery surfaces: {repo['periphery_surfaces']} · "
        f"Behavior-mismatch surfaces: {repo['behavior_mismatch_surfaces']}",
    ]


# ==========================================================================
# blind-spots
# ==========================================================================
def render_blind_spots_md(data: dict) -> str:
    repo = data["repository"]
    out = [
        "# Arkheionx Blind Spot Map",
        "",
        "> Local/static heuristic review map. Blind spot candidates are not",
        "> vulnerabilities. Criticality potential is not severity. Human review required.",
        "",
        "## Boundary",
        "",
    ]
    out += _boundary_block(data["safety"])
    out += ["", "## Repository Summary", ""]
    out += _repo_lines(repo)
    out += ["", "## Top Blind Spot Candidates", ""]
    if not data["candidates"]:
        out.append("_No blind spot candidates surfaced (no high-impact weakly-reviewed surfaces)._")
    for c in data["candidates"]:
        out += [
            f"### {c['id']} — {c['target']}",
            "",
            f"- Surface: {c['surface']}",
            f"- Contract: {c['contract'] or '—'}",
            f"- Function: {c['function'] or '—'}",
            f"- Source: {c['source'] or '—'}",
            f"- Criticality potential: **{c['criticality_potential']}** (heuristic blast radius, not severity)",
            f"- Review density: **{c['review_density']}** (heuristic)",
            f"- Blind spot score: **{c['blind_spot_score']}** "
            f"(impact {c['score_components']['impact']} + review-gap {c['score_components']['review_gap']} "
            f"+ complexity {c['score_components']['complexity']} + assumption {c['score_components']['assumption']}) "
            f"→ priority {c['blind_spot_priority']}",
            f"- Risk signals: {', '.join(c['risk_signals']) or '—'}",
            f"- Review-density signals: {', '.join(c['review_density_signals'])}",
            f"- Why this may be skipped: {c['why_it_may_be_skipped']}",
            f"- Why it may matter: {c['why_it_may_matter']}",
            f"- Suggested counterfactual: {c['suggested_counterfactual'] or '—'}"
            + (f" ({c['suggested_counterfactual_id']})" if c['suggested_counterfactual_id'] else ""),
            f"- Suggested local test: {c['suggested_local_test']}",
            f"- Evidence needed: {c['evidence_needed']}",
            f"- Do not claim: {c['do_not_claim']}",
            "",
        ]
    out += ["## Blind Spot Reasoning", "",
            "Each blind spot score is additive and transparent:",
            "",
            "```text",
            data["scoring"]["formula"],
            "```",
            "",
            f"{data['scoring']['note']}",
            "",
            "A surface scores higher when high impact (value exit, accounting, authorization,",
            "liquidation, oracle, external call, periphery/core, admin, cross-contract) meets",
            "weak review density, structural complexity (loops, try/catch, signature/Merkle),",
            "and unproven assumptions. Per-candidate reasons are listed above.",
            ""]
    out += ["## Unknown Surfaces", ""]
    if data["unknown_surfaces"]:
        out.append("_Surfaces with insufficient local evidence to mark reviewed. Unknown is not vulnerable._")
        out.append("")
        for u in data["unknown_surfaces"][:20]:
            out.append(f"- `{u['target']}` — {u['why_unknown']} (criticality potential: {u['criticality_potential']})")
    else:
        out.append("_No unknown surfaces surfaced._")
    out += ["", "## Notable Non-Blind-Spots", ""]
    if data["notable_non_blind_spots"]:
        out.append("_High criticality potential with a direct test observed — lower immediate priority._")
        out.append("")
        for n in data["notable_non_blind_spots"][:12]:
            out.append(f"- `{n['target']}` — criticality {n['criticality_potential']}, review density {n['review_density']}")
    else:
        out.append("_No high-value surfaces with strong test signals surfaced._")
    out += ["", "## Next Actions", "",
            "- Generate counterfactuals: `arkheionx counterfactuals .`",
            "- Map criticality potential: `arkheionx criticality-map .`",
            "- Build a research pack: `arkheionx research-pack . --out .arkheionx/research-pack`",
            "- Write local tests for the top candidates, then record results in `arkheionx hypothesis-log .`",
            "", "---", "", data["safety"]["disclaimer"], ""]
    return "\n".join(out) + "\n"


def render_blind_spots_cli(data: dict, repo: str) -> str:
    r = data["repository"]
    lines = [
        "ARKHEIONX BLIND SPOT MAP",
        "View: Blind Spot Intelligence (v5)",
        "Local/static heuristic review map.",
        "Blind spot candidates are not vulnerabilities. Criticality potential is not severity.",
        "Human review required.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {data['mode']}",
        "",
        "Summary",
        f"  Contracts: {r['contracts']} · Functions: {r['functions']} · Test gaps: {r['test_gaps']}",
        f"  Authorization: {r['authorization_surfaces']} · Periphery: {r['periphery_surfaces']} · "
        f"Behavior-mismatch: {r['behavior_mismatch_surfaces']}",
        f"  Blind spot candidates: {len(data['candidates'])} · Unknown surfaces: {len(data['unknown_surfaces'])}",
        "",
        "Top blind spot candidates (criticality potential, not severity)",
    ]
    if data["candidates"]:
        for c in data["candidates"][:6]:
            lines.append(
                f"  {c['id']} {c['target']} [crit {c['criticality_potential']}; "
                f"density {c['review_density']}; score {c['blind_spot_score']} -> {c['blind_spot_priority']}]")
    else:
        lines.append("  - none surfaced")
    lines += ["", "Next",
              f"  Full map (Markdown): arkheionx blind-spots {repo} --out .arkheionx/blind-spots",
              f"  Counterfactuals:     arkheionx counterfactuals {repo}",
              f"  Research pack:       arkheionx research-pack {repo} --out .arkheionx/research-pack",
              f"  Machine readable:    arkheionx blind-spots {repo} --json",
              "",
              "Boundary",
              "  Local/static only. No RPC, no exploit automation, no severity, no bug claims.",
              "  Blind spot candidates are review prompts. Human review required."]
    return "\n".join(lines) + "\n"


# ==========================================================================
# criticality-map
# ==========================================================================
def render_criticality_map_md(data: dict) -> str:
    repo = data["repository"]
    out = [
        "# Arkheionx Criticality Potential Map",
        "",
        "> Criticality potential is not severity. No vulnerability is claimed.",
        "> It estimates blast radius if a bug existed. Human review required.",
        "",
        "## Boundary",
        "",
    ]
    out += _boundary_block(data["safety"])
    out += ["", "## Repository Summary", ""]
    out += _repo_lines(repo)
    out += ["", "## Criticality Dimensions", "",
            "Each surface accumulates heuristic impact points across these dimensions:",
            ""]
    for d in data["dimensions"]:
        out.append(f"- {d['dimension']} (+{d['points']})")
    out += ["", "## Surface Table", "",
            "| Surface | Contract | Function | Source | Criticality potential | Primary dimension | Secondary dimensions | Why it could matter |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in data["surfaces"]:
        secondary = ", ".join(s["secondary_dimensions"]) or "—"
        why = s["why_it_could_matter"].replace("|", "\\|")
        out.append(
            f"| `{s['target']}` | {s['contract'] or '—'} | {s['function'] or '—'} | {s['source'] or '—'} "
            f"| {s['criticality_potential']} | {s['primary_dimension']} | {secondary} | {why} |")
    out += ["", "## Highest Blast-Radius Surfaces", ""]
    if data["highest_blast_radius"]:
        for s in data["highest_blast_radius"]:
            out.append(f"- `{s['target']}` — criticality potential **{s['criticality_potential']}** "
                       f"(primary: {s['primary_dimension']})")
    else:
        out.append("_No high-criticality surfaces surfaced._")
    out += ["", "## Criticality vs Review Density", "",
            "_Surfaces where high criticality potential meets weak review density — inspect first._", ""]
    if data["criticality_vs_review_density"]:
        for s in data["criticality_vs_review_density"]:
            out.append(f"- `{s['target']}` — criticality {s['criticality_potential']}, "
                       f"review density {s['review_density']} (priority {s['blind_spot_priority']})")
    else:
        out.append("_No high-criticality weak-coverage surfaces surfaced._")
    out += ["", "## Safety Note", "",
            "Criticality potential is a heuristic estimate of blast radius if a bug existed.",
            "It is not a severity, not a probability, and not a vulnerability claim. Do not",
            "submit criticality potential as a finding. Human review is required.",
            "", "---", "", data["safety"]["disclaimer"], ""]
    return "\n".join(out) + "\n"


def render_criticality_map_cli(data: dict, repo: str) -> str:
    r = data["repository"]
    lines = [
        "ARKHEIONX CRITICALITY POTENTIAL MAP",
        "View: Criticality Potential (v5)",
        "Criticality potential is not severity. No vulnerability is claimed.",
        "It estimates blast radius if a bug existed. Human review required.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {data['mode']}",
        "",
        "Summary",
        f"  Surfaces scored: {len(data['surfaces'])}",
        f"  Highest blast-radius surfaces: {len(data['highest_blast_radius'])}",
        f"  High criticality + weak review density: {len(data['criticality_vs_review_density'])}",
        "",
        "Highest blast-radius surfaces (criticality potential, not severity)",
    ]
    if data["highest_blast_radius"]:
        for s in data["highest_blast_radius"][:6]:
            lines.append(f"  {s['target']} [crit {s['criticality_potential']}; primary {s['primary_dimension']}]")
    else:
        lines.append("  - none surfaced")
    lines += ["", "Next",
              f"  Full map (Markdown): arkheionx criticality-map {repo} --out .arkheionx/criticality-map",
              f"  Blind spots:         arkheionx blind-spots {repo}",
              f"  Machine readable:    arkheionx criticality-map {repo} --json",
              "",
              "Boundary",
              "  Local/static only. Criticality potential is not severity. No bug claims.",
              "  Human review required."]
    return "\n".join(lines) + "\n"


# ==========================================================================
# counterfactuals
# ==========================================================================
def render_counterfactuals_md(data: dict) -> str:
    repo = data["repository"]
    out = [
        "# Arkheionx Counterfactual Research Plan",
        "",
        "> Counterfactuals are research prompts, not findings. Each is a testable",
        "> question of the form \"what if this assumption is false?\". Human review required.",
        "",
        "## Boundary",
        "",
    ]
    out += _boundary_block(data["safety"])
    out += ["", "## Repository Summary", ""]
    out += _repo_lines(repo)
    out += ["", "## Top Counterfactuals", ""]
    if not data["counterfactuals"]:
        out.append("_No counterfactuals generated (no guarding assumptions detected)._")
    for cf in data["counterfactuals"]:
        out += [
            f"### {cf['id']} — {cf['topic']}",
            "",
            f"- Assumption: {cf['assumption']}",
            f"- Surface: {cf['surface']}",
            f"- Contract/function: `{cf['target']}`" if cf["target"] else "- Contract/function: —",
            f"- Source: {cf['source'] or '—'}",
            f"- What if this is false? {cf['what_if_false']}",
            f"- Potential impact area: {cf['why_it_could_matter']} (impact potential: {cf['impact_potential']})",
            f"- Local test idea: {cf['local_test_direction']}",
            f"- Evidence needed: {cf['evidence_needed']}",
            f"- Stop condition: {cf['stop_condition']}",
            f"- Testability: {cf['testability']} · Priority: {cf['priority']}",
            f"- Do not claim: {cf['do_not_claim']}",
            "",
        ]
    out += ["## Counterfactual Matrix", "",
            "| Assumption | False-world scenario | Impact potential | Testability | Priority | Evidence required |",
            "| --- | --- | --- | --- | --- | --- |"]
    for row in data["counterfactual_matrix"]:
        asm = row["assumption"].replace("|", "\\|")
        fw = row["false_world_scenario"].replace("|", "\\|")
        ev = row["evidence_required"].replace("|", "\\|")
        out.append(f"| {asm} | {fw} | {row['impact_potential']} | {row['testability']} | {row['priority']} | {ev} |")
    out += ["", "## Next Actions", "",
            "- Turn the highest-priority counterfactuals into local Foundry tests.",
            "- Record each as a hypothesis in `arkheionx hypothesis-log .` (status starts `open`).",
            "- If a tested invariant holds, mark the hypothesis `rejected` — that is useful research memory.",
            "- A finding is only ever confirmed by a human with independent local proof.",
            "", "---", "", data["safety"]["disclaimer"], ""]
    return "\n".join(out) + "\n"


def render_counterfactuals_cli(data: dict, repo: str) -> str:
    lines = [
        "ARKHEIONX COUNTERFACTUAL RESEARCH PLAN",
        "View: Counterfactuals (v5)",
        "Counterfactuals are research prompts, not findings. Human review required.",
        "Each negates an assumption into a testable question.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {data['mode']}",
        "",
        "Summary",
        f"  Counterfactuals: {len(data['counterfactuals'])}",
        f"  Assumptions considered: {len(data['assumptions'])}",
        "",
        "Top counterfactuals",
    ]
    if data["counterfactuals"]:
        for cf in data["counterfactuals"][:6]:
            tgt = f" -> {cf['target']}" if cf["target"] else ""
            lines.append(f"  {cf['id']} [{cf['priority']}] {cf['topic']}{tgt}")
            lines.append(f"      What if false: {cf['what_if_false']}")
    else:
        lines.append("  - none generated")
    lines += ["", "Next",
              f"  Full plan (Markdown): arkheionx counterfactuals {repo} --out .arkheionx/counterfactuals",
              f"  Research pack:        arkheionx research-pack {repo} --out .arkheionx/research-pack",
              f"  Machine readable:     arkheionx counterfactuals {repo} --json",
              "",
              "Boundary",
              "  Local/static only. Counterfactuals are research prompts, not findings.",
              "  Do not submit a counterfactual without a local proof. Human review required."]
    return "\n".join(lines) + "\n"
