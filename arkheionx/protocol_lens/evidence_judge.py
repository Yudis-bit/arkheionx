"""Judge whether local tests/evidence prove a lens task (section 14).

This reads local test files (and optional local-validation / PoC notes), grades any
discovered candidate test on a transparent rubric, and assigns an evidence grade
(A-F) and a decision. It is local/static: it never runs ``forge`` and never
compiles. Grade A — a strong local proof of a material economic violation — is a
human judgment; this static judge will not auto-assign A and will not auto-emit
``VALIDATED_CANDIDATE``. Candidate-with-evidence is not a confirmed vulnerability.
"""
from __future__ import annotations

import re
from pathlib import Path

from arkheionx.protocol.semantic_adapter import find_solidity_files

from . import models as m
from . import safety
from .common import common_header

_MAX_FILE_BYTES = 2_000_000
_ASSERT_RE = re.compile(r"\bassert(?:Eq|Gt|Lt|Ge|Le|True|False|Approx[A-Za-z]*)?\b")
_REVERT_RE = re.compile(r"\bvm\.expectRevert\b|\bexpectRevert\b")
_BALANCE_RE = re.compile(r"\bbalanceOf\b|\bbalance\b|delta|withdrawable|credit|debt|collateral", re.IGNORECASE)
_ACTORS_RE = re.compile(r"\bmakeAddr\b|\bvm\.prank\b|\bvm\.startPrank\b|\baddress\s*\(", re.IGNORECASE)
_TEST_FN_RE = re.compile(r"function\s+(test\w*|invariant_\w+)\s*\(")
_RUN_PASS_RE = re.compile(r"\[PASS\]|test result:|Suite result:", re.IGNORECASE)
_RUN_NOTE_DIRS = (".arkheionx/lens-pack", ".arkheionx/runs", ".arkheionx/private", "test", "tests")

RUBRIC = (
    ("does_compile", "Does the test compile locally?"),
    ("does_run", "Does the test run locally (forge test), recorded in a local note?"),
    ("realistic_actors", "Does it use realistic, untrusted actors?"),
    ("scoped_contracts", "Does it exercise only in-scope contracts?"),
    ("no_trusted_role_assumption", "Does it avoid relying on trusted-role misbehaviour?"),
    ("no_weird_token_assumption", "Does it avoid unrealistic token assumptions?"),
    ("proves_value_movement", "Does it demonstrate concrete value movement?"),
    ("quantifies_impact", "Does it quantify the impact (numbers, not adjectives)?"),
    ("addresses_duplicate_risk", "Does it address duplicate risk vs known families?"),
)


def scoring_rubric() -> list[dict]:
    return [{"check": c, "question": q} for c, q in RUBRIC]


def _read(path: Path) -> str:
    try:
        if path.stat().st_size > _MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _has_run_note(root: Path) -> bool:
    for rel in _RUN_NOTE_DIRS:
        d = root / rel
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if p.is_file() and p.suffix.lower() in (".txt", ".md", ".json", ".log"):
                if _RUN_PASS_RE.search(_read(p)):
                    return True
    return False


def _grade_test(name: str, text: str, fn_hints: list[str], run_note: bool) -> m.EvidenceGrade:
    YES, NO, UNK = "yes", "no", m.EV_UNKNOWN
    has_assert = bool(_ASSERT_RE.search(text) or _REVERT_RE.search(text))
    value_mv = YES if (has_assert and _BALANCE_RE.search(text)) else NO
    actors = YES if _ACTORS_RE.search(text) else UNK
    grade = m.EvidenceGrade(
        test_name=name,
        invariant_tested=next((h for h in fn_hints if h.lower() in text.lower()), m.UNKNOWN_IN_LOCAL_REPO),
        does_compile=UNK,  # static: not compiled here
        does_run=(YES if run_note else UNK),
        realistic_actors=actors,
        scoped_contracts=UNK,
        no_trusted_role_assumption=UNK,
        no_weird_token_assumption=UNK,
        proves_value_movement=value_mv,
        quantifies_impact=(YES if value_mv == YES else NO),
        addresses_duplicate_risk=(YES if re.search(r"known|duplicate|patch", text, re.IGNORECASE) else NO),
    )
    # Conservative grading. Grade A (and VALIDATED_CANDIDATE) is a human judgment and
    # is never auto-assigned by this static judge.
    if not has_assert:
        grade.grade = m.GRADE_F
        grade.decision = m.JUDGE_INSUFFICIENT_EVIDENCE
        grade.notes = ["No assertion or revert expectation found; cannot support a conclusion."]
    elif value_mv == YES:
        grade.grade = m.GRADE_C
        grade.decision = m.JUDGE_NEEDS_HUMAN_REVIEW
        grade.notes = ["Asserts on value-relevant state; a human must confirm impact, scope, and grade.",
                       "Grade A / VALIDATED_CANDIDATE requires a human-confirmed material economic violation."]
    else:
        grade.grade = m.GRADE_C
        grade.decision = m.JUDGE_INSUFFICIENT_EVIDENCE
        grade.notes = ["Asserts, but no clear value movement; strengthen the test before human review."]
    return grade


def judge_evidence(ctx: dict, root: Path | str, tasks_data: dict | None = None,
                   evidence_dir: str | None = None) -> dict:
    root = Path(root)
    lens = ctx["lens"]
    fn_hints = lens.periphery_function_names() + [
        f for inv in lens.economic_invariants() for f in inv.relevant_functions]
    fn_hints = sorted(set(fn_hints))

    _sources, tests = find_solidity_files(root)
    run_note = _has_run_note(root)
    grades: list[dict] = []
    for p in tests:
        text = _read(Path(p))
        if not text:
            continue
        if not any(h.lower() in text.lower() for h in fn_hints):
            continue
        try:
            rel = Path(p).resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = Path(p).as_posix()
        fns = _TEST_FN_RE.findall(text)
        if not fns:
            continue
        for fn in fns[:8]:
            grades.append(_grade_test(f"{rel}::{fn}", text, fn_hints, run_note).to_dict())

    counts: dict[str, int] = {g: 0 for g in m.GRADES}
    decisions: dict[str, int] = {d: 0 for d in m.JUDGE_DECISIONS}
    for g in grades:
        counts[g["grade"]] = counts.get(g["grade"], 0) + 1
        decisions[g["decision"]] = decisions.get(g["decision"], 0) + 1

    data = common_header(m.KIND_LENS_EVIDENCE, "lens-evidence", ctx)
    data["kind"] = "lens-evidence-judge"
    data.update({
        "rubric": scoring_rubric(),
        "grades_vocabulary": {
            "A": "strong local proof of material economic violation (human-assigned)",
            "B": "likely issue, needs one more test or line confirmation",
            "C": "interesting but impact unclear",
            "D": "rejected by local test",
            "F": "invalid setup or out of scope",
        },
        "decisions_vocabulary": list(m.JUDGE_DECISIONS),
        "evidence_dir_used": evidence_dir or "(default test discovery)",
        "tasks_aligned": bool(tasks_data),
        "run_note_present": run_note,
        "graded_count": len(grades),
        "grades": grades,
        "grade_counts": counts,
        "decision_counts": decisions,
        "note": ("Only grade A may become VALIDATED_CANDIDATE, and only a human may assign it. "
                 "This static judge never auto-confirms a vulnerability. Human review is required."),
        "safety": safety.safety_block(),
    })
    return data
