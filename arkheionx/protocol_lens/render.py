"""Deterministic Markdown + compact CLI renderers for v7.5 lens artifacts.

Pure-Python renderers (no template engine; the package has no third-party
dependencies). Every Markdown artifact restates the four-line planning notice:
planning artifact / evidence quality is not validity / human review required /
no RPC, no live-chain, no exploit automation.
"""
from __future__ import annotations

from . import models as m
from . import safety


def _bullets(items, empty: str = "_None recorded._") -> str:
    items = [str(i).strip() for i in (items or []) if str(i).strip()]
    if not items:
        return empty
    return "\n".join(f"- {i}" for i in items)


def _boundary_md() -> str:
    return (
        "## Boundary\n\n"
        + "\n".join(safety.PLANNING_NOTICE)
        + "\n\nA protocol lens models a protocol; it does not confirm vulnerabilities, "
        "assign severity, or replace an audit.\n"
    )


def _lens_line(header: dict) -> str:
    lens = header.get("lens", {})
    rs = header.get("repo_summary", {})
    return (f"- Lens: {lens.get('display_name', '')} (`{lens.get('lens_id', '')}`)\n"
            f"- Repo: {rs.get('repo_path', '')} ({rs.get('contracts', 0)} contracts, "
            f"{rs.get('functions', 0)} functions)\n"
            f"- Scope: {'provided' if header.get('scope_file_used') else 'none — ' + m.SCOPE_INCOMPLETE_LOCAL_ONLY}")


# --------------------------------------------------------------------------
# Pack section renderers
# --------------------------------------------------------------------------
def render_run_context_md(data: dict) -> str:
    lens = data.get("lens", {})
    out = ["# Lens Run Context", "", _boundary_md(), "",
           "## Run", "", _lens_line(data), "",
           f"- Generated at: {data.get('generated_at', '')}",
           f"- Arkheionx version: {data.get('arkheionx_version', '')} (lens layer {data.get('lens_layer', '')})",
           f"- Schema version: {data.get('schema_version', '')}", "",
           "## Protocol families modeled", "",
           _bullets(lens.get("families", [])), "",
           "## Known surfaces", "",
           _bullets(lens.get("known_surfaces", [])), ""]
    return "\n".join(out) + "\n"


def render_scope_map_md(data: dict) -> str:
    sm = data.get("scope_map", {})
    out = ["# Lens Scope Map", "", _boundary_md(), "",
           f"- Scope status: `{sm.get('scope_status', '')}`",
           f"- Valid findings require Medium/High impact: {'yes' if sm.get('requires_medium_high') else 'not explicitly stated'}",
           "", "## Scope Summary", "", sm.get("scope_summary") or "_No scope summary provided._", "",
           "## In Scope", "", _bullets(sm.get("in_scope", [])), "",
           "## Out of Scope", "", _bullets(sm.get("out_of_scope", [])), "",
           "## Trusted Assumptions", "", _bullets(sm.get("trusted_assumptions", [])), "",
           "## Dependency Assumptions", "", _bullets(sm.get("dependency_assumptions", [])), "",
           "## Known Issues", "", _bullets(sm.get("known_issues", [])), "",
           "## Accepted Risks", "", _bullets(sm.get("accepted_risks", [])), "",
           "## Invariants To Preserve (from scope)", "", _bullets(sm.get("invariants", [])), "",
           "## Focus Areas", "", _bullets(sm.get("focus_areas", [])), ""]
    return "\n".join(out) + "\n"


def render_protocol_model_md(model: dict) -> str:
    out = ["# Protocol Model", "", _boundary_md(), "",
           f"- Lens: `{model.get('lens_id', '')}`",
           f"- Source files scanned: {len(model.get('source_files', []))}",
           f"- Terms discovered: {len(model.get('discovered_terms', []))}",
           f"- Terms unknown locally: {len(model.get('unknown_terms', []))} ({m.UNKNOWN_IN_LOCAL_REPO})",
           "", "## Extraction groups", ""]
    for g in model.get("groups", []):
        out.append(f"### {g.get('title', g.get('group_id', ''))}")
        out.append("")
        found = [f"`{f['term']}` — {f['file_count']} file(s)" for f in g.get("found", [])]
        out.append("Found:")
        out.append("")
        out.append(_bullets(found, "_None found locally._"))
        out.append("")
        unknown = g.get("unknown", [])
        if unknown:
            out.append(f"Unknown ({m.UNKNOWN_IN_LOCAL_REPO}): " + ", ".join(f"`{u}`" for u in unknown))
            out.append("")
    notes = model.get("notes", [])
    if notes:
        out += ["## Notes", "", _bullets(notes), ""]
    return "\n".join(out) + "\n"


def render_value_flow_md(value_flows: list) -> str:
    out = ["# Value Flow Map", "", _boundary_md(), ""]
    for vf in value_flows or []:
        out.append(f"## {vf.get('id', '')} — {vf.get('name', '')}")
        out.append("")
        out.append(f"- Entry: {vf.get('entry', '')}")
        out.append(f"- Movement: {vf.get('movement', '')}")
        out.append(f"- Exit: {vf.get('exit', '')}")
        out.append(f"- Status: `{vf.get('status', '')}`")
        observed = vf.get("discovered_signals", [])
        out.append(f"- Observed signals: {', '.join(observed) if observed else 'none locally'}")
        out.append("")
    if not value_flows:
        out += ["_No value-flow templates for this lens._", ""]
    return "\n".join(out) + "\n"


def render_behavior_promises_md(promises: list) -> str:
    out = ["# Behavior Promises", "", _boundary_md(), "",
           "Each promise is a property the protocol is expected to keep. A promise is not a finding.", ""]
    for p in promises or []:
        out.append(f"## {p.get('id', '')} — {p.get('text', '')}")
        out.append("")
        out.append(f"- Source basis: {p.get('source_basis', '')}")
        out.append(f"- Relevant files: {', '.join(p.get('relevant_files', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append(f"- Relevant functions: {', '.join(p.get('relevant_functions', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append(f"- State variables: {', '.join(p.get('state_variables', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append(f"- Violation condition: {p.get('violation_condition', '')}")
        out.append(f"- Possible impact: {p.get('possible_impact', '')}")
        out.append(f"- Existing evidence: {', '.join(p.get('existing_evidence', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append("- Missing evidence:")
        out.append("")
        out.append(_bullets(p.get("missing_evidence", [])))
        out.append("")
    return "\n".join(out) + "\n"


def render_economic_invariants_md(invs: list) -> str:
    out = ["# Economic Invariants", "", _boundary_md(), "",
           "Each invariant is a property to preserve. An invariant at risk is not a finding.", ""]
    for inv in invs or []:
        out.append(f"## {inv.get('id', '')}")
        out.append("")
        out.append(f"- Statement: {inv.get('statement', '')}")
        out.append(f"- Mathematical form: `{inv.get('mathematical_form', '')}`")
        out.append(f"- Relevant files: {', '.join(inv.get('relevant_files', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append(f"- Relevant functions: {', '.join(inv.get('relevant_functions', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append(f"- State variables: {', '.join(inv.get('state_variables', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append(f"- Existing direct tests: {', '.join(inv.get('existing_direct_tests', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append("- Missing tests:")
        out.append("")
        out.append(_bullets(inv.get("missing_tests", [])))
        out.append("")
        out.append(f"- Impact if broken: {inv.get('impact_if_broken', '')}")
        out.append("")
    return "\n".join(out) + "\n"


def render_temporal_windows_md(windows: list) -> str:
    out = ["# Temporal Windows", "", _boundary_md(), ""]
    for w in windows or []:
        out.append(f"## {w.get('id', '')} — {w.get('name', '')}")
        out.append("")
        out.append(f"- Window: {w.get('window_description', '')}")
        out.append(f"- Observable state: {w.get('observable_state', '')}")
        out.append(f"- Risk: {w.get('risk', '')}")
        out.append(f"- Relevant functions: {', '.join(w.get('relevant_functions', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append("")
    if not windows:
        out += ["_No temporal windows for this lens._", ""]
    return "\n".join(out) + "\n"


def render_periphery_bundle_map_md(model: dict) -> str:
    out = ["# Periphery / Bundle Map", "", _boundary_md(), "",
           "Periphery functions and their cap/target dimensions. Cap dimension and net/gross "
           "must be confirmed by reading the function; they are not inferred.", ""]
    periphery = model.get("periphery_functions", [])
    if not periphery:
        out += [f"_No periphery/bundle functions discovered locally ({m.UNKNOWN_IN_LOCAL_REPO})._", ""]
        return "\n".join(out) + "\n"
    for pf in periphery:
        out.append(f"## {pf.get('name', '')}")
        out.append("")
        out.append(f"- Source: {pf.get('source', '') or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append(f"- Target kind: {pf.get('target_kind', '')}")
        out.append(f"- Side: {pf.get('side', '')}")
        out.append(f"- Gross/net: {pf.get('gross_net', '')}")
        out.append(f"- Caps observed: {', '.join(pf.get('caps', [])) or m.UNKNOWN_IN_LOCAL_REPO}")
        out.append(f"- Notes: {pf.get('notes', '')}")
        out.append("")
    return "\n".join(out) + "\n"


def render_evidence_map_md(data: dict) -> str:
    out = ["# Evidence Map", "", _boundary_md(), "",
           f"- Test files scanned: {data.get('test_files_scanned', 0)}",
           f"- Invariants: {data.get('summary', {}).get('invariants', 0)}",
           f"- Strong/proven: {data.get('summary', {}).get('strong_or_proven', 0)}",
           f"- Untested/unknown: {data.get('summary', {}).get('untested_or_unknown', 0)}",
           "", "## Status per invariant", ""]
    for it in data.get("items", []):
        out.append(f"- `{it.get('invariant_id', '')}` — **{it.get('status', '')}** — {it.get('rationale', '')}")
        tests = it.get("supporting_tests", [])
        if tests:
            out.append(f"  - Tests: {', '.join(tests[:6])}")
    out += ["", "## Classification rules", "", _bullets(data.get("rules", [])), ""]
    return "\n".join(out) + "\n"


def render_review_lanes_md(data: dict) -> str:
    out = ["# Review Lanes", "", _boundary_md(), "",
           "Review lanes are planning artifacts, not findings. Lane priority is review order, not severity.", "",
           f"- Lanes: {data.get('lane_count', 0)}", ""]
    for lane in data.get("lanes", []):
        out.append(f"## {lane.get('id', '')} — {lane.get('title', '')}  (priority: {lane.get('priority', '')})")
        out.append("")
        out.append(f"- Why this lane matters: {lane.get('why_this_lane_matters', '')}")
        out.append(f"- Scope basis: {lane.get('scope_basis', '')}")
        out.append(f"- Source files: {', '.join(lane.get('source_files', []))}")
        out.append(f"- Functions: {', '.join(lane.get('functions', []))}")
        out.append(f"- State variables: {', '.join(lane.get('state_variables', []))}")
        out.append(f"- Invariants at risk: {', '.join(lane.get('invariants_at_risk', []))}")
        out.append(f"- Promises at risk: {', '.join(lane.get('promises_at_risk', []))}")
        out.append("- First hypotheses:")
        out.append("")
        out.append(_bullets(lane.get("first_hypotheses", [])))
        out.append("")
        out.append("- Required evidence:")
        out.append("")
        out.append(_bullets(lane.get("required_evidence", [])))
        out.append("")
        out.append(f"- Stop condition: {lane.get('stop_condition', '')}")
        out.append(f"- {lane.get('not_severity', '')}")
        out.append("")
    return "\n".join(out) + "\n"


def render_scope_tasks_md(data: dict) -> str:
    out = ["# Scope Tasks", "", _boundary_md(), "",
           "Each task is a local-test research instruction, not an exploit instruction and not a finding.", "",
           f"- Tasks: {data.get('task_count', 0)}", ""]
    for t in data.get("tasks", []):
        out.append(f"## {t.get('id', '')}  (lane {t.get('lane_id', '')})")
        out.append("")
        out.append(f"- Hypothesis: {t.get('hypothesis', '')}")
        out.append(f"- Invariant at risk: {t.get('invariant_at_risk', '')}")
        out.append(f"- Files: {', '.join(t.get('files', []))}")
        out.append(f"- Functions: {', '.join(t.get('functions', []))}")
        out.append(f"- Setup needed: {t.get('setup_needed', '')}")
        out.append(f"- Local-test attempt: {t.get('exploit_attempt_description', '')}")
        out.append(f"- Expected safe behavior: {t.get('expected_safe_behavior', '')}")
        out.append(f"- Failure condition: {t.get('failure_condition', '')}")
        out.append(f"- Suggested test file: `{t.get('suggested_test_file', '')}`")
        out.append(f"- Suggested test name: `{t.get('suggested_test_name', '')}`")
        out.append(f"- Duplicate risk: {t.get('duplicate_risk', '')}")
        out.append(f"- Decision rule: {t.get('decision_rule', '')}")
        out.append("")
    return "\n".join(out) + "\n"


def render_blindspot_ranking_md(data: dict) -> str:
    out = ["# Blind Spot Ranking", "", _boundary_md(), "",
           "These are blind spots (places to look), not confirmed bugs.", "",
           f"- Formula: {data.get('formula', '')}",
           f"- Candidates: {data.get('candidate_count', 0)}", ""]
    for i, c in enumerate(data.get("blind_spots", []), start=1):
        s = c.get("scores", {})
        out.append(f"## {i}. {c.get('title', '')}  (score {c.get('blind_spot_score', 0)})")
        out.append("")
        out.append(f"- Why it is a blind spot: {c.get('why_blind_spot', '')}")
        out.append(f"- Source files: {', '.join(c.get('source_files', []))}")
        out.append(f"- Functions: {', '.join(c.get('functions', []))}")
        out.append(f"- State variables: {', '.join(c.get('state_variables', []))}")
        out.append(f"- Invariant at risk: {c.get('invariant_at_risk', '')}")
        out.append(f"- Existing evidence: {c.get('existing_evidence', '')}")
        out.append(f"- Why evidence is insufficient: {c.get('why_evidence_insufficient', '')}")
        out.append(f"- Impact if broken: {c.get('impact_if_broken', '')}")
        out.append(f"- Duplicate risk: {c.get('duplicate_risk', '')}")
        out.append(f"- PoC objective: {c.get('poc_objective', '')}")
        out.append(f"- Suggested test file: `{c.get('suggested_test_file', '')}`")
        out.append(f"- Suggested test name: `{c.get('suggested_test_name', '')}`")
        out.append(f"- Expected failure condition: {c.get('expected_failure_condition', '')}")
        out.append(f"- Scores: importance {s.get('importance')}, evidence-weakness {s.get('evidence_weakness')}, "
                   f"cross-surface {s.get('cross_surface_complexity')}, exploitability {s.get('exploitability_plausibility')}, "
                   f"severity {s.get('potential_severity')}, duplicate-risk {s.get('duplicate_risk')}")
        out.append("")
    return "\n".join(out) + "\n"


def render_evidence_rubric_md(data: dict) -> str:
    out = ["# Evidence Rubric", "", _boundary_md(), "",
           "How local evidence is graded. Grade A and VALIDATED_CANDIDATE are human judgments; "
           "the static judge never auto-confirms a vulnerability.", "",
           "## Checks", ""]
    for r in data.get("rubric", []):
        out.append(f"- **{r.get('check', '')}** — {r.get('question', '')}")
    vocab = data.get("grades_vocabulary", {})
    out += ["", "## Grades", ""]
    for g in m.GRADES:
        out.append(f"- `{g}` — {vocab.get(g, '')}")
    out += ["", "## Decisions", "", _bullets(list(data.get("decisions_vocabulary", m.JUDGE_DECISIONS))), ""]
    if data.get("grades"):
        out += ["## Graded local tests", ""]
        for g in data.get("grades", []):
            out.append(f"- `{g.get('test_name', '')}` — grade {g.get('grade', '')}, decision {g.get('decision', '')}")
        out.append("")
    out += [data.get("note", ""), ""]
    return "\n".join(out) + "\n"


def render_report_filter_md(data: dict) -> str:
    out = ["# Report Filter", "", _boundary_md(), "",
           "The report filter never says 'submit now'. Human decision required for every candidate.", "",
           f"- Candidates: {data.get('candidate_count', 0)}",
           f"- Valid findings require Medium/High impact: {'yes' if data.get('requires_medium_high') else 'not stated'}",
           "", "## Outcomes", "", _bullets(list(data.get("outcomes_vocabulary", m.REPORT_OUTCOMES))), "",
           "## Pre-submission checklist", "", _bullets(list(data.get("checklist", []))), "",
           "## Decisions", ""]
    for d in data.get("decisions", []):
        out.append(f"### {d.get('candidate_id', '')} — {d.get('title', '')}")
        out.append("")
        out.append(f"- Outcome: **{d.get('outcome', '')}**")
        out.append(f"- Reasons: {', '.join(d.get('reasons', []))}")
        out.append("")
    if not data.get("decisions"):
        out += ["_No candidates surfaced; nothing to classify._", ""]
    out += [data.get("note", ""), ""]
    return "\n".join(out) + "\n"


def render_agent_input_md(data: dict) -> str:
    lens = data.get("lens", {})
    return "\n".join([
        "# Agent Input (model-agnostic)",
        "",
        _boundary_md(),
        "",
        f"You are a local security-research assistant working the {lens.get('display_name', '')} "
        f"(`{lens.get('lens_id', '')}`) from an authorized scope. Follow these rules.",
        "",
        _bullets([
            "Treat lanes and tasks as research instructions, not findings or exploit instructions.",
            "For each task, write a local Foundry test that reproduces the failure condition.",
            "Do not claim a finding without local test evidence and human review.",
            "Do not modify protocol source to make a test pass.",
            "Do not rely on trusted-role behaviour unless the scope marks it valid.",
            "Do not treat known or accepted issues as new findings.",
            "Grade evidence with the rubric; a candidate-with-evidence is not confirmed.",
            "Never use RPC, live-chain calls, private keys, or exploit automation.",
            "Never include private or target-identifying details in any output.",
        ]),
        "",
        "## Your loop",
        "",
        "1. Take one task from `10-scope-tasks.md`.",
        "2. Write a local Foundry test that reproduces the failure condition.",
        "3. Record the result and grade it with `12-evidence-rubric.md`.",
        "4. Classify candidates with `13-report-filter.md`.",
        "5. Hand candidates to a human; the human makes the final call.",
        "",
        f"Scope status: `{data.get('scope_status', '')}`.",
        "",
    ]) + "\n"


# --------------------------------------------------------------------------
# Top-level command renderers (Markdown)
# --------------------------------------------------------------------------
def render_lens_map_md(data: dict) -> str:
    parts = [
        render_run_context_md(data),
        render_scope_map_md(data),
        render_protocol_model_md(data.get("protocol_model", {})),
        render_value_flow_md(data.get("value_flow_paths", [])),
        render_behavior_promises_md(data.get("behavior_promises", [])),
        render_economic_invariants_md(data.get("economic_invariants", [])),
        render_temporal_windows_md(data.get("temporal_windows", [])),
        render_periphery_bundle_map_md(data.get("protocol_model", {})),
    ]
    return "\n".join(parts)


def render_lens_list_md(data: dict) -> str:
    out = ["# Protocol Lenses", "", _boundary_md(), "", "## Implemented", ""]
    for lens in data.get("implemented", []):
        out.append(f"- `{lens.get('lens_id', '')}` — {lens.get('display_name', '')} ({lens.get('protocol_family', '')})")
    out += ["", "## Planned (not implemented)", ""]
    for pid, name in data.get("planned", []):
        out.append(f"- `{pid}` — {name}")
    out.append("")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# CLI renderers (compact)
# --------------------------------------------------------------------------
def _cli_header(title: str) -> list[str]:
    return [title,
            "Local/static protocol-lens planning artifact. Not a finding, not severity. Human review required.",
            ""]


def render_lens_list_cli(data: dict) -> str:
    lines = _cli_header("ARKHEIONX PROTOCOL LENSES")
    lines.append("Implemented")
    for lens in data.get("implemented", []):
        lines.append(f"  {lens.get('lens_id', ''):<18} {lens.get('display_name', '')}")
    lines.append("")
    lines.append("Planned (not implemented)")
    for pid, name in data.get("planned", []):
        lines.append(f"  {pid:<18} {name}")
    lines += ["", "Boundary", "  Lens list is informational. Human review required."]
    return "\n".join(lines) + "\n"


def render_lens_map_cli(data: dict, repo: str) -> str:
    lens = data.get("lens", {})
    model = data.get("protocol_model", {})
    sm = data.get("scope_map", {})
    lines = _cli_header("ARKHEIONX LENS MAP")
    lines += [
        f"Repo            {repo}",
        f"Lens            {lens.get('display_name', '')} ({lens.get('lens_id', '')})",
        f"Scope           {'provided' if data.get('scope_file_used') else m.SCOPE_INCOMPLETE_LOCAL_ONLY}",
        f"Terms found     {len(model.get('discovered_terms', []))}",
        f"Terms unknown   {len(model.get('unknown_terms', []))}",
        f"Promises        {len(data.get('behavior_promises', []))}",
        f"Invariants      {len(data.get('economic_invariants', []))}",
        f"Periphery fns   {len(model.get('periphery_functions', []))}",
        "",
        "Next",
        "  arkheionx lens-lanes <repo> --lens " + str(lens.get("lens_id", "")) + " --scope-file <scope>",
        "  arkheionx lens-pack  <repo> --lens " + str(lens.get("lens_id", "")) + " --scope-file <scope> --out .arkheionx/lens-pack",
        "",
        "Boundary",
        "  Lens map is a planning artifact. Human review required.",
    ]
    return "\n".join(lines) + "\n"


def render_lens_lanes_cli(data: dict, repo: str) -> str:
    lines = _cli_header("ARKHEIONX LENS LANES")
    lines += [f"Repo   {repo}", f"Lens   {data.get('lens', {}).get('lens_id', '')}",
              f"Lanes  {data.get('lane_count', 0)}", ""]
    for lane in data.get("lanes", []):
        lines.append(f"  {lane.get('priority', ''):<10} {lane.get('id', '')}  {lane.get('title', '')}")
    lines += ["", "Boundary", "  Lane priority is review order, not severity. Human review required."]
    return "\n".join(lines) + "\n"


def render_lens_tasks_cli(data: dict, repo: str) -> str:
    lines = _cli_header("ARKHEIONX LENS TASKS")
    lines += [f"Repo   {repo}", f"Lens   {data.get('lens', {}).get('lens_id', '')}",
              f"Tasks  {data.get('task_count', 0)}", ""]
    for t in data.get("tasks", [])[:14]:
        lines.append(f"  {t.get('id', '')}  ({t.get('lane_id', '')})  {t.get('hypothesis', '')[:80]}")
    lines += ["", "Boundary", "  Tasks are research instructions, not exploit instructions. Human review required."]
    return "\n".join(lines) + "\n"


def render_lens_evidence_cli(data: dict, repo: str) -> str:
    lines = _cli_header("ARKHEIONX LENS EVIDENCE")
    summary = data.get("summary", {})
    lines += [f"Repo            {repo}", f"Lens            {data.get('lens', {}).get('lens_id', '')}",
              f"Invariants      {summary.get('invariants', 0)}",
              f"Strong/proven   {summary.get('strong_or_proven', 0)}",
              f"Untested/unknown {summary.get('untested_or_unknown', 0)}", ""]
    for it in data.get("items", []):
        lines.append(f"  {it.get('invariant_id', ''):<10} {it.get('status', '')}")
    lines += ["", "Boundary", "  Evidence quality is not vulnerability validity. Human review required."]
    return "\n".join(lines) + "\n"


def render_lens_report_filter_cli(data: dict, repo: str) -> str:
    lines = _cli_header("ARKHEIONX LENS REPORT FILTER")
    lines += [f"Repo        {repo}", f"Lens        {data.get('lens', {}).get('lens_id', '')}",
              f"Candidates  {data.get('candidate_count', 0)}", ""]
    for outcome, n in data.get("outcome_counts", {}).items():
        if n:
            lines.append(f"  {outcome:<32} {n}")
    lines += ["", "Boundary", "  Report filter is not final triage. Human decision required."]
    return "\n".join(lines) + "\n"
