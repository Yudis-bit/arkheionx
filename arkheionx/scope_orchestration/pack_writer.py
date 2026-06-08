"""Assemble a complete local scope-aware research pack (v7).

Writes the numbered pack files, the optional machine-readable JSON sidecars, and a
manifest. Everything is local/static and vendor-agnostic. The pack never contains a
private scope's contents in the manifest. Human review is required.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.review_map.model import ReviewMap
from arkheionx.version import PACKAGE_VERSION

from . import models as m
from . import render
from . import safety
from . import scope_parser
from .json_output import _json, _write, default_scope_pack_dir
from .lane_builder import build_scope_lanes, build_scope_map, do_not_waste_time, scope_filters
from .task_builder import build_scope_tasks
from .evidence_judge import judge_evidence, scoring_rubric
from .report_filter import PRE_SUBMISSION_CHECKLIST, filter_report_candidates

PACK_FILES = (
    "00-README.md", "01-scope-map.md", "02-review-lanes.md", "03-scope-tasks.md",
    "04-do-not-waste-time.md", "05-evidence-template.md", "06-evidence-judge-rubric.md",
    "07-report-filter-checklist.md", "08-human-review-checklist.md", "09-agent-input.md",
    "10-case-study-template.md", "manifest.json",
)
JSON_SIDECARS = ("scope-map.json", "scope-lanes.json", "scope-tasks.json", "report-filter.json")


def _readme(scope: m.ScopeData) -> str:
    return "\n".join([
        "# Scope-Aware Research Pack",
        "",
        "Local/static planning artifacts for an authorized smart-contract review. "
        "Nothing here is a finding, a severity, or a confirmed vulnerability. Human review is required.",
        "",
        "## What this pack is",
        "",
        "- `01-scope-map.md` — the scope turned into structured review rules.",
        "- `02-review-lanes.md` — generic review lanes selected for this scope.",
        "- `03-scope-tasks.md` — precise, bounded, testable tasks per lane.",
        "- `04-do-not-waste-time.md` — known/accepted/trusted/out-of-scope/low-only filters.",
        "- `05-evidence-template.md` — how to record local test evidence.",
        "- `06-evidence-judge-rubric.md` — how evidence is graded.",
        "- `07-report-filter-checklist.md` — how candidates are classified before submission.",
        "- `08-human-review-checklist.md` — the human gate before any report.",
        "- `09-agent-input.md` — model-agnostic instructions for an AI agent.",
        "- `10-case-study-template.md` — a sanitized research-session template.",
        "",
        "## How to use it",
        "",
        "1. Read `01-scope-map.md` and `04-do-not-waste-time.md` first.",
        "2. Give `09-agent-input.md` plus `03-scope-tasks.md` to a review agent or reviewer.",
        "3. For each task, write local Foundry tests and record output using `05-evidence-template.md`.",
        "4. Run `arkheionx evidence-judge <repo> --scope-file <scope>` to grade the evidence.",
        "5. Run `arkheionx report-filter <repo> --scope-file <scope>` to classify candidates.",
        "6. Use `08-human-review-checklist.md` before considering any report.",
        "",
        "## What not to submit",
        "",
        "- Do not submit a task or a judge result as a finding.",
        "- Do not submit known, accepted, out-of-scope, or low-only issues.",
        "- Do not submit anything without a local proof-of-concept and human review.",
        "- A candidate-with-evidence result is not a confirmed vulnerability.",
        "",
        f"Scope file used: {'yes' if scope.scope_file_used else 'no (generic pack inferred from repo structure)'}.",
        "",
    ]) + "\n"


def _do_not_waste(scope: m.ScopeData) -> str:
    f = scope_filters(scope)
    out = ["# Do Not Waste Time", "",
           "These are out of scope for a useful submission under this program. Confirm against the "
           "real scope before trusting any line.", ""]
    sections = [
        ("Known issues", scope.known_issues),
        ("Accepted risks", scope.accepted_risks),
        ("Trusted assumptions", f["trusted_assumptions"]),
        ("External dependency assumptions", f["dependency_assumptions"]),
        ("Low-only patterns", scope.low_only_patterns),
        ("Out-of-scope patterns", scope.out_of_scope),
        ("Prior audit acknowledged risks", scope.prior_audit_notes),
        ("Invalid patterns", scope.invalid_patterns),
    ]
    for title, items in sections:
        out += [f"## {title}", "", render._bullets(items), ""]
    out += ["## Centralization-only patterns", "",
            "Do not submit centralization-only concerns (an admin *could* misbehave) unless the scope "
            "explicitly marks them valid. Tie any admin issue to a path that does not rely on trusted-role "
            "misbehaviour.", ""]
    return "\n".join(out) + "\n"


def _evidence_template() -> str:
    return "\n".join([
        "# Evidence Template",
        "",
        "Record one block per task. Keep it local and reproducible.",
        "",
        "```text",
        "Task ID:            TASK-XXX",
        "Target:             Contract.function",
        "Lane:               LANE-XX <name>",
        "Hypothesis:         <what you tried to prove>",
        "Counterfactual:     <the thing that must not happen>",
        "Local test file:    test/<Name>.t.sol",
        "Command:            forge test --match-test <name> -vvvv   (run locally; Arkheionx does not run it)",
        "Result:             pass | fail | mixed",
        "Setup:              <actors, balances, state>",
        "Action:             <call(s) under test>",
        "Assertions:         <pre/post state, deltas, reverts>",
        "Impact path:        <loss | lock | incorrect-accounting | unauthorized-action | invariant-break>",
        "In scope:           yes | no",
        "Known/accepted:     no | <which>",
        "Medium/High impact: yes | no",
        "Human review:       required",
        "```",
        "",
        "Evidence quality is not vulnerability validity. Human review is required.",
        "",
    ]) + "\n"


def _rubric_doc() -> str:
    out = ["# Evidence Judge Rubric", "",
           "Each piece of evidence is graded on these checks:", ""]
    for r in scoring_rubric():
        out.append(f"- **{r['check']}** — {r['question']}")
    out += ["", "## Evidence quality labels", "",
            "- `strong` — sets up, acts, asserts, checks pre/post state, and exercises a negative/boundary path.",
            "- `medium` — acts and asserts with some state/negative coverage.",
            "- `weak` — acts and asserts but shallow (missing setup or state delta).",
            "- `insufficient` — barely exercises the target; cannot support a conclusion.",
            "- `invalid` — does not call the target, has no assertion, or only asserts no-revert.",
            "- `unknown` — cannot be classified.",
            "", "## Judgment labels", "",
            "- `rejected-with-strong-evidence` / `rejected-with-medium-evidence` — the guard appears to hold "
            "(not proof the protocol has no bugs).",
            "- `candidate-with-evidence` — a human should review the candidate (not a confirmed vulnerability).",
            "- `insufficient-evidence` / `invalid-test` — strengthen or rewrite the test.",
            "- `likely-known-issue` / `likely-accepted-risk` / `likely-trusted-role-assumption` / "
            "`likely-out-of-scope` / `likely-low-only` — filtered by the scope.",
            "- `needs-human-review` — ambiguous; a human must decide.",
            "", "Human review is required for every conclusion.", ""]
    return "\n".join(out) + "\n"


def _report_checklist_doc(scope: m.ScopeData) -> str:
    out = ["# Report Filter Checklist", "",
           "Classify every candidate before submission. Classifications:", ""]
    for label in m.CLASSIFICATIONS:
        out.append(f"- `{label}`")
    out += ["", "## Human pre-submission checklist", "", render._bullets(PRE_SUBMISSION_CHECKLIST), "",
            "Report filter is not final triage. Human review is required.", ""]
    return "\n".join(out) + "\n"


def _human_checklist() -> str:
    return "\n".join([
        "# Human Review Checklist",
        "",
        "A human makes the security call. Before treating anything as a report candidate:",
        "",
        render._bullets([
            "I read the scope map and the do-not-waste-time filters.",
            "I confirmed the surface is in scope and matches the deployed snapshot.",
            "I have a local proof-of-concept that exercises the target and asserts the impact.",
            "The impact is a concrete loss / lock / incorrect-accounting / unauthorized-action / invariant-break.",
            "The impact meets the scope's severity bar (Medium/High where required).",
            "It is not a known issue, accepted risk, or out-of-scope area.",
            "It does not rely on trusted-role misbehaviour unless the scope marks that valid.",
            "It is not centralization-only and not a pure spec/UX deviation without qualifying impact.",
            "I considered duplicate risk for common bug classes and differentiated the impact.",
            "The write-up is minimal, evidence-backed, and free of any private/target-identifying detail.",
        ]),
        "",
        "Arkheionx provides review context, not final security judgments.",
        "",
    ]) + "\n"


def _agent_input(scope: m.ScopeData) -> str:
    return "\n".join([
        "# Agent Input (model-agnostic)",
        "",
        "You are a local security-research assistant working from an authorized scope. Follow these rules.",
        "",
        render._bullets([
            "Do not claim a finding without local test evidence.",
            "Do not write a report until evidence exists.",
            "Do not rely on trusted-role misbehaviour unless the scope says it is valid.",
            "Do not treat known or accepted risks as new findings.",
            "Do not submit low-only issues when the contest requires Medium/High impact.",
            "For each task, write local tests, record command output, and explain the evidence.",
            "Return rejected / candidate / insufficient only with reasoning.",
            "A candidate-with-evidence result still requires human review and is not a confirmed vulnerability.",
            "Never use RPC, live-chain calls, private keys, or exploit automation.",
            "Never include private or target-identifying details in any output.",
        ]),
        "",
        "## Your loop",
        "",
        "1. Take one task from `03-scope-tasks.md`.",
        "2. Write a local Foundry test that reproduces the counterfactual.",
        "3. Record the result with `05-evidence-template.md`.",
        "4. Judge it against `06-evidence-judge-rubric.md`.",
        "5. Hand candidates to a human via `08-human-review-checklist.md`.",
        "",
        f"Scope file used: {'yes' if scope.scope_file_used else 'no (work from repo structure and confirm scope manually)'}.",
        "",
    ]) + "\n"


def _case_study_template() -> str:
    return "\n".join([
        "# Case Study Template (sanitized)",
        "",
        "Record a research session without any private or target-identifying detail.",
        "",
        "## Context",
        "- Generic protocol type: <stablecoin | vault | oracle | cross-chain | ...>",
        "- Lanes worked: <LANE-XX ...>",
        "",
        "## Hypotheses tested",
        "- <hypothesis> -> <rejected | candidate | insufficient> (evidence: <file>)",
        "",
        "## What the evidence showed",
        "- <summary of local test results; no claims of confirmed vulnerabilities>",
        "",
        "## Human decision",
        "- <what a human decided to do; what was escalated for review>",
        "",
        "## Lessons / reusable lane notes",
        "- <generic, non-identifying notes for next time>",
        "",
        "Nothing here is a finding or a severity. Human review is required.",
        "",
    ]) + "\n"


def build_scope_pack(rm: ReviewMap, root: Path | str, scope_file: str | None = None,
                     out_dir: Path | str | None = None, *,
                     source_files: int = 0, test_files: int = 0, write: bool = True) -> dict:
    root = Path(root)
    scope = scope_parser.parse_scope_file(scope_file)
    out = Path(out_dir).expanduser() if out_dir else default_scope_pack_dir(root)

    scope_map = build_scope_map(rm, root, scope_file, source_files=source_files, test_files=test_files)
    lanes = build_scope_lanes(rm, root, scope_file, source_files=source_files, test_files=test_files)
    tasks = build_scope_tasks(rm, root, scope_file, source_files=source_files, test_files=test_files)
    judge = judge_evidence(rm, root, scope_file, source_files=source_files, test_files=test_files)
    report = filter_report_candidates(rm, root, scope_file, source_files=source_files,
                                      test_files=test_files, tasks_data=tasks, judge_data=judge)

    contents: dict[str, str] = {
        "00-README.md": _readme(scope),
        "01-scope-map.md": render.render_scope_map_md(scope_map),
        "02-review-lanes.md": render.render_scope_lanes_md(lanes),
        "03-scope-tasks.md": render.render_scope_tasks_md(tasks),
        "04-do-not-waste-time.md": _do_not_waste(scope),
        "05-evidence-template.md": _evidence_template(),
        "06-evidence-judge-rubric.md": _rubric_doc(),
        "07-report-filter-checklist.md": _report_checklist_doc(scope),
        "08-human-review-checklist.md": _human_checklist(),
        "09-agent-input.md": _agent_input(scope),
        "10-case-study-template.md": _case_study_template(),
    }
    sidecars: dict[str, dict] = {
        "scope-map.json": scope_map,
        "scope-lanes.json": lanes,
        "scope-tasks.json": tasks,
        "report-filter.json": report,
    }

    manifest = {
        "schema_version": m.SCHEMA_VERSION,
        "arkheionx_version": PACKAGE_VERSION,
        "kind": m.KIND_SCOPE_PACK_MANIFEST,
        "command": "scope-pack",
        "generated_at": rm.generated_at,
        "scope_file_used": scope.scope_file_used,
        "generated_artifacts": list(PACK_FILES),
        "artifact_list": list(PACK_FILES) + list(JSON_SIDECARS),
        "json_sidecars": list(JSON_SIDECARS),
        "counts": {
            "lanes": lanes.get("lane_count", 0),
            "tasks": tasks.get("task_count", 0),
            "report_candidates": report.get("candidate_count", 0),
            "evidence_items": judge.get("summary", {}).get("evidence_items", 0),
        },
        "safety_flags": safety.safety_flags(),
        "human_review_required": True,
        "safety_boundary": safety.SAFETY_BOUNDARY,
    }

    written: dict[str, str] = {}
    if write:
        for name, text in contents.items():
            written[name] = _write(out / name, text)
        for name, payload in sidecars.items():
            written[name] = _write(out / name, _json(payload))
        written["manifest.json"] = _write(out / "manifest.json", _json(manifest))

    return {"manifest": manifest, "out_dir": str(out), "artifacts": written,
            "scope_map": scope_map, "lanes": lanes, "tasks": tasks,
            "report": report, "judge": judge}
