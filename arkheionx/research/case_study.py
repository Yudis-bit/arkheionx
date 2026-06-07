"""Case study generator (v4.1).

Generates a safe, sanitized case-study / research-session report from review-map
artifacts and research surfaces. When a hypothesis log already exists (via
``--from``), the case study incorporates its statuses (tested / rejected /
confirmed). Otherwise it emits an empty template with review-map-derived
sections to fill in.

A case study is not an audit report and does not claim protocol safety. It makes
no vulnerability claim unless a finding has been independently confirmed by a
human.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.review_map.model import ReviewMap, priority_rank

from .hypotheses import generate_hypotheses
from .surfaces import INSPECT_FIRST, build_research_surfaces

SAFETY_NOTE = (
    "This case study is local/static review context. It is not an audit report "
    "and does not claim protocol safety. Hypotheses are not vulnerabilities. No "
    "finding is claimed unless it has been independently confirmed locally and "
    "signed off by a human. ArkheionX performs no RPC, live-chain, or exploit "
    "automation."
)

DEFAULT_COMMANDS = [
    "arkheionx review-map <path>",
    "arkheionx agent-brief <path>",
    "arkheionx hypothesis-log <path>",
    "arkheionx case-study <path>",
]


def _top_value_paths(rm: ReviewMap, limit: int = 5) -> list[dict]:
    paths = sorted(rm.value_paths, key=lambda p: (priority_rank(p.review_priority), p.id))
    return [{"id": p.id, "label": p.label, "entry": p.entry_function,
             "exit": p.exit_function, "review_priority": p.review_priority,
             "coverage": p.test_coverage_hint} for p in paths[:limit]]


def _top_assumptions(rm: ReviewMap, limit: int = 5) -> list[dict]:
    return [{"id": a.id, "title": a.title, "category": a.category, "status": a.status}
            for a in rm.assumptions[:limit]]


def _top_test_gaps(rm: ReviewMap, limit: int = 5) -> list[dict]:
    gaps = sorted(rm.test_gaps, key=lambda g: g.id)
    return [{"id": g.id, "function": g.related_function, "confidence": g.confidence}
            for g in gaps[:limit]]


def _hypothesis_brief(h: dict) -> dict:
    return {
        "id": h.get("id", ""),
        "status": h.get("status", "open"),
        "bug_class": h.get("bug_class", ""),
        "target": h.get("target", ""),
        "rejection_reason": h.get("rejection_reason", ""),
        "confirmation_notes": h.get("confirmation_notes", ""),
        "human_decision": h.get("human_decision", ""),
    }


def build_case_study(rm: ReviewMap, surfaces, hypotheses: list[dict], *, commands: list[str] | None = None,
                     target: str = "") -> dict:
    briefs = [_hypothesis_brief(h) for h in hypotheses]
    tested = [b for b in briefs if b["status"] in ("testing", "rejected", "confirmed", "needs-human-review")]
    rejected = [b for b in briefs if b["status"] == "rejected"]
    confirmed = [b for b in briefs if b["status"] == "confirmed"]
    open_ = [b for b in briefs if b["status"] == "open"]
    needs_human = [b for b in briefs if b["status"] == "needs-human-review"]

    what_held = [
        {"id": b["id"], "bug_class": b["bug_class"], "target": b["target"],
         "rejection_reason": b["rejection_reason"]}
        for b in rejected
    ]
    next_areas = [r["surface"] for r in surfaces.coverage_ranking if r["weakness_priority"] == INSPECT_FIRST][:8]
    unresolved_assumptions = [{"id": a.id, "title": a.title} for a in rm.assumptions if a.status != "verified"]

    return {
        "schema_version": "1.0.0",
        "kind": "case-study",
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "target": target or Path(rm.repo_path).name,
        "scope_note": (
            "Local/static review of an authorized repository. Review context only — "
            "not an audit, not a severity assessment, not a safety claim."
        ),
        "commands_run": list(commands or DEFAULT_COMMANDS),
        "review_map_summary": {
            "contracts": rm.summary.contracts_analyzed,
            "functions": rm.summary.functions_mapped,
            "value_paths": rm.summary.value_paths,
            "assumptions": rm.summary.assumptions,
            "test_gaps": rm.summary.test_gaps,
        },
        "top_value_paths": _top_value_paths(rm),
        "top_assumptions": _top_assumptions(rm),
        "top_test_gaps": _top_test_gaps(rm),
        "authorization_surfaces": [
            {"target": r["target"], "signal": r["signal"], "source": r["source"]}
            for r in surfaces.authorization_surfaces
        ],
        "periphery_surfaces": [
            {"target": r["target"], "interaction_type": r["interaction_type"], "source": r["source"]}
            for r in surfaces.periphery_surfaces
        ],
        "hypotheses_tested": tested,
        "rejected_hypotheses": rejected,
        "confirmed_findings": confirmed,
        "open_hypotheses": open_,
        "needs_human_review": needs_human,
        "what_held": what_held,
        "what_was_noisy": [],
        "unresolved": {
            "open_hypotheses": [b["id"] for b in open_],
            "needs_human_review": [b["id"] for b in needs_human],
            "unresolved_assumptions": unresolved_assumptions,
        },
        "next_review_areas": next_areas,
        "safety_note": SAFETY_NOTE,
    }


def build_case_study_from_review_map(rm: ReviewMap, root, *, commands: list[str] | None = None,
                                     existing_hypotheses: list[dict] | None = None, target: str = "") -> dict:
    surfaces = build_research_surfaces(rm, root)
    hypotheses = existing_hypotheses if existing_hypotheses is not None else generate_hypotheses(rm, surfaces)
    return build_case_study(rm, surfaces, hypotheses, commands=commands, target=target)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def render_case_study_md(data: dict) -> str:
    rm = data["review_map_summary"]
    out = [
        f"# Case Study: {data['target']}",
        "",
        "> Local/static review context. Not an audit. Not a safety claim.",
        "> Hypotheses are not vulnerabilities. Human review required.",
        "",
        "## 1. Scope note",
        "",
        data["scope_note"],
        "",
        "## 2. Commands run",
        "",
    ]
    for cmd in data["commands_run"]:
        out.append(f"- `{cmd}`")
    out += [
        "",
        "## 3. Review-map summary",
        "",
        f"- Contracts: {rm['contracts']} · Functions: {rm['functions']} · "
        f"Value paths: {rm['value_paths']} · Assumptions: {rm['assumptions']} · Test gaps: {rm['test_gaps']}",
        "",
        "## 4. Top value paths",
        "",
    ]
    out += [f"- `{p['id']}` {p['label']} [{p['review_priority']}; coverage {p['coverage']}]" for p in data["top_value_paths"]] or ["_None._"]
    out += ["", "## 5. Top assumptions", ""]
    out += [f"- `{a['id']}` {a['title']} ({a['category']}; {a['status']})" for a in data["top_assumptions"]] or ["_None._"]
    out += ["", "## 6. Top test gaps", ""]
    out += [f"- `{g['id']}` `{g['function']}` ({g['confidence']})" for g in data["top_test_gaps"]] or ["_None._"]
    out += ["", "## 7. Authorization surfaces", ""]
    out += [f"- `{r['target']}` — {r['signal']} — Source: {r['source'] or '—'}" for r in data["authorization_surfaces"]] or ["_None detected (heuristic)._"]
    out += ["", "## 8. Periphery / core surfaces", ""]
    out += [f"- `{r['target']}` — {', '.join(r['interaction_type'])} — Source: {r['source'] or '—'}" for r in data["periphery_surfaces"]] or ["_None detected (heuristic)._"]
    out += ["", "## 9. Hypotheses tested", ""]
    out += _briefs_md(data["hypotheses_tested"], "_None tested yet — fill in as you test._")
    out += ["", "## 10. Rejected hypotheses", ""]
    out += _rejected_md(data["rejected_hypotheses"])
    out += ["", "## 11. Confirmed findings", ""]
    if data["confirmed_findings"]:
        out += _briefs_md(data["confirmed_findings"], "")
    else:
        out.append("_None. No vulnerability is claimed unless independently confirmed locally and signed off by a human._")
    out += ["", "## 12. What held", ""]
    if data["what_held"]:
        for w in data["what_held"]:
            reason = f" — {w['rejection_reason']}" if w["rejection_reason"] else ""
            out.append(f"- `{w['target']}` ({w['bug_class']}){reason}")
    else:
        out.append("_Record here which invariants/behaviors held once hypotheses are tested and rejected._")
    out += ["", "## 13. What was noisy", ""]
    out += [f"- {n}" for n in data["what_was_noisy"]] or ["_Record heuristic signals that turned out not to matter, to reduce future noise._"]
    out += ["", "## 14. What remains unresolved", ""]
    unresolved = data["unresolved"]
    out.append(f"- Open hypotheses: {', '.join(unresolved['open_hypotheses']) or '—'}")
    out.append(f"- Needs human review: {', '.join(unresolved['needs_human_review']) or '—'}")
    out.append(f"- Unresolved assumptions: {', '.join(a['id'] for a in unresolved['unresolved_assumptions']) or '—'}")
    out += ["", "## 15. Next review areas", ""]
    out += [f"- `{s}`" for s in data["next_review_areas"]] or ["_None surfaced._"]
    out += ["", "## 16. Safety note", "", data["safety_note"], ""]
    return "\n".join(out) + "\n"


def _briefs_md(briefs: list[dict], empty: str) -> list[str]:
    if not briefs:
        return [empty] if empty else []
    return [f"- {b['id']} [{b['status']}] {b['bug_class']} -> `{b['target']}`" for b in briefs]


def _rejected_md(briefs: list[dict]) -> list[str]:
    if not briefs:
        return ["_None yet. A rejected hypothesis means a tested invariant/behavior held — record it here as evidence._"]
    out = []
    for b in briefs:
        reason = f" — {b['rejection_reason']}" if b["rejection_reason"] else ""
        out.append(f"- {b['id']} {b['bug_class']} -> `{b['target']}`{reason}")
    return out


def render_case_study_cli(data: dict, repo: str) -> str:
    rm = data["review_map_summary"]
    lines = [
        "ARKHEIONX CASE STUDY",
        "View: Case Study (research memory)",
        "Local/static review context only. Not an audit. Not a safety claim.",
        "Hypotheses are not vulnerabilities. Human review required.",
        "",
        "Scope",
        f"  Target: {data['target']}",
        f"  Repo: {repo}",
        f"  Mode: {data['mode']}",
        "",
        "Summary",
        f"  Contracts: {rm['contracts']} · Functions: {rm['functions']} · "
        f"Value paths: {rm['value_paths']} · Test gaps: {rm['test_gaps']}",
        f"  Hypotheses tested: {len(data['hypotheses_tested'])} · "
        f"rejected: {len(data['rejected_hypotheses'])} · "
        f"confirmed: {len(data['confirmed_findings'])} · "
        f"open: {len(data['unresolved']['open_hypotheses'])}",
        "",
        "Next review areas",
    ]
    if data["next_review_areas"]:
        for s in data["next_review_areas"][:5]:
            lines.append(f"  - {s}")
    else:
        lines.append("  - none surfaced")
    lines += [
        "",
        "Next",
        f"  Full case study (Markdown): arkheionx case-study {repo} --out .arkheionx/research",
        f"  From a hypothesis log:      arkheionx case-study {repo} --from .arkheionx/research",
        "",
        "Safety note",
        "  No vulnerability is claimed unless independently confirmed locally and",
        "  signed off by a human. No RPC, no exploit automation. Human review required.",
    ]
    return "\n".join(lines) + "\n"
