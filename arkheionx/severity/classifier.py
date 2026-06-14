"""Economic severity classifier (Layer 7) — the decision tree.

Step 1 reachability/scope/dedup -> Step 2 impact -> Step 3 cap -> Step 4
repeatability/gas -> Step 5 realism -> Step 6 final label. Conservative by design:
dust, trusted-role, buffer-capped, and unproven candidates are capped or killed.
"""
from __future__ import annotations

from . import caps, exploitability, gas_profit, impact_model, models as S, realism, score


def _incomplete_fields(candidate):
    """Fields a candidate must carry before it can be a SUBMIT_* (Rule 001.3/001.4)."""
    missing = []
    if not (candidate.attacker_capability or candidate.attacker):
        missing.append("attacker")
    if not candidate.victim:
        missing.append("victim")
    if not candidate.asset:
        missing.append("asset")
    if not candidate.broken_invariant:
        missing.append("broken_invariant")
    return missing


def _base_label(candidate, context):
    family = candidate.invariant_family
    decimals = int(context.get("asset_decimals", 0) or 0)
    dust_only = bool(context.get("dust_only", False))

    if family == "DEBT_REPAYMENT_RECONCILIATION":
        # No attacker profit; loss is lender dust bounded by token base units.
        if dust_only or (decimals and decimals >= 18):
            return S.KILL_DUST
        return S.VALID_BUT_LOW
    if family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA":
        return S.NEEDS_FORK_PROOF
    if family == "SWAP_ACTUAL_RECEIVED_VS_CREDITED":
        return S.NEEDS_FORK_PROOF if candidate.fork_requirement else S.SUBMIT_MEDIUM_CANDIDATE
    if family == "CROSS_CHAIN_SUPPLY_CONSERVATION":
        # Replayable destination mint inflates supply systemically; the replay itself
        # is locally provable, so a non-fork candidate is High, not Medium.
        return S.NEEDS_FORK_PROOF if candidate.fork_requirement else S.SUBMIT_HIGH_CANDIDATE
    if family == "DEPOSIT_CONSUMPTION":
        return S.SUBMIT_HIGH_CANDIDATE
    if family == "ORACLE_DECIMAL_NORMALIZATION":
        if dust_only:
            return S.VALID_BUT_LOW
        # An unprivileged over-borrow from a mis-scaled price is high-impact and
        # locally provable; fork only if a real deployed feed sets the magnitude.
        return S.NEEDS_FORK_PROOF if candidate.fork_requirement else S.SUBMIT_HIGH_CANDIDATE
    if family in ("VAULT_SHARE_ASSET_RECONCILIATION", "BORROW_CONSERVATION",
                  "COLLATERAL_STATUS_RELEASE"):
        if dust_only:
            return S.VALID_BUT_LOW
        return S.SUBMIT_MEDIUM_CANDIDATE
    return S.VALID_BUT_LOW_LIKELIHOOD


def classify(candidate, scope=None, context=None) -> S.SeverityVerdict:
    context = context or {}
    family = candidate.invariant_family
    reasons = []

    # --- Step 1: reachability / scope / dedup (hard gates) -----------------
    if candidate.scope_risk == "OUT_OF_SCOPE":
        label = S.KILL_OUT_OF_SCOPE
        reasons.append("Out of scope per scope rules.")
    elif candidate.duplicate_risk == "SAME_ROOT_CAUSE":
        label = S.KILL_DUPLICATE_ROOT_CAUSE
        reasons.append("Same root cause as a known/previous finding.")
    elif candidate.role_gated:
        label = S.KILL_TRUSTED_ROLE
        reasons.append("Reachable only by a trusted role; not an unprivileged bug.")
    else:
        label = _base_label(candidate, context)
        # A submit-worthy label requires complete attacker/victim/asset/invariant.
        missing = _incomplete_fields(candidate)
        if label in S.SUBMIT_LABELS and missing:
            label = S.PARK_INCOMPLETE
            reasons.append("Cannot submit: missing " + ", ".join(missing) + ".")

    impact_pair = impact_model.impact(family)
    cap_pair = caps.cap(family)
    reach = exploitability.reachability(candidate)
    like = exploitability.likelihood(candidate)
    rep = exploitability.repeatability(family)
    gas_text = gas_profit.gas(family)
    real_text = realism.realism(family, candidate)
    itype, _ = score.impact_type(family)
    ctype, _ = score.cap_type(family)
    proof_q = score.proof_quality(candidate)
    sev_score = score.build_score(candidate, label)

    if label == S.NEEDS_FORK_PROOF:
        reasons.append("Real external state (AMM liquidity / deployed config) sets the actual "
                       "loss; prove on a fork before any submission decision.")
    if label == S.VALID_BUT_LOW:
        reasons.append("Technically valid but economically capped; submit only as low if the "
                       "program accepts it.")
    if label == S.KILL_DUST:
        reasons.append("Loss is dust with no attacker profit (immune for 18-decimal assets).")
    if label == S.PARK_INCOMPLETE:
        reasons.append("Park until the missing attacker/victim/asset/invariant fields are filled.")

    verdict = S.SeverityVerdict(
        candidate_id=candidate.id, label=label,
        impact=f"{impact_pair[0]}: {impact_pair[1]}", impact_type=itype,
        likelihood=f"{reach}; {like}",
        cap=f"{cap_pair[0]}: {cap_pair[1]}", cap_type=ctype, proof_quality=proof_q,
        repeatability=rep, gas=gas_text, realism=real_text,
        reasons=reasons, score=sev_score.to_dict(),
        final_recommendation=label, confidence=candidate.confidence,
    )

    # --- annotate the candidate -------------------------------------------
    candidate.economic_severity = label
    candidate.recommendation = label
    candidate.severity_detail = {
        "impact": verdict.impact, "impact_type": itype, "likelihood": verdict.likelihood,
        "cap": verdict.cap, "cap_type": ctype, "proof_quality": proof_q,
        "repeatability": verdict.repeatability, "gas": verdict.gas, "realism": verdict.realism,
        "score": sev_score.to_dict(), "reasons": verdict.reasons,
    }
    return verdict


def apply_gate(graph, scope=None, context=None) -> list:
    return [classify(c, scope=scope, context=context) for c in graph.candidates]
