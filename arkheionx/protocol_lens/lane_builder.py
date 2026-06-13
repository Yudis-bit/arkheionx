"""Build lens review lanes and the combined protocol-aware lens map.

Review lanes are the lens's canonical research tracks (LANE-01 .. LANE-10 for
Fixed Credit Market), bound to discovered repository surfaces, enriched with the
scope's focus and filters. Lanes are planning artifacts, never findings; lane
priority is review order, never severity. Human review is required.
"""
from __future__ import annotations

from . import models as m
from . import safety
from .common import (
    bind_lane,
    common_header,
    lane_priority,
    scope_filters,
    scope_mentions_lane,
    scope_status,
)


def _bind_refs(ctx: dict, function_hints: list[str], state_vars: list[str]) -> tuple[list[str], list[str]]:
    """Resolve (files, function targets) for a set of function/state hints."""
    records = ctx["records"]
    term_files: dict[str, list[str]] = ctx["term_files"]
    hints = [h.lower() for h in function_hints if h]
    files: list[str] = []
    functions: list[str] = []
    for rec in records:
        fn = (rec.function or "").lower()
        if fn and any(h in fn for h in hints):
            if rec.target not in functions:
                functions.append(rec.target)
            f = (rec.source or "").split(":", 1)[0]
            if f and f not in files:
                files.append(f)
    for sv in state_vars:
        for f in term_files.get(sv.lower(), []):
            if f not in files:
                files.append(f)
    return files[:12], functions[:12]


def _scope_basis(lane_def: m.LensLaneDef, scope) -> str:
    if scope_mentions_lane(lane_def, scope):
        focus_blob = " ".join(getattr(scope, "focus_areas", [])).lower()
        if any(k in focus_blob for k in lane_def.focus_keywords):
            return "scope focus area"
        return "scope mentions this lane"
    if getattr(scope, "scope_file_used", False):
        return "lens default (not specifically highlighted by scope)"
    return f"lens default ({m.SCOPE_INCOMPLETE_LOCAL_ONLY})"


def build_review_lanes(ctx: dict) -> dict:
    lens = ctx["lens"]
    scope = ctx["scope"]
    lanes: list[dict] = []
    for ld in lens.review_lanes():
        b = bind_lane(ctx, ld)
        lane = m.ReviewLane(
            id=ld.lane_id,
            title=ld.title,
            priority=lane_priority(ld, b["matched_records"], scope),
            scope_basis=_scope_basis(ld, scope),
            source_files=b["source_files"],
            functions=b["functions"],
            state_variables=b["state_variables"],
            invariants_at_risk=list(ld.invariants_at_risk),
            promises_at_risk=list(ld.promises_at_risk),
            why_this_lane_matters=ld.why_this_lane_matters,
            first_hypotheses=list(ld.first_hypotheses),
            required_evidence=list(ld.required_evidence),
            stop_condition=ld.stop_condition,
        )
        lanes.append(lane.to_dict())
    lanes.sort(key=lambda d: (m.priority_rank(d["priority"]), d["id"]))

    data = common_header(m.KIND_LENS_LANES, "lens-lanes", ctx)
    data.update({
        "lane_count": len(lanes),
        "lanes": lanes,
        "mandatory_lane_ids": [ld.lane_id for ld in lens.review_lanes()],
        "priorities": [{"lane_id": d["id"], "title": d["title"], "priority": d["priority"]} for d in lanes],
        "filters": scope_filters(scope),
        "safety": safety.safety_block(),
    })
    return data


def _promise_dict(ctx: dict, promise: m.BehaviorPromise) -> dict:
    files, functions = _bind_refs(ctx, promise.relevant_functions, promise.state_variables)
    d = promise.to_dict()
    d["relevant_files"] = files or [m.UNKNOWN_IN_LOCAL_REPO]
    d["bound_functions"] = functions or [m.UNKNOWN_IN_LOCAL_REPO]
    if not d.get("existing_evidence"):
        d["existing_evidence"] = [m.UNKNOWN_IN_LOCAL_REPO]
    return d


def _invariant_dict(ctx: dict, inv: m.EconomicInvariant) -> dict:
    files, functions = _bind_refs(ctx, inv.relevant_functions, inv.state_variables)
    d = inv.to_dict()
    d["relevant_files"] = files or [m.UNKNOWN_IN_LOCAL_REPO]
    d["bound_functions"] = functions or [m.UNKNOWN_IN_LOCAL_REPO]
    if not d.get("existing_direct_tests"):
        d["existing_direct_tests"] = [m.UNKNOWN_IN_LOCAL_REPO]
    return d


def _scope_map_block(ctx: dict) -> dict:
    scope = ctx["scope"]
    from .common import requires_medium_high
    trusted = scope.trusted_roles + scope.admin_assumptions + scope.off_chain_assumptions
    deps = scope.trusted_integrations + scope.external_dependency_assumptions
    return {
        "scope_status": scope_status(scope),
        "scope_summary": scope.summary or (
            "No scope file provided; this map is inferred from repository structure. "
            "Confirm the real program scope manually." if not scope.scope_file_used else ""),
        "in_scope": list(scope.in_scope),
        "out_of_scope": list(scope.out_of_scope),
        "requires_medium_high": requires_medium_high(scope),
        "trusted_assumptions": trusted or ["No explicit trusted roles provided; confirm the trust model manually."],
        "dependency_assumptions": deps or ["No explicit dependency assumptions provided; confirm integrations manually."],
        "known_issues": list(scope.known_issues),
        "accepted_risks": list(scope.accepted_risks),
        "invariants": list(scope.invariants),
        "focus_areas": list(scope.focus_areas),
        "filters": scope_filters(scope),
    }


def build_lens_map(ctx: dict) -> dict:
    """The combined protocol-aware map: protocol model + scope + promises + invariants."""
    lens = ctx["lens"]
    data = common_header(m.KIND_LENS_MAP, "lens-map", ctx)
    data.update({
        "protocol_model": ctx["protocol_model"],
        "scope_map": _scope_map_block(ctx),
        "value_flow_paths": ctx["protocol_model"].get("value_flow_paths", []),
        "behavior_promises": [_promise_dict(ctx, p) for p in lens.behavior_promises()],
        "economic_invariants": [_invariant_dict(ctx, i) for i in lens.economic_invariants()],
        "temporal_windows": [w.to_dict() for w in lens.temporal_windows()],
        "in_scope_lane_titles": [ld.title for ld in lens.review_lanes()],
        "safety": safety.safety_block(),
    })
    return data
