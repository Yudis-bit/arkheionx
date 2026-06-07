"""Counterfactual research planning for the v5 Blind Spot Intelligence layer.

A counterfactual is a research question of the form "what if this assumption is
false?". This module negates the review map's guarding assumptions (and the
authorization / periphery signals that imply assumptions) into deterministic,
testable prompts.

A counterfactual is a research prompt, never a finding. It carries a local test
direction, the evidence required, and a stop condition, but it is only ever
settled by a human-reviewed local test.
"""
from __future__ import annotations

from arkheionx.review_map.model import ReviewMap
from arkheionx.research.surfaces import ResearchSurfaces

from . import models as m

# topic -> counterfactual template. Generic; never tied to a real protocol.
_TEMPLATES: dict[str, dict] = {
    "oracle-fresh": {
        "assumption": "The oracle/price value is fresh, correctly scaled, and cannot be stale-but-positive.",
        "what_if_false": "A stale but positive (or wrongly scaled) price reaches accounting unchecked.",
        "why": "Accounting and liquidation decisions depend on the price; a wrong value propagates into balances.",
        "test": "Drive a stale, zero, and extreme price through the dependent path and assert it is rejected or bounded before it reaches accounting.",
        "evidence": "A local test showing a stale/zero/extreme price is rejected or bounded.",
        "stop": "If freshness, scaling, and bounds are enforced and the test proves rejection, mark the hypothesis rejected.",
        "testability": "high",
    },
    "erc20-standard": {
        "assumption": "Tokens behave like a standard ERC20 and the transferred amount equals the accounting delta.",
        "what_if_false": "A fee-on-transfer, rebasing, or non-returning token makes the accounting delta differ from the transfer.",
        "why": "Value entry/exit accounting assumes amount-in equals amount-credited.",
        "test": "Route the value path through a fee-on-transfer / non-standard token mock and assert accounting matches the actual balance change.",
        "evidence": "A local test with a non-standard token mock showing accounting stays correct (or exactly how it breaks).",
        "stop": "If accounting reconciles to the real balance delta, mark the hypothesis rejected.",
        "testability": "high",
    },
    "admin-bounded": {
        "assumption": "The admin/owner path cannot move user value outside the documented emergency/trust boundary.",
        "what_if_false": "A privileged path moves or redirects user value beyond the documented boundary.",
        "why": "Privileged configuration guards value movement and trust.",
        "test": "Call the privileged path as the admin and assert it cannot reach user value outside the documented boundary.",
        "evidence": "A local test demonstrating the privileged boundary holds.",
        "stop": "If the privileged path is bounded as documented, mark the hypothesis rejected.",
        "testability": "medium",
    },
    "reward-monotonic": {
        "assumption": "The reward/accrual index is monotonic and updated before balance changes.",
        "what_if_false": "The index moves out of order or a balance changes before the index updates.",
        "why": "Reward accounting depends on ordering and monotonicity across repeated operations.",
        "test": "Interleave accrual and balance changes and assert the index never decreases and rewards are conserved.",
        "evidence": "A local test of interleaved accrual/balance operations.",
        "stop": "If the index stays monotonic and rewards are conserved, mark the hypothesis rejected.",
        "testability": "high",
    },
    "share-proportional": {
        "assumption": "Deposits/withdrawals preserve proportional ownership across rounding and donation scenarios.",
        "what_if_false": "A first-deposit or direct-donation rounding edge lets an early actor skew share price.",
        "why": "Share accounting controls who can claim deposited value.",
        "test": "Deposit 1 wei, donate assets directly, then deposit again and assert the first depositor cannot capture later deposits.",
        "evidence": "A local test of first-deposit share math plus a direct donation.",
        "stop": "If share math resists the donation and rounding edge, mark the hypothesis rejected.",
        "testability": "high",
    },
    "no-reentrancy": {
        "assumption": "External calls cannot re-enter or reorder unsafe state.",
        "what_if_false": "A callback or external call re-enters before state is settled, or reorders state.",
        "why": "State settled after an external call can be observed mid-update by a reentrant caller.",
        "test": "Re-enter through the external call/callback before state settles and assert the guard holds.",
        "evidence": "A local test re-entering through the callback and from an unexpected caller.",
        "stop": "If reentry and unexpected callers are handled safely, mark the hypothesis rejected.",
        "testability": "medium",
    },
    "decimals-normalized": {
        "assumption": "Token and price decimals are consistently normalized in value math.",
        "what_if_false": "A decimals mismatch scales a value by orders of magnitude.",
        "why": "Mis-scaled math silently mis-prices value.",
        "test": "Run the value math with mismatched token/price decimals and assert scaling stays correct.",
        "evidence": "A local test with mismatched decimals.",
        "stop": "If scaling is normalized correctly, mark the hypothesis rejected.",
        "testability": "high",
    },
    "fee-bounded": {
        "assumption": "Configurable fees are bounded and validated.",
        "what_if_false": "A fee can be set outside a safe bound and capture value.",
        "why": "An unbounded fee redirects value.",
        "test": "Set the fee to boundary and out-of-bound values and assert validation rejects unsafe values.",
        "evidence": "A local test of fee bounds.",
        "stop": "If fee bounds are enforced, mark the hypothesis rejected.",
        "testability": "high",
    },
    "liquidation-bounded": {
        "assumption": "Liquidation/health math cannot liquidate healthy positions or block unhealthy liquidation.",
        "what_if_false": "An off-by-one or rounding edge liquidates a healthy position or blocks a needed liquidation.",
        "why": "Liquidation boundaries decide who loses value.",
        "test": "Test a position exactly at the health boundary (just-healthy vs just-unhealthy) and assert it behaves as documented.",
        "evidence": "A local test at the exact health-factor boundary.",
        "stop": "If the boundary behaves as documented with no early/late seizure, mark the hypothesis rejected.",
        "testability": "high",
    },
    "signature-binds": {
        "assumption": "The signed digest binds every value-relevant field and the domain data.",
        "what_if_false": "A signature binds less than expected and authorizes a different action, amount, or domain.",
        "why": "Authorization controls value movement.",
        "test": "Build two actions differing in one value-moving field and assert a signature for one cannot authorize the other; also vary signer, nonce, deadline, chain id, and verifying contract.",
        "evidence": "A local test showing the unauthorized alternative is rejected.",
        "stop": "If the digest binds the full field set and the test proves rejection, mark the hypothesis rejected.",
        "testability": "high",
    },
    "merkle-binds": {
        "assumption": "The Merkle leaf encodes every field needed to bind the proof to the intended claim and root.",
        "what_if_false": "A proof for one claim authorizes a different claim shape or amount, or a wrong-shape proof is accepted.",
        "why": "The proof gates value-moving claims.",
        "test": "Test a proof for a different leaf, a different root, a malformed/wrong-length proof, and a leaf missing a bound field; assert all are rejected.",
        "evidence": "A local test showing each malformed/alternative proof is rejected.",
        "stop": "If the leaf binds all fields and malformed proofs are rejected, mark the hypothesis rejected.",
        "testability": "high",
    },
    "replay-enforced": {
        "assumption": "Replay protection (nonce) and expiry (deadline) are enforced in all execution paths.",
        "what_if_false": "A used nonce or an expired deadline still authorizes an action on some path.",
        "why": "Replayable authorization can repeat a value-moving action.",
        "test": "Replay a used signature/nonce and submit an expired deadline through every entry path and assert all are rejected.",
        "evidence": "A local test replaying a used nonce and an expired deadline.",
        "stop": "If replay and expiry are rejected on all paths, mark the hypothesis rejected.",
        "testability": "high",
    },
    "periphery-equivalence": {
        "assumption": "The periphery path is equivalent to the direct core path, or documented differences are tested.",
        "what_if_false": "Routing through the periphery produces different core accounting than the equivalent direct call.",
        "why": "Periphery/core mismatches can mis-account value.",
        "test": "Compare core state after a periphery call vs the equivalent direct call and assert they match.",
        "evidence": "A local test comparing periphery vs direct-call accounting.",
        "stop": "If periphery and direct-call accounting match, mark the hypothesis rejected.",
        "testability": "high",
    },
    "skip-after-safe": {
        "assumption": "Malformed items are skipped only after all pre-skip computation is safe.",
        "what_if_false": "Pre-skip computation reverts earlier than the documented skip handler, so a bad item breaks the batch.",
        "why": "Documented skip/continue-on-error behavior can be defeated by an earlier revert.",
        "test": "Feed one malformed item among many and assert the documented skip path is reached and the batch continues.",
        "evidence": "A local test of the partial-failure / skip path with one malformed item.",
        "stop": "If the skip path is reached as documented, mark the hypothesis rejected.",
        "testability": "high",
    },
    "callback-ordering": {
        "assumption": "A callback cannot reorder state or arrive from an unexpected caller.",
        "what_if_false": "A callback reorders state or is invoked by an unexpected caller.",
        "why": "Callback ordering assumptions guard state consistency.",
        "test": "Invoke the callback from an unexpected caller and during a state update and assert the guard holds.",
        "evidence": "A local test exercising callback ordering and caller assumptions.",
        "stop": "If ordering and caller checks hold, mark the hypothesis rejected.",
        "testability": "medium",
    },
}

_CATEGORY_TO_TOPIC = {
    "oracle": "oracle-fresh",
    "token": "erc20-standard",
    "access-control": "admin-bounded",
    "reentrancy": "no-reentrancy",
    "math": "decimals-normalized",
    "config": "fee-bounded",
    "lending": "liquidation-bounded",
}
# accounting category maps by assumption id (two accounting assumptions exist).
_ASM_ID_TO_TOPIC = {
    "asm-reward-monotonic": "reward-monotonic",
    "asm-share-proportional": "share-proportional",
}
_AUTH_KIND_TO_TOPIC = {
    "signature": "signature-binds",
    "domain": "signature-binds",
    "merkle": "merkle-binds",
    "replay": "replay-enforced",
}

_DO_NOT_CLAIM = ("This is a research prompt, not a finding. It is not a vulnerability "
                 "unless a local proof demonstrates it and a human confirms it.")


def _first_target(used_by: list[str]) -> str:
    for t in used_by:
        if "." in t:
            return t
    return used_by[0] if used_by else ""


def build_counterfactuals(rm: ReviewMap, surfaces: ResearchSurfaces,
                          records: list[m.SurfaceRecord], *, limit: int = 24) -> list[dict]:
    """Generate deterministic counterfactuals from assumptions + auth/periphery signals."""
    crit_by_target = {r.target: r.criticality_potential for r in records}
    src_by_target = {r.target: r.source for r in records}
    seen: set[tuple[str, str]] = set()
    out: list[dict] = []

    def add(topic: str, target: str, contract: str, function: str, source: str, surface_label: str):
        tmpl = _TEMPLATES.get(topic)
        if tmpl is None:
            return
        key = (topic, target)
        if key in seen:
            return
        seen.add(key)
        impact = crit_by_target.get(target, m.CRIT_UNKNOWN)
        out.append({
            "assumption": tmpl["assumption"],
            "topic": topic,
            "surface": surface_label,
            "contract": contract,
            "function": function,
            "target": target,
            "source": source or src_by_target.get(target, ""),
            "what_if_false": tmpl["what_if_false"],
            "why_it_could_matter": tmpl["why"],
            "impact_potential": impact,
            "testability": tmpl["testability"],
            "priority": _priority(impact, tmpl["testability"]),
            "local_test_direction": tmpl["test"],
            "evidence_needed": tmpl["evidence"],
            "stop_condition": tmpl["stop"],
            "do_not_claim": _DO_NOT_CLAIM,
            "status": m.STATUS_OPEN,
            "manual_review_required": True,
        })

    # 1. Review-map assumptions (formal guarding properties).
    for asm in sorted(rm.assumptions, key=lambda a: a.id):
        topic = _ASM_ID_TO_TOPIC.get(asm.id) or _CATEGORY_TO_TOPIC.get(asm.category)
        if not topic:
            continue
        target = _first_target(asm.used_by)
        contract, _, function = target.partition(".")
        add(topic, target, contract, function, "", f"{asm.category} assumption ({asm.id})")

    # 2. Authorization signals (signature / domain / Merkle / replay).
    for row in surfaces.authorization_surfaces:
        topic = _AUTH_KIND_TO_TOPIC.get(row.get("kind", ""))
        if not topic or not row.get("function"):
            continue
        add(topic, row["target"], row["contract"], row["function"], row.get("source", ""),
            "authorization surface")

    # 3. Periphery signals (periphery/core, skip-on-revert, callback).
    for row in surfaces.periphery_surfaces:
        interactions = set(row.get("interaction_type", []))
        target, contract, function = row["target"], row["contract"], row["function"]
        source = row.get("source", "")
        add("periphery-equivalence", target, contract, function, source, "periphery surface")
        if {"try-catch", "loop-with-external-call"} & interactions:
            add("skip-after-safe", target, contract, function, source, "periphery surface")
        if "low-level-call" in interactions or "periphery-keyword" in interactions:
            add("callback-ordering", target, contract, function, source, "periphery/callback surface")

    # Deterministic order: priority, then impact potential, then target, then topic.
    out.sort(key=lambda c: (m.blind_spot_rank(c["priority"]), m.criticality_rank(c["impact_potential"]),
                            c["target"], c["topic"]))
    out = out[:limit]
    for i, cf in enumerate(out, 1):
        cf_id = f"CF-{i:03d}"
        out[i - 1] = {"id": cf_id, **cf}
    return out


def _priority(impact_potential: str, testability: str) -> str:
    """Counterfactual priority from impact potential + testability (heuristic)."""
    rank = m.criticality_rank(impact_potential)
    if rank <= 0:
        return m.BSP_VERY_HIGH
    if rank == 1:
        return m.BSP_VERY_HIGH if testability == "high" else m.BSP_HIGH
    if rank == 2:
        return m.BSP_HIGH if testability == "high" else m.BSP_MEDIUM
    if rank == 3:
        return m.BSP_MEDIUM
    return m.BSP_MEDIUM if testability == "high" else m.BSP_MONITOR
