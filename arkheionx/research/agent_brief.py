"""Agent brief (v4.1).

Builds a focused, safe, review-ready brief for an AI/security agent from the
review map and research surfaces, and renders it as Markdown and a bounded CLI
view. The brief replaces a vague "find bugs in this repo" prompt with a scoped
plan: value paths, assumptions, weakly-covered surfaces, authorization surfaces,
periphery/core flows, behavior-mismatch surfaces, and open hypotheses.

Review guidance only. Hypotheses are not vulnerabilities. Human review required.
"""
from __future__ import annotations

from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER
from arkheionx.review_map.model import ReviewMap, priority_rank

from .hypotheses import generate_hypotheses
from .surfaces import INSPECT_FIRST, ResearchSurfaces, build_research_surfaces

DO_NOT_CLAIM = [
    "These are hypotheses and review prompts, not vulnerabilities.",
    "Validate every hypothesis locally with a test before drawing any conclusion.",
    "Do not submit anything as a finding without independent local proof.",
    "No live-chain action. ArkheionX requires no RPC, private keys, or secrets.",
    "ArkheionX does not assign severity and does not automate exploitation.",
    "Human review is required for every conclusion.",
]

_SHARE_WORDS = ("share", "debt", "credit", "collateral", "loss", "withdrawable", "reserve", "liquidity")


def _src(fs) -> str:
    return f"{fs.path}:{fs.line}" if fs.path and fs.line > 0 else (fs.path or "")


def _repository_summary(rm: ReviewMap, source_files: int, test_files: int) -> dict:
    s = rm.summary
    return {
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "protocol_types": list(s.protocol_types),
        "contracts": s.contracts_analyzed,
        "functions": s.functions_mapped,
        "source_files": source_files,
        "test_files": test_files,
        "value_paths": s.value_paths,
        "assumptions": s.assumptions,
        "test_gaps": s.test_gaps,
    }


def _review_priority_summary(rm: ReviewMap, surfaces: ResearchSurfaces) -> dict:
    inspect_first = [r for r in surfaces.coverage_ranking if r["weakness_priority"] == INSPECT_FIRST]
    weak_high = [r["surface"] for r in inspect_first]
    strong_high = [r["surface"] for r in surfaces.coverage_ranking
                   if r["review_priority"] == "high" and r["coverage_signal"] == "tested"]
    unresolved = [{"id": a.id, "title": a.title, "category": a.category}
                  for a in rm.assumptions if a.status != "verified"]
    return {
        "top_inspect_first": [
            {"surface": r["surface"], "risk_signals": r["risk_signals"],
             "coverage_signal": r["coverage_signal"], "reason": r["reason"]}
            for r in inspect_first[:8]
        ],
        "high_value_weak_coverage": weak_high,
        "high_value_strong_coverage": strong_high,
        "unresolved_assumptions": unresolved,
    }


def _value_movement(rm: ReviewMap) -> dict:
    entries, exits, accounting, external = [], [], [], []
    for fs in rm.functions:
        src = _src(fs)
        item = {"target": fs.display_id, "source": src}
        if fs.value_direction in ("in", "both"):
            entries.append(item)
        if fs.value_direction in ("out", "both"):
            exits.append(item)
        if fs.mutability == "state-changing" and (fs.value_direction != "none"
                                                   or any(w in " ".join(fs.value_keywords).lower() for w in _SHARE_WORDS)
                                                   or any(w in fs.name.lower() for w in _SHARE_WORDS)):
            accounting.append(item)
        if "external-call" in fs.risk_signals:
            external.append(item)
    return {
        "entry_points": entries,
        "exit_points": exits,
        "accounting_mutations": accounting,
        "external_call_interactions": external,
    }


def _test_gap_summary(rm: ReviewMap) -> list[dict]:
    fs_by_id = {f.display_id: f for f in rm.functions}
    out = []
    for gap in rm.test_gaps:
        fs = fs_by_id.get(gap.related_function)
        out.append({
            "id": gap.id,
            "function": gap.related_function,
            "source": _src(fs) if fs else "",
            "why_it_matters": gap.rationale or "",
            "suggested_local_test": gap.suggested_test or "",
        })
    return sorted(out, key=lambda g: g["id"])


def build_agent_brief(rm: ReviewMap, surfaces: ResearchSurfaces, hypotheses: list[dict],
                      *, source_files: int = 0, test_files: int = 0) -> dict:
    return {
        "schema_version": "1.0.0",
        "kind": "agent-brief",
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "repository": _repository_summary(rm, source_files, test_files),
        "review_priority": _review_priority_summary(rm, surfaces),
        "value_movement": _value_movement(rm),
        "test_gaps": _test_gap_summary(rm),
        "authorization_surfaces": surfaces.authorization_surfaces,
        "periphery_surfaces": surfaces.periphery_surfaces,
        "behavior_mismatch_surfaces": surfaces.behavior_mismatch_surfaces,
        "coverage_ranking": surfaces.coverage_ranking,
        "hypotheses": hypotheses,
        "do_not_claim": list(DO_NOT_CLAIM),
        "safety": {
            "disclaimer": LOCAL_ONLY_DISCLAIMER,
            "human_review_required": True,
        },
    }


def build_agent_brief_from_review_map(rm: ReviewMap, root, *, source_files: int = 0, test_files: int = 0) -> dict:
    surfaces = build_research_surfaces(rm, root)
    hypotheses = generate_hypotheses(rm, surfaces)
    return build_agent_brief(rm, surfaces, hypotheses, source_files=source_files, test_files=test_files)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def render_agent_brief_md(data: dict) -> str:
    repo = data["repository"]
    rp = data["review_priority"]
    vm = data["value_movement"]
    out = [
        "# Agent Brief",
        "",
        "> Local/static review guidance only. Hypotheses are not vulnerabilities.",
        "> Validate locally. Do not submit without independent proof. Human review required.",
        "",
        "Use this brief instead of a vague prompt. Review these value paths,",
        "assumptions, weakly-covered surfaces, authorization surfaces, and",
        "periphery/core flows. Generate local hypotheses and validate them with",
        "tests. Do not claim bugs without proof.",
        "",
        "## 1. Repository",
        "",
        f"- Path: `{repo['repo_path']}`",
        f"- Mode: {repo['mode']} (heuristic)",
        f"- Protocol types: {', '.join(repo['protocol_types']) or 'generic'}",
        f"- Contracts: {repo['contracts']} · Functions: {repo['functions']} · "
        f"Source files: {repo['source_files']} · Test files: {repo['test_files']}",
        f"- Value paths: {repo['value_paths']} · Assumptions: {repo['assumptions']} · Test gaps: {repo['test_gaps']}",
        "",
        "## 2. Review priority (inspect first)",
        "",
    ]
    if rp["top_inspect_first"]:
        out.append("_High-value surfaces with weak coverage — heuristic review order, not severity._")
        out.append("")
        for r in rp["top_inspect_first"]:
            risks = ", ".join(r["risk_signals"]) or "value-relevant"
            out.append(f"- `{r['surface']}` — {risks} — coverage: {r['coverage_signal']}")
    else:
        out.append("_No inspect-first surfaces surfaced._")
    out += ["", "## 3. Value movement", ""]
    out.append(f"- Entry points: {_join_targets(vm['entry_points'])}")
    out.append(f"- Exit points: {_join_targets(vm['exit_points'])}")
    out.append(f"- Accounting mutations: {_join_targets(vm['accounting_mutations'])}")
    out.append(f"- External-call interactions: {_join_targets(vm['external_call_interactions'])}")
    out += ["", "## 4. Test gaps", ""]
    if data["test_gaps"]:
        for g in data["test_gaps"]:
            src = f" — Source: {g['source']}" if g["source"] else ""
            out.append(f"- {g['id']} `{g['function']}`{src}")
            if g["suggested_local_test"]:
                out.append(f"  - Suggested local test: {g['suggested_local_test']}")
    else:
        out.append("_No test gaps surfaced._")
    out += ["", "## 5. Authorization surfaces", ""]
    out += _render_auth_md(data["authorization_surfaces"])
    out += ["", "## 6. Periphery / core surfaces", ""]
    out += _render_periphery_md(data["periphery_surfaces"])
    out += ["", "## 7. Behavior-mismatch surfaces", ""]
    out += _render_behavior_md(data["behavior_mismatch_surfaces"])
    out += ["", "## 8. Suggested hypotheses", ""]
    out += _render_hypotheses_md(data["hypotheses"])
    out += ["", "## 9. Do not claim", ""]
    for line in data["do_not_claim"]:
        out.append(f"- {line}")
    out += ["", "---", "", f"{data['safety']['disclaimer']}", ""]
    return "\n".join(out) + "\n"


def _join_targets(items: list[dict], limit: int = 12) -> str:
    names = [i["target"] for i in items[:limit]]
    extra = "" if len(items) <= limit else f" (+{len(items) - limit} more)"
    return ", ".join(f"`{n}`" for n in names) + extra if names else "—"


def _render_auth_md(rows: list[dict]) -> list[str]:
    if not rows:
        return ["_No authorization signals detected (heuristic)._"]
    out = []
    for r in rows:
        out.append(f"- `{r['target']}` — signal: {r['signal']} ({r['kind']}) — Source: {r['source'] or '—'}")
        out.append(f"  - Why it matters: {r['why_it_matters']}")
        if r["suggested_local_tests"]:
            out.append(f"  - Suggested local tests: {'; '.join(r['suggested_local_tests'])}")
    return out


def _render_periphery_md(rows: list[dict]) -> list[str]:
    if not rows:
        return ["_No periphery/core interaction surfaces detected (heuristic)._"]
    out = []
    for r in rows:
        targets = ", ".join(r["core_targets"]) or "—"
        out.append(f"- `{r['target']}` — interaction: {', '.join(r['interaction_type'])} — core target(s): {targets} — Source: {r['source'] or '—'}")
        out.append(f"  - Why it matters: {r['why_it_matters']}")
        out.append(f"  - Suggested local tests: {'; '.join(r['suggested_local_tests'])}")
    return out


def _render_behavior_md(rows: list[dict]) -> list[str]:
    if not rows:
        return ["_No behavior-mismatch signals detected (heuristic)._"]
    out = []
    for r in rows:
        out.append(f"- {r['label']}: `{r['target']}` — signal: {r['signal']} — Source: {r['source'] or '—'}")
        out.append(f"  - Why it may matter: {r['why_it_may_matter']}")
        if r["suggested_local_test"]:
            out.append(f"  - Suggested local test: {'; '.join(r['suggested_local_test'])}")
    return out


def _render_hypotheses_md(rows: list[dict]) -> list[str]:
    if not rows:
        return ["_No hypotheses generated._"]
    out = []
    for h in rows:
        out.append(f"### {h['id']} — {h['bug_class']} [{h['status']}]")
        out.append(f"- Surface: {h['surface']}")
        out.append(f"- Target: `{h['target']}`" + (f" — Source: {h['source']}" if h["source"] else ""))
        if h["value_path"]:
            out.append(f"- Value path: `{h['value_path']}`")
        out.append(f"- Why it matters: {h['why_it_matters']}")
        out.append(f"- Local test direction: {h['suggested_local_test']}")
        out.append(f"- Evidence required: {h['evidence_required']}")
        if h["test_gap"]:
            out.append(f"- Related test gap: `{h['test_gap']}`")
        out.append("- Human review required: yes")
        out.append("")
    if out and out[-1] == "":
        out.pop()
    return out


def render_agent_brief_cli(data: dict, repo: str) -> str:
    repo_sum = data["repository"]
    rp = data["review_priority"]
    lines = [
        "ARKHEIONX AGENT BRIEF",
        "View: Agent Brief",
        "Local/static review guidance only.",
        "Hypotheses are review prompts, not confirmed bugs. Human review required.",
        "Priority is review order, not severity.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {data['mode']}",
        "",
        "Summary",
        f"  Contracts: {repo_sum['contracts']} · Functions: {repo_sum['functions']} · "
        f"Value paths: {repo_sum['value_paths']} · Test gaps: {repo_sum['test_gaps']}",
        f"  Authorization surfaces: {len(data['authorization_surfaces'])} · "
        f"Periphery surfaces: {len(data['periphery_surfaces'])} · "
        f"Behavior-mismatch: {len(data['behavior_mismatch_surfaces'])}",
        f"  Hypotheses (open): {len(data['hypotheses'])}",
        "",
        "Inspect first (high value, weak coverage)",
    ]
    if rp["top_inspect_first"]:
        for r in rp["top_inspect_first"][:5]:
            risks = ", ".join(r["risk_signals"]) or "value-relevant"
            lines.append(f"  - {r['surface']} [{risks}; coverage {r['coverage_signal']}]")
    else:
        lines.append("  - none surfaced")
    lines += ["", "Top hypotheses"]
    if data["hypotheses"]:
        for h in data["hypotheses"][:5]:
            lines.append(f"  {h['id']} {h['bug_class']} -> {h['target']} [{h['status']}]")
    else:
        lines.append("  - none generated")
    lines += [
        "",
        "Next",
        f"  Full brief (Markdown): arkheionx agent-brief {repo} --out .arkheionx/research",
        f"  Track hypotheses:      arkheionx hypothesis-log {repo}",
        f"  Machine readable:      arkheionx agent-brief {repo} --json",
        "",
        "Do not claim",
        "  Hypotheses are not vulnerabilities. Validate locally; do not submit without proof.",
        "  No live-chain action, no RPC, no exploit automation. Human review required.",
    ]
    return "\n".join(lines) + "\n"
