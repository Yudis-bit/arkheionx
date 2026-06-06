"""Focused Value Paths view over the existing review-map artifact data.

Pure helpers over :class:`ReviewMap` and ``value-paths.json``. This module does
not add analysis or a second model; it only centralizes the artifact-compatible
payload shape and the bounded human CLI renderer for ``arkheionx value-paths``.
"""
from __future__ import annotations

from .model import ReviewMap, priority_rank, to_dict


def build_value_paths_payload(rm: ReviewMap) -> dict:
    """Return the exact payload shape written to ``value-paths.json``."""

    return {
        "schema_version": rm.schema_version,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "value_paths": to_dict(rm.value_paths),
    }


def _paths(data: object) -> list[dict]:
    if isinstance(data, list):
        return [p for p in data if isinstance(p, dict)]
    if isinstance(data, dict):
        value_paths = data.get("value_paths", [])
        if isinstance(value_paths, list):
            return [p for p in value_paths if isinstance(p, dict)]
    return []


def _bucket(paths: list[dict], priority: str) -> int:
    return sum(1 for path in paths if path.get("review_priority") == priority)


def _target_for_proof(path: dict) -> str:
    for key in ("exit_function", "entry_function"):
        target = str(path.get(key) or "").strip()
        if "." in target:
            return target
    return ""


def _one_line(values: object, fallback: str = "none") -> str:
    if isinstance(values, list):
        return ", ".join(str(value) for value in values if str(value).strip()) or fallback
    text = str(values or "").strip()
    return text or fallback


def render_value_paths_cli(data: object, repo: str, *, top: int = 5, source: str = "", mode: str = "") -> str:
    """Render a concise human report for the focused value-paths command."""

    paths = _paths(data)
    ranked = sorted(
        paths,
        key=lambda path: (priority_rank(str(path.get("review_priority", ""))), str(path.get("id", ""))),
    )
    top_paths = ranked[:max(0, top)]
    value_exit = sum(1 for path in paths if path.get("exit_function"))
    with_assumptions = sum(1 for path in paths if path.get("assumptions"))
    referenced = sum(1 for path in paths if path.get("test_coverage_hint") == "referenced")
    display_mode = mode or (str(data.get("mode", "")) if isinstance(data, dict) else "") or "review-map value-path artifact"

    lines = [
        "ARKHEIONX VALUE PATHS",
        "View: Value Paths",
        "Local/static review guidance only.",
        "Value paths are review guidance, not confirmed bugs. Human review required.",
        "Priority is review order, not severity.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {display_mode}",
    ]
    if source:
        lines.append(f"  Source: {source}")
    lines += [
        "",
        "Summary",
        f"  Total value paths: {len(paths)}",
        f"  Priority buckets: high {_bucket(paths, 'high')}, medium {_bucket(paths, 'medium')}, low {_bucket(paths, 'low')}",
        f"  Value exits: {value_exit}",
        f"  With assumptions: {with_assumptions}",
        f"  Test references: {referenced}",
        "",
        "Top Value Paths",
    ]

    if top_paths:
        for index, path in enumerate(top_paths, 1):
            label = str(path.get("label") or path.get("id") or "value path")
            priority = str(path.get("review_priority") or "unknown")
            evidence = str(path.get("evidence_level") or "unknown")
            coverage = str(path.get("test_coverage_hint") or "unknown")
            lines.append(f"  {index}. {label} [{priority}; {evidence}; coverage {coverage}]")
            lines.append(f"     Entry: {path.get('entry_function') or 'unknown'}")
            lines.append(f"     Exit: {path.get('exit_function') or 'none'}")
            lines.append(f"     Conditions: {_one_line(path.get('conditions'))}")
            lines.append(f"     Assumptions: {_one_line(path.get('assumptions'))}")
    else:
        lines.append("  No value paths surfaced. Inspect the full review map for contract/function context.")

    lines += [
        "",
        "Next",
        f"  Full review map: arkheionx review-map {repo}",
        f"  Test gaps: arkheionx test-gap-map {repo}",
    ]
    if top_paths:
        target = _target_for_proof(top_paths[0])
        if target:
            lines.append(f"  First local proof: arkheionx prove {repo} --target {target} --run")
    lines += [
        "",
        "Boundary",
        "  Local/static only. No RPC, no private keys, no live-chain calls.",
        "  No exploit automation, no transaction broadcasting, no auto-submit.",
        "  Review guidance only. Human review required.",
    ]
    return "\n".join(lines) + "\n"
