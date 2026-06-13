"""Classify local-test evidence for each lens economic invariant.

For every invariant, this inspects local test files and assigns one of nine
evidence statuses. The classifier is deliberately conservative: a happy-path test
is not strong evidence, a comment is not evidence, fuzzing counts as targeted only
when the property is explicit, and a "strong" status is reserved for a test that
clearly targets the invariant. When the mapping is uncertain it marks ``UNKNOWN``.
It never invents confidence and it never claims a vulnerability.
"""
from __future__ import annotations

import re
from pathlib import Path

from arkheionx.protocol.semantic_adapter import find_solidity_files

from . import models as m
from . import safety
from .common import common_header

_MAX_FILE_BYTES = 2_000_000
_ASSERT_RE = re.compile(r"\bassert(?:Eq|Gt|Lt|Ge|Le|True|False|Approx[A-Za-z]*)?\b|\bvm\.expectRevert\b")
_REVERT_RE = re.compile(r"\bvm\.expectRevert\b|\bexpectRevert\b|\.selector\b")
_FUZZ_RE = re.compile(r"\btestFuzz|\bfunction\s+invariant_|\bStdInvariant\b", re.IGNORECASE)
_FORMAL_RE = re.compile(r"\brule\s+|\binvariant\s+\w+\s*\(|certora|halmos|kontrol", re.IGNORECASE)
_COMMENT_RE = re.compile(r"^\s*(//|\*|/\*)")


def _read(path: Path) -> str:
    try:
        if path.stat().st_size > _MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _load_tests(root: Path) -> dict[str, str]:
    _sources, tests = find_solidity_files(root)
    out: dict[str, str] = {}
    for p in tests:
        pp = Path(p)
        try:
            rel = pp.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = pp.as_posix()
        out[rel] = _read(pp)
    return out


def _mentions_only_in_comments(text: str, token: str) -> bool:
    pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])")
    saw = False
    for line in text.splitlines():
        if pat.search(line):
            saw = True
            if not _COMMENT_RE.match(line):
                return False
    return saw  # appeared, and every occurrence was on a comment line


def _classify_invariant(inv: m.EconomicInvariant, tests: dict[str, str]) -> dict:
    if not tests:
        return {"status": m.EV_UNKNOWN, "tests": [],
                "rationale": "No local test files were found; evidence is unknown."}

    fn_tokens = [f for f in inv.relevant_functions if f]
    sv_tokens = [s for s in inv.state_variables if s]
    fn_res = [re.compile(rf"(?<![A-Za-z0-9_]){re.escape(t)}(?![A-Za-z0-9_])", re.IGNORECASE) for t in fn_tokens]
    sv_res = [re.compile(rf"(?<![A-Za-z0-9_]){re.escape(t)}(?![A-Za-z0-9_])", re.IGNORECASE) for t in sv_tokens]

    related: list[str] = []
    code_related: list[str] = []
    comment_only_files: list[str] = []
    has_assert = has_revert = has_fuzz = has_formal = has_state = targets_id = False

    for rel, text in tests.items():
        if not text:
            continue
        fn_hit = any(r.search(text) for r in fn_res)
        sv_hit = any(r.search(text) for r in sv_res)
        id_hit = inv.id.lower() in text.lower()
        if not (fn_hit or sv_hit or id_hit):
            continue
        related.append(rel)
        # If the only mentions are in comments, it is not code evidence.
        only_comment = all(
            _mentions_only_in_comments(text, t)
            for t in (fn_tokens + ([] if not id_hit else [inv.id]))
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(t)}(?![A-Za-z0-9_])", text, re.IGNORECASE)
        ) if (fn_hit or id_hit) else False
        if only_comment and not sv_hit:
            comment_only_files.append(rel)
            continue
        code_related.append(rel)
        if _ASSERT_RE.search(text):
            has_assert = True
        if _REVERT_RE.search(text):
            has_revert = True
        if _FUZZ_RE.search(text):
            has_fuzz = True
        if _FORMAL_RE.search(text):
            has_formal = True
        if sv_hit:
            has_state = True
        if id_hit:
            targets_id = True

    if not related:
        return {"status": m.EV_UNTESTED, "tests": [],
                "rationale": "No local test references the invariant's functions or state variables."}
    if not code_related and comment_only_files:
        return {"status": m.EV_COMMENT_ONLY, "tests": sorted(comment_only_files),
                "rationale": "The invariant's symbols appear only in comments; a comment is not evidence."}

    tests_sorted = sorted(set(code_related))
    if has_formal and targets_id:
        status = m.EV_FORMALLY_PROVEN
        rationale = "A formal-spec rule explicitly references this invariant id."
    elif targets_id and has_assert:
        status = m.EV_DIRECTLY_TESTED_STRONG
        rationale = "A local test explicitly targets this invariant id and asserts an outcome."
    elif has_fuzz and has_state:
        status = m.EV_FUZZED_BUT_NOT_TARGETED
        rationale = "A fuzz/invariant test touches these symbols but the target property is not explicitly this invariant."
    elif has_assert and (has_revert or has_state):
        status = m.EV_DIRECTLY_TESTED_WEAK
        rationale = "A local test exercises the functions and asserts, but it is not confirmed to target this invariant."
    elif has_assert:
        status = m.EV_HAPPY_PATH_ONLY
        rationale = "A local test asserts a positive path only; no negative/boundary coverage for this invariant."
    else:
        status = m.EV_INDIRECTLY_TESTED
        rationale = "The functions are referenced by a test without a direct assertion on this invariant."
    return {"status": status, "tests": tests_sorted, "rationale": rationale}


def build_evidence_map(ctx: dict, root: Path | str) -> dict:
    lens = ctx["lens"]
    tests = _load_tests(Path(root))
    items: list[dict] = []
    counts: dict[str, int] = {s: 0 for s in m.EVIDENCE_STATUSES}
    for inv in lens.economic_invariants():
        c = _classify_invariant(inv, tests)
        counts[c["status"]] = counts.get(c["status"], 0) + 1
        item = m.EvidenceItem(
            invariant_id=inv.id,
            status=c["status"],
            test_name=", ".join(c["tests"][:6]),
            source=", ".join(c["tests"][:6]),
            rationale=c["rationale"],
        )
        d = item.to_dict()
        d["statement"] = inv.statement
        d["supporting_tests"] = c["tests"]
        items.append(d)

    strong = sum(counts.get(s, 0) for s in m.EVIDENCE_STRONG_STATUSES)
    data = common_header(m.KIND_LENS_EVIDENCE, "lens-evidence", ctx)
    data.update({
        "evidence_statuses": list(m.EVIDENCE_STATUSES),
        "test_files_scanned": len(tests),
        "items": items,
        "counts": counts,
        "summary": {
            "invariants": len(items),
            "strong_or_proven": strong,
            "untested_or_unknown": counts.get(m.EV_UNTESTED, 0) + counts.get(m.EV_UNKNOWN, 0),
        },
        "rules": [
            "A test is strong only if it directly targets the invariant.",
            "A happy-path test is not strong safety evidence.",
            "A comment is not evidence.",
            "A formal proof only counts for the exact property it proves.",
            "Fuzzing counts as strong only if the target property is explicit.",
            "When the mapping is uncertain, the status is UNKNOWN. Confidence is never invented.",
        ],
        "safety": safety.safety_block(),
    })
    return data
