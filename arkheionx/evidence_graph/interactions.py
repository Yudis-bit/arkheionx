"""Interaction Matrix builder (v6).

Detects meaningful combinations of review surfaces that may hide bugs when
tested together (value-exit x external-call, liquidation x oracle,
signature x nonce, periphery x core accounting, ...), scores each by a
transparent additive priority, and classifies the combination's evidence state.

An interaction is a review candidate, never a vulnerability. Interaction
priority is a heuristic review order, never a severity. Human review is required.
"""
from __future__ import annotations

from arkheionx.blind_spots.counterfactuals import build_counterfactuals
from arkheionx.blind_spots.models import SurfaceRecord
from arkheionx.blind_spots.signals import build_surface_records
from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER
from arkheionx.research.surfaces import ResearchSurfaces, build_research_surfaces
from arkheionx.review_map.model import ReviewMap

from . import classifier, models as m

# --------------------------------------------------------------------------
# Surface categorisation
# --------------------------------------------------------------------------
_SHARE_NAMES = ("preview", "converttoshares", "converttoassets", "maxwithdraw", "maxredeem",
                "shares", "share", "exchangerate", "totalassets", "totalsupply")
_PREVIEW_NAMES = ("preview", "converttoshares", "converttoassets", "maxwithdraw", "maxredeem", "quote")
_EXECUTE_NAMES = ("deposit", "mint", "withdraw", "redeem")
_ORACLE_NAMES = ("oracle", "price", "feed", "aggregator", "twap", "rate", "latestround", "latestprice")
_LIQUIDATION_NAMES = ("liquidate", "liquidation", "seize", "health", "collateral", "ltv", "closefactor")
_BADDEBT_NAMES = ("debt", "baddebt", "borrow", "insolven", "loss")
_CONNECTOR_NAMES = ("connector", "adapter", "strategy", "balanceofunderlying")
_BLOCKLIST_NAMES = ("blocklist", "blacklist", "denylist", "allowlist", "whitelist", "restricted", "frozen")
_FEE_NAMES = ("fee", "commission", "skim", "performancefee", "managementfee")
_DISPATCH_NAMES = ("dispatcher", "recipient", "collect")
_PAUSE_NAMES = ("pause", "unpause")
_EMERGENCY_NAMES = ("emergency", "shutdown", "kill", "rescue", "sweep")
_UPGRADE_NAMES = ("upgrade", "implementation")
_INIT_NAMES = ("initialize", "init", "migrate")
_LIFECYCLE_NAMES = ("settle", "maturity", "expiry", "close", "deadline")
_VALUE_EXIT_NAMES = ("withdraw", "redeem", "claim", "collect", "unstake", "refund", "payout", "transfer")
_ACCOUNTING_NAMES = ("deposit", "withdraw", "borrow", "repay", "liquidate", "mint", "burn",
                     "redeem", "stake", "unstake", "accrue", "settle", "collect", "skim",
                     "sync", "rebalance", "harvest", "seize", "supply")
_ADMIN_PREFIXES = ("set", "configure", "pause", "unpause", "upgrade", "initialize",
                   "init", "migrate", "kill", "shutdown", "rescue", "sweep", "emergency")


def _name(record: SurfaceRecord) -> str:
    return (record.function or "").lower()


def surface_categories(record: SurfaceRecord) -> set[str]:
    """Return the set of interaction-relevant category tags for a surface."""
    name = _name(record)
    risk = " ".join(record.risk_signals).lower()
    auth = set(record.auth_kinds)
    periph = set(record.periphery_interactions)
    behavior = set(record.behavior_signals)
    cats: set[str] = set()

    # Value / accounting categories are name-anchored: the upstream detector
    # over-labels some surfaces with a coarse "value exit" risk signal, so we do
    # not trust that label alone for the categories that drive most interactions.
    if any(k in name for k in ("withdraw", "redeem", "claim", "collect", "unstake", "refund", "payout")):
        cats.add("value-exit")
    if any(k in name for k in ("deposit", "mint", "supply", "stake", "fund", "lock")):
        cats.add("value-entry")
    if any(k in name for k in _ACCOUNTING_NAMES):
        cats.add("accounting")
    if any(k in name for k in _SHARE_NAMES) or (
        any(k in name for k in ("deposit", "withdraw", "redeem", "mint")) and "accounting" in cats):
        cats.add("share-math")
    if any(k in name for k in _PREVIEW_NAMES):
        cats.add("preview")
    if "external call/callback" in risk or "low-level-call" in periph or "callback" in periph:
        cats.add("external-call")
    if "callback" in periph or any(k in name for k in ("callback", "hook", "onerc", "onsettlement", "receive")):
        cats.add("callback")
    if "authorization" in risk or auth:
        cats.add("authorization")
    if {"signature", "domain"} & auth:
        cats.add("signature")
    if "merkle" in auth:
        cats.add("merkle")
    if "replay" in auth:
        cats.update({"nonce", "deadline"})
    if "oracle" in risk or any(k in name for k in _ORACLE_NAMES):
        cats.update({"oracle", "decimals"})
    if "liquidation" in risk or any(k in name for k in _LIQUIDATION_NAMES):
        cats.add("liquidation")
    if any(k in name for k in _BADDEBT_NAMES):
        cats.add("bad-debt")
    if "periphery/core interaction" in risk or periph or record.cross_contract_targets:
        cats.add("periphery")
    if record.cross_contract_targets or "cross-contract-call" in periph:
        cats.add("cross-contract")
    if any(k in name for k in _CONNECTOR_NAMES):
        cats.add("connector")
    if "admin control" in risk or any(name.startswith(p) for p in _ADMIN_PREFIXES):
        cats.add("admin")
    if any(k in name for k in _EMERGENCY_NAMES) or "pause" in name:
        cats.add("emergency")
    if any(k in name for k in _PAUSE_NAMES):
        cats.add("pause")
    if any(k in name for k in _UPGRADE_NAMES):
        cats.add("upgrade")
    if any(k in name for k in _INIT_NAMES):
        cats.add("init")
    if any(k in name for k in _LIFECYCLE_NAMES) or "upgrade" in cats or "init" in cats:
        cats.add("lifecycle")
    if any(k in name for k in _BLOCKLIST_NAMES):
        cats.add("blocklist")
    if any(k in name for k in _FEE_NAMES):
        cats.add("fee")
    if any(k in name for k in _DISPATCH_NAMES):
        cats.add("dispatcher")
    if "loop-with-external-call" in periph or "require-in-loop" in behavior:
        cats.add("loop")
    if "try-catch" in periph or "try-catch" in behavior or "partial-failure" in behavior or "periphery-keyword" in periph:
        cats.add("bundle")
    if "transfer" in name or "value-exit" in cats:
        cats.add("transfer")
    if "share-math" in cats and "accounting" in cats:
        cats.add("donation")
    return cats


# --------------------------------------------------------------------------
# Impact / complexity scoring (transparent, additive)
# --------------------------------------------------------------------------
# Category -> (impact dimension label, points). Distinct dimensions are summed.
_DIMENSION = {
    "value-exit": ("value exit", 25),
    "value-entry": ("token/share mutation", 10),
    "transfer": ("token/share mutation", 10),
    "accounting": ("accounting mutation", 20),
    "share-math": ("share/fee accounting", 12),
    "fee": ("share/fee accounting", 12),
    "commission": ("share/fee accounting", 12),
    "dispatcher": ("share/fee accounting", 12),
    "donation": ("share/fee accounting", 12),
    "authorization": ("authorization", 20),
    "signature": ("authorization", 20),
    "merkle": ("authorization", 20),
    "replay": ("authorization", 20),
    "nonce": ("authorization", 20),
    "deadline": ("authorization", 20),
    "liquidation": ("liquidation/seizure", 20),
    "bad-debt": ("liquidation/seizure", 20),
    "oracle": ("oracle dependency", 18),
    "decimals": ("oracle dependency", 18),
    "external-call": ("external call/callback", 15),
    "callback": ("external call/callback", 15),
    "periphery": ("periphery/core boundary", 15),
    "connector": ("connector", 12),
    "admin": ("admin/emergency control", 12),
    "emergency": ("admin/emergency control", 12),
    "pause": ("admin/emergency control", 12),
    "blocklist": ("admin/emergency control", 12),
    "upgrade": ("lifecycle/upgrade", 10),
    "init": ("lifecycle/upgrade", 10),
    "lifecycle": ("lifecycle/upgrade", 10),
    "cross-contract": ("cross-contract dependency", 10),
}

_COMPLEXITY_POINTS = {
    "cross-contract": 15,
    "external-call": 12,
    "periphery": 10,
    "lifecycle": 10,
    "signature/merkle": 10,
    "oracle/accounting": 10,
    "loop/batch": 8,
}


def _impact(cats: set[str]) -> tuple[int, list[str], list[str]]:
    dims: dict[str, int] = {}
    for cat in cats:
        if cat in _DIMENSION:
            label, pts = _DIMENSION[cat]
            dims[label] = pts
    ordered = sorted(dims.items(), key=lambda kv: (-kv[1], kv[0]))
    score = sum(pts for _, pts in ordered)
    labels = [label for label, _ in ordered]
    reasons = [f"+{pts} impact: {label}" for label, pts in ordered]
    return score, labels, reasons


def _complexity(cats: set[str], cross: bool) -> tuple[int, list[str]]:
    flags: set[str] = set()
    if cross or "cross-contract" in cats:
        flags.add("cross-contract")
    if "external-call" in cats or "callback" in cats:
        flags.add("external-call")
    if "periphery" in cats:
        flags.add("periphery")
    if "lifecycle" in cats or "upgrade" in cats or "init" in cats:
        flags.add("lifecycle")
    if "signature" in cats or "merkle" in cats:
        flags.add("signature/merkle")
    if "oracle" in cats or "accounting" in cats:
        flags.add("oracle/accounting")
    if "loop" in cats or "bundle" in cats:
        flags.add("loop/batch")
    score = sum(_COMPLEXITY_POINTS[f] for f in flags)
    reasons = [f"+{_COMPLEXITY_POINTS[f]} complexity: {f}" for f in sorted(flags)]
    return score, reasons


_GAP_POINTS = {m.STRENGTH_NONE: 30, m.STRENGTH_UNKNOWN: 30, m.STRENGTH_WEAK: 20,
               m.STRENGTH_MEDIUM: 10, m.STRENGTH_STRONG: 0}


def _priority_label(score: int) -> str:
    if score >= 85:
        return m.IP_VERY_HIGH
    if score >= 65:
        return m.IP_HIGH
    if score >= 40:
        return m.IP_MEDIUM
    return m.IP_MONITOR


# --------------------------------------------------------------------------
# Interaction rules
# --------------------------------------------------------------------------
# (interaction_class, cat_a, cat_b, why, invariant, counterfactual, stop_condition)
_INTRA_RULES = [
    ("value-exit x authorization", "value-exit", "authorization",
     "A value-exit path also performs an authorization check; a gap in either lets value leave under the wrong caller.",
     "Only an authorized caller can move value out, and an unauthorized caller always reverts.",
     "What if the authorization check does not actually bind this value-exit path?",
     "Stop when a negative-path test shows the unauthorized caller reverts and the authorized caller's accounting is conserved."),
    ("value-exit x external-call", "value-exit", "external-call",
     "Value leaves the system and an external call happens on the same path; ordering / reentrancy of state vs call matters.",
     "Balances and accounting are updated before the external call, and a reentrant call cannot double-spend.",
     "What if the external call can re-enter before accounting is finalised?",
     "Stop when a reentrancy-style test shows accounting is finalised before the external call."),
    ("value-exit x share-accounting", "value-exit", "share-math",
     "A value-exit burns shares; rounding or share/asset conversion errors here drain or trap value.",
     "Round-tripping entry then exit conserves accounting for first, last, and dust amounts.",
     "What if the share->asset conversion rounds in the user's favour on exit?",
     "Stop when a rounding test covers first/last/dust amounts with conserved accounting."),
    ("value-exit x fee", "value-exit", "fee",
     "A fee is taken on a value-exit path; fee math and recipient routing can over- or under-charge.",
     "The fee charged on exit matches the documented rate and the net amount is conserved.",
     "What if the fee is applied to the wrong base or rounds against the protocol?",
     "Stop when a fee-edge test confirms the charged fee and net payout at boundary amounts."),
    ("value-exit x blocklist", "value-exit", "blocklist",
     "A blocklist/allowlist gates a value-exit; a bypass or stale entry changes who can exit.",
     "A blocked address cannot exit and an allowed address is not wrongly blocked.",
     "What if the blocklist is checked on the wrong address or can be bypassed via periphery?",
     "Stop when a test shows blocked and allowed addresses behave as documented on every exit path."),
    ("deposit x share-math", "value-entry", "share-math",
     "A value-entry mints shares; first-deposit, rounding, or donation can distort the share price.",
     "Minted shares are proportional and a donation cannot let an attacker steal later depositors' value.",
     "What if a donation before the first real deposit inflates the share price?",
     "Stop when a first-deposit + donation test shows later depositors are not diluted."),
    ("share-math x donation", "share-math", "donation",
     "Share accounting can be skewed by a direct token donation to the vault.",
     "totalAssets / share price cannot be manipulated by an unsolicited transfer.",
     "What if totalAssets reads balanceOf and a donation inflates it?",
     "Stop when a donation test shows the share price is not manipulable."),
    ("preview x actual-execute", "preview", "value-exit",
     "A preview/quote function should match what the matching execute actually does.",
     "preview* equals the realised amount of the matching deposit/withdraw/redeem at the same state.",
     "What if preview and the actual execution diverge at a boundary or after a fee?",
     "Stop when a test asserts preview == realised for first/last/dust and post-fee."),
    ("liquidation x oracle", "liquidation", "oracle",
     "Liquidation eligibility depends on an oracle price; a stale or extreme price liquidates a healthy position or blocks a needed one.",
     "The health boundary uses a fresh, bounded price and behaves correctly just inside and outside the boundary.",
     "What if the oracle price is stale, zero, or extreme when liquidation is evaluated?",
     "Stop when a test drives stale/zero/extreme prices and asserts the boundary behaves as documented."),
    ("liquidation x bad-debt", "liquidation", "bad-debt",
     "Liquidation and debt accounting interact; rounding at the seizure boundary can create or hide bad debt.",
     "Seizing collateral conserves total debt/credit accounting and cannot seize a healthy position.",
     "What if the seizure rounds so that debt and seized collateral do not reconcile?",
     "Stop when a boundary test reconciles debt and seized value at just-healthy vs just-unhealthy."),
    ("oracle x decimals", "oracle", "decimals",
     "Oracle values and token decimals interact; a decimals mismatch scales value wrongly.",
     "Price * amount scaling matches the documented decimals for every asset.",
     "What if the oracle and the asset use different decimals than assumed?",
     "Stop when a test confirms scaling for the actual decimals of each asset."),
    ("signature x nonce", "signature", "nonce",
     "A signed authorization is replay-protected by a nonce; a nonce gap allows replay.",
     "A used nonce cannot be reused and the nonce increments exactly once per authorized action.",
     "What if the same signature can be replayed because the nonce is not bound or not incremented?",
     "Stop when a replay test shows a used nonce is rejected."),
    ("signature x deadline", "signature", "deadline",
     "A signed authorization expires at a deadline; a deadline gap allows stale use.",
     "An expired authorization is rejected and the boundary deadline behaves as documented.",
     "What if an expired signature is still accepted at or past the deadline?",
     "Stop when a test rejects an expired deadline and accepts a just-valid one."),
    ("signature x Merkle", "signature", "merkle",
     "Both a signature and a Merkle gate exist in the same authorization surface; one path may bypass the other.",
     "Neither the signature path nor the Merkle path can authorize a claim the other would reject.",
     "What if one authorization path is weaker and can be used to bypass the other?",
     "Stop when tests show both paths bind the same claim fields."),
    ("Merkle x amount", "merkle", "value-exit",
     "A Merkle leaf gates a claimable amount; if the leaf does not bind the amount, any amount can be claimed.",
     "The Merkle leaf binds the claimer and the amount, and a proof for one leaf cannot claim another amount.",
     "What if the leaf does not bind the amount, so a valid proof claims an arbitrary amount?",
     "Stop when a test shows a proof is bound to a specific amount."),
    ("admin x emergency", "admin", "emergency",
     "Admin and emergency controls interact; an emergency path can bypass normal admin checks.",
     "Emergency functions are bounded and cannot be used to bypass the documented admin trust model.",
     "What if an emergency path lets an admin move value outside the normal flow?",
     "Stop when a test confirms emergency powers are scoped as documented."),
    ("upgrade x init", "upgrade", "init",
     "Upgrade and initialization interact; a re-initialization after upgrade can reset trust state.",
     "Initialization can run exactly once and an upgrade cannot re-open it.",
     "What if initialize can be called again after an upgrade?",
     "Stop when a test shows re-initialization is rejected."),
    ("pause x withdraw", "pause", "value-exit",
     "Pause and value-exit interact; pausing may trap user funds or fail to stop an exit.",
     "Pause stops the documented paths and never permanently traps user withdrawals beyond the documented policy.",
     "What if pause blocks withdrawals that the policy says should remain open (or vice versa)?",
     "Stop when a test confirms the pause policy on each exit path."),
    ("blocklist x transfer", "blocklist", "transfer",
     "A blocklist gates transfers; a missed check or wrong address lets a blocked party move value.",
     "A blocked party cannot send or receive on the gated path.",
     "What if the blocklist is checked on sender but not recipient (or vice versa)?",
     "Stop when a test covers blocked sender and blocked recipient."),
    ("loop x external-call", "loop", "external-call",
     "A loop performs external calls per item; one item can revert, reenter, or grief the batch.",
     "One failing item behaves as documented (skip/continue) and cannot corrupt the rest of the batch.",
     "What if a crafted item reverts before the documented skip handler, or re-enters mid-loop?",
     "Stop when a test shows a malformed item is skipped and the batch state stays consistent."),
    ("callback x state-order", "callback", "accounting",
     "A callback runs while accounting is mid-update; state ordering or an unexpected caller can corrupt state.",
     "The callback cannot be called by an unexpected caller and cannot observe or mutate mid-update state.",
     "What if the callback is invoked by an unexpected caller or before accounting is finalised?",
     "Stop when a test asserts the caller check and the pre/post state around the callback."),
    ("external-call x accounting-update", "external-call", "accounting",
     "An external call and an accounting update share a path; ordering determines reentrancy safety.",
     "Accounting is finalised before the external call and a reentrant call cannot observe stale state.",
     "What if accounting is updated after the external call returns?",
     "Stop when a checks-effects-interactions test confirms the ordering."),
    ("fee x share-accounting", "fee", "share-math",
     "Fees and share accounting interact; a fee taken in shares can dilute holders unexpectedly.",
     "Fee accrual in shares matches the documented rate and does not silently dilute holders.",
     "What if the fee mints shares against the wrong base?",
     "Stop when a test reconciles fee shares against the documented rate."),
]


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def _safety() -> dict:
    return {
        "disclaimer": LOCAL_ONLY_DISCLAIMER,
        "boundary": list(m.BOUNDARY_LINES),
        "do_not_claim": list(m.DO_NOT_CLAIM),
        "human_review_required": True,
    }


def _surface_state(record: SurfaceRecord, memory: dict[str, str]) -> tuple[str, str]:
    strength = classifier.evidence_strength(record)
    state, _why, _ur = classifier.classify_state(record, strength, memory_status=memory.get(record.target))
    return state, strength


def _interaction_evidence(strengths: list[str]) -> tuple[str, str, str]:
    """Return (evidence_state, evidence_strength, review_density) for a combo."""
    weakest = m.STRENGTH_STRONG
    for s in strengths:
        weakest = m.weaker_strength(weakest, s)
    if weakest in (m.STRENGTH_NONE, m.STRENGTH_UNKNOWN):
        state = m.STATE_UNRESOLVED
    elif weakest == m.STRENGTH_WEAK:
        state = m.STATE_INSUFFICIENT_EVIDENCE
    elif weakest == m.STRENGTH_MEDIUM:
        state = m.STATE_NEEDS_HUMAN_REVIEW
    else:
        state = m.STATE_TESTED
    density = {m.STRENGTH_STRONG: m.DENSITY_STRONG, m.STRENGTH_MEDIUM: m.DENSITY_MEDIUM,
               m.STRENGTH_WEAK: m.DENSITY_WEAK, m.STRENGTH_NONE: m.DENSITY_NONE,
               m.STRENGTH_UNKNOWN: m.DENSITY_UNKNOWN}[weakest]
    return state, weakest, density


def _best_crit(records: list[SurfaceRecord]) -> str:
    best = m.CRIT_UNKNOWN
    for r in records:
        if m.criticality_rank(r.criticality_potential) < m.criticality_rank(best):
            best = r.criticality_potential
    return best


def _make_interaction(idx, interaction_class, records, defining_cats, why, invariant, counterfactual,
                      stop, cross, cf_by_target, memory) -> m.Interaction:
    # Score from the categories that DEFINE this interaction class (plus a
    # cross-contract bonus), not from every category a surface happens to carry.
    cats: set[str] = set(defining_cats)
    if cross:
        cats.add("cross-contract")
    impact, dims, impact_reasons = _impact(cats)
    complexity, complexity_reasons = _complexity(cats, cross)
    strengths = [_surface_state(r, memory)[1] for r in records]
    state, strength, density = _interaction_evidence(strengths)
    gap = _GAP_POINTS.get(strength, 30)
    gap_reason = f"+{gap} review gap: weakest constituent evidence is {strength}"
    priority_score = impact + gap + complexity
    tests_detected = sum(1 for r in records if r.test_reference_count > 0)
    # Suggested counterfactual: prefer a generated CF on a constituent surface.
    cf_id = ""
    for r in records:
        if cf_by_target.get(r.target):
            cf_id = cf_by_target[r.target][0]
            break
    suggested_cf = counterfactual + (f" ({cf_id})" if cf_id else "")
    sources = sorted({r.source for r in records if r.source})
    return m.Interaction(
        interaction_id=f"IX-{idx:03d}",
        interaction_class=interaction_class,
        surfaces=[r.target for r in records],
        contracts=sorted({r.contract for r in records if r.contract}),
        functions=[r.function for r in records],
        source_refs=sources,
        why_combination_matters=why,
        criticality_potential=_best_crit(records),
        review_density=density,
        evidence_state=state,
        evidence_strength=strength,
        tests_detected=tests_detected,
        impact_score=impact,
        review_gap_score=gap,
        interaction_complexity_score=complexity,
        interaction_priority=_priority_label(priority_score),
        score_reasons=impact_reasons + [gap_reason] + complexity_reasons,
        missing_test_direction=invariant,
        suggested_invariant=invariant,
        suggested_counterfactual=suggested_cf,
        stop_condition=stop,
        human_review_required=True,
    )


def build_interaction_matrix(rm: ReviewMap, surfaces: ResearchSurfaces, *,
                             source_files: int = 0, test_files: int = 0,
                             memory: dict[str, str] | None = None,
                             package_version: str = "") -> dict:
    memory = memory or {}
    records = build_surface_records(rm, surfaces)
    by_target = {r.target: r for r in records}
    cats_by_target = {r.target: surface_categories(r) for r in records}
    counterfactuals = build_counterfactuals(rm, surfaces, records)
    cf_by_target: dict[str, list[str]] = {}
    for cf in counterfactuals:
        cf_by_target.setdefault(cf["target"], []).append(cf["id"])

    seen: set[tuple] = set()
    raw: list[tuple] = []  # (records, class, defining_cats, why, invariant, cf, stop, cross)

    # 1) Intra-surface interactions (both categories on one function).
    for r in records:
        cats = cats_by_target[r.target]
        for cls, a, b, why, inv, cf, stop in _INTRA_RULES:
            if a in cats and b in cats:
                key = (cls, (r.target,))
                if key in seen:
                    continue
                seen.add(key)
                raw.append(([r], cls, {a, b}, why, inv, cf, stop, False))

    # 2) Cross-contract periphery -> core interactions.
    periphery_records = [r for r in records if r.cross_contract_targets]
    for p in periphery_records:
        p_cats = cats_by_target[p.target]
        for core_target in p.cross_contract_targets:
            core = by_target.get(core_target)
            if core is None:
                continue
            core_cats = cats_by_target[core.target]
            pairs = [
                ({"accounting", "periphery"}, "accounting x periphery", "Value-relevant accounting is reached through a periphery route; the routed path may not equal the direct path.",
                 "The periphery path produces the same core accounting as the equivalent direct call.",
                 "What if the periphery route produces different accounting than the direct call?",
                 "Stop when a test asserts periphery == direct accounting for the same inputs."),
                ({"periphery"}, "periphery x direct-call-equivalence", "A periphery route wraps a core call; wrappers can diverge from the core path.",
                 "The wrapper preserves every core check and accounting effect of the direct call.",
                 "What if the wrapper drops a check the direct call enforces?",
                 "Stop when a test shows the wrapper enforces the same checks as the direct call."),
            ]
            if "accounting" in core_cats or "value-exit" in core_cats or "value-entry" in core_cats:
                for dcats, cls, why, inv, cf, stop in pairs:
                    key = (cls, tuple(sorted((p.target, core.target))))
                    if key in seen:
                        continue
                    seen.add(key)
                    raw.append(([p, core], cls, dcats, why, inv, cf, stop, True))
            if "connector" in p_cats and ("accounting" in core_cats):
                cls = "connector x vault-accounting"
                key = (cls, tuple(sorted((p.target, core.target))))
                if key not in seen:
                    seen.add(key)
                    raw.append(([p, core], cls, {"connector", "accounting"},
                                "A connector/adapter feeds a vault's accounting; connector errors corrupt core accounting.",
                                "Connector-reported balances reconcile with core accounting.",
                                "What if the connector reports a balance the core trusts without validation?",
                                "Stop when a test reconciles connector balances with core accounting.", True))

    # 3) Same-contract cross-function interactions (preview/execute, pause/withdraw,
    #    admin/emergency, upgrade/init, signature/Merkle).
    by_contract: dict[str, list[SurfaceRecord]] = {}
    for r in records:
        by_contract.setdefault(r.contract, []).append(r)
    contract_rules = [
        ("preview x actual-execute", "preview", "value-exit",
         "A preview/quote in this contract should match the matching execute path.",
         "preview* equals the realised amount of the matching execute at the same state.",
         "What if preview and the actual execution diverge at a boundary or post-fee?",
         "Stop when a test asserts preview == realised for first/last/dust and post-fee."),
        ("pause x withdraw", "pause", "value-exit",
         "Pause and a value-exit live in the same contract; the pause policy on exits must be exact.",
         "Pause stops the documented paths and never permanently traps withdrawals beyond policy.",
         "What if pause blocks withdrawals that should remain open (or vice versa)?",
         "Stop when a test confirms the pause policy on each exit path."),
        ("admin x emergency", "admin", "emergency",
         "Admin and emergency controls coexist; an emergency path may bypass the normal admin model.",
         "Emergency functions are bounded and cannot bypass the documented admin trust model.",
         "What if an emergency path moves value outside the normal flow?",
         "Stop when a test confirms emergency powers are scoped as documented."),
        ("upgrade x init", "upgrade", "init",
         "Upgrade and initialization coexist; re-initialization after upgrade can reset trust state.",
         "Initialization runs exactly once and an upgrade cannot re-open it.",
         "What if initialize can be called again after an upgrade?",
         "Stop when a test shows re-initialization is rejected."),
        ("lifecycle x authorization", "lifecycle", "authorization",
         "A lifecycle transition and an authorization check coexist; a transition may skip a guard.",
         "Each lifecycle transition enforces the documented authorization.",
         "What if a lifecycle transition can be triggered without the expected authorization?",
         "Stop when a negative-path test shows each transition is gated."),
        ("value-exit x fee", "value-exit", "fee",
         "A value-exit and a fee control live in the same contract; the fee on exit must use the documented base and rate.",
         "The fee charged on exit matches the documented rate and the net amount is conserved.",
         "What if the fee is applied to the wrong base or rounds against the protocol?",
         "Stop when a fee-edge test confirms the charged fee and net payout at boundary amounts."),
        ("value-exit x blocklist", "value-exit", "blocklist",
         "A value-exit and a blocklist/freeze control coexist; the gate must be checked on the right party on every exit.",
         "A blocked account cannot exit and an allowed account is not wrongly blocked.",
         "What if the blocklist is checked on the wrong address or can be bypassed via a periphery route?",
         "Stop when a test shows blocked and allowed accounts behave as documented on every exit path."),
        ("blocklist x transfer", "blocklist", "transfer",
         "A blocklist gates value transfers in this contract; a missed check lets a blocked party move value.",
         "A blocked party cannot send or receive on the gated path.",
         "What if the blocklist is checked on sender but not recipient (or vice versa)?",
         "Stop when a test covers a blocked sender and a blocked recipient."),
        ("fee x share-accounting", "fee", "share-math",
         "A fee control and share accounting coexist; a fee taken in shares can dilute holders unexpectedly.",
         "Fee accrual matches the documented rate and does not silently dilute share holders.",
         "What if the fee mints or burns shares against the wrong base?",
         "Stop when a test reconciles fee effects against the documented rate and the share supply."),
        ("connector x vault-accounting", "connector", "accounting",
         "A connector/adapter control and the vault's accounting coexist; connector values feed core accounting.",
         "Connector-reported balances reconcile with the vault's share/asset accounting.",
         "What if the connector reports a balance the vault trusts without validation?",
         "Stop when a test reconciles connector balances with vault accounting across a rotation."),
    ]
    for contract, recs in by_contract.items():
        for cls, a, b, why, inv, cf, stop in contract_rules:
            a_rec = next((r for r in recs if a in cats_by_target[r.target]), None)
            b_rec = next((r for r in recs if b in cats_by_target[r.target] and r.target != (a_rec.target if a_rec else "")), None)
            if a_rec and b_rec:
                key = (cls, tuple(sorted((a_rec.target, b_rec.target))))
                if key in seen:
                    continue
                seen.add(key)
                raw.append(([a_rec, b_rec], cls, {a, b}, why, inv, cf, stop, a_rec.contract != b_rec.contract))

    interactions = [
        _make_interaction(i, cls, recs, dcats, why, inv, cf, stop, cross, cf_by_target, memory)
        for i, (recs, cls, dcats, why, inv, cf, stop, cross) in enumerate(raw, 1)
    ]
    # Deterministic order: priority, then class, then surfaces.
    interactions.sort(key=lambda ix: (m.interaction_priority_rank(ix.interaction_priority),
                                      -(ix.impact_score + ix.review_gap_score + ix.interaction_complexity_score),
                                      ix.interaction_class, tuple(ix.surfaces)))
    # Re-id in sorted order so IX ids are stable and priority-ordered.
    for i, ix in enumerate(interactions, 1):
        ix.interaction_id = f"IX-{i:03d}"

    unresolved = [ix for ix in interactions
                  if ix.interaction_priority in (m.IP_VERY_HIGH, m.IP_HIGH)
                  and ix.evidence_strength in (m.STRENGTH_NONE, m.STRENGTH_WEAK, m.STRENGTH_UNKNOWN)]

    summary = {
        "total_interactions": len(interactions),
        "high_impact_interactions": sum(1 for ix in interactions
                                        if ix.interaction_priority in (m.IP_VERY_HIGH, m.IP_HIGH)),
        "unresolved_interactions": len(unresolved),
        "tested_interactions": sum(1 for ix in interactions if ix.evidence_state == m.STATE_TESTED),
        "weak_evidence_interactions": sum(1 for ix in interactions
                                          if ix.evidence_strength in (m.STRENGTH_WEAK, m.STRENGTH_NONE, m.STRENGTH_UNKNOWN)),
        "interaction_classes": sorted({ix.interaction_class for ix in interactions}),
    }

    return {
        "schema_version": m.SCHEMA_VERSION,
        "package_version": package_version,
        "command": "interaction-matrix",
        "kind": m.KIND_INTERACTION_MATRIX,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "matrix_summary": summary,
        "interactions": [ix.to_dict() for ix in interactions],
        "unresolved_interactions": [ix.to_dict() for ix in unresolved],
        "scoring": {
            "formula": "interaction_priority = impact_score + review_gap_score + interaction_complexity_score",
            "note": "Heuristic review order. Not a probability, not a severity, not an exploitability estimate.",
            "thresholds": {"very-high": 85, "high": 65, "medium": 40, "monitor": 0},
        },
        "safety": _safety(),
        "human_review_required": True,
    }


def build_interaction_matrix_from_review_map(rm: ReviewMap, root, *,
                                             source_files: int = 0, test_files: int = 0,
                                             memory: dict[str, str] | None = None,
                                             package_version: str = "") -> dict:
    surfaces = build_research_surfaces(rm, root)
    return build_interaction_matrix(rm, surfaces, source_files=source_files, test_files=test_files,
                                    memory=memory, package_version=package_version)
