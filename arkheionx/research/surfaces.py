"""Research surface engine (v4.1): coverage ranking + authorization, periphery,
and behavior-mismatch surfaces.

Consumes an already-built :class:`~arkheionx.review_map.model.ReviewMap` and the
repository root, and adds review-oriented surfaces by statically scanning the
source files the review map already located. Everything here is heuristic and
labelled as such. Surfaces are review prompts, never findings; all test
suggestions are local-test directions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from arkheionx.review_map.model import ReviewMap, priority_rank

from . import signals as sig

# Coverage signals (heuristic; name/test evidence only).
TESTED = "tested"
NO_DIRECT_TEST = "no direct test observed"
PARTIAL = "partially tested"
UNKNOWN = "unknown"

# Coverage-weakness priority buckets (review order, never severity).
INSPECT_FIRST = "inspect-first"
IMPORTANT_LOWER = "important-lower-priority"
MAYBE_LATER = "maybe-later"
MONITOR = "monitor"
_BUCKET_ORDER = {INSPECT_FIRST: 0, IMPORTANT_LOWER: 1, MAYBE_LATER: 2, MONITOR: 3}

_WEAK_COVERAGE = {NO_DIRECT_TEST, PARTIAL, UNKNOWN}


@dataclass
class ResearchSurfaces:
    """All v4.1 research surfaces derived from one review map (JSON-ready dicts)."""

    coverage_ranking: list[dict] = field(default_factory=list)
    authorization_surfaces: list[dict] = field(default_factory=list)
    periphery_surfaces: list[dict] = field(default_factory=list)
    behavior_mismatch_surfaces: list[dict] = field(default_factory=list)
    # display_id -> set of contributing signal kinds (for coverage ranking).
    auth_by_function: dict[str, set] = field(default_factory=dict)
    periphery_by_function: dict[str, set] = field(default_factory=dict)


def _read_lines(root: Path, rel_path: str) -> list[str]:
    """Read a source file's lines. Resolves repo-relative or absolute paths."""
    for candidate in (Path(rel_path), root / rel_path):
        try:
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
    return []


def _source_ref(path: str, line: int) -> str:
    return f"{path}:{line}" if path and line > 0 else (path or "")


def _files_with_functions(rm: ReviewMap) -> dict[str, str]:
    """Map each source file path to a representative contract name."""
    files: dict[str, str] = {}
    for cs in rm.contracts:
        if cs.path:
            files.setdefault(cs.path, cs.name)
    for fs in rm.functions:
        if fs.path:
            files.setdefault(fs.path, fs.contract)
    return files


# --------------------------------------------------------------------------
# Authorization surfaces (Phase 5)
# --------------------------------------------------------------------------
def build_authorization_surfaces(rm: ReviewMap, root: Path) -> list[dict]:
    rows: dict[tuple, dict] = {}
    for path, default_contract in _files_with_functions(rm).items():
        lines = _read_lines(root, path)
        if not lines:
            continue
        spans = sig.function_spans(rm.functions, path, lines)
        for m in sig.scan_auth(lines, spans, default_contract):
            key = (m.contract, m.function, m.signal)
            if key in rows:
                continue
            rows[key] = {
                "contract": m.contract,
                "function": m.function,
                "target": f"{m.contract}.{m.function}" if m.function else m.contract,
                "source": _source_ref(path, m.line),
                "signal": m.signal,
                "kind": m.kind,
                "why_it_matters": m.why,
                "suggested_local_tests": list(m.tests),
                "evidence_level": "HEURISTIC",
                "manual_review_required": True,
            }
    return sorted(rows.values(), key=lambda r: (r["contract"], r["function"], r["signal"]))


# --------------------------------------------------------------------------
# Periphery / core surfaces (Phase 6)
# --------------------------------------------------------------------------
_DIRECT_VS_PERIPHERY = "direct call vs periphery call produce identical accounting"
_STATE_BEFORE_AFTER = "core accounting state before vs after the periphery call is consistent"
_SKIP_ON_REVERT = "a malformed item, or one failed item among many, behaves as documented (skip-on-revert / continue-on-error) and does not revert earlier than documented"
_CALLBACK_SAFETY = "callback caller/state assumptions hold (reentrancy / unexpected caller)"


def _name_matches(name: str, spec) -> bool:
    if spec.mode == sig.WORD:
        return name == spec.patterns[0] or any(p == name for p in spec.patterns)
    return any(p in name for p in spec.patterns)


def _periphery_keyword_hits(fs_by_id: dict, spans: list[sig.FunctionSpan]) -> dict[str, set]:
    """Periphery keyword hits by function name (not arbitrary lines).

    Only the function name is matched; cross-contract calls, try/catch, loops,
    and low-level calls are detected separately from code. This keeps internal
    helpers from inheriting a periphery label from their contract name.
    """
    hits: dict[str, set] = {}
    for span in spans:
        name = span.name.lower()
        for spec in sig.PERIPHERY_KEYWORD_SPECS:
            if _name_matches(name, spec):
                hits.setdefault(span.display_id, set()).add(spec.kind)
    return hits


def build_periphery_surfaces(rm: ReviewMap, root: Path) -> list[dict]:
    fs_by_id = {f.display_id: f for f in rm.functions}
    rows: list[dict] = []
    for path, _default in _files_with_functions(rm).items():
        lines = _read_lines(root, path)
        if not lines:
            continue
        spans = sig.function_spans(rm.functions, path, lines)
        keyword_hits = _periphery_keyword_hits(fs_by_id, spans)
        for span in spans:
            fs = fs_by_id.get(span.display_id)
            if fs is None:
                continue
            code = sig.analyze_function_code(lines, span)
            interaction: list[str] = []
            if span.display_id in keyword_hits:
                interaction.append("periphery-keyword")
            if code.has_low_level_call:
                interaction.append("low-level-call")
            if code.has_try_catch:
                interaction.append("try-catch")
            if code.has_loop and (code.cross_contract_calls or code.has_low_level_call):
                interaction.append("loop-with-external-call")
            if code.cross_contract_calls:
                interaction.append("cross-contract-call")
            if not interaction:
                continue
            tests = [_DIRECT_VS_PERIPHERY, _STATE_BEFORE_AFTER]
            if code.has_try_catch or code.has_loop:
                tests.append(_SKIP_ON_REVERT)
            if "callback" in keyword_hits.get(span.display_id, set()) or code.has_low_level_call:
                tests.append(_CALLBACK_SAFETY)
            why = (
                "This function calls into other contracts and/or runs partial-failure "
                "logic, then participates in accounting. Periphery/core mismatches and "
                "partial-failure behavior are worth review here."
            )
            rows.append({
                "contract": span.contract,
                "function": span.name,
                "target": span.display_id,
                "core_targets": list(code.cross_contract_calls),
                "source": _source_ref(path, span.start),
                "interaction_type": sorted(set(interaction)),
                "why_it_matters": why,
                "suggested_local_tests": tests,
                "evidence_level": "HEURISTIC",
                "manual_review_required": True,
            })
    return sorted(rows, key=lambda r: (priority_rank(_fs_priority(fs_by_id, r["target"])), r["target"]))


def _fs_priority(fs_by_id: dict, display_id: str) -> str:
    fs = fs_by_id.get(display_id)
    return fs.review_priority if fs else "low"


# --------------------------------------------------------------------------
# Behavior-mismatch surfaces (Phase 7)
# --------------------------------------------------------------------------
def build_behavior_surfaces(rm: ReviewMap, root: Path) -> list[dict]:
    fs_by_id = {f.display_id: f for f in rm.functions}
    rows: dict[tuple, dict] = {}
    for path, default_contract in _files_with_functions(rm).items():
        lines = _read_lines(root, path)
        if not lines:
            continue
        spans = sig.function_spans(rm.functions, path, lines)
        # Comment/string word signals.
        for m in sig.scan_behavior(lines, spans, default_contract):
            key = (m.contract, m.function, m.signal)
            if key in rows:
                continue
            rows[key] = _behavior_row(path, m.line, m.contract, m.function, m.signal, m.kind, m.why, m.tests)
        # Code-pattern signals (try/catch, loop+require, loop+external call).
        for span in spans:
            code = sig.analyze_function_code(lines, span)
            if code.has_try_catch:
                key = (span.contract, span.name, "try-catch")
                rows.setdefault(key, _behavior_row(
                    path, span.start, span.contract, span.name, "try-catch", "partial-failure",
                    "A try/catch block exists. Confirm computation before the external call "
                    "cannot revert earlier than the documented catch/skip handler.",
                    ("a failing inner call is caught/skipped as documented",
                     "a pre-call computation revert is handled as documented"),
                ))
            if code.has_require_in_loop:
                key = (span.contract, span.name, "require-in-loop")
                rows.setdefault(key, _behavior_row(
                    path, span.start, span.contract, span.name, "require-in-loop", "partial-failure",
                    "A require runs inside a loop over items. Confirm one bad item does not "
                    "revert the whole batch unless that is the documented behavior.",
                    ("one malformed item among many behaves as documented",)))
    return sorted(rows.values(), key=lambda r: (priority_rank(_fs_priority(fs_by_id, r["target"])), r["target"], r["signal"]))


def _behavior_row(path, line, contract, function, signal, kind, why, tests) -> dict:
    return {
        "label": "Potential behavior-mismatch review surface",
        "contract": contract,
        "function": function,
        "target": f"{contract}.{function}" if function else contract,
        "source": _source_ref(path, line),
        "signal": signal,
        "kind": kind,
        "why_it_may_matter": why,
        "suggested_local_test": list(tests),
        "evidence_level": "HEURISTIC",
        "manual_review_required": True,
    }


# --------------------------------------------------------------------------
# Coverage weakness ranking (Phase 4)
# --------------------------------------------------------------------------
def _coverage_signal(fs) -> str:
    if fs.test_references:
        return TESTED
    if fs.value_direction != "none" or fs.risk_signals:
        return NO_DIRECT_TEST
    return UNKNOWN


_RISK_LABEL = {
    "value-out": "value exit",
    "value-in": "value entry",
    "oracle-dependent": "oracle",
    "external-call": "external call/callback",
    "privileged": "admin control",
    "debt-or-liquidation": "liquidation",
}


def _risk_labels(fs, auth_kinds: set, is_periphery: bool) -> list[str]:
    labels: list[str] = []
    for s in fs.risk_signals:
        if s in _RISK_LABEL:
            labels.append(_RISK_LABEL[s])
    if fs.mutability == "state-changing" and (fs.value_direction != "none" or "value-out" in fs.risk_signals):
        labels.append("accounting mutation")
    if auth_kinds:
        labels.append("authorization")
        if auth_kinds & {"signature", "merkle", "domain", "replay"}:
            labels.append("signature/Merkle")
    if is_periphery:
        labels.append("periphery/core interaction")
    # Deterministic, de-duplicated order.
    seen: list[str] = []
    for lbl in labels:
        if lbl not in seen:
            seen.append(lbl)
    return seen


def _is_high_value(fs, auth_kinds: set, is_periphery: bool) -> bool:
    return fs.review_priority == "high" or bool(auth_kinds) or is_periphery


def _bucket(high_value: bool, coverage: str, value_relevant: bool) -> tuple[str, str]:
    weak = coverage in _WEAK_COVERAGE
    if high_value and weak:
        return INSPECT_FIRST, "High-value surface with weak coverage — inspect first."
    if high_value and coverage == TESTED:
        return IMPORTANT_LOWER, "High-value surface with a direct test observed — important, lower immediate priority."
    if not high_value and weak and value_relevant:
        return MAYBE_LATER, "Lower-value surface with weak coverage — review later."
    if weak:
        return MONITOR, "Weak coverage but limited value relevance — monitor."
    return MONITOR, "Coverage observed — monitor."


def build_coverage_ranking(rm: ReviewMap, auth_by_function: dict[str, set], periphery_by_function: dict[str, set]) -> list[dict]:
    rows: list[dict] = []
    for fs in rm.functions:
        auth_kinds = auth_by_function.get(fs.display_id, set())
        is_periphery = fs.display_id in periphery_by_function
        value_relevant = fs.value_direction != "none" or bool(fs.risk_signals)
        # Skip pure low-priority views with no value/auth/periphery relevance.
        if not value_relevant and not auth_kinds and not is_periphery and fs.review_priority == "low":
            continue
        coverage = _coverage_signal(fs)
        high_value = _is_high_value(fs, auth_kinds, is_periphery)
        bucket, reason = _bucket(high_value, coverage, value_relevant)
        rows.append({
            "surface": fs.display_id,
            "source": _source_ref(fs.path, fs.line),
            "risk_signals": _risk_labels(fs, auth_kinds, is_periphery),
            "coverage_signal": coverage,
            "review_priority": fs.review_priority,
            "weakness_priority": bucket,
            "reason": reason,
            "basis": "heuristic (name/value-flow/test-reference signals only)",
        })
    rows.sort(key=lambda r: (_BUCKET_ORDER.get(r["weakness_priority"], 9), priority_rank(r["review_priority"]), r["surface"]))
    return rows


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------
def build_research_surfaces(rm: ReviewMap, root: Path) -> ResearchSurfaces:
    auth = build_authorization_surfaces(rm, root)
    periphery = build_periphery_surfaces(rm, root)
    behavior = build_behavior_surfaces(rm, root)

    auth_by_function: dict[str, set] = {}
    for row in auth:
        if row["function"]:
            auth_by_function.setdefault(row["target"], set()).add(row["kind"])
    periphery_by_function: dict[str, set] = {}
    for row in periphery:
        periphery_by_function.setdefault(row["target"], set()).update(row["interaction_type"])

    coverage = build_coverage_ranking(rm, auth_by_function, periphery_by_function)
    return ResearchSurfaces(
        coverage_ranking=coverage,
        authorization_surfaces=auth,
        periphery_surfaces=periphery,
        behavior_mismatch_surfaces=behavior,
        auth_by_function=auth_by_function,
        periphery_by_function=periphery_by_function,
    )
