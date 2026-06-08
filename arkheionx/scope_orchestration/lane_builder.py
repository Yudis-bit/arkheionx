"""Build scope-aware review lanes and the structured scope map (v7).

A lane is one focused, generic research track (LANE-01 .. LANE-14). It is selected
only when a repository surface or the scope note makes it relevant, enriched with
the scope's trusted assumptions, known/accepted filters, hypotheses, and required
evidence. Lanes are planning artifacts, never findings. Human review is required.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.blind_spots.models import SurfaceRecord
from arkheionx.review_map.model import ReviewMap
from arkheionx.version import PACKAGE_VERSION

from . import models as m
from . import safety
from . import scope_parser
from .repo_context import build_repo_context

_CRIT_TO_PRIORITY = {
    "very-high": m.PRIORITY_VERY_HIGH,
    "high": m.PRIORITY_HIGH,
    "medium": m.PRIORITY_MEDIUM,
    "low": m.PRIORITY_MONITOR,
    "unknown": m.PRIORITY_MONITOR,
}


def _haystack(rec: SurfaceRecord) -> str:
    bits = [rec.target, rec.contract, rec.function, rec.source]
    bits += rec.risk_signals + rec.auth_kinds + rec.periphery_interactions + rec.behavior_signals
    return " ".join(b for b in bits if b).lower()


def _lane_matches_record(ld: m.LaneDef, rec: SurfaceRecord) -> bool:
    h = _haystack(rec)
    return any(k in h for k in ld.keywords)


def _scope_mentions_lane(ld: m.LaneDef, scope: m.ScopeData) -> bool:
    blob = scope.haystack()
    if not blob:
        return False
    return any(k in blob for k in ld.keywords)


def select_lanes(records: list[SurfaceRecord], scope: m.ScopeData) -> list[tuple[m.LaneDef, list[SurfaceRecord]]]:
    """Return (LaneDef, matched_records) for every relevant lane, in canonical order."""
    selected: list[tuple[m.LaneDef, list[SurfaceRecord]]] = []
    for ld in m.LANE_DEFS:
        matched = [r for r in records if _lane_matches_record(ld, r)]
        if matched or _scope_mentions_lane(ld, scope):
            selected.append((ld, matched))
    return selected


def _bump(priority: str) -> str:
    order = [m.PRIORITY_MONITOR, m.PRIORITY_MEDIUM, m.PRIORITY_HIGH, m.PRIORITY_VERY_HIGH]
    i = order.index(priority) if priority in order else 0
    return order[min(i + 1, len(order) - 1)]


def _lane_priority(ld: m.LaneDef, matched: list[SurfaceRecord], scope: m.ScopeData) -> str:
    best = m.PRIORITY_MONITOR
    rank = m.priority_rank(best)
    for r in matched:
        p = _CRIT_TO_PRIORITY.get(r.criticality_potential, m.PRIORITY_MONITOR)
        if m.priority_rank(p) < rank:
            best, rank = p, m.priority_rank(p)
    if not matched and _scope_mentions_lane(ld, scope):
        best = m.PRIORITY_MEDIUM
    # A lane the sponsor explicitly asked us to focus on is bumped one level.
    focus_blob = " ".join(scope.focus_areas + scope.changed_since_audit).lower()
    if focus_blob and any(k in focus_blob for k in ld.keywords):
        best = _bump(best)
    return best


def _filter_lines(items: list[str], keywords: tuple[str, ...]) -> list[str]:
    out = [it for it in items if any(k in it.lower() for k in keywords)]
    return out


def scope_filters(scope: m.ScopeData) -> dict:
    """The do-not-waste-time filter sets, reused by lanes/tasks/report-filter."""
    trusted = scope.trusted_roles + scope.admin_assumptions + scope.off_chain_assumptions
    deps = scope.trusted_integrations + scope.external_dependency_assumptions
    return {
        "known_issues": list(scope.known_issues),
        "accepted_risks": list(scope.accepted_risks),
        "trusted_assumptions": list(trusted),
        "dependency_assumptions": list(deps),
        "low_only_patterns": list(scope.low_only_patterns),
        "out_of_scope": list(scope.out_of_scope),
        "invalid_patterns": list(scope.invalid_patterns),
    }


def do_not_waste_time(scope: m.ScopeData) -> list[str]:
    """Tagged list of things not worth a researcher's time under this scope."""
    out: list[str] = []
    for item in scope.known_issues:
        out.append(f"[known-issue] {item}")
    for item in scope.accepted_risks:
        out.append(f"[accepted-risk] {item}")
    for item in (scope.trusted_roles + scope.admin_assumptions):
        out.append(f"[trusted-role] {item}")
    for item in (scope.trusted_integrations + scope.external_dependency_assumptions):
        out.append(f"[external-dependency] {item}")
    for item in scope.off_chain_assumptions:
        out.append(f"[off-chain-assumption] {item}")
    for item in scope.low_only_patterns:
        out.append(f"[low-only] {item}")
    for item in scope.out_of_scope:
        out.append(f"[out-of-scope] {item}")
    for item in scope.invalid_patterns:
        out.append(f"[invalid-pattern] {item}")
    if not out:
        out = [
            "[no-scope-file] No explicit scope file was provided. Confirm known issues, "
            "accepted risks, trusted roles, and out-of-scope areas manually before testing.",
            "[centralization] Do not submit centralization-only concerns unless the scope marks them valid.",
            "[low-only] Do not submit low-only or informational issues when the scope requires Medium/High impact.",
        ]
    return out


def _targets(matched: list[SurfaceRecord], limit: int = 6) -> list[str]:
    out: list[str] = []
    for r in matched[:limit]:
        src = f" ({r.source})" if r.source else ""
        out.append(f"{r.target}{src}")
    return out


def _lane_dict(ld: m.LaneDef, matched: list[SurfaceRecord], scope: m.ScopeData) -> dict:
    priority = _lane_priority(ld, matched, scope)
    assumptions: list[str] = []
    for r in matched:
        assumptions.extend(r.assumptions)
    relevant_known = _filter_lines(scope.known_issues, ld.keywords)
    relevant_accepted = _filter_lines(scope.accepted_risks, ld.keywords)
    relevant_trusted = _filter_lines(scope.trusted_roles + scope.admin_assumptions, ld.keywords)
    relevant_invalid = _filter_lines(scope.invalid_patterns + scope.low_only_patterns, ld.keywords)
    relevant_invariants = _filter_lines(scope.invariants, ld.keywords)
    invalid_conditions = [ld.what_is_likely_invalid] + relevant_invalid
    known_accepted = relevant_known + relevant_accepted + relevant_trusted
    return {
        "lane_id": ld.lane_id,
        "lane_name": ld.lane_name,
        "slug": ld.slug,
        "priority": priority,
        "scope": ld.what_can_be_valid,
        "why_it_matters": ld.why_it_matters,
        "target_files_functions": _targets(matched),
        "surface_count": len(matched),
        "linked_value_paths": [r.target for r in matched if "value" in " ".join(r.risk_signals).lower()][:6],
        "linked_blind_spots": [r.target for r in matched
                               if r.review_density in ("weak", "none", "unknown")][:6],
        "linked_interactions": sorted({t for r in matched for t in r.cross_contract_targets})[:6],
        "relevant_assumptions": sorted(set(assumptions))[:8] or relevant_invariants,
        "known_accepted_filters": known_accepted or ["None specific to this lane in the provided scope."],
        "high_impact_hypothesis_directions": list(ld.first_hypotheses),
        "local_test_strategy": (
            f"Write local Foundry tests for {ld.lane_name.lower()} surfaces: exercise the target, "
            f"assert the guarding invariant, and record pre/post state. {ld.stop_condition}"),
        "what_can_be_valid": ld.what_can_be_valid,
        "what_is_likely_invalid": ld.what_is_likely_invalid,
        "evidence_required": list(ld.required_evidence),
        "stop_conditions": [ld.stop_condition],
        "invalid_conditions": invalid_conditions,
        "task_categories": list(ld.task_categories),
        "human_review_required": True,
    }


def _common(kind: str, command: str, generated_at: str, scope: m.ScopeData, repo_summary: dict) -> dict:
    return {
        "schema_version": m.SCHEMA_VERSION,
        "arkheionx_version": PACKAGE_VERSION,
        "kind": kind,
        "command": command,
        "generated_at": generated_at,
        "scope_file_used": scope.scope_file_used,
        "repo_summary": repo_summary,
        "human_review_required": True,
        "safety_boundary": safety.SAFETY_BOUNDARY,
    }


def build_scope_lanes(rm: ReviewMap, root: Path | str, scope_file: str | None = None, *,
                      source_files: int = 0, test_files: int = 0) -> dict:
    scope = scope_parser.parse_scope_file(scope_file)
    ctx = build_repo_context(rm, root, source_files=source_files, test_files=test_files)
    records = ctx["records"]
    selected = select_lanes(records, scope)
    lanes = [_lane_dict(ld, matched, scope) for ld, matched in selected]
    lanes.sort(key=lambda d: (m.priority_rank(d["priority"]), d["lane_id"]))
    priorities = [{"lane_id": d["lane_id"], "lane_name": d["lane_name"], "priority": d["priority"]}
                  for d in lanes]
    data = _common(m.KIND_SCOPE_LANES, "scope-lanes", ctx["generated_at"], scope, ctx["repo_summary"])
    data.update({
        "lane_count": len(lanes),
        "lanes": lanes,
        "priorities": priorities,
        "filters": scope_filters(scope),
        "safety": safety.safety_block(),
    })
    return data


def _in_scope_surface_classes(records: list[SurfaceRecord], scope: m.ScopeData) -> list[str]:
    out: list[str] = []
    for ld, matched in select_lanes(records, scope):
        if matched or _scope_mentions_lane(ld, scope):
            out.append(ld.lane_name)
    return out


def build_scope_map(rm: ReviewMap, root: Path | str, scope_file: str | None = None, *,
                    source_files: int = 0, test_files: int = 0) -> dict:
    scope = scope_parser.parse_scope_file(scope_file)
    ctx = build_repo_context(rm, root, source_files=source_files, test_files=test_files)
    records = ctx["records"]

    trusted_assumptions = scope.trusted_roles + scope.admin_assumptions + scope.off_chain_assumptions
    dependency_assumptions = scope.trusted_integrations + scope.external_dependency_assumptions
    summary = scope.summary
    if not scope.scope_file_used or not summary:
        summary = (summary or "") + (
            " No explicit scope file was provided; this scope map is inferred from repository "
            "structure. Confirm the real program scope manually."
            if not scope.scope_file_used else "")
        summary = summary.strip()

    data = _common(m.KIND_SCOPE_MAP, "scope-map", ctx["generated_at"], scope, ctx["repo_summary"])
    data.update({
        "scope_summary": summary,
        "in_scope_surface_classes": _in_scope_surface_classes(records, scope),
        "in_scope": list(scope.in_scope),
        "out_of_scope": list(scope.out_of_scope),
        "severity_conditions": list(scope.severity_conditions),
        "requires_medium_high": scope_parser.requires_medium_high(scope),
        "trusted_assumptions": trusted_assumptions or [
            "No explicit trusted roles were provided; confirm the trust model manually."],
        "dependency_assumptions": dependency_assumptions or [
            "No explicit external-dependency assumptions were provided; confirm integrations manually."],
        "known_issues": list(scope.known_issues),
        "accepted_risks": list(scope.accepted_risks),
        "prior_audit_notes": list(scope.prior_audit_notes),
        "changed_since_audit": list(scope.changed_since_audit),
        "design_choices": list(scope.design_choices),
        "invariants": list(scope.invariants),
        "off_chain_assumptions": list(scope.off_chain_assumptions),
        "admin_assumptions": list(scope.admin_assumptions),
        "compliance_expectations": list(scope.compliance_expectations),
        "eip_expectations": list(scope.eip_expectations),
        "array_gas_limits": list(scope.array_gas_limits),
        "focus_areas": list(scope.focus_areas),
        "do_not_waste_time": do_not_waste_time(scope),
        "report_candidate_requirements": list(scope.report_candidate_requirements) or [
            "A local proof-of-concept test demonstrating the impact.",
            "A clear loss / lock / incorrect-accounting / unauthorized-action / invariant-break path.",
            "Confirmation the issue is not a known, accepted, or out-of-scope item.",
        ],
        "safety": safety.safety_block(),
    })
    return data
