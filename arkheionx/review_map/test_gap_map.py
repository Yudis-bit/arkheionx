"""Test Gap Map: a derived, developer-first view of review-map test gaps.

Pure functions over an existing :class:`ReviewMap` (no I/O, no new analysis).
They answer one question — "which tests or local proofs should I write first?"
— by joining each existing test gap to its review priority, scenario category,
related value paths/assumptions, suggested scenarios, proof suggestion, and
evidence status. The canonical id is the existing ``gap-<contract>-<func>`` id,
so this is an enriched view of ``test-gaps.json``, not a second source of truth.

Review guidance only. Priority is review order, never severity. Most signals
stay HEURISTIC unless stronger evidence already exists in the review map.
"""
from __future__ import annotations

from .model import ReviewMap, priority_rank
from .tests import _scenario_kind


def _source_ref(source: object) -> str:
    """Render an honest 'path:line' reference, or just 'path', or '' if unknown.

    Uses only data already present on the function surface (no new analysis,
    no invented line numbers). Line 0 means the line is unknown, so only the
    file path is shown.
    """
    if not isinstance(source, dict):
        return ""
    path = str(source.get("path") or "").strip()
    if not path:
        return ""
    try:
        line_no = int(source.get("line") or 0)
    except (TypeError, ValueError):
        line_no = 0
    return f"{path}:{line_no}" if line_no > 0 else path


def _why_it_matters(fs, gap) -> str:
    if fs and fs.value_direction in ("out", "both"):
        lead = "Value can leave the system through this path. "
    elif fs and fs.value_direction == "in":
        lead = "Value enters the system through this path. "
    else:
        lead = ""
    return (lead + (gap.rationale or "")).strip()


def _evidence_links(gap, fname: str, rm: ReviewMap) -> list[dict]:
    return [
        {"id": e.id, "source": e.source, "artifact_path": e.artifact_path, "evidence_level": e.evidence_level}
        for e in rm.evidence_links
        if e.related_target == gap.related_function or e.related_target.endswith("." + fname) or e.related_target == fname
    ]


def _item(gap, rm: ReviewMap, fs_by_id: dict, proofs_by_gap: dict) -> dict:
    fs = fs_by_id.get(gap.related_function)
    contract, _, function = gap.related_function.partition(".")
    if fs:
        contract, function = fs.contract, fs.name
    priority = fs.review_priority if fs else "low"
    scenarios = [s.strip() for s in gap.suggested_test.split(";") if s.strip()]
    suggested = {"name": f"{function} scenarios", "scenarios": scenarios}

    proof = proofs_by_gap.get(gap.id)
    if proof:
        suggested.update(
            objective=proof.objective, setup=list(proof.setup),
            action=proof.action, assertions=list(proof.assertions),
        )
        next_command = proof.foundry_hint
        proof_suggestion = {"available": True, "id": proof.id, "workflow_hint": proof.foundry_hint}
    else:
        next_command = f"arkheionx prove . --target {gap.related_function} --run"
        proof_suggestion = {"available": False, "id": "", "workflow_hint": next_command}

    links = _evidence_links(gap, function, rm)
    status = "linked" if links else "missing"
    return {
        "id": gap.id,
        "target": gap.related_function,
        "contract": contract,
        "function": function,
        "source": {"path": fs.path, "line": fs.line} if fs else {"path": "", "line": 0},
        "category": _scenario_kind(fs) or "" if fs else "",
        "priority": priority,
        "confidence": gap.confidence,
        "evidence_status": status,
        "why_it_matters": _why_it_matters(fs, gap),
        "related_value_paths": sorted(
            vp.id for vp in rm.value_paths if gap.related_function in (vp.exit_function, vp.entry_function)
        ),
        "related_assumptions": sorted(
            a.id for a in rm.assumptions if gap.related_function in a.used_by or gap.id in a.missing_tests
        ),
        "suggested_test": suggested,
        "proof_suggestion": proof_suggestion,
        "evidence": {"status": status, "links": links},
        "next_command": next_command,
    }


def build_test_gap_map(rm: ReviewMap) -> dict:
    """Build the Test Gap Map payload from an existing ReviewMap. Deterministic."""

    fs_by_id = {fs.display_id: fs for fs in rm.functions}
    proofs_by_gap = {p.related_test_gap: p for p in rm.proof_suggestions if p.related_test_gap}
    items = [_item(gap, rm, fs_by_id, proofs_by_gap) for gap in rm.test_gaps]
    items.sort(key=lambda it: (priority_rank(it["priority"]), it["id"]))
    for index, item in enumerate(items, 1):
        item["index"] = index

    summary = {
        "total_test_gaps": len(items),
        "high_priority": sum(1 for it in items if it["priority"] == "high"),
        "medium_priority": sum(1 for it in items if it["priority"] == "medium"),
        "low_priority": sum(1 for it in items if it["priority"] == "low"),
        "with_proof_suggestions": sum(1 for it in items if it["proof_suggestion"]["available"]),
        "with_evidence": sum(1 for it in items if it["evidence_status"] == "linked"),
        "missing_evidence": sum(1 for it in items if it["evidence_status"] == "missing"),
    }
    return {
        "schema_version": rm.schema_version,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "summary": summary,
        "items": items,
    }


def render_test_gap_map_md(data: dict) -> str:
    """Render the concise human Test Gap Map from a built payload (no ANSI)."""

    s = data["summary"]
    out = [
        "# Test Gap Map",
        "",
        "> Review guidance only. Not confirmed vulnerabilities. Human review required.",
        "> Local/static and heuristic; most signals start at HEURISTIC.",
        "",
        "## Summary",
        "",
        f"- Total test gaps: {s['total_test_gaps']}",
        f"- High priority: {s['high_priority']} · Medium: {s['medium_priority']} · Low: {s['low_priority']}",
        f"- With proof suggestion: {s['with_proof_suggestions']}",
        f"- Missing evidence: {s['missing_evidence']}",
        "",
        "## Review First",
        "",
    ]
    top = data["items"][:5]
    if top:
        out.append("_The highest-priority gaps to test or prove before review._")
        out.append("")
        for it in top:
            cat = f" — {it['category']}" if it["category"] else ""
            out.append(f"{it['index']}. `{it['target']}` [{it['priority']}]{cat}")
            out.append(f"   - Next: `{it['next_command']}`")
    else:
        out.append("_No test gaps surfaced (try --include-low-confidence)._")
    out += ["", "## Test Gap Details", ""]
    if data["items"]:
        for it in data["items"]:
            scenarios = "; ".join(it["suggested_test"]["scenarios"]) or "—"
            rvp = ", ".join(f"`{x}`" for x in it["related_value_paths"]) or "—"
            rasm = ", ".join(f"`{x}`" for x in it["related_assumptions"]) or "—"
            out += [
                f"### {it['index']}. `{it['target']}` ({it['priority']} · {it['confidence']} confidence)",
                f"- Category: {it['category'] or '—'}",
                f"- Source: {_source_ref(it.get('source')) or '—'}",
                f"- Why it matters: {it['why_it_matters'] or '—'}",
                f"- Suggested test: {scenarios}",
                f"- Related value path: {rvp}",
                f"- Related assumption: {rasm}",
                f"- Evidence status: {it['evidence_status']}",
                f"- Next command: `{it['next_command']}`",
                "",
            ]
    else:
        out.append("_None surfaced._")
    out += ["## Boundary", "", "Review guidance only. Not confirmed vulnerabilities. Human review required.", ""]
    return "\n".join(out) + "\n"


def _repo_command(command: str, repo: str) -> str:
    if command.startswith("arkheionx prove . "):
        return command.replace("arkheionx prove . ", f"arkheionx prove {repo} ", 1)
    if command.startswith("arkheionx review-map ."):
        return command.replace("arkheionx review-map .", f"arkheionx review-map {repo}", 1)
    return command


def render_test_gap_map_cli(data: dict, repo: str, *, top: int = 5, source: str = "") -> str:
    """Render a bounded terminal report for the focused Test Gap Map command."""

    summary = data.get("summary", {})
    items = list(data.get("items", []))
    top_items = items[:max(0, top)]
    lines = [
        "ARKHEIONX TEST GAP MAP",
        "View: Test Gap Map",
        "Local/static review guidance only.",
        "Priority is review order, not severity.",
        "Test gaps are suggestions, not confirmed bugs. Human review required.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {data.get('mode', 'unknown')}",
    ]
    if source:
        lines.append(f"  Source: {source}")
    lines += [
        "",
        "Summary",
        f"  Total test gaps: {summary.get('total_test_gaps', len(items))}",
        (
            "  Priority buckets: "
            f"high {summary.get('high_priority', 0)}, "
            f"medium {summary.get('medium_priority', 0)}, "
            f"low {summary.get('low_priority', 0)}"
        ),
        f"  Evidence-linked: {summary.get('with_evidence', 0)}",
        f"  With proof suggestions: {summary.get('with_proof_suggestions', 0)}",
        "",
        "Top Test Gaps",
    ]
    if top_items:
        for item in top_items:
            target = item.get("target", "")
            priority = item.get("priority", "unknown")
            confidence = item.get("confidence", "unknown")
            category = item.get("category", "") or "uncategorized"
            proof = item.get("proof_suggestion", {})
            next_command = _repo_command(str(item.get("next_command") or proof.get("workflow_hint") or ""), repo)
            proof_id = proof.get("id") or "none"
            proof_status = f"yes ({proof_id})" if proof.get("available") else "not linked"
            lines.append(f"  {item.get('index', '-')}. {target} [{priority}; {confidence}; {category}]")
            source_ref = _source_ref(item.get("source"))
            if source_ref:
                lines.append(f"     Source: {source_ref}")
            lines.append(f"     Proof suggestion: {proof_status}")
            if next_command:
                lines.append(f"     Next: {next_command}")
    else:
        lines.append("  No test gaps surfaced. Try --include-low-confidence or inspect the full review map.")

    lines += [
        "",
        "Next",
        f"  Full review map: arkheionx review-map {repo}",
    ]
    if top_items:
        command = _repo_command(str(top_items[0].get("next_command", "")), repo)
        if command:
            lines.append(f"  First local proof: {command}")
    lines += [
        "",
        "Boundary",
        "  Local/static only. No RPC, no private keys, no live-chain calls.",
        "  No exploit automation, no transaction broadcasting, no auto-submit.",
        "  Review guidance only. Human review required.",
    ]
    return "\n".join(lines) + "\n"
