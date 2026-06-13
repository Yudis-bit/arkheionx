"""Classify report candidates before submission (section 15).

Runs the pre-submission checklist over candidates surfaced by the evidence judge and
assigns one of six outcomes. It never outputs "submit now": the most positive
outcome is ``READY_FOR_HUMAN_REVIEW`` and even that means a human must decide. Weak,
out-of-scope, duplicate-prone, or invalid candidates are blocked. Local/static only.
"""
from __future__ import annotations

from pathlib import Path

from . import models as m
from . import safety
from .common import common_header, requires_medium_high
from .evidence_judge import judge_evidence

# The section 15 pre-submission checklist (human-facing).
PRE_SUBMISSION_CHECKLIST = (
    "Is impact in scope?",
    "Is the actor realistic?",
    "Is the transaction path realistic?",
    "Does the PoC compile?",
    "Does the PoC run?",
    "Is protocol src unmodified?",
    "Is impact material?",
    "Is this more than dust?",
    "Is this not trusted-role behavior?",
    "Is this not user error?",
    "Is this not documented behavior?",
    "Is this not duplicate-only?",
    "Are exact source lines known?",
    "Is mitigation clear?",
    "Is severity justified by numbers?",
)


def _checklist_for(grade: dict) -> dict:
    """Map an EvidenceGrade dict to checklist answers (yes/no/unknown)."""
    g = grade
    return {
        "impact_in_scope": g.get("scoped_contracts", m.EV_UNKNOWN),
        "actor_realistic": g.get("realistic_actors", m.EV_UNKNOWN),
        "tx_path_realistic": m.EV_UNKNOWN,
        "poc_compiles": g.get("does_compile", m.EV_UNKNOWN),
        "poc_runs": g.get("does_run", m.EV_UNKNOWN),
        "src_unmodified": "assumed-yes (confirm: never modify protocol source)",
        "impact_material": g.get("proves_value_movement", "no"),
        "more_than_dust": g.get("quantifies_impact", "no"),
        "not_trusted_role": g.get("no_trusted_role_assumption", m.EV_UNKNOWN),
        "not_user_error": m.EV_UNKNOWN,
        "not_documented_behavior": m.EV_UNKNOWN,
        "not_duplicate_only": g.get("addresses_duplicate_risk", "no"),
        "exact_source_lines_known": m.EV_UNKNOWN,
        "mitigation_clear": m.EV_UNKNOWN,
        "severity_by_numbers": g.get("quantifies_impact", "no"),
    }


def _outcome_for(grade: dict, checklist: dict) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if grade.get("grade") == m.GRADE_F or grade.get("decision") == m.JUDGE_INSUFFICIENT_EVIDENCE:
        if grade.get("grade") == m.GRADE_F:
            reasons.append("Invalid setup: no assertion / cannot support a conclusion.")
            return m.REPORT_DO_NOT_SUBMIT_INVALID_SETUP, reasons
    if checklist["impact_in_scope"] == "no":
        reasons.append("Candidate is not shown to be in scope.")
        return m.REPORT_DO_NOT_SUBMIT_OUT_OF_SCOPE, reasons
    if checklist["not_duplicate_only"] != "yes" and grade.get("addresses_duplicate_risk") == "no":
        # Not auto-blocked, but flagged; only block when impact is also weak.
        pass
    if checklist["impact_material"] != "yes" or checklist["more_than_dust"] != "yes":
        reasons.append("Impact is not shown to be material / more than dust locally.")
        return m.REPORT_DO_NOT_SUBMIT_WEAK_IMPACT, reasons
    # Material impact asserted, but static analysis cannot confirm compile+run+scope.
    if grade.get("does_run") != "yes" or checklist["impact_in_scope"] != "yes":
        reasons.append("Local run / scope not yet confirmed; strengthen evidence and confirm scope.")
        return m.REPORT_NEEDS_MORE_EVIDENCE, reasons
    reasons.append("All static checks favourable; a human must still make the final call.")
    return m.REPORT_READY_FOR_HUMAN_REVIEW, reasons


def build_report_filter(ctx: dict, root: Path | str, judge_data: dict | None = None) -> dict:
    root = Path(root)
    if judge_data is None:
        judge_data = judge_evidence(ctx, root)
    scope = ctx["scope"]

    decisions: list[dict] = []
    # Candidates are judge grades that a human might consider (exclude clear invalids
    # only after recording them as blocked).
    for i, g in enumerate(judge_data.get("grades", []), start=1):
        checklist = _checklist_for(g)
        outcome, reasons = _outcome_for(g, checklist)
        if requires_medium_high(scope) and checklist["severity_by_numbers"] != "yes" \
                and outcome == m.REPORT_NEEDS_MORE_EVIDENCE:
            reasons.append("Scope requires Medium/High impact justified by numbers.")
        dec = m.ReportFilterDecision(
            candidate_id=f"CAND-{i:03d}",
            title=g.get("test_name", ""),
            checklist=checklist,
            outcome=outcome,
            reasons=reasons,
        )
        decisions.append(dec.to_dict())

    counts: dict[str, int] = {o: 0 for o in m.REPORT_OUTCOMES}
    for d in decisions:
        counts[d["outcome"]] = counts.get(d["outcome"], 0) + 1

    data = common_header(m.KIND_LENS_REPORT_FILTER, "lens-report-filter", ctx)
    data.update({
        "checklist": list(PRE_SUBMISSION_CHECKLIST),
        "outcomes_vocabulary": list(m.REPORT_OUTCOMES),
        "candidate_count": len(decisions),
        "decisions": decisions,
        "outcome_counts": counts,
        "requires_medium_high": requires_medium_high(scope),
        "note": "The report filter never says 'submit now'. Human decision required for every candidate.",
        "safety": safety.safety_block(),
    })
    return data
