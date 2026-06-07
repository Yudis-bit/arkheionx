"""Hypothesis log / rejected-finding memory (v4.1).

Generates a structured research log from review-map surfaces and gaps. The log
records what looked dangerous, what was tested, why it was rejected, what
evidence supports that rejection, and what remains open. ArkheionX emits a
template with every hypothesis at status ``open`` and empty tracking fields; a
human or an agent under human review fills them in after local Foundry tests.

A rejected hypothesis means the tested invariant/behavior held under the
attempted conditions. That is research memory, not wasted work.
"""
from __future__ import annotations

from arkheionx.review_map.model import ReviewMap

from .hypotheses import BUG_CLASSES, generate_hypotheses
from .surfaces import build_research_surfaces

STATUSES = ("open", "testing", "rejected", "confirmed", "needs-human-review")

REJECTED_IS_EVIDENCE = (
    "Rejected findings are evidence. A rejected hypothesis means the tested "
    "invariant or behavior held under the attempted conditions. That is useful "
    "research memory, not wasted work: it records what was checked, which "
    "invariant held, and where later reviewers should not duplicate effort."
)

HOW_TO_FILL = [
    "For each hypothesis, write a local Foundry test for the suggested direction.",
    "Set Status to testing while you work, then to rejected, confirmed, or needs-human-review.",
    "Record the exact Test command you ran and the Result (pass/fail).",
    "If rejected: write the Rejection reason (which invariant/behavior held).",
    "If confirmed: only after independent local proof; record Confirmation notes and require human sign-off.",
    "Human decision is always the final field and is always made by a person.",
]

# Tracking fields a human/agent fills in after local tests (empty in the template).
_TRACKING_FIELDS = {
    "test_command": "",
    "result": "",
    "rejection_reason": "",
    "confirmation_notes": "",
    "human_decision": "",
}


def build_hypothesis_log(rm: ReviewMap, hypotheses: list[dict]) -> dict:
    entries = []
    for h in hypotheses:
        entry = {
            "id": h["id"],
            "status": h.get("status", "open"),
            "surface": h.get("surface", ""),
            "contract": h.get("contract", ""),
            "function": h.get("function", ""),
            "target": h.get("target", ""),
            "source": h.get("source", ""),
            "value_path": h.get("value_path", ""),
            "bug_class": h.get("bug_class", ""),
            "why_it_matters": h.get("why_it_matters", ""),
            "suggested_local_test": h.get("suggested_local_test", ""),
            "evidence_required": h.get("evidence_required", ""),
            "related_test_gap": h.get("test_gap", ""),
            "manual_review_required": True,
        }
        entry.update(dict(_TRACKING_FIELDS))
        entries.append(entry)

    by_class: dict[str, int] = {}
    for e in entries:
        by_class[e["bug_class"]] = by_class.get(e["bug_class"], 0) + 1

    return {
        "schema_version": "1.0.0",
        "kind": "hypothesis-log",
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "summary": {
            "total": len(entries),
            "statuses": list(STATUSES),
            "by_status": {"open": len(entries)},
            "by_bug_class": dict(sorted(by_class.items())),
        },
        "notes": {
            "rejected_findings_are_evidence": REJECTED_IS_EVIDENCE,
            "how_to_fill": list(HOW_TO_FILL),
        },
        "hypotheses": entries,
    }


def build_hypothesis_log_from_review_map(rm: ReviewMap, root) -> dict:
    surfaces = build_research_surfaces(rm, root)
    hypotheses = generate_hypotheses(rm, surfaces)
    return build_hypothesis_log(rm, hypotheses)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def render_hypothesis_log_md(data: dict) -> str:
    s = data["summary"]
    out = [
        "# Hypothesis Log",
        "",
        "> Local/static research memory. Hypotheses are not vulnerabilities.",
        "> Rejected hypotheses are useful evidence. Human review required.",
        "",
        f"- Repository: `{data['repo_path']}`",
        f"- Mode: {data['mode']} (heuristic)",
        f"- Hypotheses: {s['total']} (all start at status `open`)",
        f"- Valid statuses: {', '.join(s['statuses'])}",
        "",
        "## Rejected findings are evidence",
        "",
        data["notes"]["rejected_findings_are_evidence"],
        "",
        "## How to fill this log",
        "",
    ]
    for line in data["notes"]["how_to_fill"]:
        out.append(f"- {line}")
    out += ["", "## Hypotheses", ""]
    if not data["hypotheses"]:
        out.append("_No hypotheses generated._")
    for h in data["hypotheses"]:
        out += [
            f"### {h['id']} — {h['bug_class']}",
            "",
            f"- Status: {h['status']}",
            f"- Surface: {h['surface']}",
            f"- Contract: {h['contract'] or '—'}",
            f"- Function: {h['function'] or '—'}",
            f"- Source: {h['source'] or '—'}",
            f"- Value path: {h['value_path'] or '—'}",
            f"- Bug class: {h['bug_class']}",
            f"- Why it matters: {h['why_it_matters']}",
            f"- Suggested local test: {h['suggested_local_test']}",
            f"- Evidence required: {h['evidence_required']}",
            f"- Related test gap: {h['related_test_gap'] or '—'}",
            f"- Test command: {h['test_command'] or '_(fill after testing)_'}",
            f"- Result: {h['result'] or '_(fill after testing)_'}",
            f"- Rejection reason: {h['rejection_reason'] or '_(fill if rejected — which invariant held)_'}",
            f"- Confirmation notes: {h['confirmation_notes'] or '_(fill only with independent local proof)_'}",
            f"- Human decision: {h['human_decision'] or '_(human makes the final call)_'}",
            "",
        ]
    return "\n".join(out) + "\n"


def render_hypothesis_log_cli(data: dict, repo: str, *, top: int = 5) -> str:
    s = data["summary"]
    lines = [
        "ARKHEIONX HYPOTHESIS LOG",
        "View: Hypothesis Log",
        "Local/static research memory only.",
        "Hypotheses are review prompts, not confirmed bugs. Human review required.",
        "Rejected hypotheses are useful evidence.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {data['mode']}",
        "",
        "Summary",
        f"  Hypotheses: {s['total']} (all open)",
        f"  Statuses: {', '.join(s['statuses'])}",
        "",
        "Top hypotheses",
    ]
    if data["hypotheses"]:
        for h in data["hypotheses"][:top]:
            src = f" {h['source']}" if h["source"] else ""
            lines.append(f"  {h['id']} [{h['status']}] {h['bug_class']} -> {h['target']}{src}")
    else:
        lines.append("  - none generated")
    lines += [
        "",
        "Rejected findings are evidence",
        "  A rejected hypothesis means the tested invariant/behavior held. Record it.",
        "",
        "Next",
        f"  Full log (Markdown): arkheionx hypothesis-log {repo} --out .arkheionx/research",
        f"  Machine readable:    arkheionx hypothesis-log {repo} --json",
        f"  Write case study:    arkheionx case-study {repo}",
        "",
        "Boundary",
        "  Local/static only. No RPC, no exploit automation, no auto-submit.",
        "  Hypotheses are not findings. Human review required.",
    ]
    return "\n".join(lines) + "\n"
