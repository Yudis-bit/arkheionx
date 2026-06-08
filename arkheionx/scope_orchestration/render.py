"""Deterministic Markdown + compact CLI renderers for v7 scope artifacts.

Markdown headings follow the v7 specification exactly. Every artifact restates the
boundary: local/static planning artifact, not a finding, not severity, human
review required.
"""
from __future__ import annotations

from . import safety


def _bullets(items: list[str], empty: str = "_None recorded._") -> str:
    items = [str(i).strip() for i in items if str(i).strip()]
    if not items:
        return empty
    return "\n".join(f"- {i}" for i in items)


def _boundary_block(extra: list[str] | None = None) -> str:
    lines = [
        "This is a local/static scope-planning artifact.",
        "It is not a finding.",
        "It is not severity.",
        "Human review required.",
    ]
    if extra:
        lines = extra + ["Human review required."]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# scope-map
# --------------------------------------------------------------------------
def render_scope_map_md(data: dict) -> str:
    rs = data.get("repo_summary", {})
    known_accepted = list(data.get("known_issues", [])) + [f"(accepted) {a}" for a in data.get("accepted_risks", [])]
    out = [
        "# Arkheionx Scope Map",
        "",
        "## Boundary",
        "",
        _boundary_block(),
        "",
        "## Scope Summary",
        "",
        data.get("scope_summary") or "_No scope summary provided._",
        "",
        f"- Scope file used: {'yes' if data.get('scope_file_used') else 'no (generic map inferred from repo structure)'}",
        f"- Repo: {rs.get('repo_path', '')} ({rs.get('contracts', 0)} contracts, {rs.get('functions', 0)} functions, mode {rs.get('mode', '')})",
        f"- Valid findings require Medium/High impact: {'yes' if data.get('requires_medium_high') else 'not explicitly stated'}",
        "",
        "## In-Scope Surface Classes",
        "",
        _bullets(data.get("in_scope_surface_classes", []), "_No in-scope surface classes detected._"),
        "",
        "## Trusted Assumptions",
        "",
        _bullets(data.get("trusted_assumptions", [])),
        "",
        "## External Dependency Assumptions",
        "",
        _bullets(data.get("dependency_assumptions", [])),
        "",
        "## Known Issues / Accepted Risks",
        "",
        _bullets(known_accepted),
        "",
        "## Prior Audit Notes",
        "",
        _bullets(data.get("prior_audit_notes", [])),
        "",
        "## Design Choices That Affect Validity",
        "",
        _bullets(data.get("design_choices", [])),
        "",
        "## Invariants To Preserve",
        "",
        _bullets(data.get("invariants", [])),
        "",
        "## Focus Areas",
        "",
        _bullets(data.get("focus_areas", [])),
        "",
        "## Do-Not-Waste-Time Filters",
        "",
        _bullets(data.get("do_not_waste_time", [])),
        "",
        "## Report Candidate Requirements",
        "",
        _bullets(data.get("report_candidate_requirements", [])),
        "",
    ]
    return "\n".join(out) + "\n"


def render_scope_map_cli(data: dict, repo: str) -> str:
    rs = data.get("repo_summary", {})
    lines = [
        "ARKHEIONX SCOPE MAP",
        "Local/static scope-planning artifact. Not a finding, not severity. Human review required.",
        "",
        f"Repo            {repo}",
        f"Scope file      {'provided' if data.get('scope_file_used') else 'none (generic map)'}",
        f"Surface classes {len(data.get('in_scope_surface_classes', []))}",
        f"Known issues    {len(data.get('known_issues', []))}",
        f"Accepted risks  {len(data.get('accepted_risks', []))}",
        f"Invariants      {len(data.get('invariants', []))}",
        f"Focus areas     {len(data.get('focus_areas', []))}",
        f"Medium/High required  {'yes' if data.get('requires_medium_high') else 'not stated'}",
        "",
        "In-scope surface classes",
    ]
    for c in data.get("in_scope_surface_classes", [])[:12]:
        lines.append(f"  - {c}")
    lines += [
        "",
        "Next",
        "  arkheionx scope-lanes <repo> --scope-file <scope> --out .arkheionx/scope-lanes",
        "  arkheionx scope-pack  <repo> --scope-file <scope> --out .arkheionx/scope-pack",
        "",
        "Boundary",
        "  Scope map is a planning artifact. Human review required.",
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# scope-lanes
# --------------------------------------------------------------------------
def render_scope_lanes_md(data: dict) -> str:
    out = ["# Arkheionx Scope-Aware Review Lanes", "", "## Boundary", "",
           "Review lanes are planning artifacts, not findings.", "Human review required.", "",
           "## Lane Priority Summary", ""]
    for p in data.get("priorities", []):
        out.append(f"- {p['priority'].upper()} — {p['lane_id']} {p['lane_name']}")
    if not data.get("priorities"):
        out.append("_No lanes selected._")
    out += ["", "## Lanes", ""]
    for lane in data.get("lanes", []):
        out += [
            f"### {lane['lane_id']} — {lane['lane_name']} ({lane['priority']})",
            "",
            f"- **Scope**: {lane.get('scope', '')}",
            f"- **Targets**: {', '.join(lane.get('target_files_functions', [])) or 'no direct repo surface matched; scope-derived lane'}",
            f"- **Why it matters**: {lane.get('why_it_matters', '')}",
            f"- **What can be valid**: {lane.get('what_can_be_valid', '')}",
            f"- **What is likely invalid**: {lane.get('what_is_likely_invalid', '')}",
            "- **Known/accepted risks to avoid**:",
            "",
            _bullets(lane.get("known_accepted_filters", [])),
            "",
            "- **First hypotheses**:",
            "",
            _bullets(lane.get("high_impact_hypothesis_directions", [])),
            "",
            "- **Required evidence**:",
            "",
            _bullets(lane.get("evidence_required", [])),
            "",
            f"- **Stop condition**: {'; '.join(lane.get('stop_conditions', []))}",
            "",
        ]
    return "\n".join(out) + "\n"


def render_scope_lanes_cli(data: dict, repo: str) -> str:
    lines = [
        "ARKHEIONX SCOPE-AWARE REVIEW LANES",
        "Review lanes are planning artifacts, not findings. Human review required.",
        "",
        f"Repo   {repo}",
        f"Lanes  {data.get('lane_count', 0)}",
        "",
        "Lane priority",
    ]
    for p in data.get("priorities", []):
        lines.append(f"  {p['priority'].upper():10} {p['lane_id']}  {p['lane_name']}")
    lines += [
        "",
        "Next",
        "  arkheionx scope-tasks <repo> --scope-file <scope> --out .arkheionx/scope-tasks",
        "",
        "Boundary",
        "  Lanes are planning artifacts, not findings. Human review required.",
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# scope-tasks
# --------------------------------------------------------------------------
def render_scope_tasks_md(data: dict) -> str:
    out = ["# Arkheionx Scope-Aware Tasks", "", "## Boundary", "",
           "Tasks are not findings.", "Tasks are not exploit instructions.", "Human review required.", "",
           "## Task Summary", "",
           f"- Tasks: {data.get('task_count', 0)}",
           f"- Lanes: {len(data.get('lanes', []))}",
           f"- Scope file used: {'yes' if data.get('scope_file_used') else 'no'}", "",
           "## Tasks", ""]
    for t in data.get("tasks", []):
        out += [
            f"### {t['task_id']} — {t['title']} ({t['priority']})",
            "",
            f"- **Lane**: {t['lane_id']} {t['lane_name']}",
            f"- **Task type**: {t['task_type']}",
            f"- **Target**: `{t['target']}`" + (f"  ({t['source_reference']})" if t.get("source_reference") else ""),
            f"- **Hypothesis**: {t['hypothesis']}",
            f"- **Counterfactual**: {t['counterfactual']}",
            f"- **Why it might matter**: {t['why_it_might_matter']}",
            f"- **Validity filter**: {t['validity_filter']}",
            f"- **Known-issue filter**: {t['known_issue_filter']}",
            f"- **Setup**: {t['setup']}",
            f"- **Action**: {t['action']}",
            "- **Required assertions**:",
            "",
            _bullets(t.get("required_assertions", [])),
            "",
            "- **Required evidence**:",
            "",
            _bullets(t.get("required_evidence", [])),
            "",
            "- **Likely invalid conditions**:",
            "",
            _bullets(t.get("likely_invalid_conditions", [])),
            "",
            f"- **Stop condition**: {t['stop_condition']}",
            f"- **Report candidate threshold**: {t['report_candidate_threshold']}",
            "- **Human review required**: yes",
            "",
        ]
    return "\n".join(out) + "\n"


def render_scope_tasks_cli(data: dict, repo: str) -> str:
    lines = [
        "ARKHEIONX SCOPE-AWARE TASKS",
        "Tasks are research instructions, not findings and not exploit instructions. Human review required.",
        "",
        f"Repo   {repo}",
        f"Tasks  {data.get('task_count', 0)} across {len(data.get('lanes', []))} lanes",
        "",
        "By lane",
    ]
    by_lane: dict[str, int] = {}
    for t in data.get("tasks", []):
        by_lane[t["lane_name"]] = by_lane.get(t["lane_name"], 0) + 1
    for name, n in by_lane.items():
        lines.append(f"  {n:2}  {name}")
    lines += [
        "",
        "Next",
        "  Hand scope-tasks.md to a review agent or reviewer; write local tests; then:",
        "  arkheionx evidence-judge <repo> --scope-file <scope> --tasks-file .arkheionx/scope-tasks/scope-tasks.json",
        "",
        "Boundary",
        "  Tasks are not findings and not exploit instructions. Human review required.",
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# evidence-judge
# --------------------------------------------------------------------------
def _ev_line(rec: dict) -> str:
    return (f"- {rec['evidence_id']} `{rec['source']}` — quality **{rec['quality']}**, "
            f"judgment **{rec['judgment']}**"
            + (f" (missing: {', '.join(rec['missing'])})" if rec.get("missing") else ""))


def render_evidence_judge_md(data: dict) -> str:
    judged = data.get("judged_evidence", [])
    summary = data.get("summary", {})
    weak_invalid = [r for r in judged if r["quality"] in ("weak", "invalid", "insufficient")]
    candidates = [r for r in judged if r["judgment"] == "candidate-with-evidence"]
    likely = [r for r in judged if r["judgment"] in (
        "invalid-test", "likely-known-issue", "likely-accepted-risk",
        "likely-trusted-role-assumption", "likely-out-of-scope", "likely-low-only")]
    out = [
        "# Arkheionx Evidence Judge",
        "",
        "## Boundary",
        "",
        "Evidence judge does not confirm vulnerabilities.",
        "Candidate-with-evidence is not a confirmed vulnerability; it only means a human should review it.",
        "Human review required.",
        "",
        "## Summary",
        "",
        f"- Evidence items judged: {summary.get('evidence_items', 0)}",
        f"- Directories scanned: {', '.join(summary.get('evidence_dirs_scanned', [])) or 'none'}",
        f"- Candidates with evidence: {summary.get('candidates_with_evidence', 0)}",
        f"- Weak or invalid: {summary.get('weak_or_invalid', 0)}",
        f"- Note: {summary.get('note', '')}",
        "",
        "## Judged Evidence",
        "",
        ("\n".join(_ev_line(r) for r in judged) if judged else "_No local evidence found._"),
        "",
        "## Weak / Invalid Tests",
        "",
        ("\n".join(_ev_line(r) for r in weak_invalid) if weak_invalid else "_None._"),
        "",
        "## Candidate With Evidence",
        "",
        ("\n".join(_ev_line(r) for r in candidates) if candidates
         else "_None. A candidate here would still require human review and is not a confirmed vulnerability._"),
        "",
        "## Likely Invalid / Known / Accepted / Out-of-Scope",
        "",
        ("\n".join(_ev_line(r) for r in likely) if likely else "_None._"),
        "",
        "## Next Actions",
        "",
        _bullets([
            "Rewrite any invalid test so it calls the target, acts, and asserts a real outcome.",
            "Strengthen weak tests with pre/post state and a negative/boundary path.",
            "Send candidate-with-evidence items to a human reviewer; do not submit them as findings.",
            "Run arkheionx report-filter to classify candidates against the scope before any submission.",
        ]),
        "",
    ]
    return "\n".join(out) + "\n"


def render_evidence_judge_cli(data: dict, repo: str) -> str:
    summary = data.get("summary", {})
    lines = [
        "ARKHEIONX EVIDENCE JUDGE",
        "Does not confirm vulnerabilities. Candidate-with-evidence is not a confirmed vulnerability.",
        "Human review required.",
        "",
        f"Repo             {repo}",
        f"Evidence items   {summary.get('evidence_items', 0)}",
        f"Dirs scanned     {', '.join(summary.get('evidence_dirs_scanned', [])) or 'none'}",
        f"Candidates       {summary.get('candidates_with_evidence', 0)}",
        f"Weak/invalid     {summary.get('weak_or_invalid', 0)}",
        "",
        "Quality counts",
    ]
    for q, n in summary.get("quality_counts", {}).items():
        if n:
            lines.append(f"  {q:12} {n}")
    lines += [
        "",
        "Boundary",
        "  Evidence quality is not vulnerability validity. Human review required.",
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# report-filter
# --------------------------------------------------------------------------
def _cand_block(c: dict) -> list[str]:
    return [
        f"### {c['candidate_id']} — {c['lane']} ({c['classification']})",
        "",
        f"- **Source task**: {c['source_task']}",
        f"- **Hypothesis**: {c['hypothesis']}",
        f"- **Lane**: {c['lane_id']} {c['lane']}",
        f"- **Evidence**: {c['evidence']}",
        f"- **Impact path**: {c['impact_path']}",
        f"- **Why this classification**: {c['why']}",
        "- **Remaining questions**:",
        "",
        _bullets(c.get("remaining_questions", [])),
        "",
        f"- **Submission risk**: {c['submission_risk']}",
        "",
    ]


def render_report_filter_md(data: dict) -> str:
    cands = data.get("candidates", [])
    reportable = [c for c in cands if c["classification"] == "potentially-reportable"]
    needs = [c for c in cands if c["classification"] in ("needs-more-evidence", "duplicate-prone")]
    invalid = [c for c in cands if c["classification"] in ("not-a-finding",)]
    filtered = [c for c in cands if c["classification"] in (
        "likely-known-issue", "likely-accepted-risk", "likely-trusted-role-assumption",
        "likely-out-of-scope", "likely-low-only")]
    out = [
        "# Arkheionx Report Filter",
        "",
        "## Boundary",
        "",
        "Report filter is not final triage.",
        "Human review required.",
        "",
        "## Candidate Summary",
        "",
        f"- Candidates classified: {data.get('candidate_count', 0)}",
    ]
    for label, n in data.get("classifications", {}).items():
        if n:
            out.append(f"- {label}: {n}")
    out += ["", "## Potentially Reportable Candidates", ""]
    if reportable:
        for c in reportable:
            out += _cand_block(c)
    else:
        out.append("_None yet. A candidate here is still not final triage and requires human review._")
    out += ["", "## Needs More Evidence", ""]
    if needs:
        for c in needs:
            out.append(f"- {c['candidate_id']} {c['lane']} ({c['classification']}): {c['hypothesis']}")
    else:
        out.append("_None._")
    out += ["", "## Likely Invalid", ""]
    if invalid:
        for c in invalid:
            out.append(f"- {c['candidate_id']} {c['lane']}: {c['why']}")
    else:
        out.append("_None classified as not-a-finding by heuristic; confirm manually._")
    out += ["", "## Known / Accepted / Trusted / Low-only Filters", ""]
    if filtered:
        for c in filtered:
            out.append(f"- {c['candidate_id']} {c['lane']} ({c['classification']}): {c['why']}")
    else:
        out.append("_No candidates matched the scope's known/accepted/trusted/low-only filters._")
    out += ["", "## Human Pre-Submission Checklist", "", _bullets(data.get("checklist", [])), ""]
    return "\n".join(out) + "\n"


def render_report_filter_cli(data: dict, repo: str) -> str:
    lines = [
        "ARKHEIONX REPORT FILTER",
        "Report filter is not final triage. Human review required.",
        "",
        f"Repo        {repo}",
        f"Candidates  {data.get('candidate_count', 0)}",
        "",
        "Classifications",
    ]
    for label, n in data.get("classifications", {}).items():
        if n:
            lines.append(f"  {n:3}  {label}")
    lines += [
        "",
        "Human pre-submission checklist",
    ]
    for item in data.get("checklist", []):
        lines.append(f"  [ ] {item}")
    lines += [
        "",
        "Boundary",
        "  Report filter is not final triage. Human review required.",
    ]
    return "\n".join(lines) + "\n"
