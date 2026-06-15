"""Fail-closed bounty-reality decision gate."""
from __future__ import annotations

from arkheionx.memory import families as F
from arkheionx.severity import models as S

from .models import BountyRealityInput, BountyRealityResult, BountyRealityVerdict as V
from .program_policy import ProgramPolicy

_BLOCKING = {
    V.DO_NOT_SUBMIT_AS_MEDIUM,
    V.DO_NOT_SUBMIT_DUPLICATE,
    V.DO_NOT_SUBMIT_PREVIOUSLY_REJECTED,
    V.DO_NOT_SUBMIT_DUST,
    V.DO_NOT_SUBMIT_PRECISION_ONLY,
    V.DO_NOT_SUBMIT_NO_PROFIT,
    V.DO_NOT_SUBMIT_VICTIM_OPT_IN,
    V.DO_NOT_SUBMIT_TRUSTED_ROLE,
    V.DO_NOT_SUBMIT_OFFCHAIN_VALIDATION,
    V.DO_NOT_SUBMIT_KEY_REUSE,
    V.DO_NOT_SUBMIT_FORCED_VALUE_TRANSFER_ONLY,
    V.DO_NOT_SUBMIT_GAS_ONLY,
    V.DO_NOT_SUBMIT_PROGRAM_CARVEOUT,
}

_PRIORITY = (
    V.DO_NOT_SUBMIT_PREVIOUSLY_REJECTED,
    V.DO_NOT_SUBMIT_DUPLICATE,
    V.DO_NOT_SUBMIT_PROGRAM_CARVEOUT,
    V.DO_NOT_SUBMIT_OFFCHAIN_VALIDATION,
    V.DO_NOT_SUBMIT_KEY_REUSE,
    V.DO_NOT_SUBMIT_FORCED_VALUE_TRANSFER_ONLY,
    V.DO_NOT_SUBMIT_TRUSTED_ROLE,
    V.DO_NOT_SUBMIT_GAS_ONLY,
    V.DO_NOT_SUBMIT_DUST,
    V.DO_NOT_SUBMIT_PRECISION_ONLY,
    V.DO_NOT_SUBMIT_NO_PROFIT,
    V.DO_NOT_SUBMIT_VICTIM_OPT_IN,
    V.DO_NOT_SUBMIT_AS_MEDIUM,
)


def _get(value, key, default=None):
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _reviewer_rows(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _add(blockers: list, tags: list, explanations: list, verdict: str, tag: str, text: str):
    if verdict not in blockers:
        blockers.append(verdict)
    if tag not in tags:
        tags.append(tag)
    explanations.append(text)


def evaluate(data: BountyRealityInput) -> BountyRealityResult:
    candidate = data.attack_candidate
    severity = data.severity_result
    memory = data.memory_match
    policy = ProgramPolicy.from_object(data.scope_policy)
    family = F.canonical(
        data.family
        or _get(candidate, "root_cause_family", "")
        or _get(candidate, "invariant_family", "")
        or _get(memory, "root_cause_family", "")
        or _get(memory, "invariant_family", "")
    )
    candidate_id = _get(candidate, "id", "") or ""
    cap_type = data.cap_type or _get(severity, "cap_type", "") or ""
    proof_quality = data.proof_quality or _get(severity, "proof_quality", "") or ""
    duplicate = data.duplicate_status or _get(candidate, "duplicate_risk", "") or ""
    blockers: list[str] = []
    tags: list[str] = []
    explanations: list[str] = []

    outcomes = _reviewer_rows(data.reviewer_outcome_memory) + _reviewer_rows(data.program_history)
    reviewer_tags = {
        tag
        for outcome in outcomes
        for tag in (_get(outcome, "reason_tags", []) or [])
    }
    reviewer_statuses = {_get(outcome, "status", "") for outcome in outcomes}
    memory_status = (_get(memory, "status", "") or "").lower()

    if memory_status == "rejected" or bool(_get(memory, "do_not_resubmit", False)) \
            or "rejected" in reviewer_statuses:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_PREVIOUSLY_REJECTED,
             "previously_rejected", "The semantic root cause has a prior rejection or do-not-resubmit flag.")

    if duplicate == "SAME_ROOT_CAUSE" or memory_status == "duplicate" \
            or "duplicate" in reviewer_statuses or "duplicate" in reviewer_tags:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_DUPLICATE,
             "duplicate", "The candidate matches a known root cause or duplicate outcome.")

    dust = (
        family == F.PRECISION_DUST_ONLY
        or cap_type == S.ROUNDING_UNIT_CAPPED
        or _get(severity, "impact_type", "") == S.DUST_ONLY
        or bool(data.cap_tiny)
        or "dust" in reviewer_tags
    )
    if dust:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_DUST,
             "dust", "The demonstrated impact is capped at dust or rounding units.")

    if family in (F.ROUNDING_REPAYMENT_RECONCILIATION, F.ROUNDING_SHARE_ASSET_RECONCILIATION,
                  F.PRECISION_DUST_ONLY) or "precision_rounding" in reviewer_tags:
        if dust or bool(data.low_decimal_asset_required):
            _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_PRECISION_ONLY,
                 "precision_rounding", "The impact depends on precision loss without a larger economic path.")

    if data.attacker_profit is False or "no_profit" in reviewer_tags \
            or "missing_profit_path" in reviewer_tags:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_NO_PROFIT,
             "no_profit", "No attacker capture or profit path is demonstrated.")

    if data.victim_opt_in is True or "victim_opt_in" in reviewer_tags \
            or "signed_terms" in reviewer_tags:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_VICTIM_OPT_IN,
             "victim_opt_in", "The affected party explicitly accepts the relevant terms.")

    trusted_role = family == F.TRUSTED_ROLE_ASSUMPTION or bool(_get(candidate, "role_gated", False))
    if trusted_role:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_TRUSTED_ROLE,
             "trusted_role", "The path depends only on trusted-role behavior.")

    offchain = family == F.OFFCHAIN_VALIDATION_OMISSION or "offchain_validation" in reviewer_tags
    if offchain and (policy.excludes_offchain_validation or family == F.OFFCHAIN_VALIDATION_OMISSION):
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_OFFCHAIN_VALIDATION,
             "offchain_validation", "The issue is limited to an off-chain validation omission.")

    key_reuse = family == F.KEY_REUSE_REPLAY or data.requires_key_reuse is True \
        or "key_reuse" in reviewer_tags
    if key_reuse and (policy.excludes_key_reuse or data.requires_key_reuse is True):
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_KEY_REUSE,
             "key_reuse", "Replay requires reused signing authority across domains.")

    forced = family == F.FORCED_VALUE_TRANSFER_NO_LOGIC_FLAW \
        or data.no_contract_logic_flaw is True or "forced_value_transfer" in reviewer_tags
    if forced:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_FORCED_VALUE_TRANSFER_ONLY,
             "forced_value_transfer", "Forced balance change is not coupled to an exploitable logic flaw.")

    gas_only = family == F.GAS_ONLY or data.gas_only is True or data.style_only is True \
        or "gas_only" in reviewer_tags
    if gas_only:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_GAS_ONLY,
             "gas_only", "The issue is gas or style only.")

    carveouts = set(data.carveout_tags or [])
    carveouts.update(policy.excluded_tags)
    if carveouts or "carveout" in reviewer_tags:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_PROGRAM_CARVEOUT,
             "carveout", "A generic policy carve-out covers the candidate.")

    if data.malicious_asset_required or data.low_impact_grief_only:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_AS_MEDIUM,
             "no_significant_risk", "The current assumptions do not support medium impact.")

    if family == F.LENDER_CONSENT_VALUE_FIELD_BINDING and (
        data.official_buffer_small is True
        or data.capture_proven is False
        or data.safe_mode_exists is True
    ):
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_AS_MEDIUM,
             "buffer_capped", "The route effect is buffer-capped and realistic capture is not proven.")

    if "out_of_scope" in reviewer_tags or policy.in_scope is False or data.not_oos is False:
        _add(blockers, tags, explanations, V.DO_NOT_SUBMIT_PROGRAM_CARVEOUT,
             "out_of_scope", "The candidate is outside the supplied policy scope.")

    primary = next((item for item in _PRIORITY if item in blockers), "")
    if primary:
        secondary = [item for item in blockers if item != primary]
        return BountyRealityResult(
            candidate_id=candidate_id,
            family=family,
            verdict=primary,
            final_verdict=V.VALID_CODE_BUG_BUT_NOT_BOUNTY_WORTHY,
            secondary_verdicts=secondary,
            reason_tags=tags,
            reviewer_risk="HIGH",
            submit_recommendation="DO_NOT_SUBMIT",
            blocked=True,
            explanation=explanations,
        )

    proof_sufficient = proof_quality in (S.LOCAL_POC_PASSING, S.FORK_POC_PASSING, S.REAL_ASSET_VALIDATED)
    economic_path = data.attacker_profit is True and data.victim_loss is True
    unprivileged = data.unprivileged is True or (
        bool(_get(candidate, "attacker_capability", ""))
        and not bool(_get(candidate, "role_gated", False))
    )
    clean_context = data.not_duplicate is not False and data.not_oos is not False \
        and duplicate != "SAME_ROOT_CAUSE"
    if proof_sufficient and economic_path and unprivileged and clean_context:
        return BountyRealityResult(
            candidate_id=candidate_id,
            family=family,
            verdict=V.SUBMITTABLE,
            final_verdict=V.SUBMITTABLE,
            reviewer_risk="LOW",
            submit_recommendation="SUBMIT_CANDIDATE",
            explanation=["An unprivileged economic loss path has passing proof and no known blocker."],
        )

    if proof_quality in ("", S.STATIC_ONLY, S.LOCAL_POC_SKELETON, S.FORK_PLAN_ONLY):
        verdict = V.NEEDS_MORE_PROOF
        recommendation = "PROVE_MORE"
    else:
        verdict = V.HUMAN_REVIEW_REQUIRED
        recommendation = "HUMAN_REVIEW"
    return BountyRealityResult(
        candidate_id=candidate_id,
        family=family,
        verdict=verdict,
        final_verdict=verdict,
        reason_tags=["incomplete_bounty_reality"],
        reviewer_risk="MEDIUM",
        submit_recommendation=recommendation,
        explanation=["No hard blocker was found, but bounty relevance is not sufficiently proven."],
    )


def evaluate_graph(graph, severity_results, *, memory_matches=None, scope_policy=None,
                   context_by_candidate=None) -> list[BountyRealityResult]:
    severity_by_id = {item.candidate_id: item for item in severity_results}
    memory_matches = memory_matches or {}
    context_by_candidate = context_by_candidate or {}
    results = []
    for candidate in graph.candidates:
        context = dict(context_by_candidate.get(candidate.id, {}))
        results.append(evaluate(BountyRealityInput(
            attack_candidate=candidate,
            severity_result=severity_by_id.get(candidate.id),
            memory_match=memory_matches.get(candidate.id),
            scope_policy=scope_policy,
            **context,
        )))
    return results


def blocks_submit(result: BountyRealityResult) -> bool:
    return result.blocked or result.verdict in _BLOCKING


def enforce_results(graph, severity_results, results) -> list[tuple[str, str]]:
    """Remove submit labels from candidates blocked by bounty reality."""
    result_by_id = {item.candidate_id: item for item in results}
    severity_by_id = {item.candidate_id: item for item in severity_results}
    changed = []
    for candidate in graph.candidates:
        result = result_by_id.get(candidate.id)
        if result is None or not blocks_submit(result):
            continue
        if candidate.economic_severity not in S.SUBMIT_LABELS:
            continue
        candidate.economic_severity = S.PARK_INCOMPLETE
        candidate.recommendation = result.verdict
        verdict = severity_by_id.get(candidate.id)
        if verdict is not None:
            verdict.label = S.PARK_INCOMPLETE
            verdict.final_recommendation = result.verdict
            verdict.reasons.append(
                f"Blocked by bounty reality gate: {result.verdict}."
            )
        changed.append((candidate.id, result.verdict))
    return changed
