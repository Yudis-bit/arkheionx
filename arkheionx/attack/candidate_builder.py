"""Attack candidate builder (Layer 5).

Seeds candidates from suspicious invariants, and additionally from role-gated
value-moving transitions (so access-control candidates reach the severity gate
and are killed rather than silently dropped).
"""
from __future__ import annotations

from . import models as M


def _call_sequence(smap, entry_qn, limit=8):
    by_caller = {}
    for e in smap.call_edges:
        by_caller.setdefault(e.caller, []).append(e)
    seq, seen, queue = [], set(), [entry_qn]
    while queue and len(seq) < limit:
        cur = queue.pop(0)
        if cur in seen:
            continue
        seen.add(cur)
        for e in by_caller.get(cur, []):
            seq.append(f"{e.caller} -> {e.callee} ({e.kind})")
            if e.kind == "internal" and e.callee not in seen:
                queue.append(e.callee)
    return seq[:limit]


_FAMILY_CONDITIONS = {
    "DEBT_REPAYMENT_RECONCILIATION": [
        "Two or more tranches whose principals do not divide the repayment evenly",
        "Repeated/partial repayments that each floor independently",
    ],
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": [
        "Cross-token predeposit where the victim bears the swap input",
        "An attacker-chosen route that is worse for the victim but valid for the loan output",
    ],
    "BORROW_CONSERVATION": [
        "Funds released before collateral is escrowed, or partial deposit consumption",
    ],
    "DEPOSIT_CONSUMPTION": [
        "A token whose transfer hands control to the attacker (reentrancy), or a replayable key",
    ],
    "VAULT_SHARE_ASSET_RECONCILIATION": [
        "Empty/near-empty vault (first depositor)",
        "A direct asset donation between the victim's approve and deposit",
    ],
    "COLLATERAL_STATUS_RELEASE": [
        "Collateral release path reachable while lender settlement is incomplete",
    ],
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": [
        "A fee-on-transfer / rebasing token, or real slippage on a fork",
    ],
}


def _root_cause(inv) -> str:
    reason = inv.suspicion_reasons[0] if inv.suspicion_reasons else inv.title
    return reason


def build_candidates(smap, emap, tmap, invset) -> M.AttackGraph:
    graph = M.AttackGraph(root=smap.root)
    covered_functions = set()
    idx = 0

    # 1) From suspicious invariants.
    for inv in invset.suspicious():
        fn_qn = inv.related_functions[0] if inv.related_functions else ""
        tr = tmap.for_function(fn_qn)
        idx += 1
        fnsem = smap.function(fn_qn)
        role_gates = list(fnsem.role_gates) if fnsem else []
        evidence = []
        if fnsem:
            evidence.append(f"{smap.contract(fnsem.contract).file}:{fnsem.line_start}"
                            if smap.contract(fnsem.contract) else fn_qn)
        evidence += [f"flag:{f}" for f in (tr.flags if tr else [])]
        cond = list(tr.preconditions) if tr else []
        cond += _FAMILY_CONDITIONS.get(inv.family, [])
        fork = inv.testability == "fork"
        cand = M.AttackCandidate(
            id=f"AC-{idx:03d}", title=inv.title,
            root_cause=_root_cause(inv), broken_invariant=inv.description,
            invariant_id=inv.id, invariant_family=inv.family,
            attacker=inv.attacker_capability, attacker_capability=inv.attacker_capability,
            victim=inv.victim, asset=inv.asset, entry_function=fn_qn,
            call_sequence=_call_sequence(smap, fn_qn), state_transition=inv.state_transition,
            exploit_hypothesis=(f"{inv.attacker_capability} drives {fn_qn.split('.')[-1]} so that "
                                f"{inv.title.lower()} fails, harming {inv.victim}."),
            required_conditions=cond, evidence=evidence,
            proof_strategy=inv.testability, fork_requirement=fork,
            role_gated=bool(role_gates), role_gates=role_gates,
            severity_hint=inv.severity_hint, confidence=inv.confidence,
        )
        graph.candidates.append(cand)
        covered_functions.add(fn_qn)

    # 2) Role-gated value movers with no invariant candidate (kill-path coverage).
    for tr in tmap.transitions:
        if tr.function in covered_functions:
            continue
        if not tr.assets_out:
            continue
        fnsem = smap.function(tr.function)
        role_gates = list(fnsem.role_gates) if fnsem else []
        is_role = role_gates or tr.actor.startswith("trusted role")
        if not is_role:
            continue
        idx += 1
        contract = smap.contract(fnsem.contract) if fnsem else None
        cand = M.AttackCandidate(
            id=f"AC-{idx:03d}",
            title=f"Value movement in {tr.function.split('.')[-1]} restricted to a trusted role",
            root_cause="Value-moving function is gated by a trusted role; no unprivileged path found.",
            broken_invariant="(access-controlled) only an authorized role may move value here",
            invariant_family="ACCESS_CONTROLLED_VALUE_MOVEMENT",
            attacker="external attacker (unprivileged)",
            attacker_capability="unprivileged caller",
            victim="protocol", asset="protocol funds",
            entry_function=tr.function, call_sequence=_call_sequence(smap, tr.function),
            state_transition=tr.id,
            exploit_hypothesis="An unprivileged attacker cannot reach this value movement; "
                               "it is gated by a trusted role.",
            required_conditions=[f"caller holds role: {', '.join(role_gates) or 'owner/admin'}"],
            evidence=([f"{contract.file}:{fnsem.line_start}"] if contract and fnsem else []),
            proof_strategy="manual", fork_requirement=False,
            role_gated=True, role_gates=role_gates,
            severity_hint="trusted-role gated", confidence=M.MEDIUM,
        )
        graph.candidates.append(cand)

    return graph
