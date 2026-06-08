"""Turn scope-aware lanes into precise, bounded, evidence-oriented scope tasks (v7).

Each task is a research instruction a model-agnostic AI agent or a human reviewer
can act on directly: a concrete hypothesis, the counterfactual to break, the setup
and action, the assertions and evidence required, the validity and known-issue
filters from the scope, and the threshold at which it becomes a report candidate.

A task is not an exploit instruction and not a finding. Human review is required.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.blind_spots.models import SurfaceRecord
from arkheionx.review_map.model import ReviewMap
from arkheionx.version import PACKAGE_VERSION

from . import models as m
from . import safety
from . import scope_parser
from .lane_builder import (
    build_repo_context,
    scope_filters,
    select_lanes,
    _lane_priority,
)

# Each category template is intentionally specific. Placeholders {target},
# {contract}, {function} are filled from the bound surface (or a scope placeholder).
_CAT = m  # alias for the TC_* constants

CATEGORY_DEFS: dict[str, dict] = {
    m.TC_AUTH_BYPASS: {
        "task_type": "access-control-test",
        "title": "Authorization bypass negative path on {target}",
        "hypothesis": "An unauthorized caller can drive {target} or its guarded effect without holding the required role.",
        "counterfactual": "Assume the access check on {function} is absent or satisfiable by any caller.",
        "why": "If a gated state change can be driven by the wrong caller, value or control moves outside the trust model.",
        "setup": "Deploy {contract} with a designated owner/role holder and a separate unauthorized address.",
        "action": "Call {function} from the unauthorized address, then (as control) from the authorized address.",
        "assertions": ["The unauthorized call reverts.",
                       "The authorized call succeeds and produces the documented effect.",
                       "The guarded state change is bound to the authorization check."],
        "evidence": ["Unauthorized-caller revert trace.", "Authorized-caller success with state delta."],
        "stop": "Both the unauthorized revert and the authorized success are demonstrated.",
    },
    m.TC_REPLAY: {
        "task_type": "negative-path-test",
        "title": "Replay / nonce / deadline protection on {target}",
        "hypothesis": "A signed or referenced action on {target} can be replayed with a used nonce or past its deadline.",
        "counterfactual": "Assume the nonce is never consumed and the deadline is never enforced.",
        "why": "Replaying a signed action can mint, transfer, or authorize value more than once.",
        "setup": "Construct a valid signed/referenced action with a fresh nonce and a future deadline.",
        "action": "Submit it once (succeeds), resubmit with the same nonce, and submit a copy with an expired deadline.",
        "assertions": ["The first submission succeeds.",
                       "The replay with the used nonce reverts.",
                       "The expired-deadline submission reverts."],
        "evidence": ["Used-nonce replay revert.", "Expired-deadline revert.", "First-submission success."],
        "stop": "Replay and expiry are both rejected while the first valid use succeeds.",
    },
    m.TC_SIG_BINDING: {
        "task_type": "negative-path-test",
        "title": "Signature purpose binding on {target}",
        "hypothesis": "A signature for {target} can authorize a modified amount, recipient, or chainId without re-signing.",
        "counterfactual": "Assume one or more signed fields are not bound into the digest.",
        "why": "If a signed field is not bound, an attacker can re-purpose a valid signature for a different action.",
        "setup": "Sign a message over the intended fields (amount, recipient, chainId, nonce) with EIP-712.",
        "action": "Mutate each signed field in turn and submit with the original signature.",
        "assertions": ["Each mutated-field submission reverts.",
                       "An unmodified submission succeeds.",
                       "chainId binding rejects a cross-chain replay."],
        "evidence": ["Per-field mutation revert traces.", "Baseline success."],
        "stop": "Every signed field is shown to be bound into the digest.",
    },
    m.TC_ORACLE: {
        "task_type": "oracle-edge-test",
        "title": "Oracle stale / deviation / decimals handling on {target}",
        "hypothesis": "A stale, zero, deviated, or wrong-decimals price lets {target} overstate value or skip a guard.",
        "counterfactual": "Assume the price is used without staleness, deviation, or decimals checks.",
        "why": "A bad price input is a classic path to overstated collateral or share value.",
        "setup": "Deploy {contract} with a mock feed you control; set decimals to the integrated token's value.",
        "action": "Drive the feed to zero, to a stale timestamp, to a large deviation, and to a mismatched decimals scale.",
        "assertions": ["Zero/stale prices revert or are rejected at the boundary.",
                       "Deviation beyond the documented threshold is handled as documented.",
                       "The valuation scales correctly for the token's actual decimals."],
        "evidence": ["Boundary behaviour at each price edge.", "Valuation delta vs expected for each decimals case."],
        "stop": "Each price edge behaves as documented at the boundary.",
    },
    m.TC_SHARE_PRICE: {
        "task_type": "invariant-test",
        "title": "Share price inflation / deflation on {target}",
        "hypothesis": "A first deposit or donation can inflate share price so a later depositor on {target} loses value.",
        "counterfactual": "Assume no minimum shares / virtual offset protects the first depositor.",
        "why": "Share-price inflation silently transfers value from later depositors to an early attacker.",
        "setup": "Deploy {contract} empty; fund an attacker and a victim depositor.",
        "action": "Attacker makes a tiny first deposit, donates assets directly, then the victim deposits.",
        "assertions": ["The victim's redeemable assets are not materially less than deposited.",
                       "Share/asset conversion is monotonic across the donation.",
                       "No caller can redeem more than their fair share of total assets."],
        "evidence": ["Victim pre/post redeemable-asset delta.", "Share price before/after the donation."],
        "stop": "A donation cannot let the attacker capture the victim's value.",
    },
    m.TC_VIRTUAL_ACCT: {
        "task_type": "accounting-delta-test",
        "title": "Virtual vs actual accounting desync on {target}",
        "hypothesis": "{target} updates a virtual/internal balance that can desync from the actual token balance.",
        "counterfactual": "Assume internal accounting is updated on a path where the real transfer does not match.",
        "why": "A desync between tracked and real balances can let value be withdrawn twice or stranded.",
        "setup": "Deploy {contract} and record both the internal accounting value and the real token balance.",
        "action": "Drive deposit/withdraw/transfer paths, including a fee-on-transfer token if integrated.",
        "assertions": ["Internal accounting equals the real balance after each operation (within documented rounding).",
                       "No path lets internal accounting exceed real backing.",
                       "Fee-on-transfer tokens do not over-credit internal accounting."],
        "evidence": ["Internal-vs-real balance table across operations."],
        "stop": "Internal accounting and real backing stay reconciled across every path.",
    },
    m.TC_REWARDS: {
        "task_type": "accounting-delta-test",
        "title": "Rewards / vesting accrual mismatch on {target}",
        "hypothesis": "A participant can claim more reward from {target} than accrued for their stake and time.",
        "counterfactual": "Assume the accrual or vesting schedule is not enforced per-claim.",
        "why": "Over-accrual drains the reward pool from honest participants.",
        "setup": "Deploy {contract}; stake from two participants over a known time/emission window.",
        "action": "Advance time, claim, re-claim, and claim across a schedule boundary.",
        "assertions": ["Total claimed never exceeds funded/accrued rewards.",
                       "A second claim in the same window does not double-pay.",
                       "Vesting releases match the documented schedule."],
        "evidence": ["Reward-pool pre/post delta.", "Claimed vs accrued reconciliation."],
        "stop": "Claims reconcile against accrued rewards with no double-pay.",
    },
    m.TC_WITHDRAW_AMOUNT: {
        "task_type": "accounting-delta-test",
        "title": "Withdrawal amount mismatch on {target}",
        "hypothesis": "{target} pays out a different amount than the caller is entitled to (over- or under-payment).",
        "counterfactual": "Assume the payout amount is computed from stale or unreconciled accounting.",
        "why": "An over-payment on a value exit is a direct loss-of-funds path.",
        "setup": "Deploy {contract}; establish a known entitlement for a user.",
        "action": "Withdraw at first, last, and dust amounts and compare paid vs entitled.",
        "assertions": ["Paid amount equals entitled amount (within documented rounding).",
                       "No caller withdraws more than entitled.",
                       "Round-trip deposit/withdraw conserves backing."],
        "evidence": ["Paid-vs-entitled table at first/last/dust amounts."],
        "stop": "Payout matches entitlement at every boundary amount.",
    },
    m.TC_CLAIM_OWNERSHIP: {
        "task_type": "lifecycle-test",
        "title": "Transferable claim ownership edge on {target}",
        "hypothesis": "A transferred claim NFT/ticket on {target} can be claimed by the old owner or by both parties.",
        "counterfactual": "Assume the claim binds to a stored address rather than current NFT ownership.",
        "why": "If a claim mis-binds ownership, value can be redirected or double-claimed after transfer.",
        "setup": "Deploy {contract}; mint a claim to user A, then transfer the claim NFT to user B.",
        "action": "Attempt to claim as A (old owner) and as B (new owner).",
        "assertions": ["Only the current NFT owner can claim.",
                       "The old owner can no longer claim after transfer.",
                       "A consumed claim cannot be claimed again by anyone."],
        "evidence": ["Old-owner claim revert.", "New-owner claim success.", "Second-claim revert."],
        "stop": "Claim authority follows current ownership and is single-use.",
    },
    m.TC_COMPLIANCE: {
        "task_type": "negative-path-test",
        "title": "Compliance / blocklist bypass on {target}",
        "hypothesis": "A blocked or frozen party can still send or receive value through {target}.",
        "counterfactual": "Assume the compliance gate is checked on only one party or only one path.",
        "why": "A compliance bypass moves value for a party the protocol must block.",
        "setup": "Deploy {contract} with the compliance list; block an address.",
        "action": "Attempt to send to and receive from the blocked address across each value path (token, vault, NFT, bridge).",
        "assertions": ["A blocked sender is rejected on every value path.",
                       "A blocked recipient is rejected on every value path.",
                       "The gate is enforced consistently across contracts."],
        "evidence": ["Per-path blocked-sender and blocked-recipient reverts."],
        "stop": "No in-scope value path lets a blocked party transact.",
    },
    m.TC_CROSSCHAIN: {
        "task_type": "lifecycle-test",
        "title": "Cross-chain stuck / refund / quarantine edge on {target}",
        "hypothesis": "A failed cross-chain delivery via {target} strands value with no refund or double-credits on retry.",
        "counterfactual": "Assume the failure/refund/quarantine branch is never exercised.",
        "why": "Stranded or double-credited cross-chain value is a direct loss or inflation path.",
        "setup": "Deploy {contract} with a mock endpoint you can force to fail delivery.",
        "action": "Send cross-chain, force a delivery failure, then trigger the refund/quarantine and any retry.",
        "assertions": ["A failed delivery refunds or quarantines the value.",
                       "A retry does not double-credit.",
                       "Compliance/accounting are preserved across the compose step."],
        "evidence": ["Failed-delivery balance trace.", "Retry no-double-credit check."],
        "stop": "Failure, refund/quarantine, and retry all conserve value and compliance.",
    },
    m.TC_ADAPTER_AMOUNT: {
        "task_type": "interaction-test",
        "title": "Adapter amount mismatch on {target}",
        "hypothesis": "{target} withdraws or reports a different amount than core accounting requested.",
        "counterfactual": "Assume the adapter trusts an external return value without strict reconciliation.",
        "why": "An adapter amount mismatch corrupts core share/asset accounting.",
        "setup": "Deploy {contract} with a controllable external-protocol mock (without mocking away the reconciliation).",
        "action": "Request a withdraw/redeem and vary the external protocol's returned/actual amount.",
        "assertions": ["The adapter delivers exactly the requested amount or reverts.",
                       "Core accounting reconciles with the adapter result.",
                       "A failed external call leaves core accounting consistent."],
        "evidence": ["Requested-vs-delivered amount table.", "Core-accounting reconciliation."],
        "stop": "Adapter amounts reconcile with core accounting on success and failure.",
    },
    m.TC_CALL_ORDERING: {
        "task_type": "interaction-test",
        "title": "External call ordering / reentrancy on {target}",
        "hypothesis": "An external call in {target} runs before state is finalized, enabling reentrancy or mid-update observation.",
        "counterfactual": "Assume checks-effects-interactions is not followed on this path.",
        "why": "Out-of-order external calls are a classic reentrancy and accounting-corruption path.",
        "setup": "Deploy {contract} with a malicious callback/receiver contract.",
        "action": "Trigger the path so the external call re-enters or observes intermediate state.",
        "assertions": ["Reentrancy is blocked or has no value effect.",
                       "No external call observes mid-update accounting.",
                       "State is finalized before the external call."],
        "evidence": ["Reentrancy attempt trace.", "Mid-update state observation check."],
        "stop": "The path is safe against reentrancy and mid-update observation.",
    },
    m.TC_LOOP_GRIEF: {
        "task_type": "boundary-test",
        "title": "Unbounded loop griefing on {target}",
        "hypothesis": "An attacker can grow a user-controlled array so {target} reverts on gas, locking a value path.",
        "counterfactual": "Assume the iterated collection has no effective upper bound.",
        "why": "An unbounded loop pushed past the block gas limit can lock funds or block users (Medium/High DoS).",
        "setup": "Deploy {contract}; identify the user-growable collection {function} iterates.",
        "action": "Grow the collection toward the block gas limit, then call the affected path.",
        "assertions": ["The core path remains callable at realistic scale, or",
                       "The unbounded case is shown to lock funds / block users (Medium/High), not just cost gas.",
                       "Any documented bound actually caps iteration."],
        "evidence": ["Gas vs collection-size curve.", "Impact characterization (lock/DoS vs cost)."],
        "stop": "The loop is bounded or its unbounded impact is shown to be Medium/High.",
    },
    m.TC_ADMIN_BOUNDARY: {
        "task_type": "access-control-test",
        "title": "Admin role boundary exceedance on {target}",
        "hypothesis": "An admin action on {target} can move value or change state beyond the documented power.",
        "counterfactual": "Assume the admin function's effect is broader than the trust model documents.",
        "why": "An admin boundary that exceeds the documented power can move or trap user value.",
        "setup": "Deploy {contract}; identify the documented admin power for {function}.",
        "action": "Exercise the admin function at and beyond its documented bound, and from a non-admin.",
        "assertions": ["A non-admin caller reverts.",
                       "The admin effect stays within the documented bound.",
                       "Emergency/rescue cannot move user value outside the documented flow."],
        "evidence": ["Non-admin revert.", "Admin-effect scope check vs documented bound."],
        "stop": "Admin power is confirmed within the documented trust model.",
    },
    m.TC_ERC_COMPLIANCE: {
        "task_type": "differential-test",
        "title": "ERC standard compliance (Medium/High impact only) on {target}",
        "hypothesis": "An ERC deviation in {target} causes a value-loss or fund-lock path, not just a spec nit.",
        "counterfactual": "Assume an integrator that follows the standard interacts with {contract}.",
        "why": "A standard deviation only qualifies for a contest when it causes Medium/High impact.",
        "setup": "Deploy {contract} and a standard-conformant integrator/mock.",
        "action": "Exercise the deviating behaviour (return value, hook, decimals, approval) through the integrator.",
        "assertions": ["The deviation is tied to a concrete value-loss or fund-lock path.",
                       "A spec-following integrator breaks in a way that loses or locks value.",
                       "If impact is only cosmetic, the task is dropped as low-only."],
        "evidence": ["Integrator breakage trace with value impact, or a note that impact is low-only."],
        "stop": "A Medium/High impact path is attached, or the item is dropped as low-only.",
    },
    m.TC_FEE_SLIPPAGE: {
        "task_type": "accounting-delta-test",
        "title": "Fee / slippage mismatch with user loss on {target}",
        "hypothesis": "Fees or slippage on {target} are applied in an order that causes a user to lose value.",
        "counterfactual": "Assume slippage is checked before fees (or after) inconsistently with the documented order.",
        "why": "A fee/slippage ordering bug can extract more from a user than the documented maximum.",
        "setup": "Deploy {contract}; set a known fee and a user-supplied minOut/slippage bound.",
        "action": "Execute the path and compare the net amount received against the user's bound and the documented fee.",
        "assertions": ["The user never receives less than their slippage bound after fees.",
                       "The fee charged matches the documented base and rate.",
                       "Fee and slippage are applied in the documented order."],
        "evidence": ["Net-received vs slippage-bound comparison.", "Fee base/rate check."],
        "stop": "The user's protected amount holds after fees in the documented order.",
    },
    m.TC_PREVIEW_ACTUAL: {
        "task_type": "differential-test",
        "title": "Preview vs actual execution mismatch on {target}",
        "hypothesis": "A preview/quote on {target} disagrees with the realised execution at the same state.",
        "counterfactual": "Assume preview and execute use different rounding or state.",
        "why": "A preview that overstates the execution result misleads integrators and can cause loss.",
        "setup": "Deploy {contract}; reach a non-trivial state (non-empty, post-donation, rounding edge).",
        "action": "Call the preview/quote, then the matching execute, at the same state.",
        "assertions": ["Preview equals the realised amount, or differs only by documented rounding direction.",
                       "Rounding favors the protocol, not an attacker.",
                       "The mismatch is exercised at first/last/dust amounts."],
        "evidence": ["Preview-vs-realised table at several states."],
        "stop": "Preview matches execution within the documented rounding direction.",
    },
    m.TC_BURN_CLAIM: {
        "task_type": "invariant-test",
        "title": "Burn-to-claim mismatch on {target}",
        "hypothesis": "Burning a token/position on {target} releases more or less value than it represents.",
        "counterfactual": "Assume the burn and the value release are not atomic or not equal.",
        "why": "A burn-to-claim mismatch is a direct over-withdrawal or stranded-value path.",
        "setup": "Deploy {contract}; mint a position with a known backing.",
        "action": "Burn the position and measure the value released.",
        "assertions": ["Value released equals the position's backing (within documented rounding).",
                       "The burn and release are atomic.",
                       "A burned position cannot be claimed again."],
        "evidence": ["Backing-vs-released comparison.", "Double-claim revert."],
        "stop": "Burn releases exactly the backing, once.",
    },
    m.TC_CAPACITY_DEBT: {
        "task_type": "invariant-test",
        "title": "Capacity / debt accounting mismatch on {target}",
        "hypothesis": "{target} lets total drawn capacity or filler debt exceed the funded/reimbursable amount.",
        "counterfactual": "Assume capacity/debt accounting is not reconciled against funding.",
        "why": "A capacity/debt overshoot leaves the protocol or a filler under-collateralized.",
        "setup": "Deploy {contract}; set a known capacity / funding amount.",
        "action": "Draw capacity / accrue filler debt up to and beyond the funded amount.",
        "assertions": ["Total drawn never exceeds funded capacity.",
                       "Filler debt reconciles with reimbursement accounting.",
                       "The boundary just inside/outside capacity behaves as documented."],
        "evidence": ["Drawn-vs-funded table at the capacity boundary."],
        "stop": "Capacity/debt never exceeds the funded/reimbursable amount.",
    },
    m.TC_BLOCKLIST_TIMING: {
        "task_type": "lifecycle-test",
        "title": "Blocklist / freeze timing interaction on {target}",
        "hypothesis": "An in-flight claim or transfer on {target} bypasses a freeze applied between request and settlement.",
        "counterfactual": "Assume the freeze is checked at request time but not at settlement time.",
        "why": "A timing gap lets a party that is frozen mid-flight still extract value.",
        "setup": "Deploy {contract}; start a deferred claim/transfer, then freeze the party before settlement.",
        "action": "Settle the in-flight claim/transfer after the freeze is applied.",
        "assertions": ["A party frozen before settlement cannot settle.",
                       "The freeze is enforced at settlement, not only at request.",
                       "Already-settled value is handled per the documented policy."],
        "evidence": ["In-flight settle-after-freeze revert."],
        "stop": "Freeze is enforced at settlement time for in-flight value.",
    },
}


def _pick_record(matched: list[SurfaceRecord], index: int) -> SurfaceRecord | None:
    if not matched:
        return None
    return matched[index % len(matched)]


def _validity_filter(scope: m.ScopeData) -> str:
    bits = []
    if scope_parser.requires_medium_high(scope):
        bits.append("Valid only if the impact is Medium/High under the scope rules.")
    else:
        bits.append("Confirm the impact qualifies under the scope's severity rules.")
    bits.append("Not valid if it relies on a trusted role acting maliciously, unless the scope marks that valid.")
    bits.append("Not valid if it is centralization-only or a pure spec/UX deviation without qualifying impact.")
    return " ".join(bits)


def _known_issue_filter(scope: m.ScopeData, lane_keywords: tuple[str, ...]) -> str:
    relevant = [it for it in (scope.known_issues + scope.accepted_risks)
                if any(k in it.lower() for k in lane_keywords)]
    base = "Confirm this is not a known issue or accepted risk in the scope before promoting it."
    if relevant:
        return base + " Scope notes to check: " + "; ".join(relevant[:3])
    return base


def _fill(text: str, target: str, contract: str, function: str) -> str:
    return text.format(target=target, contract=contract, function=function)


def build_scope_tasks(rm: ReviewMap, root: Path | str, scope_file: str | None = None, *,
                      source_files: int = 0, test_files: int = 0) -> dict:
    scope = scope_parser.parse_scope_file(scope_file)
    ctx = build_repo_context(rm, root, source_files=source_files, test_files=test_files)
    records = ctx["records"]
    selected = select_lanes(records, scope)

    requires_mh = scope_parser.requires_medium_high(scope)
    validity = _validity_filter(scope)

    tasks: list[dict] = []
    lane_index: list[dict] = []
    counter = 0
    for ld, matched in selected:
        priority = _lane_priority(ld, matched, scope)
        lane_index.append({"lane_id": ld.lane_id, "lane_name": ld.lane_name,
                           "priority": priority, "surface_count": len(matched)})
        for i, cat in enumerate(ld.task_categories):
            cdef = CATEGORY_DEFS.get(cat)
            if not cdef:
                continue
            rec = _pick_record(matched, i)
            if rec is not None:
                target = rec.target
                contract = rec.contract or target.split(".")[0]
                function = rec.function or (target.split(".")[1] if "." in target else target)
                source_ref = rec.source
            else:
                contract = (scope.in_scope[0].split("/")[-1].replace(".sol", "")
                            if scope.in_scope else "InScopeContract")
                function = "theScopedFunction"
                target = f"{contract}.{function}"
                source_ref = ""
            counter += 1
            tasks.append({
                "task_id": f"TASK-{counter:03d}",
                "lane_id": ld.lane_id,
                "lane_name": ld.lane_name,
                "category": cat,
                "task_type": cdef["task_type"],
                "priority": priority,
                "target": target,
                "target_contract": contract,
                "target_function": function,
                "source_reference": source_ref,
                "title": _fill(cdef["title"], target, contract, function),
                "hypothesis": _fill(cdef["hypothesis"], target, contract, function),
                "counterfactual": _fill(cdef["counterfactual"], target, contract, function),
                "why_it_might_matter": _fill(cdef["why"], target, contract, function),
                "validity_filter": validity,
                "known_issue_filter": _known_issue_filter(scope, ld.keywords),
                "setup": _fill(cdef["setup"], target, contract, function),
                "action": _fill(cdef["action"], target, contract, function),
                "required_assertions": [_fill(a, target, contract, function) for a in cdef["assertions"]],
                "required_evidence": [_fill(e, target, contract, function) for e in cdef["evidence"]],
                "likely_invalid_conditions": [
                    "The test does not call the target function.",
                    "The test asserts only that the call did not revert.",
                    "The test relies on a trusted-role mistake the scope marks invalid.",
                    "The test reproduces a known or accepted issue.",
                ],
                "stop_condition": _fill(cdef["stop"], target, contract, function),
                "report_candidate_threshold": (
                    "Promote to a report candidate only with a passing local PoC that shows the impact path, "
                    "is confirmed in-scope, is not a known/accepted issue, and "
                    + ("is Medium/High impact." if requires_mh else "meets the scope's severity bar.")),
                "human_review_required": True,
            })

    data = {
        "schema_version": m.SCHEMA_VERSION,
        "arkheionx_version": PACKAGE_VERSION,
        "kind": m.KIND_SCOPE_TASKS,
        "command": "scope-tasks",
        "generated_at": ctx["generated_at"],
        "scope_file_used": scope.scope_file_used,
        "repo_summary": ctx["repo_summary"],
        "task_count": len(tasks),
        "tasks": tasks,
        "lanes": lane_index,
        "report_filters": scope_filters(scope),
        "human_review_required": True,
        "safety_boundary": safety.SAFETY_BOUNDARY,
        "safety": safety.safety_block(),
    }
    return data
