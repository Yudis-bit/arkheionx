"""Judge whether local tests / evidence actually prove the intended task (v7).

Local/static and heuristic. The judge reads Foundry test files (``*.t.sol``) and
structured evidence submissions (``*.json``) from the evidence directories, then
grades each on a transparent rubric: does it call the target, set up, act, assert,
check pre/post state, exercise the negative/boundary path, and avoid mocking away
the risk, depending only on in-scope, non-known, non-trusted-role behaviour.

The judge does not run any test and does not confirm a vulnerability. Evidence
quality is not vulnerability validity. Candidate-with-evidence is not a confirmed
vulnerability; it only means a human should review the candidate. Human review is
required.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from arkheionx.review_map.model import ReviewMap
from arkheionx.version import PACKAGE_VERSION

from . import models as m
from . import safety
from . import scope_parser
from .lane_builder import scope_filters

DEFAULT_EVIDENCE_DIRS = (
    ".arkheionx/scope-pack",
    ".arkheionx/evidence",
    ".arkheionx/private",
    "test",
    "tests",
)

_TEST_FN_RE = re.compile(r"function\s+(test\w*)\s*\(")
_CANDIDATE_HINTS = ("attacker", "steal", "drain", "inflat", "bypass", "profit", "exploit", "unauthorizedgain")


def scoring_rubric() -> list[dict]:
    """The transparent rubric used to grade evidence (also rendered in the pack)."""
    return [
        {"check": "calls-target", "question": "Does the test call or mention the target function?"},
        {"check": "right-lane", "question": "Does it exercise the right lane / behaviour?"},
        {"check": "counterfactual", "question": "Does it reproduce the counterfactual (the thing that must not happen)?"},
        {"check": "setup", "question": "Does it set up actors and state (deal/prank/deploy)?"},
        {"check": "action", "question": "Does it perform the action under test?"},
        {"check": "assertion", "question": "Does it assert an outcome (not just that the call did not revert)?"},
        {"check": "pre-post-state", "question": "Does it check pre/post state or accounting deltas where value moves?"},
        {"check": "actor-separation", "question": "Does it separate attacker/victim/role where relevant?"},
        {"check": "negative-path", "question": "Does it test the negative path for authorization/compliance?"},
        {"check": "boundary", "question": "Does it test a boundary (first/last/dust/just-inside/outside)?"},
        {"check": "no-mock-away", "question": "Does it avoid mocking away the actual risk?"},
        {"check": "not-trusted-role", "question": "Does it avoid relying on a trusted-role mistake the scope marks invalid?"},
        {"check": "not-known-accepted", "question": "Does it avoid duplicating a known or accepted issue?"},
        {"check": "impact-bar", "question": "Does it avoid low-only impact when Medium/High is required?"},
        {"check": "records-result", "question": "Does it record the command result / output?"},
        {"check": "impact-path", "question": "Does it explain the loss/lock/accounting/unauthorized/invariant impact?"},
    ]


def _evidence_dirs(root: Path, evidence_dir: str | None) -> list[Path]:
    if evidence_dir:
        p = Path(evidence_dir).expanduser()
        return [p] if p.is_dir() else []
    return [root / d for d in DEFAULT_EVIDENCE_DIRS if (root / d).is_dir()]


def _collect_files(dirs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for d in dirs:
        for pat in ("*.t.sol", "*.json"):
            files.extend(sorted(d.rglob(pat)))
    # De-duplicate while preserving order.
    seen: set[Path] = set()
    out: list[Path] = []
    for f in files:
        if f not in seen and f.is_file():
            seen.add(f)
            out.append(f)
    return out


_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
_ASSERT_RE = re.compile(r"\b(assert\w*|expectrevert|require)\s*\(", re.IGNORECASE)
_ACTION_RE = re.compile(r"\.\w+\s*\(.*\)\s*;")
_BOUNDARY_RE = re.compile(r"\b(max|min|dust|boundary|first|last|zero)\b|type\(uint|1 wei", re.IGNORECASE)


def _checks_for_solidity(text: str) -> dict:
    code = _COMMENT_RE.sub(" ", text)  # ignore comment text (e.g. the word "assertion")
    low = code.lower()
    has_assert = bool(_ASSERT_RE.search(code))
    has_expect_revert = "expectrevert" in low
    return {
        "has_test_fn": bool(_TEST_FN_RE.search(code)),
        "setup": any(k in low for k in ("vm.prank", "vm.deal", "vm.startprank", "setup(", "new ", "deploy")),
        "action": bool(_ACTION_RE.search(code)),
        "assertion": has_assert,
        "only_no_revert": not has_assert,
        "pre_post_state": any(k in low for k in ("balanceof", "totalsupply", "totalassets", "before", "after", "delta")),
        "negative_path": has_expect_revert,
        "boundary": bool(_BOUNDARY_RE.search(code)),
        "no_mock_away": not (low.count("mock") >= 2 and not has_assert),
        "candidate_signal": any(k in low for k in _CANDIDATE_HINTS),
        "records_result": True,  # a committed test file is itself a recorded artifact
    }


def _quality_from_checks(c: dict) -> str:
    if not c.get("has_test_fn") or not c.get("action") or not c.get("assertion") or c.get("only_no_revert"):
        return m.QUALITY_INVALID
    strong_signals = sum(bool(c.get(k)) for k in ("setup", "pre_post_state", "negative_path", "boundary"))
    if c.get("setup") and c.get("pre_post_state") and (c.get("negative_path") or c.get("boundary")):
        return m.QUALITY_STRONG
    if strong_signals >= 2:
        return m.QUALITY_MEDIUM
    if strong_signals == 1:
        return m.QUALITY_WEAK
    return m.QUALITY_INSUFFICIENT


_GENERIC_SCOPE_TOKENS = {
    "test", "tests", "mock", "mocks", "helper", "helpers", "script", "scripts",
    "deploy", "deployment", "gas", "optimization", "optimizations", "any", "the",
}


def _named_targets(item: str) -> list[str]:
    """Extract concrete target tokens (CamelCase names or .sol files) from a scope line."""
    import re as _re
    targets: list[str] = []
    for fname in _re.findall(r"([A-Za-z0-9_]+)\.sol", item):
        targets.append(fname.lower())
    for camel in _re.findall(r"\b([A-Z][a-z]+[A-Za-z0-9]*[A-Z][A-Za-z0-9]*)\b", item):
        if camel.lower() not in _GENERIC_SCOPE_TOKENS:
            targets.append(camel.lower())
    return targets


def _scope_judgment(path_str: str, text: str, scope: m.ScopeData) -> str | None:
    # Match only the test *content* against concrete named targets in the scope.
    # Never match on the evidence file's own path (a test under test/ is not
    # "out of scope" just because the scope excludes the protocol's test helpers).
    low = text.lower()

    def hit(items: list[str]) -> bool:
        for it in items:
            for tok in _named_targets(it):
                if tok and tok in low:
                    return True
        return False

    if hit(scope.out_of_scope):
        return m.JUDGE_LIKELY_OUT_OF_SCOPE
    if hit(scope.known_issues):
        return m.JUDGE_LIKELY_KNOWN
    if hit(scope.accepted_risks):
        return m.JUDGE_LIKELY_ACCEPTED
    if hit(scope.low_only_patterns):
        return m.JUDGE_LIKELY_LOW_ONLY
    return None


def _judgment_from_quality(quality: str, c: dict) -> str:
    if quality == m.QUALITY_INVALID:
        return m.JUDGE_INVALID
    if quality == m.QUALITY_INSUFFICIENT:
        return m.JUDGE_INSUFFICIENT
    candidate_style = c.get("candidate_signal") and not c.get("negative_path")
    if quality == m.QUALITY_STRONG:
        return m.JUDGE_CANDIDATE if candidate_style else m.JUDGE_REJECTED_STRONG
    if quality == m.QUALITY_MEDIUM:
        return m.JUDGE_CANDIDATE if candidate_style else m.JUDGE_REJECTED_MEDIUM
    return m.JUDGE_NEEDS_HUMAN  # weak


def _missing_checks(c: dict) -> list[str]:
    labels = {
        "setup": "no actor/state setup", "assertion": "no assertion",
        "pre_post_state": "no pre/post state or balance delta", "negative_path": "no negative path",
        "boundary": "no boundary case", "no_mock_away": "appears to mock away the risk",
    }
    out = []
    for key, label in labels.items():
        if not c.get(key):
            out.append(label)
    if c.get("only_no_revert"):
        out.append("asserts only that the call did not revert")
    return out


def _judge_solidity(path: Path, root: Path, scope: m.ScopeData, tasks_by_target: dict) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    c = _checks_for_solidity(text)
    quality = _quality_from_checks(c)
    scope_judge = _scope_judgment(str(path), text, scope)
    judgment = scope_judge or _judgment_from_quality(quality, c)
    rel = str(path.relative_to(root)) if _under(path, root) else str(path)
    linked_task = ""
    for target, tid in tasks_by_target.items():
        fn = target.split(".")[-1].lower()
        if fn and fn in text.lower():
            linked_task = tid
            break
    return {
        "evidence_id": "",
        "source": rel,
        "evidence_type": "foundry-test",
        "linked_task": linked_task,
        "quality": quality,
        "judgment": judgment,
        "checks_passed": sorted(k for k, v in c.items() if v and k != "candidate_signal"),
        "missing": _missing_checks(c),
        "reasoning": _reasoning(quality, judgment, c),
        "human_review_required": True,
    }


def _judge_json(path: Path, root: Path, scope: m.ScopeData) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    # Only treat JSON that looks like an evidence submission.
    if not any(k in payload for k in ("evidence", "command", "result", "output", "target", "task_id")):
        return None
    text = json.dumps(payload).lower()
    has_cmd = bool(payload.get("command"))
    has_output = bool(payload.get("output") or payload.get("result"))
    has_target = bool(payload.get("target") or payload.get("task_id"))
    has_assertions = bool(payload.get("assertions")) or "assert" in text
    score = sum([has_cmd, has_output, has_target, has_assertions])
    quality = (m.QUALITY_STRONG if score == 4 else m.QUALITY_MEDIUM if score == 3
               else m.QUALITY_WEAK if score == 2 else m.QUALITY_INSUFFICIENT)
    result = str(payload.get("result", "")).lower()
    scope_judge = _scope_judgment(str(path), text, scope)
    if scope_judge:
        judgment = scope_judge
    elif not has_target or not has_output:
        judgment = m.JUDGE_INSUFFICIENT
    elif any(h in text for h in _CANDIDATE_HINTS) and result != "pass-as-guard":
        judgment = m.JUDGE_CANDIDATE
    elif quality in (m.QUALITY_STRONG, m.QUALITY_MEDIUM):
        judgment = m.JUDGE_NEEDS_HUMAN
    else:
        judgment = m.JUDGE_INSUFFICIENT
    rel = str(path.relative_to(root)) if _under(path, root) else str(path)
    return {
        "evidence_id": "",
        "source": rel,
        "evidence_type": "evidence-submission",
        "linked_task": str(payload.get("task_id", "")),
        "quality": quality,
        "judgment": judgment,
        "checks_passed": [k for k, v in (("records-command", has_cmd), ("records-output", has_output),
                                          ("names-target", has_target), ("states-assertions", has_assertions)) if v],
        "missing": [k for k, v in (("command", has_cmd), ("output/result", has_output),
                                    ("target", has_target), ("assertions", has_assertions)) if not v],
        "reasoning": _reasoning(quality, judgment, {}),
        "human_review_required": True,
    }


def _reasoning(quality: str, judgment: str, c: dict) -> str:
    base = f"Heuristic evidence quality is {quality}; judgment is {judgment}."
    if judgment == m.JUDGE_CANDIDATE:
        base += " Candidate-with-evidence is not a confirmed vulnerability; a human must review it."
    if judgment in (m.JUDGE_REJECTED_STRONG, m.JUDGE_REJECTED_MEDIUM):
        base += " Rejected-with-evidence is not proof the protocol has no bugs."
    if judgment == m.JUDGE_INVALID:
        base += " The test does not prove the intended claim; rewrite it before trusting any result."
    return base


def _under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _tasks_by_target(tasks_file: str | None) -> dict:
    if not tasks_file:
        return {}
    p = Path(tasks_file).expanduser()
    if not p.is_file():
        return {}
    try:
        payload = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ValueError):
        return {}
    out: dict[str, str] = {}
    for t in payload.get("tasks", []) if isinstance(payload, dict) else []:
        target = t.get("target")
        tid = t.get("task_id")
        if target and tid:
            out.setdefault(target, tid)
    return out


def judge_evidence(rm: ReviewMap, root: Path | str, scope_file: str | None = None, *,
                   tasks_file: str | None = None, evidence_dir: str | None = None,
                   source_files: int = 0, test_files: int = 0) -> dict:
    root = Path(root)
    scope = scope_parser.parse_scope_file(scope_file)
    tasks_by_target = _tasks_by_target(tasks_file)

    dirs = _evidence_dirs(root, evidence_dir)
    files = _collect_files(dirs)
    judged: list[dict] = []
    for f in files:
        if f.name.endswith(".t.sol"):
            judged.append(_judge_solidity(f, root, scope, tasks_by_target))
        elif f.suffix == ".json":
            rec = _judge_json(f, root, scope)
            if rec:
                judged.append(rec)
    for i, rec in enumerate(judged, 1):
        rec["evidence_id"] = f"EV-{i:03d}"

    counts_quality = {q: 0 for q in m.EVIDENCE_QUALITIES}
    counts_judgment = {j: 0 for j in m.JUDGMENTS}
    for rec in judged:
        counts_quality[rec["quality"]] = counts_quality.get(rec["quality"], 0) + 1
        counts_judgment[rec["judgment"]] = counts_judgment.get(rec["judgment"], 0) + 1

    summary = {
        "evidence_dirs_scanned": [str(d.relative_to(root)) if _under(d, root) else str(d) for d in dirs],
        "evidence_items": len(judged),
        "quality_counts": counts_quality,
        "judgment_counts": counts_judgment,
        "candidates_with_evidence": counts_judgment.get(m.JUDGE_CANDIDATE, 0),
        "weak_or_invalid": counts_quality.get(m.QUALITY_WEAK, 0) + counts_quality.get(m.QUALITY_INVALID, 0),
        "note": ("No local evidence found in the scanned directories. Write local tests and re-run."
                 if not judged else
                 "Evidence quality is not vulnerability validity. Human review is required."),
    }

    return {
        "schema_version": m.SCHEMA_VERSION,
        "arkheionx_version": PACKAGE_VERSION,
        "kind": m.KIND_EVIDENCE_JUDGE,
        "command": "evidence-judge",
        "generated_at": rm.generated_at,
        "scope_file_used": scope.scope_file_used,
        "judged_evidence": judged,
        "summary": summary,
        "rubric": scoring_rubric(),
        "filters": scope_filters(scope),
        "human_review_required": True,
        "safety_boundary": safety.SAFETY_BOUNDARY,
        "safety": safety.safety_block(),
    }
