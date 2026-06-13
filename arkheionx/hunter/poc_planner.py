"""PoC planner for hunter mode.

Produces a minimal, honest PoC plan for every *pursueable* lead (PURSUE_NOW /
NEEDS_POC). It never plans a PoC for a killed duplicate, an out-of-scope lead, or a
trusted-role-only lead. Every plan ends with the same rule:

    Do not write a report until the expected assertion passes.

Plans prefer an existing local harness, keep mocks minimal, and state how any mock
affects validity. A plan is a research scaffold, not an exploit.
"""
from __future__ import annotations

from . import lane_templates
from . import models as M

_DO_NOT_REPORT = "Do not write a report until the expected assertion passes."


def _status(lead: M.HunterLead, *, rpc_ran: bool, baseline_provided: bool) -> str:
    if lead.source_status in M.SOURCE_INADEQUATE:
        return M.POC_NEEDS_SOURCE
    if lead.lead_type in (M.DEPLOYMENT_MISMATCH, M.LIVE_REGISTRY_DIFF) and not rpc_ran:
        return M.POC_NEEDS_DEPLOYMENT_STATE
    if lead.freshness_status in M.FRESHNESS_NO_BASELINE and not baseline_provided:
        return M.POC_NEEDS_BASELINE
    return M.POC_READY


def _skeleton(lead: M.HunterLead, attack: str, assertion: str) -> str:
    contract = lead.contract or "Target"
    return "\n".join([
        "// SPDX-License-Identifier: UNLICENSED",
        "pragma solidity ^0.8.20;",
        "",
        'import {Test} from "forge-std/Test.sol";',
        f"// import the in-scope contract: {contract}",
        "",
        f"contract {contract}_HunterPoC is Test {{",
        "    function setUp() public {",
        "        // deploy / fork the in-scope contract; reuse the existing harness if present",
        "    }",
        "",
        f"    function test_{lead.lead_type.lower()}() public {{",
        f"        // Attack: {attack}",
        f"        // Expected assertion: {assertion}",
        "        // assertTrue(invariantBroken); // prove or kill the lead",
        "    }",
        "}",
    ])


def build_poc_plans(leads: list, *, rpc_ran: bool, baseline_provided: bool) -> list:
    plans: list = []
    n = 0
    for lead in leads:
        if lead.decision not in M.PURSUEABLE:
            continue
        n += 1
        templates = lane_templates.templates_for_lead_type(lead.lead_type)
        tmpl = templates[0] if templates else None
        attack = tmpl["minimal_poc_shape"] if tmpl else (
            f"Exercise {lead.surface or lead.contract} to move value without authorization "
            "and assert an accounting/balance invariant breaks.")
        assertion = (
            "A value/accounting invariant is violated for attacker profit (e.g. attacker "
            "balance increases or protocol solvency decreases beyond rounding).")
        plan_id = f"POC-{n:03d}"
        lead.poc_plan_id = plan_id
        status = _status(lead, rpc_ran=rpc_ran, baseline_provided=baseline_provided)
        plans.append(M.PocPlan(
            poc_plan_id=plan_id,
            lead_id=lead.lead_id,
            status=status,
            hypothesis=f"{lead.surface or lead.contract} ({lead.lead_type}) can be driven to a "
                       "value/accounting violation by an unprivileged attacker.",
            why_eligible=f"Scope confidence {lead.scope_confidence}; severity ceiling "
                         f"{lead.expected_severity_ceiling}; attacker reachability {lead.attacker_reachability}.",
            why_not_duplicate=f"Dedup status {lead.known_match_status} ({lead.dedup_status}); "
                              "confirm the exact root behavior against known/audit/test material first.",
            why_not_oos="Surface is within the in-scope contracts; re-confirm against the scope exclusions.",
            why_not_trusted_role_only=("An unprivileged external path reaches this surface."
                                       if lead.attacker_reachability == "UNPRIVILEGED_EXTERNAL"
                                       else "Confirm a non-privileged path exists before investing time."),
            baseline=("Provided baseline." if baseline_provided else
                      "No baseline; capture current behavior before/after the attack."),
            attack=attack,
            expected_assertion=assertion,
            measured_impact="Quantify attacker gain / protocol loss (principal, yield, fees, or freeze).",
            required_actors=["attacker (unprivileged)", "victim depositor/user"],
            required_balances=["attacker: minimal seed", "victim: realistic deposit"],
            required_contract_state=[f"{lead.contract} deployed and funded"] +
                                    ([f"value paths: {', '.join(lead.value_path_ids)}"] if lead.value_path_ids else []),
            required_mocks=["Only mock external dependencies that are out of scope; note that any "
                            "mock weakens validity and must mirror real behavior."],
            existing_harness="Reuse the repo's existing Foundry test harness if present (prefer over new scaffolding).",
            target_files=list(lead.linked_files or []),
            target_functions=[lead.surface] if lead.surface else [],
            suggested_test_filename=f"test/{(lead.contract or 'Target')}_{lead.lead_type}.t.sol",
            minimal_skeleton=_skeleton(lead, attack, assertion),
            kill_condition=(lead.kill_conditions[0] if lead.kill_conditions else
                            "Kill if a local test shows the invariant holds and no value moves without authorization."),
            stop_condition="Stop if the attack requires a trusted role, out-of-scope contract, or unrealistic state.",
            report_condition=_DO_NOT_REPORT,
        ))
    return plans
