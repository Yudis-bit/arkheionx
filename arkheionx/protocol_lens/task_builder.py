"""Turn lens review lanes into precise, bounded, evidence-oriented scope tasks.

Each task is a research instruction a model-agnostic agent or a human reviewer can
act on: a concrete hypothesis, the invariant at risk, the files/functions, the
setup and the local-test attempt, the expected safe behavior, the failure
condition, a suggested local test, duplicate-risk handling, and a decision rule.

A task is not an exploit instruction and not a finding. Tasks describe local
Foundry tests only. Human review is required.
"""
from __future__ import annotations

import re

from . import models as m
from . import safety
from .common import bind_lane, common_header, scope_filters


def _slug_to_test(slug: str) -> str:
    return "test_" + re.sub(r"[^a-z0-9]+", "_", slug.lower()).strip("_")


def _camel(slug: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[^a-z0-9]+", slug) if part)


def _invariant_statement(lens, inv_id: str) -> str:
    inv = lens.invariant_by_id().get(inv_id)
    return inv.statement if inv else ""


def _duplicate_risk(lane_def: m.LensLaneDef) -> str:
    return ("Credit-market issues cluster into known families; before treating this as novel, "
            "compare against documented known issues and a patched-behavior model (INV-MM-12).")


def _tasks_for_lane(ctx: dict, lane_def: m.LensLaneDef) -> list[dict]:
    lens = ctx["lens"]
    b = bind_lane(ctx, lane_def)
    files = b["source_files"]
    functions = b["functions"]
    invs = list(lane_def.invariants_at_risk) or [""]
    lane_num = lane_def.lane_id.split("-")[-1]
    camel = _camel(lane_def.slug)
    test_base = _slug_to_test(lane_def.slug)

    tasks: list[dict] = []
    for idx, hypothesis in enumerate(lane_def.first_hypotheses, start=1):
        inv_id = invs[(idx - 1) % len(invs)]
        safe = _invariant_statement(lens, inv_id) or lane_def.stop_condition
        task = m.ScopeTask(
            id=f"TASK-MM-{lane_num}-{idx:02d}",
            lane_id=lane_def.lane_id,
            hypothesis=hypothesis,
            invariant_at_risk=inv_id or m.UNKNOWN_IN_LOCAL_REPO,
            files=files,
            functions=functions,
            setup_needed=(
                "Deploy the in-scope contracts with realistic, untrusted actors "
                "(lender, borrower, maker, taker, liquidator) and a single in-scope market. "
                "Use only behaviour the scope does not mark trusted."),
            exploit_attempt_description=(
                f"Write a local Foundry test that drives the hypothesis: {hypothesis} "
                "Exercise the real path end to end and observe credit/debt/withdrawable/collateral deltas. "
                "This is a local test instruction, not an exploit; no RPC and no live chain."),
            expected_safe_behavior=safe,
            failure_condition=(
                f"The test shows the invariant can break ({inv_id}): the protocol allows the hypothesis to hold "
                "with realistic actors and in-scope contracts, moving value against intent."),
            suggested_test_file=f"test/lens/{camel}.t.sol",
            suggested_test_name=f"{test_base}_{idx:02d}",
            duplicate_risk=_duplicate_risk(lane_def),
            decision_rule=(
                "If the failure condition reproduces with realistic actors and in-scope contracts and the impact is "
                "material (loss/lock/incorrect-accounting/unauthorized-action/invariant-break), escalate as a candidate "
                "for human review — not a confirmed vulnerability. Otherwise record it as rejected-with-test."),
            kill_condition=(
                f"Abandon this hypothesis if the in-scope local test shows the invariant holds ({inv_id or 'the lane invariant'}: {safe}) "
                "for realistic actors, or if the only way to break it relies on a trusted role the scope marks valid, "
                "on out-of-scope/known/accepted surface, or without material impact. A held invariant is a rejection, not a finding."),
        )
        tasks.append(task.to_dict())
    return tasks


def build_scope_tasks(ctx: dict) -> dict:
    lens = ctx["lens"]
    scope = ctx["scope"]
    tasks: list[dict] = []
    for ld in lens.review_lanes():
        tasks.extend(_tasks_for_lane(ctx, ld))

    data = common_header(m.KIND_LENS_TASKS, "lens-tasks", ctx)
    data.update({
        "task_count": len(tasks),
        "tasks": tasks,
        "filters": scope_filters(scope),
        "format_note": (
            "Each task lists hypothesis, invariant at risk, files, functions, setup, local-test attempt, "
            "expected safe behavior, failure condition, suggested test file/name, duplicate risk, and a decision rule."),
        "safety": safety.safety_block(),
    })
    return data
