"""Shared helpers for the lens builders (headers, binding, priority, filters).

Leaf-ish module: imports only models/safety and the lower v7 layer, so every
builder can share it without an import cycle.
"""
from __future__ import annotations

from arkheionx.scope_orchestration import scope_parser as _v7_scope_parser
from arkheionx.scope_orchestration.lane_builder import scope_filters as _v7_scope_filters
from arkheionx.version import PACKAGE_VERSION

from . import models as m
from . import safety
from .base import ProtocolLens

ARKHEIONX_VERSION = PACKAGE_VERSION

# Re-exported so builders can use one import site.
scope_filters = _v7_scope_filters
requires_medium_high = _v7_scope_parser.requires_medium_high


def scope_status(scope) -> str:
    """``SCOPE_INCOMPLETE_LOCAL_ONLY`` when no scope file was provided."""
    return "complete" if getattr(scope, "scope_file_used", False) else m.SCOPE_INCOMPLETE_LOCAL_ONLY


def rec_haystack(rec) -> str:
    bits = [rec.target, rec.contract, rec.function, rec.source]
    bits += rec.risk_signals + rec.auth_kinds + rec.periphery_interactions + rec.behavior_signals
    return " ".join(b for b in bits if b).lower()


def lane_matches_record(lane_def: m.LensLaneDef, rec) -> bool:
    h = rec_haystack(rec)
    return any(k in h for k in lane_def.focus_keywords)


def scope_mentions_lane(lane_def: m.LensLaneDef, scope) -> bool:
    blob = scope.haystack() if hasattr(scope, "haystack") else ""
    if not blob:
        return False
    return any(k in blob for k in lane_def.focus_keywords)


def _bump(priority: str) -> str:
    order = [m.PRIORITY_MONITOR, m.PRIORITY_MEDIUM, m.PRIORITY_HIGH, m.PRIORITY_VERY_HIGH]
    i = order.index(priority) if priority in order else 0
    return order[min(i + 1, len(order) - 1)]


def lane_priority(lane_def: m.LensLaneDef, matched: list, scope) -> str:
    """Base on the lens default; bump one level if the scope asks to focus here."""
    priority = lane_def.default_priority
    focus_blob = " ".join(getattr(scope, "focus_areas", []) + getattr(scope, "changed_since_audit", [])).lower()
    if focus_blob and any(k in focus_blob for k in lane_def.focus_keywords):
        priority = _bump(priority)
    return priority


def state_vars_for(lens: ProtocolLens, lane_def: m.LensLaneDef) -> list[str]:
    """Gather state variables from the lane's invariants and promises."""
    inv_by_id = lens.invariant_by_id()
    prom_by_id = lens.promise_by_id()
    out: list[str] = []
    for iid in lane_def.invariants_at_risk:
        inv = inv_by_id.get(iid)
        if inv:
            out.extend(inv.state_variables)
    for pid in lane_def.promises_at_risk:
        prom = prom_by_id.get(pid)
        if prom:
            out.extend(prom.state_variables)
    # Deterministic, de-duplicated.
    seen: dict[str, None] = {}
    for s in out:
        seen.setdefault(s, None)
    return list(seen)


def functions_for(lens: ProtocolLens, lane_def: m.LensLaneDef) -> list[str]:
    """Function-name hints for a lane, from its invariants and promises."""
    inv_by_id = lens.invariant_by_id()
    prom_by_id = lens.promise_by_id()
    out: list[str] = []
    for iid in lane_def.invariants_at_risk:
        inv = inv_by_id.get(iid)
        if inv:
            out.extend(inv.relevant_functions)
    for pid in lane_def.promises_at_risk:
        prom = prom_by_id.get(pid)
        if prom:
            out.extend(prom.relevant_functions)
    seen: dict[str, None] = {}
    for s in out:
        seen.setdefault(s.lower(), None)
    return list(seen)


def bind_lane(ctx: dict, lane_def: m.LensLaneDef) -> dict:
    """Bind a lane to repository surfaces, source files, functions, and state vars."""
    lens: ProtocolLens = ctx["lens"]
    records = ctx["records"]
    term_files: dict[str, list[str]] = ctx["term_files"]

    matched = [r for r in records if lane_matches_record(lane_def, r)]
    fn_targets = [r.target for r in matched[:8]]
    src_files: list[str] = []
    for r in matched:
        f = (r.source or "").split(":", 1)[0]
        if f and f not in src_files:
            src_files.append(f)
    # Add files where the lane's focus keywords were discovered as terms.
    for kw in lane_def.focus_keywords:
        for f in term_files.get(kw.lower(), []):
            if f not in src_files:
                src_files.append(f)
    if not fn_targets:
        fn_targets = functions_for(lens, lane_def)
    return {
        "matched_records": matched,
        "source_files": src_files[:12] or [m.UNKNOWN_IN_LOCAL_REPO],
        "functions": fn_targets[:12] or [m.UNKNOWN_IN_LOCAL_REPO],
        "state_variables": state_vars_for(lens, lane_def) or [m.UNKNOWN_IN_LOCAL_REPO],
    }


def common_header(kind: str, command: str, ctx: dict) -> dict:
    """The shared header object embedded in every lens JSON artifact."""
    lens: ProtocolLens = ctx["lens"]
    scope = ctx["scope"]
    return {
        "schema_version": m.SCHEMA_VERSION,
        "lens_layer": m.LENS_LAYER,
        "arkheionx_version": ARKHEIONX_VERSION,
        "kind": kind,
        "command": command,
        "lens": lens.meta().to_dict(),
        "generated_at": ctx["generated_at"],
        "scope_file_used": getattr(scope, "scope_file_used", False),
        "scope_status": scope_status(scope),
        "repo_summary": ctx["repo_summary"],
        "human_review_required": True,
        "safety_boundary": safety.SAFETY_BOUNDARY,
    }
