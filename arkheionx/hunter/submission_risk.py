"""Submission-risk engine for hunter mode.

For every lead it estimates *why a reviewer might reject a report* before any time is
spent writing one: duplicate risk, out-of-scope risk, trusted-role risk, known-corpus
gap risk, deployment-context gap risk, materiality risk, and proof difficulty. It also
states the submit-ready threshold. This is a rejection-risk model, not a payout
promise — the human always makes the final call.
"""
from __future__ import annotations

from . import models as M

_HIGH, _MED, _LOW = M.RISK_HIGH, M.RISK_MEDIUM, M.RISK_LOW


def _dup_risk(lead: M.HunterLead) -> str:
    if lead.known_match_status in (M.LIKELY_DUPLICATE, M.PUBLIC_TEST_COVERED, M.ACKNOWLEDGED_RISK):
        return _HIGH
    if lead.known_match_status == M.SIMILAR_KNOWN or lead.duplicate_risk_score >= 55:
        return _MED
    if lead.dedup_status == M.DEDUP_BLIND:
        return _MED  # unknown duplicate risk in a blind corpus is itself a risk
    return _LOW


def _corpus_gap_risk(lead: M.HunterLead) -> str:
    return {M.DEDUP_BLIND: _HIGH, M.DEDUP_PARTIAL: _MED,
            M.DEDUP_USABLE: _LOW, M.DEDUP_STRONG: _LOW}.get(lead.dedup_status, _MED)


def _deployment_gap_risk(lead: M.HunterLead, rpc_ran: bool) -> str:
    if lead.lead_type in (M.DEPLOYMENT_MISMATCH, M.LIVE_REGISTRY_DIFF) and not rpc_ran:
        return _HIGH
    if lead.deployment_status in M.DEPLOYMENT_MISMATCH_STATUSES:
        return _LOW
    return _MED if not rpc_ran and lead.lead_type == M.DEPLOYMENT_MISMATCH else _LOW


def build_submission_risks(leads: list, *, rpc_ran: bool, scope_provided: bool) -> list:
    risks: list = []
    for lead in leads:
        dup = _dup_risk(lead)
        oos = _HIGH if lead.known_match_status == M.OUT_OF_SCOPE else (_MED if not scope_provided else _LOW)
        trusted = _HIGH if lead.known_match_status == M.TRUSTED_ROLE_ONLY else (
            _MED if lead.trusted_role_risk_score >= 60 else _LOW)
        corpus_gap = _corpus_gap_risk(lead)
        deploy_gap = _deployment_gap_risk(lead, rpc_ran)
        materiality = {M.HIGH: _LOW, M.MEDIUM: _MED, M.LOW: _HIGH}.get(lead.materiality, _MED)
        proof = {M.HIGH: _HIGH, M.MEDIUM: _MED, M.LOW: _LOW}.get(lead.proof_difficulty, _MED)

        pushback: list = []
        if dup != _LOW:
            pushback.append("Reviewer may mark this a duplicate; cite the exact differing root behavior.")
        if oos != _LOW:
            pushback.append("Reviewer may mark this out of scope; confirm the surface against scope rules.")
        if trusted != _LOW:
            pushback.append("Reviewer may say it needs a trusted role; show an unprivileged path.")
        if corpus_gap != _LOW:
            pushback.append("Dedup corpus is incomplete; a known finding may exist that was not parsed.")
        if deploy_gap == _HIGH:
            pushback.append("Live deployment context is unverified; verify read-only before claiming a mismatch.")
        if materiality != _LOW:
            pushback.append("Materiality may be questioned; quantify principal/yield/fee loss or freeze.")

        evidence_needed: list = []
        if lead.decision in M.PURSUEABLE:
            evidence_needed.append("A passing local PoC assertion that demonstrates the value/accounting break.")
        if corpus_gap != _LOW:
            evidence_needed.append("A dedup search across known issues, audits, and public tests for the root behavior.")
        if deploy_gap != _LOW:
            evidence_needed.append("Read-only on-chain confirmation of the deployed wiring.")

        threshold = (
            "Submit only after: a passing PoC assertion, a clean dedup check, confirmed in-scope "
            "surface, and (if relevant) verified live deployment context.")

        risks.append(M.SubmissionRisk(
            lead_id=lead.lead_id,
            status=lead.submission_risk,
            expected_severity_ceiling=lead.expected_severity_ceiling,
            expected_payout_eligibility=(M.HIGH if lead.decision == M.PURSUE_NOW else
                                         (M.MEDIUM if lead.decision == M.NEEDS_POC else M.LOW)),
            duplicate_rejection_risk=dup,
            oos_rejection_risk=oos,
            trusted_role_rejection_risk=trusted,
            known_corpus_gap_risk=corpus_gap,
            deployment_context_gap_risk=deploy_gap,
            materiality_risk=materiality,
            proof_difficulty_risk=proof,
            reviewer_pushback=pushback,
            evidence_needed=evidence_needed,
            submit_ready_threshold=threshold,
        ))
    return risks
