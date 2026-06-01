"""Deterministic rendering for the Protocol Review Map.

Human CLI text and Markdown artifacts. No ANSI is emitted here; the CLI applies
restrained color to the human text only, never to artifacts or JSON.
"""
from __future__ import annotations

from .model import HIGH, ReviewMap

_DEFAULT_LIST = 8


def status_of(review_map: ReviewMap) -> str:
    return "ok" if review_map.mode == "compiler-confirmed" else "warning"


def _summary_lines(rm: ReviewMap) -> list[str]:
    s = rm.summary
    return [
        "Summary",
        f"  Contracts analyzed: {s.contracts_analyzed}",
        f"  Functions mapped: {s.functions_mapped}",
        f"  Value paths: {s.value_paths}",
        f"  Assumptions: {s.assumptions}",
        f"  Test gaps: {s.test_gaps}",
        f"  Proof suggestions: {s.proof_suggestions}",
        f"  Evidence links: {s.evidence_links}",
    ]


def render_cli(rm: ReviewMap, project: str, artifacts: dict[str, str], top: int) -> str:
    out = ["ARKHEIONX REVIEW MAP", f"Status: {status_of(rm)}", ""]
    out += _summary_lines(rm)
    out += ["", "Top Review Targets"]
    if rm.reviewer_notes:
        for i, note in enumerate(rm.reviewer_notes[:top], 1):
            out.append(f"{i}. {note.title} [{note.priority}]")
            out.append(f"   Why: {note.body}")
            out.append(f"   Suggested next step: {note.next_step.replace('arkheionx prove . ', f'arkheionx prove {project} ')}")
    else:
        out.append("  No value-sensitive review targets detected.")
    out += ["", "Value Paths"]
    if rm.value_paths:
        for p in rm.value_paths[:_DEFAULT_LIST]:
            exit_label = p.exit_function or "(no value exit)"
            out.append(f"  {p.entry_function} -> {exit_label} [{p.review_priority}] (tests: {p.test_coverage_hint})")
    else:
        out.append("  No value paths detected.")
    out += ["", "Test Gaps"]
    if rm.test_gaps:
        for g in rm.test_gaps[:_DEFAULT_LIST]:
            out.append(f"  {g.related_function}: {g.suggested_test} (confidence: {g.confidence})")
    else:
        out.append("  No test gaps surfaced (try --include-low-confidence).")
    out += ["", "Assumptions"]
    if rm.assumptions:
        for a in rm.assumptions[:_DEFAULT_LIST]:
            out.append(f"  {a.title} [{a.category}]")
    else:
        out.append("  No assumptions inferred.")
    out += ["", "Evidence Links"]
    if rm.evidence_links:
        for e in rm.evidence_links[:_DEFAULT_LIST]:
            out.append(f"  {e.source}: {e.related_target} ({e.evidence_level})")
    else:
        out.append("  No existing evidence artifact linked. Run arkheionx prove/trace/evidence to create some.")
    if artifacts:
        out += ["", "Artifacts"]
        for _label, path in artifacts.items():
            out.append(f"  {path}")
    out += ["", "Safety", f"  {rm.safety.disclaimer}", "  Review guidance only; most signals start at HEURISTIC. Human review remains required."]
    out += ["", "Next",
            f"  arkheionx hunt {project} --top 5",
            f"  arkheionx evidence-status {project}",
            f"  arkheionx validate-artifacts {project}",
            "  open review-map.md and use the existing arkheionx prove / trace / evidence workflow"]
    return "\n".join(out) + "\n"


def render_markdown(rm: ReviewMap) -> str:
    s = rm.summary
    md = [
        "# Protocol Review Map",
        "",
        f"- Repository: `{rm.repo_path}`",
        f"- Mode: {rm.mode}",
        f"- Generated: {rm.generated_at}",
        f"- Protocol types: {', '.join(s.protocol_types) or 'generic'}",
        "",
        "> Review-map outputs are review guidance. They are not confirmed vulnerabilities",
        "> unless connected to proof, trace, and human review. Most signals start at HEURISTIC.",
        "",
        "## Summary",
        "",
        f"- Contracts analyzed: {s.contracts_analyzed}",
        f"- Functions mapped: {s.functions_mapped}",
        f"- Value paths: {s.value_paths}",
        f"- Assumptions: {s.assumptions}",
        f"- Test gaps: {s.test_gaps}",
        f"- Proof suggestions: {s.proof_suggestions}",
        f"- Evidence links: {s.evidence_links}",
        "",
        "## Top Review Targets",
        "",
    ]
    if rm.reviewer_notes:
        for i, note in enumerate(rm.reviewer_notes, 1):
            md += [f"{i}. **{note.title}** ({note.priority})", f"   - {note.body}", f"   - Next: `{note.next_step}`"]
    else:
        md.append("_None detected._")
    md += ["", "## Value Paths", ""]
    if rm.value_paths:
        for p in rm.value_paths:
            md += [
                f"### {p.label} ({p.review_priority})",
                f"- Entry: `{p.entry_function}`",
                f"- Movement: {', '.join(p.movement) or '—'}",
                f"- Exit: `{p.exit_function or '—'}`",
                f"- Conditions to verify: {', '.join(p.conditions) or '—'}",
                f"- Assumptions: {', '.join(p.assumptions) or '—'}",
                f"- Test coverage hint: {p.test_coverage_hint}",
                f"- Evidence level: {p.evidence_level}",
                "",
            ]
    else:
        md.append("_None detected._")
    md += ["## Assumptions", ""]
    if rm.assumptions:
        for a in rm.assumptions:
            md += [
                f"### {a.title} ({a.category})",
                f"- {a.description}",
                f"- Used by: {', '.join(a.used_by) or '—'}",
                f"- Missing tests: {', '.join(a.missing_tests) or '—'}",
                f"- Status: {a.status} ({a.evidence_level})",
                "",
            ]
    else:
        md.append("_None inferred._")
    md += ["## Test Gaps", ""]
    if rm.test_gaps:
        for g in rm.test_gaps:
            md += [
                f"### {g.title} ({g.confidence})",
                f"- Function: `{g.related_function}`",
                f"- Suggested tests: {g.suggested_test}",
                f"- Rationale: {g.rationale}",
                f"- Status: {g.status} ({g.evidence_level})",
                "",
            ]
    else:
        md.append("_None surfaced._")
    md += ["## Proof Suggestions", ""]
    if rm.proof_suggestions:
        for p in rm.proof_suggestions:
            md += [
                f"### {p.title}",
                f"- Target: `{p.target}`",
                f"- Objective: {p.objective}",
                f"- Setup: {'; '.join(p.setup)}",
                f"- Action: {p.action}",
                f"- Assertions: {'; '.join(p.assertions)}",
                f"- Foundry hint: `{p.foundry_hint}`",
                "",
            ]
    else:
        md.append("_None._")
    md += ["## Evidence Links", ""]
    if rm.evidence_links:
        for e in rm.evidence_links:
            md.append(f"- {e.source}: `{e.artifact_path}` -> {e.related_target} ({e.evidence_level})")
    else:
        md.append("_No existing evidence artifact linked._")
    md += ["", "## Safety Boundaries", ""]
    md += [f"- {b}" for b in rm.safety.boundaries]
    md += [
        "",
        "## Next Steps",
        "",
        "1. Open the highest-priority value paths and confirm the conditions hold.",
        "2. Add the suggested local tests for the high-priority test gaps.",
        "3. Use `arkheionx prove` / `trace` / `evidence` to raise evidence levels.",
        "4. Require human review before drawing any conclusion.",
        "",
    ]
    return "\n".join(md) + "\n"


def render_summary_md(rm: ReviewMap) -> str:
    s = rm.summary
    md = [
        "# Review Summary",
        "",
        f"{s.text}",
        "",
        "## Look at these first",
        "",
    ]
    if rm.reviewer_notes:
        for i, note in enumerate(rm.reviewer_notes[:5], 1):
            md.append(f"{i}. `{note.title}` ({note.priority}) — {note.body}")
    else:
        md.append("_No high-priority targets detected._")
    md += [
        "",
        "## Reminder",
        "",
        "Review-map outputs are review guidance, not confirmed vulnerabilities. Human review remains required.",
        "",
    ]
    return "\n".join(md) + "\n"


def render_mermaid(rm: ReviewMap) -> str:
    lines = ["flowchart LR"]
    for p in rm.value_paths[:12]:
        entry = _node(p.entry_function)
        exit_node = _node(p.exit_function or f"{p.id}-exit")
        lines.append(f'  {entry}["{p.entry_function}"] --> {exit_node}["{p.exit_function or "exit"}"]')
        for asm in p.assumptions[:2]:
            lines.append(f'  {exit_node} -.assumes.-> {_node(asm)}["{asm}"]')
    if len(lines) == 1:
        lines.append("  empty[No value paths detected]")
    return "\n".join(lines) + "\n"


def _node(text: str) -> str:
    import re
    return "n_" + re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
