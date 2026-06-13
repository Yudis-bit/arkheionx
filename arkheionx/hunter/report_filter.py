"""Report filter for hunter mode.

Blocks weak, out-of-scope, duplicate, or under-proven candidates before any report is
written. The default is always ``Submit: NO``. A row only relaxes to
``AFTER_POC_ASSERTION_PASSES`` (never a bare "yes" in a static run) when every gate
passes: in scope, non-duplicate, not public-test-covered, not documented, not
trusted-role-only, attacker reachable, material, severity eligible, PoC ready, source
and deployment context adequate, and no unresolved scope collision. A human rewrite is
always required.
"""
from __future__ import annotations

from . import models as M

SUBMIT_NO = "NO"
SUBMIT_AFTER_POC = "AFTER_POC_ASSERTION_PASSES"

_IMPACT_KILLERS = (M.VALUE_OUT_PATH, M.WITHDRAWAL_QUEUE, M.CLAIM_QUEUE, M.ADAPTER_WITHDRAWABILITY,
                   M.BRIDGE_MESSAGE_ACCOUNTING, M.EMERGENCY_EXIT_ACCOUNTING, M.STATE_MACHINE_VALUE_FLOW,
                   M.DEPLOYMENT_MISMATCH, M.CROSS_POOL_ISOLATION, M.CROSS_CHAIN_DOMAIN_SEPARATION)


def build_report_filter(
    leads: list,
    *,
    poc_status_by_lead: dict,
    scope_collision: bool,
    rpc_ran: bool,
) -> list:
    rows: list = []
    for lead in leads:
        poc_status = poc_status_by_lead.get(lead.lead_id, "")
        gates_passed, reason = _gates(lead, poc_status, scope_collision)
        submit = SUBMIT_AFTER_POC if gates_passed else SUBMIT_NO

        principal = lead.lead_type in (M.VALUE_OUT_PATH, M.SHARE_ACCOUNTING, M.WITHDRAWAL_QUEUE,
                                       M.ADAPTER_WITHDRAWABILITY, M.CROSS_POOL_ISOLATION, M.DEPLOYMENT_MISMATCH)
        yield_theft = lead.lead_type in (M.REWARD_ACCOUNTING, M.FEE_DISPATCH, M.ORACLE_RATE_ACCOUNTING)
        fee_theft = lead.lead_type == M.FEE_DISPATCH
        freeze = lead.lead_type in (M.MIGRATION_ACCOUNTING, M.LOCK_UNLOCK_ACCOUNTING, M.INITIALIZATION_WIRING)

        rows.append(M.ReportFilterRow(
            lead_id=lead.lead_id,
            title=lead.title,
            contract=lead.contract,
            address="",
            function=lead.function,
            lead_type=lead.lead_type,
            severity_candidate=lead.expected_severity_ceiling,
            eligibility=("eligible" if lead.decision in M.PURSUEABLE else "not yet"),
            scope=lead.scope_confidence,
            freshness=lead.freshness_status,
            dedup=lead.known_match_status,
            deployment=lead.deployment_status or "n/a",
            attacker=lead.attacker_reachability,
            trusted_role_required=(lead.known_match_status == M.TRUSTED_ROLE_ONLY or lead.trusted_role_risk_score >= 60),
            principal_loss=principal,
            yield_theft=yield_theft,
            fee_theft=fee_theft,
            permanent_freeze=freeze,
            temporary_freeze=False,
            materiality=lead.materiality,
            oos_flags=(["OUT_OF_SCOPE"] if lead.known_match_status == M.OUT_OF_SCOPE else []),
            known_issue_flags=([lead.known_match_status] if lead.known_match_status in
                               (M.LIKELY_DUPLICATE, M.DOCUMENTED_BEHAVIOR, M.ACKNOWLEDGED_RISK) else []),
            public_test_flags=(["PUBLIC_TEST_COVERED"] if lead.known_match_status == M.PUBLIC_TEST_COVERED else []),
            poc_status=poc_status or "NOT_PLANNED",
            expected_assertion=("value/accounting invariant broken for attacker profit"
                                if lead.decision in M.PURSUEABLE else ""),
            submit=submit,
            human_rewrite_required=True,
            reason=reason,
        ))
    return rows


def _gates(lead: M.HunterLead, poc_status: str, scope_collision: bool) -> tuple[bool, str]:
    if scope_collision:
        return False, "Unresolved scope collision: resolve the product/version/chain first."
    if lead.decision in M.KILL_DECISIONS:
        return False, f"Killed ({lead.decision}); do not write a report."
    if lead.decision in M.PARK_DECISIONS:
        return False, f"Parked ({lead.decision}); gather the missing context first."
    if lead.known_match_status in (M.OUT_OF_SCOPE, M.PUBLIC_TEST_COVERED, M.DOCUMENTED_BEHAVIOR,
                                   M.LIKELY_DUPLICATE, M.TRUSTED_ROLE_ONLY):
        return False, f"Dedup/scope status {lead.known_match_status} blocks submission."
    if lead.attacker_reachability != "UNPRIVILEGED_EXTERNAL":
        return False, "Not confirmed unprivileged-attacker reachable."
    if lead.materiality != M.HIGH:
        return False, "Material impact not established at HIGH."
    if lead.expected_severity_ceiling in (M.LOW_ONLY, M.INFO_ONLY, M.NOT_ELIGIBLE):
        return False, "Severity ceiling not eligible for a reward."
    if lead.source_status in M.SOURCE_INADEQUATE:
        return False, "Source/deployment context inadequate."
    if poc_status != M.POC_READY:
        return False, f"PoC not ready ({poc_status or 'NOT_PLANNED'})."
    return True, ("All gates pass: in scope, non-duplicate, reachable, material, eligible, PoC ready. "
                  "Submit only AFTER the PoC assertion passes; a human must rewrite the report.")
