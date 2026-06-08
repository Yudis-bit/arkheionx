"""Filter hypotheses / report candidates before submission (v7).

Critical for real contests: it classifies each candidate against the scope rules
(known issues, accepted risks, trusted-role assumptions, out-of-scope areas,
low-only patterns, duplicate-prone classes) and the local evidence judged so far,
so a researcher does not waste a submission on an invalid or duplicate report.

The report filter is not final triage. Human review is required.
"""
from __future__ import annotations

import json
from pathlib import Path

from arkheionx.review_map.model import ReviewMap
from arkheionx.version import PACKAGE_VERSION

from . import models as m
from . import safety
from . import scope_parser
from .lane_builder import scope_filters
from .task_builder import build_scope_tasks
from .evidence_judge import judge_evidence

# Bug classes that are commonly duplicated in contests (heuristic).
_DUP_PRONE = {
    m.TC_ORACLE, m.TC_SHARE_PRICE, m.TC_REPLAY, m.TC_ERC_COMPLIANCE,
    m.TC_PREVIEW_ACTUAL, m.TC_FEE_SLIPPAGE,
}
_LOW_ONLY_PRONE = {m.TC_ERC_COMPLIANCE, m.TC_PREVIEW_ACTUAL}
_TRUSTED_ROLE_PRONE = {m.TC_ADMIN_BOUNDARY, m.TC_AUTH_BYPASS}

PRE_SUBMISSION_CHECKLIST = [
    "Is it in scope?",
    "Is it not a known or accepted issue?",
    "Does it avoid relying only on trusted-role mistakes?",
    "Is the impact Medium/High under the scope rules?",
    "Is there a local proof-of-concept?",
    "Is there a clear loss / lock / incorrect-accounting / unauthorized-action / invariant-break path?",
    "Is it not merely a UX or spec deviation unless the impact qualifies?",
    "Is it not centralization-only?",
    "Is it not an external-dependency failure unless the scope marks it valid?",
    "Is the report minimal and evidence-backed?",
]


def _matches(text: str, items: list[str]) -> str | None:
    low = text.lower()
    for it in items:
        token = it.strip().lower()
        if not token:
            continue
        head = token.split(".")[0][:24]
        if head and head in low:
            return it
    return None


def _evidence_for_target(target: str, judged: list[dict]) -> dict | None:
    fn = target.split(".")[-1].lower()
    if not fn:
        return None
    # Prefer a judged item whose source mentions the function name.
    for rec in judged:
        if fn in rec.get("source", "").lower():
            return rec
    return None


def _classify(task: dict, scope: m.ScopeData, judged: list[dict], requires_mh: bool) -> dict:
    text = " ".join([task["title"], task["hypothesis"], task["target"], task["lane_name"]])
    category = task.get("category", "")
    ev = _evidence_for_target(task["target"], judged)
    ev_quality = ev.get("quality") if ev else "none"
    ev_judgment = ev.get("judgment") if ev else "none"

    classification = m.CLASS_NEEDS_HUMAN
    rationale = "Ambiguous under the provided scope; a human must classify it."
    submission_risk = "Confirm scope, evidence, and duplicate status before submitting."

    out = _matches(text, scope.out_of_scope)
    known = _matches(text, scope.known_issues)
    accepted = _matches(text, scope.accepted_risks)
    low_only = _matches(text, scope.low_only_patterns)

    if out:
        classification, rationale = m.CLASS_LIKELY_OUT_OF_SCOPE, f"Matches an out-of-scope area: {out}"
    elif known:
        classification, rationale = m.CLASS_LIKELY_KNOWN, f"Matches a known issue: {known}"
    elif accepted:
        classification, rationale = m.CLASS_LIKELY_ACCEPTED, f"Matches an accepted risk: {accepted}"
    elif category in _TRUSTED_ROLE_PRONE and (scope.trusted_roles or scope.admin_assumptions):
        classification = m.CLASS_LIKELY_TRUSTED_ROLE
        rationale = ("This class often depends on a trusted role; the scope marks trusted roles as "
                     "valid, so only report a path that does not rely on trusted-role misbehaviour.")
    elif low_only or (requires_mh and category in _LOW_ONLY_PRONE):
        classification = m.CLASS_LIKELY_LOW_ONLY
        rationale = ("Likely low-only impact; the scope requires Medium/High, so attach a qualifying "
                     "impact path or drop it.")
    elif ev_judgment == m.JUDGE_CANDIDATE:
        classification = m.CLASS_POTENTIALLY_REPORTABLE
        rationale = "A local test gives candidate-with-evidence support; this still requires human review and is not final triage."
    elif ev_judgment in (m.JUDGE_REJECTED_STRONG, m.JUDGE_REJECTED_MEDIUM):
        classification = m.CLASS_NOT_A_FINDING
        rationale = ("Local evidence indicates the guard holds here (rejected-with-evidence). This is not "
                     "proof the protocol has no bugs; re-check before discarding.")
    elif ev_quality in (m.QUALITY_WEAK, m.QUALITY_INVALID, m.QUALITY_INSUFFICIENT) or ev is None:
        if category in _DUP_PRONE:
            classification = m.CLASS_DUPLICATE_PRONE
            rationale = ("Common, duplicate-prone bug class with no strong local evidence yet; build a "
                         "differentiated PoC before submitting.")
        else:
            classification = m.CLASS_NEEDS_MORE_EVIDENCE
            rationale = "No strong local evidence yet; write the local test before considering a report."

    if category in _DUP_PRONE:
        submission_risk = "Duplicate-prone class: many researchers test it. Differentiate the impact path."

    return {
        "candidate_id": "",
        "source_task": task["task_id"],
        "hypothesis": task["hypothesis"],
        "lane": task["lane_name"],
        "lane_id": task["lane_id"],
        "category": category,
        "target": task["target"],
        "classification": classification,
        "evidence": (f"{ev['evidence_id']} ({ev_quality}/{ev_judgment})" if ev else "none"),
        "impact_path": task["why_it_might_matter"],
        "why": rationale,
        "remaining_questions": [
            "Is the impact path demonstrated by a passing local test?",
            "Is it confirmed in-scope and not a known/accepted issue?",
            task["report_candidate_threshold"],
        ],
        "submission_risk": submission_risk,
        "human_review_required": True,
    }


def filter_report_candidates(rm: ReviewMap, root: Path | str, scope_file: str | None = None, *,
                             source_files: int = 0, test_files: int = 0,
                             tasks_data: dict | None = None, judge_data: dict | None = None) -> dict:
    scope = scope_parser.parse_scope_file(scope_file)
    requires_mh = scope_parser.requires_medium_high(scope)
    if tasks_data is None:
        tasks_data = build_scope_tasks(rm, root, scope_file, source_files=source_files, test_files=test_files)
    if judge_data is None:
        judge_data = judge_evidence(rm, root, scope_file, source_files=source_files, test_files=test_files)
    judged = judge_data.get("judged_evidence", [])

    candidates: list[dict] = []
    for i, task in enumerate(tasks_data.get("tasks", []), 1):
        c = _classify(task, scope, judged, requires_mh)
        c["candidate_id"] = f"CAND-{i:03d}"
        candidates.append(c)

    counts = {label: 0 for label in m.CLASSIFICATIONS}
    for c in candidates:
        counts[c["classification"]] = counts.get(c["classification"], 0) + 1

    return {
        "schema_version": m.SCHEMA_VERSION,
        "arkheionx_version": PACKAGE_VERSION,
        "kind": m.KIND_REPORT_FILTER,
        "command": "report-filter",
        "generated_at": rm.generated_at,
        "scope_file_used": scope.scope_file_used,
        "repo_summary": tasks_data.get("repo_summary", {}),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "classifications": counts,
        "filters": scope_filters(scope),
        "checklist": list(PRE_SUBMISSION_CHECKLIST),
        "requires_medium_high": requires_mh,
        "human_review_required": True,
        "safety_boundary": safety.SAFETY_BOUNDARY,
        "safety": safety.safety_block(),
    }
