"""Builder for the v8 one-command review pack (`arkheionx review`)."""
from __future__ import annotations

from pathlib import Path

from arkheionx.version import PACKAGE_VERSION
from arkheionx.review_map import (
    build_assumptions_payload,
    build_review_map,
    build_value_paths_payload,
)
from arkheionx.review_map.model import ReviewMap
from arkheionx import scope_orchestration as so
from arkheionx.scope_orchestration import render as so_render
from arkheionx.scope_orchestration import safety as so_safety

SCHEMA_VERSION = "1.0.0"
ARTIFACT_TYPE = "review-pack"

# Core (always written) numbered artifacts, plus the two machine-readable files.
CORE_ARTIFACTS = (
    "00-run-context.md",
    "01-scope-map.md",
    "02-value-flow-map.md",
    "03-interaction-map.md",
    "04-assumptions.md",
    "05-review-lanes.md",
    "06-evidence-tasks.md",
    "07-evidence-rubric.md",
    "08-report-filter.md",
    "09-agent-input.md",
    "review.json",
    "manifest.json",
)

# Protocol-aware artifacts, written only when a lens is selected.
LENS_ARTIFACTS = (
    "10-protocol-model.md",
    "11-behavior-promises.md",
    "12-economic-invariants.md",
    "13-temporal-windows.md",
    "14-lens-review-lanes.md",
    "15-lens-evidence-tasks.md",
)

SAFETY_FLAGS = {
    "no_rpc": True,
    "no_live_chain": True,
    "no_exploit_automation": True,
    "no_auto_submit": True,
    "no_vulnerability_claims": True,
    "no_severity_claims": True,
    "human_review_required": True,
}

EXIT_CODE_SEMANTICS = {
    "0": "Review pack generated; no heuristic warning requires attention.",
    "1": (
        "Review pack generated, but heuristic output needs human review. This is a "
        "warning-style exit code, not a crash. In CI, inspect the decision fields in "
        "review.json instead of treating a non-zero analysis exit as fatal."
    ),
    "2": "Usage or runtime error (for example, the repo or scope path was not found).",
}

_SAFETY_LINES = (
    "Planning artifact, not a finding.",
    "A review lane is not a vulnerability.",
    "Evidence quality is not vulnerability validity.",
    "A candidate with evidence is not automatically valid.",
    "No RPC. No live-chain scanning. No auto-submit. Human review required.",
)


def default_review_dir(root: Path | str) -> Path:
    return Path(root) / ".arkheionx" / "review"


def _as_list(payload: object, key: str) -> list[dict]:
    if isinstance(payload, dict):
        items = payload.get(key, [])
        return [i for i in items if isinstance(i, dict)] if isinstance(items, list) else []
    if isinstance(payload, list):
        return [i for i in payload if isinstance(i, dict)]
    return []


def build_interaction_payload(rm: ReviewMap) -> dict:
    """Derive a cross-contract interaction map from the review map (local/static)."""
    contracts = [
        {
            "contract": c.name,
            "path": c.path,
            "external_calls": list(c.external_calls),
            "value_sensitive": bool(c.value_sensitive),
            "review_priority": c.review_priority,
        }
        for c in rm.contracts
    ]
    edges: list[dict] = []
    for vp in rm.value_paths:
        endpoints = [vp.entry_function, vp.exit_function, *list(vp.movement)]
        touched = sorted({e.split(".")[0] for e in endpoints if isinstance(e, str) and "." in e})
        if len(touched) > 1:
            edges.append({"value_path": vp.id, "label": vp.label, "contracts": touched})
    return {
        "schema_version": rm.schema_version,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "contracts": contracts,
        "cross_contract_paths": edges,
    }


def _boundary_md() -> str:
    return "\n".join(f"- {line}" for line in _SAFETY_LINES)


def _render_run_context(meta: dict) -> str:
    counts = meta["counts"]
    out = [
        "# Arkheionx Review — Run Context",
        "",
        "## Boundary",
        "",
        _boundary_md(),
        "",
        "## Run",
        "",
        f"- Arkheionx version: {meta['arkheionx_version']}",
        f"- Command: `arkheionx review`",
        f"- Repo: {meta['repo_path']}",
        f"- Scope file: {'provided' if meta['scope_file_used'] else 'none (generic pack inferred from repo structure)'}",
        f"- Lens: {meta['lens'] or 'none (generic review)'}",
        f"- Generated at: {meta['generated_at']}",
        "",
        "## Surface counts",
        "",
        f"- Contracts: {counts['contracts']}",
        f"- Functions: {counts['functions']}",
        f"- Value paths: {counts['value_paths']}",
        f"- Assumptions: {counts['assumptions']}",
        f"- Review lanes: {counts['review_lanes']}",
        f"- Evidence tasks: {counts['evidence_tasks']}",
        f"- Report candidates: {counts['report_candidates']}",
        "",
        "## Read order",
        "",
        "1. `01-scope-map.md` and `04-assumptions.md` — what is in scope and what it relies on.",
        "2. `02-value-flow-map.md` and `03-interaction-map.md` — where value moves and how contracts interact.",
        "3. `05-review-lanes.md` and `06-evidence-tasks.md` — what to review and the tasks (with kill conditions).",
        "4. `07-evidence-rubric.md` and `08-report-filter.md` — how to grade evidence and filter candidates.",
        "5. `09-agent-input.md` — model-agnostic instructions for an AI-assisted reviewer.",
        "",
        "## Exit codes",
        "",
        f"- `0` — {EXIT_CODE_SEMANTICS['0']}",
        f"- `1` — {EXIT_CODE_SEMANTICS['1']}",
        f"- `2` — {EXIT_CODE_SEMANTICS['2']}",
        "",
    ]
    return "\n".join(out) + "\n"


def _render_value_flow(payload: dict) -> str:
    paths = _as_list(payload, "value_paths")
    out = ["# Value-Flow Map", "", _boundary_md(), "",
           f"- Value paths: {len(paths)}", ""]
    if not paths:
        out += ["_No value paths detected locally._", ""]
    for vp in paths:
        movement = ", ".join(str(m) for m in vp.get("movement", [])) or "—"
        out += [
            f"## {vp.get('id', '')} — {vp.get('label', '')}  (review priority: {vp.get('review_priority', '')})",
            "",
            f"- Entry: `{vp.get('entry_function', '')}`",
            f"- Movement: {movement}",
            f"- Exit: `{vp.get('exit_function', '')}`",
            f"- Assets: {', '.join(vp.get('assets', [])) or '—'}",
            f"- Test coverage hint: {vp.get('test_coverage_hint', 'none')}",
            f"- Evidence level: {vp.get('evidence_level', 'HEURISTIC')}",
            "",
        ]
    return "\n".join(out) + "\n"


def _render_interaction(payload: dict) -> str:
    contracts = payload.get("contracts", [])
    edges = payload.get("cross_contract_paths", [])
    out = ["# Interaction Map", "", _boundary_md(), "",
           "Cross-contract and external-call interactions derived locally from the review map.", "",
           f"- Contracts: {len(contracts)}   Cross-contract value paths: {len(edges)}", "",
           "## Contracts and external calls", ""]
    if not contracts:
        out += ["_No contracts detected locally._", ""]
    for c in contracts:
        calls = ", ".join(c.get("external_calls", [])) or "none detected"
        flag = " (value-sensitive)" if c.get("value_sensitive") else ""
        out.append(f"- `{c.get('contract', '')}`{flag} — external calls: {calls}")
    out += ["", "## Cross-contract value paths", ""]
    if not edges:
        out += ["_No multi-contract value paths detected locally._", ""]
    for e in edges:
        out.append(f"- {e.get('value_path', '')} ({e.get('label', '')}): {', '.join(e.get('contracts', []))}")
    out.append("")
    return "\n".join(out) + "\n"


def _render_assumptions(payload: dict) -> str:
    items = _as_list(payload, "assumptions")
    out = ["# Assumptions", "", _boundary_md(), "",
           "Assumptions are protective properties the value paths appear to rely on. They are "
           "review prompts, not findings.", "",
           f"- Assumptions: {len(items)}", ""]
    if not items:
        out += ["_No assumptions detected locally._", ""]
    for a in items:
        out += [
            f"## {a.get('id', '')} — {a.get('title', '')}  ({a.get('category', 'general')})",
            "",
            f"- {a.get('description', '')}",
            f"- Used by: {', '.join(a.get('used_by', [])) or '—'}",
            f"- Missing tests: {', '.join(a.get('missing_tests', [])) or '—'}",
            f"- Status: {a.get('status', 'unverified')} (evidence level: {a.get('evidence_level', 'HEURISTIC')})",
            "",
        ]
    return "\n".join(out) + "\n"


def _render_agent_input(meta: dict, tasks: list[dict], lanes: list[dict], lens_summary: str) -> str:
    out = [
        "# Agent Input (model-agnostic)",
        "",
        "## Role boundary",
        "",
        "You are a local security-research assistant working an authorized scope. You produce "
        "review context and local test evidence. You never decide impact, exploitability, or "
        "severity. A human makes the security call.",
        "",
        "## Hard rules",
        "",
        "- Do not claim a finding without a local test that proves the property.",
        "- Do not submit reports or bounties.",
        "- Do not use live-chain assumptions, RPC, private keys, or exploit automation.",
        "- Do not treat a review lane as a vulnerability.",
        "- Reject a hypothesis when its kill condition holds.",
        "- Preserve scope boundaries: out-of-scope, known, accepted, and trusted-role-only items are not findings.",
        "- Mark uncertain claims as uncertain.",
        "",
        "## Context",
        "",
        f"- Repo: {meta['repo_path']} ({meta['counts']['contracts']} contracts, {meta['counts']['functions']} functions)",
        f"- Scope: {'provided' if meta['scope_file_used'] else 'none (confirm scope manually)'}",
        f"- Value paths: {meta['counts']['value_paths']}   Assumptions: {meta['counts']['assumptions']}",
        f"- Lens: {lens_summary}",
        "",
        "## Review lanes",
        "",
    ]
    if lanes:
        for lane in lanes[:12]:
            out.append(f"- {lane.get('id', '')} — {lane.get('title', lane.get('name', ''))} (priority: {lane.get('priority', '')})")
    else:
        out.append("- See `05-review-lanes.md`.")
    out += ["", "## Top tasks and kill conditions", ""]
    if tasks:
        for t in tasks[:8]:
            tid = t.get("task_id") or t.get("id") or ""
            out.append(f"- {tid}: {t.get('hypothesis', '')}")
            out.append(f"  - Kill condition: {t.get('kill_condition', '')}")
    else:
        out.append("- See `06-evidence-tasks.md`.")
    out += [
        "",
        "## Evidence rules",
        "",
        "- For each task, write a local Foundry test, record the command output, and explain the evidence.",
        "- Evidence quality is not vulnerability validity. A held invariant is a rejection, not a finding.",
        "- Grade evidence with `07-evidence-rubric.md` before drawing any conclusion.",
        "",
        "## Report-filter rules",
        "",
        "- Classify every candidate with `08-report-filter.md` before considering a report.",
        "- Only `READY_FOR_HUMAN_REVIEW` candidates go to a human; everything else is held back.",
        "- Never emit a SUBMIT/VALID/CONFIRMED decision; those are not allowed.",
        "",
        "## Forbidden assumptions",
        "",
        "- Do not assume trusted roles misbehave unless the scope marks that valid.",
        "- Do not assume live-chain state, mempool ordering, or off-chain actors beyond the scope.",
        "- Do not assume a heuristic signal is a confirmed defect.",
        "",
        "## Output format expected from you",
        "",
        "For each task, return: `task_id`, `hypothesis`, `local_test` (file + command), `result` "
        "(pass/fail/mixed), `evidence` (state deltas / reverts), `judgement` (rejected / candidate / "
        "insufficient / out-of-scope), `kill_condition_met` (yes/no), and `uncertainty` notes. Keep it "
        "local, reproducible, and free of any private or target-identifying detail.",
        "",
        "## Boundary",
        "",
        _boundary_md(),
        "",
    ]
    return "\n".join(out) + "\n"


def build_review_pack(
    root: Path | str,
    scope_file: str | None = None,
    lens_id: str | None = None,
    out_dir: Path | str | None = None,
    *,
    rm: ReviewMap | None = None,
    write: bool = True,
) -> dict:
    """Build a one-command review pack. Returns a result dict; writes files when ``write``."""
    root = Path(root)
    scope_file = (scope_file or "").strip() or None
    lens_id = (lens_id or "").strip() or None
    out = Path(out_dir).expanduser() if out_dir else default_review_dir(root)

    if rm is None:
        rm = build_review_map(root)

    # Scope-aware orchestration (always). build_scope_pack returns the structured data.
    scope_result = so.build_scope_pack(rm, root, scope_file, write=False)
    scope_map = scope_result["scope_map"]
    lanes = scope_result["lanes"]
    tasks = scope_result["tasks"]
    report = scope_result["report"]
    judge = scope_result["judge"]

    value_payload = build_value_paths_payload(rm)
    assumptions_payload = build_assumptions_payload(rm)
    interaction_payload = build_interaction_payload(rm)

    counts = {
        "contracts": rm.summary.contracts_analyzed,
        "functions": rm.summary.functions_mapped,
        "value_paths": len(_as_list(value_payload, "value_paths")),
        "assumptions": len(_as_list(assumptions_payload, "assumptions")),
        "review_lanes": lanes.get("lane_count", 0),
        "evidence_tasks": tasks.get("task_count", 0),
        "report_candidates": report.get("candidate_count", 0),
    }

    meta = {
        "arkheionx_version": PACKAGE_VERSION,
        "repo_path": str(rm.repo_path),
        "scope_file_used": bool(scope_map.get("scope_file_used")),
        "lens": lens_id,
        "generated_at": rm.generated_at,
        "counts": counts,
    }

    # Optional protocol-aware lens layer.
    lens_data: dict | None = None
    lens_files: dict[str, str] = {}
    lens_summary = "none (generic review)"
    if lens_id:
        from arkheionx import protocol_lens as pl
        from arkheionx.protocol_lens import render as pl_render

        lens = pl.get_lens(lens_id)
        lens_summary = f"{lens.display_name} (`{lens.lens_id}`)"
        lens_result = pl.build_lens_pack(lens, rm, root, scope_file, write=False)
        lens_map = lens_result["lens_map"]
        lens_lanes = lens_result["lanes"]
        lens_tasks = lens_result["tasks"]
        lens_data = {
            "lens": lens.meta().to_dict(),
            "lens_map": lens_map,
            "review_lanes": lens_lanes,
            "scope_tasks": lens_tasks,
            "evidence_map": lens_result["evidence"],
            "report_filter": lens_result["report"],
        }
        lens_files = {
            "10-protocol-model.md": pl_render.render_protocol_model_md(lens_map.get("protocol_model", {})),
            "11-behavior-promises.md": pl_render.render_behavior_promises_md(lens_map.get("behavior_promises", [])),
            "12-economic-invariants.md": pl_render.render_economic_invariants_md(lens_map.get("economic_invariants", [])),
            "13-temporal-windows.md": pl_render.render_temporal_windows_md(lens_map.get("temporal_windows", [])),
            "14-lens-review-lanes.md": pl_render.render_review_lanes_md(lens_lanes),
            "15-lens-evidence-tasks.md": pl_render.render_scope_tasks_md(lens_tasks),
        }

    agent_tasks = lens_data["scope_tasks"]["tasks"] if lens_data else tasks.get("tasks", [])
    agent_lanes = lens_data["review_lanes"]["lanes"] if lens_data else lanes.get("lanes", [])

    contents: dict[str, str] = {
        "00-run-context.md": _render_run_context(meta),
        "01-scope-map.md": so_render.render_scope_map_md(scope_map),
        "02-value-flow-map.md": _render_value_flow(value_payload),
        "03-interaction-map.md": _render_interaction(interaction_payload),
        "04-assumptions.md": _render_assumptions(assumptions_payload),
        "05-review-lanes.md": so_render.render_scope_lanes_md(lanes),
        "06-evidence-tasks.md": so_render.render_scope_tasks_md(tasks),
        "07-evidence-rubric.md": so_render.render_evidence_judge_md(judge),
        "08-report-filter.md": so_render.render_report_filter_md(report),
        "09-agent-input.md": _render_agent_input(meta, agent_tasks, agent_lanes, lens_summary),
    }
    contents.update(lens_files)

    artifact_paths = list(CORE_ARTIFACTS) + (list(LENS_ARTIFACTS) if lens_id else [])

    review_json = {
        "schema_version": SCHEMA_VERSION,
        "arkheionx_version": PACKAGE_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "command": "review",
        "generated_at": rm.generated_at,
        "repo_path": str(rm.repo_path),
        "scope_file": scope_file or "",
        "scope_file_used": meta["scope_file_used"],
        "lens": lens_id or "",
        "counts": counts,
        "safety_flags": SAFETY_FLAGS,
        "exit_code_semantics": EXIT_CODE_SEMANTICS,
        "human_review_required": True,
        "safety_boundary": so_safety.SAFETY_BOUNDARY,
        "data": {
            "scope_map": scope_map,
            "value_flow": value_payload,
            "interactions": interaction_payload,
            "assumptions": assumptions_payload,
            "review_lanes": lanes,
            "evidence_tasks": tasks,
            "evidence_judge": judge,
            "report_filter": report,
            "lens": lens_data,
        },
    }

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "arkheionx_version": PACKAGE_VERSION,
        "artifact_type": "review-pack-manifest",
        "command": "review",
        "repo_path": str(rm.repo_path),
        "scope_file": scope_file or "",
        "lens": lens_id or "",
        "generated_at": rm.generated_at,
        "artifact_count": len(artifact_paths),
        "artifact_paths": artifact_paths,
        "counts": counts,
        "safety_flags": SAFETY_FLAGS,
        "exit_code_semantics": EXIT_CODE_SEMANTICS,
        "human_review_required": True,
        "safety_boundary": so_safety.SAFETY_BOUNDARY,
    }

    written: dict[str, str] = {}
    if write:
        out.mkdir(parents=True, exist_ok=True)
        for name, text in contents.items():
            (out / name).write_text(text, encoding="utf-8")
            written[name] = str(out / name)
        written["review.json"] = _write_json(out / "review.json", review_json)
        written["manifest.json"] = _write_json(out / "manifest.json", manifest)

    return {
        "out_dir": str(out),
        "manifest": manifest,
        "review": review_json,
        "artifacts": written,
        "artifact_paths": artifact_paths,
        "contents": contents,
        "counts": counts,
    }


def _write_json(path: Path, payload: dict) -> str:
    import json

    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(path)
