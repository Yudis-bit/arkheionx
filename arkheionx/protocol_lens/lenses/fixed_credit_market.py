"""Fixed Credit Market protocol lens (``fixed-credit-market``).

Models the Fixed Credit Market protocol family as a specific economic system rather
than generic DeFi: a fixed-maturity credit market with credit/debt unit accounting,
settlement-time liquidity, offer-based trading with no locked maker capital, maker
group exposure, multi-collateral solvency, lazy bad-debt / loss-factor accounting,
gated access control, and periphery bundle composition.

This file encodes *protocol-aware structure* only: extraction hints, behavior
promises, economic invariants, temporal windows, and review lanes. It contains no
line numbers and no specific known bug. It is a model, not a finding. Human review
is required for every conclusion.
"""
from __future__ import annotations

from .. import models as m
from ..base import ProtocolLens

LENS_ID = "fixed-credit-market"

_BOUNDARY = (
    "The Fixed Credit Market lens models a protocol; it does not confirm vulnerabilities, "
    "assign severity, or replace an audit. Planning artifact, not a finding. Human review required."
)

_FAMILIES = (
    "fixed-maturity credit market",
    "credit/debt unit accounting",
    "settlement-time liquidity",
    "offer-based trading",
    "maker group exposure",
    "multi-collateral solvency",
    "bad-debt and loss-factor accounting",
    "gated access control",
    "periphery bundle composition",
)

_KNOWN_SURFACES = (
    "credit market (markets, maturity, collateral, lltv/lif, gates, fees)",
    "positions (credit, debt, pending fees, loss factor, collateral bitmap)",
    "market state (total units, withdrawable, loss factor, continuous fee credit)",
    "offers (maker/taker, tick/price, caps, callbacks, ratifier, reduceOnly)",
    "periphery bundles (target/max assets/units, repay, collateral moves, referral)",
)


# --------------------------------------------------------------------------
# Extraction groups (section 6 of the spec)
# --------------------------------------------------------------------------
_GROUPS: tuple[m.ExtractionGroup, ...] = (
    m.ExtractionGroup("markets", "Markets", (
        "market", "maturity", "loanToken", "collateral", "lltv", "lif", "maxLIF",
        "gate", "tickSpacing", "settlementFee", "continuousFee", "claimableSettlementFee",
    )),
    m.ExtractionGroup("positions", "Positions", (
        "credit", "debt", "pendingFee", "lastLossFactor", "lastAccrual",
        "collateral", "collateralBitmap",
    )),
    m.ExtractionGroup("market_state", "Market state", (
        "totalUnits", "withdrawable", "lossFactor", "continuousFeeCredit",
        "consumed", "group",
    )),
    m.ExtractionGroup("offers", "Offers", (
        "maker", "taker", "buy", "tick", "price", "start", "expiry", "maxAssets",
        "maxUnits", "group", "callback", "receiver", "ratifier", "ratifierData",
        "reduceOnly",
    )),
    m.ExtractionGroup("periphery", "Periphery / bundles", (
        "bundle", "targetAssets", "targetUnits", "maxAssets", "maxUnits", "repay",
        "withdrawCollateral", "supplyCollateral", "referral", "fee", "skip",
        "revert", "callback", "receiver",
    )),
)

# Periphery/bundle function-name hints (substrings matched against discovered fns).
_PERIPHERY_FUNCTIONS = (
    "bundle", "settle", "take", "fill", "repay", "withdrawCollateral",
    "supplyCollateral", "borrow", "liquidate",
)


# --------------------------------------------------------------------------
# Behavior promises (section 8: PROMISE-FCM-01 .. PROMISE-FCM-14)
# --------------------------------------------------------------------------
def _promises() -> list[m.BehaviorPromise]:
    P = m.BehaviorPromise
    return [
        P("PROMISE-FCM-01", "Fixed maturity: debt should not be increasable after maturity, while unwind paths remain possible.",
          source_basis="Fixed-maturity credit market: maturity is a hard boundary on new debt, not on unwinding.",
          relevant_functions=["borrow", "maturity", "settle"],
          state_variables=["maturity", "debt"],
          violation_condition="A post-maturity path increases debt, or a maturity check blocks a legitimate unwind/liquidation.",
          possible_impact="Debt grows after the credit window closes, or borrowers are trapped unable to unwind.",
          missing_evidence=["A test that calls a debt-increasing path after maturity and asserts it reverts.",
                            "A test that confirms unwind/liquidation still works after maturity."]),
        P("PROMISE-FCM-02", "Credit/debt unit conservation: credit and debt units must move consistently with actual asset settlement.",
          source_basis="Credit/debt unit accounting: units are a claim on assets and must track settled assets.",
          relevant_functions=["settle", "repay", "borrow", "liquidate"],
          state_variables=["credit", "debt", "totalUnits"],
          violation_condition="Units change without a matching asset settlement, or asset settlement does not update units.",
          possible_impact="Unit accounting desyncs from backing, letting a party claim more than settled.",
          missing_evidence=["A conservation test: sum of credit/debt deltas equals settled-asset delta over an action."]),
        P("PROMISE-FCM-03", "Settlement-time liquidity: offers do not lock maker capital, but settlement must not finalize economic state without required payment.",
          source_basis="Settlement-time liquidity: makers post intent, not capital; finality requires payment at settlement.",
          relevant_functions=["settle", "take", "fill", "callback"],
          state_variables=["credit", "debt", "withdrawable"],
          violation_condition="A settlement finalizes state changes before the required payment is actually received.",
          possible_impact="A taker captures economic state without paying, draining makers or the market.",
          missing_evidence=["A test that withholds payment at settlement and asserts no state is finalized."]),
        P("PROMISE-FCM-04", "Maker group exposure cap: a maker's group budget must cap exposure across offers and markets according to signed intent.",
          source_basis="Maker group exposure: a group budget is the maker's signed cap across many offers/markets.",
          relevant_functions=["take", "fill", "settle"],
          state_variables=["group", "consumed", "maxAssets", "maxUnits"],
          violation_condition="Total consumed exposure for a maker/group exceeds the signed budget across offers or markets.",
          possible_impact="A maker is exposed beyond intent, taking losses they never authorized.",
          missing_evidence=["A multi-offer/multi-market test that sums consumed exposure against the signed group budget."]),
        P("PROMISE-FCM-05", "Multi-collateral solvency: borrowers must not withdraw collateral or end a transaction unsafe beyond intended liquidation rules.",
          source_basis="Multi-collateral solvency: final position health must hold across all collateral.",
          relevant_functions=["withdrawCollateral", "borrow", "settle", "liquidate"],
          state_variables=["collateral", "collateralBitmap", "debt", "lltv"],
          violation_condition="A transaction ends with a position below the documented health threshold.",
          possible_impact="An undercollateralized position is created, risking bad debt to lenders.",
          missing_evidence=["A test that ends a tx with final debt/fees/lossFactor applied and asserts health holds."]),
        P("PROMISE-FCM-06", "Bad-debt socialization: bad debt must reduce lender credit consistently once realized.",
          source_basis="Lazy bad-debt accounting: realized bad debt reduces lender credit via the loss factor.",
          relevant_functions=["liquidate", "settle", "accrue"],
          state_variables=["lossFactor", "credit", "withdrawable"],
          violation_condition="Realized bad debt is not reflected in lender credit, or is applied unevenly.",
          possible_impact="Some lenders avoid loss they should share; others over-absorb it.",
          missing_evidence=["A test that realizes bad debt and asserts lender credit reduces by the loss factor."]),
        P("PROMISE-FCM-07", "Liquidation consistency: different liquidation input modes must not create materially different economic outcomes unless documented and harmless.",
          source_basis="Liquidation may accept multiple input modes (by debt, by collateral, by units).",
          relevant_functions=["liquidate"],
          state_variables=["debt", "collateral", "lossFactor", "lif"],
          violation_condition="Two liquidation input modes for the same position produce materially different seized/repaid amounts.",
          possible_impact="An actor picks the mode that over-seizes collateral or under-repays debt.",
          missing_evidence=["A differential test comparing liquidation input modes on an identical position."]),
        P("PROMISE-FCM-08", "Post-maturity debt handling: after maturity, outstanding debt should remain unwindable or liquidatable according to protocol rules.",
          source_basis="Fixed maturity closes new borrowing but not resolution of existing debt.",
          relevant_functions=["liquidate", "repay", "settle", "maturity"],
          state_variables=["maturity", "debt", "collateral"],
          violation_condition="Outstanding debt becomes neither repayable nor liquidatable after maturity.",
          possible_impact="Value is trapped; lenders cannot recover and borrowers cannot exit.",
          missing_evidence=["A test that advances past maturity and asserts repay/liquidate still resolve debt."]),
        P("PROMISE-FCM-09", "Gates: gates should restrict entry without trapping safe exits or breaking accounting.",
          source_basis="Gated access control restricts who can enter; it must not break exit or accounting.",
          relevant_functions=["gate", "borrow", "repay", "withdrawCollateral", "liquidate"],
          state_variables=["gate"],
          violation_condition="A gate blocks repay/withdraw/liquidation for an already-entered party, or desyncs accounting.",
          possible_impact="A gated-out party is trapped, or a gate inconsistency corrupts accounting.",
          missing_evidence=["A test that gates a party post-entry and asserts safe exit/repay/liquidation still works."]),
        P("PROMISE-FCM-10", "Fees: settlement fees, continuous fees, referral fees, and claimable fees must not create unbacked value.",
          source_basis="Multiple fee streams (settlement, continuous, referral) must be fully backed.",
          relevant_functions=["settle", "accrue", "claim", "fee"],
          state_variables=["settlementFee", "continuousFee", "claimableSettlementFee", "pendingFee", "continuousFeeCredit"],
          violation_condition="A fee is credited or claimed without corresponding backing in the market.",
          possible_impact="Fee accounting mints unbacked value, diluting lenders or the market.",
          missing_evidence=["A test that accrues and claims each fee stream and asserts backing is conserved."]),
        P("PROMISE-FCM-11", "Periphery target correctness: target-based periphery functions must not treat target completion using the wrong unit, wrong side, or wrong net/gross amount.",
          source_basis="Periphery bundles use target/max in assets or units; the dimension must be correct.",
          relevant_functions=["bundle", "settle", "take", "fill"],
          state_variables=["targetAssets", "targetUnits", "maxAssets", "maxUnits"],
          violation_condition="A target is measured in the wrong unit/side/net-gross, marking completion incorrectly.",
          possible_impact="A bundle under- or over-fills, moving value against the user's intent.",
          missing_evidence=["A test asserting target completion uses the correct unit, side, and net/gross amount."]),
        P("PROMISE-FCM-12", "Cap correctness: maxAssets, maxUnits, targetAssets, and targetUnits must cap the economically relevant amount.",
          source_basis="Caps must bind the dimension that actually moves value, not a proxy.",
          relevant_functions=["bundle", "settle", "take", "fill"],
          state_variables=["maxAssets", "maxUnits", "targetAssets", "targetUnits"],
          violation_condition="A cap binds a dimension that is not the one moving value (e.g. caps units while assets move).",
          possible_impact="A user pays or receives more than their stated cap.",
          missing_evidence=["A boundary test driving each cap to its limit and asserting the value dimension is bound."]),
        P("PROMISE-FCM-13", "Callback finality: callbacks may observe intermediate state only if final transaction invariants still prevent economic violation.",
          source_basis="Settlement/periphery callbacks run mid-transaction; finality must still hold after.",
          relevant_functions=["callback", "settle", "take", "bundle"],
          state_variables=["credit", "debt", "withdrawable"],
          violation_condition="A callback observes or acts on intermediate state to violate a final invariant.",
          possible_impact="Re-entrant or mid-update observation lets a callback extract value.",
          missing_evidence=["A reentrancy/callback test asserting final invariants hold regardless of mid-tx observation."]),
        P("PROMISE-FCM-14", "Market identity isolation: state, signatures, ratifications, offers, groups, and accounting must not be reusable across markets unless explicitly intended.",
          source_basis="Each market has an identity; signed intent and accounting are bound to it.",
          relevant_functions=["settle", "take", "ratifier", "borrow", "liquidate"],
          state_variables=["market", "group", "ratifierData"],
          violation_condition="An offer/signature/ratification/accounting entry from one market is honored in another.",
          possible_impact="Cross-market reuse authorizes value movement that was never intended for that market.",
          missing_evidence=["A cross-market test reusing an offer/signature/ratification and asserting rejection."]),
    ]


# --------------------------------------------------------------------------
# Economic invariants (section 9: INV-FCM-01 .. INV-FCM-12)
# --------------------------------------------------------------------------
def _invariants() -> list[m.EconomicInvariant]:
    I = m.EconomicInvariant
    return [
        I("INV-FCM-01", "Any credit increase, debt reduction, collateral withdrawal, or receiver payout must be backed by actual payment or valid existing position reduction.",
          relevant_functions=["settle", "take", "repay", "withdrawCollateral", "bundle"],
          state_variables=["credit", "debt", "collateral", "withdrawable"],
          mathematical_form="delta(value_out) <= delta(payment_in) + valid_position_reduction",
          missing_tests=["A test that attempts value-out without payment and asserts it reverts or nets to zero."],
          impact_if_broken="Unbacked value leaves the market: a direct loss to lenders or the protocol."),
        I("INV-FCM-02", "Debt reduced must not exceed actual loan assets paid, adjusted only by documented mechanics.",
          relevant_functions=["repay", "settle", "liquidate"],
          state_variables=["debt", "loanToken"],
          mathematical_form="delta(debt_down) <= assets_paid * documented_factor",
          missing_tests=["A test asserting debt reduction never exceeds assets paid (plus documented adjustments)."],
          impact_if_broken="Borrowers erase more debt than they pay, stranding lenders."),
        I("INV-FCM-03", "Collateral withdrawal must only be possible when final position health is valid under final debt, fees, and lossFactor.",
          relevant_functions=["withdrawCollateral", "bundle", "settle"],
          state_variables=["collateral", "debt", "lltv", "lossFactor", "pendingFee"],
          mathematical_form="health(final_debt + fees, final_collateral, lossFactor) >= threshold",
          missing_tests=["A test withdrawing collateral with final debt/fees/lossFactor applied and asserting health holds."],
          impact_if_broken="Borrowers extract collateral while leaving an unsafe position, creating bad debt."),
        I("INV-FCM-04", "Credit minted or preserved must correspond to future withdrawable backing after fees, bad debt, and lossFactor.",
          relevant_functions=["settle", "accrue", "liquidate"],
          state_variables=["credit", "withdrawable", "lossFactor", "continuousFeeCredit"],
          mathematical_form="credit_value <= withdrawable_after(fees, bad_debt, lossFactor)",
          missing_tests=["A test reconciling minted/preserved credit against withdrawable after all adjustments."],
          impact_if_broken="Credit overstates backing; later withdrawers find the market short."),
        I("INV-FCM-05", "withdrawable must not exceed loan token value actually owed to lenders after repayments, liquidations, fees, and bad debt.",
          relevant_functions=["settle", "repay", "liquidate", "accrue"],
          state_variables=["withdrawable", "totalUnits", "lossFactor"],
          mathematical_form="withdrawable <= owed_to_lenders(repayments, liquidations, fees, bad_debt)",
          missing_tests=["A solvency test asserting withdrawable never exceeds owed loan-token value."],
          impact_if_broken="The market promises more than it holds: a run leaves late withdrawers unpaid."),
        I("INV-FCM-06", "For any maker and group, total economic exposure must not exceed the intended cap.",
          relevant_functions=["take", "fill", "settle"],
          state_variables=["group", "consumed", "maxAssets", "maxUnits"],
          mathematical_form="sum_over_offers(consumed[maker, group]) <= signed_budget[maker, group]",
          missing_tests=["A multi-offer/multi-market test summing consumed exposure against the signed cap."],
          impact_if_broken="A maker is forced into exposure beyond their signed intent."),
        I("INV-FCM-07", "A target-based periphery function must not stop early unless the actual user-intended target has been achieved.",
          relevant_functions=["bundle", "settle", "take", "fill"],
          state_variables=["targetAssets", "targetUnits"],
          mathematical_form="stop <=> achieved(target_in_correct_dimension)",
          missing_tests=["A test asserting the bundle only stops when the user-intended target (correct dimension) is met."],
          impact_if_broken="A bundle under-delivers while reporting success, harming the user."),
        I("INV-FCM-08", "If a path includes fees or receiver payouts, caps and targets must apply to the correct gross or net amount.",
          relevant_functions=["bundle", "settle", "fee"],
          state_variables=["maxAssets", "maxUnits", "settlementFee", "referral"],
          mathematical_form="cap binds amount net/gross of fees per documented intent",
          missing_tests=["A test with non-zero fees asserting caps/targets bind the correct gross/net amount."],
          impact_if_broken="Fees push the real amount past the user's cap, or short their target."),
        I("INV-FCM-09", "One actor must not force disproportionate loss onto another actor through undocumented delay or stale state.",
          relevant_functions=["accrue", "settle", "liquidate"],
          state_variables=["lastLossFactor", "lastAccrual", "lossFactor"],
          mathematical_form="loss_share(actor) is order-independent for documented mechanics",
          missing_tests=["An ordering test: vary accrual/realization order and assert loss share is invariant."],
          impact_if_broken="A timing game shifts loss from one lender to another."),
        I("INV-FCM-10", "Accounting or authorization from one market must not affect another market unless explicitly designed.",
          relevant_functions=["settle", "take", "ratifier", "liquidate"],
          state_variables=["market", "group"],
          mathematical_form="state(market_a) independent of state(market_b) unless designed",
          missing_tests=["A cross-market isolation test asserting one market's action cannot move another's state."],
          impact_if_broken="Cross-market contamination authorizes or funds movement that was never intended."),
        I("INV-FCM-11", "Gate logic must not create inconsistent states where entry is blocked but safe exit, repayment, or liquidation becomes broken.",
          relevant_functions=["gate", "repay", "withdrawCollateral", "liquidate"],
          state_variables=["gate", "debt", "collateral"],
          mathematical_form="gated_entry does not imply broken(exit | repay | liquidate)",
          missing_tests=["A test gating a party and asserting exit/repay/liquidation still function and reconcile."],
          impact_if_broken="A gated party is trapped, or the gate desyncs accounting."),
        I("INV-FCM-12", "Candidates near known bug families must be tested against a patch model before being considered new.",
          relevant_functions=["settle", "bundle", "liquidate"],
          state_variables=[],
          mathematical_form="candidate is novel iff it survives the patched-behavior model",
          missing_tests=["A differential test against a patched-behavior model to rule out a known/fixed family."],
          impact_if_broken="Effort is wasted on duplicates, or a known-fixed issue is mis-reported as new."),
    ]


# --------------------------------------------------------------------------
# Temporal windows
# --------------------------------------------------------------------------
def _temporal_windows() -> list[m.TemporalWindow]:
    W = m.TemporalWindow
    return [
        W("WIN-MM-01", "Settlement callback window",
          "Between the start of settlement and final invariant checks, a callback can observe intermediate credit/debt/withdrawable state.",
          observable_state="credit, debt, withdrawable mid-settlement",
          risk="A callback acts on intermediate state to violate a final invariant.",
          relevant_functions=["settle", "callback"]),
        W("WIN-MM-02", "Periphery bundle composition window",
          "Within a bundle, intermediate steps (take/repay/withdrawCollateral) run before the bundle's final health/target checks.",
          observable_state="position health and target progress between steps",
          risk="An intermediate step locks in target/health using stale or pre-fee values.",
          relevant_functions=["bundle", "withdrawCollateral", "repay"]),
        W("WIN-MM-03", "Maturity boundary window",
          "Around maturity, debt-increasing paths should close while unwind/liquidation paths stay open.",
          observable_state="maturity vs current time, outstanding debt",
          risk="A path increases debt just after maturity, or blocks a needed unwind.",
          relevant_functions=["borrow", "settle", "liquidate"]),
        W("WIN-MM-04", "Loss-factor realization window",
          "Between bad-debt occurrence and its lazy realization, lossFactor may be stale for some actors.",
          observable_state="lastLossFactor vs current lossFactor",
          risk="An actor exits before realization to avoid a loss others then absorb.",
          relevant_functions=["accrue", "settle", "liquidate"]),
    ]


# --------------------------------------------------------------------------
# Review lanes (section 10: LANE-01 .. LANE-10)
# --------------------------------------------------------------------------
def _lanes() -> list[m.LensLaneDef]:
    L = m.LensLaneDef
    return [
        L("LANE-01", "Periphery target accounting", "periphery-target-accounting",
          m.PRIORITY_VERY_HIGH,
          ("targetassets", "targetunits", "maxassets", "maxunits", "bundle", "skip", "fee", "referral", "partial", "fill"),
          "Target/cap accounting in periphery bundles decides how much value moves; a unit/side/net-gross mismatch moves value against intent.",
          ("INV-FCM-07", "INV-FCM-08", "INV-FCM-12"), ("PROMISE-FCM-11", "PROMISE-FCM-12"),
          ("Can a targetUnits path mark completion before gross fee-adjusted settlement is paid?",
           "Does a cap bind units while assets actually move (or vice versa)?"),
          ("target completion uses the correct unit/side", "cap binds the value dimension", "fee gross/net handled at the boundary"),
          "Target completion and caps are shown to bind the correct economic dimension under fees and partial fills."),
        L("LANE-02", "Collateral movement after composed target", "collateral-after-composed-target",
          m.PRIORITY_VERY_HIGH,
          ("withdrawcollateral", "collateral", "bundle", "repay", "take", "health", "stale", "underfill"),
          "Composed bundles move collateral after take/repay steps; stale debt/fees or an underfilled target can leave an unsafe position.",
          ("INV-FCM-03", "INV-FCM-07"), ("PROMISE-FCM-05", "PROMISE-FCM-11"),
          ("Can collateral be withdrawn using stale debt/fees from before the composed step?",
           "Does an underfilled target still permit collateral withdrawal?"),
          ("final health uses final debt/fees/lossFactor", "collateral move blocked when target underfilled"),
          "Collateral withdrawal is shown to use final debt/fees/lossFactor and to block on underfill."),
        L("LANE-03", "Settlement-time liquidity", "settlement-time-liquidity",
          m.PRIORITY_VERY_HIGH,
          ("settle", "offer", "callback", "receiver", "take", "fill", "payment"),
          "Offers lock no maker capital, so settlement is the moment payment and state must reconcile; an early finalization drains makers.",
          ("INV-FCM-01", "INV-FCM-02"), ("PROMISE-FCM-03", "PROMISE-FCM-13"),
          ("Can settlement finalize credit/debt before the required payment is received?",
           "Can a receiver/callback path take value without paying?"),
          ("state finalization is gated on payment", "no value-out without payment-in"),
          "Settlement is shown to finalize state only after the required payment is received."),
        L("LANE-04", "Maker group cap", "maker-group-cap",
          m.PRIORITY_HIGH,
          ("group", "consumed", "maxassets", "maxunits", "reduceonly", "maker", "budget", "signed"),
          "A maker's group budget caps exposure across offers and markets; a leak lets a maker be exposed beyond signed intent.",
          ("INV-FCM-06",), ("PROMISE-FCM-04",),
          ("Can total consumed exposure exceed the signed group budget across multiple offers?",
           "Does multi-market use double-count or bypass the group cap?"),
          ("consumed exposure summed across offers/markets", "exposure never exceeds signed budget"),
          "Total consumed maker exposure is shown to stay within the signed group budget across offers and markets."),
        L("LANE-05", "Bad debt and lossFactor", "bad-debt-loss-factor",
          m.PRIORITY_HIGH,
          ("lossfactor", "lastlossfactor", "withdrawable", "credit", "baddebt", "bad debt", "stale", "realization"),
          "Lazy bad-debt accounting via the loss factor can be gamed by ordering; some lenders may dodge loss others absorb.",
          ("INV-FCM-04", "INV-FCM-05", "INV-FCM-09"), ("PROMISE-FCM-06",),
          ("Can an actor exit before bad-debt realization to avoid a loss others absorb?",
           "Does stale lossFactor let withdrawable exceed real backing?"),
          ("bad debt reduces lender credit consistently", "withdrawable never exceeds owed value"),
          "Bad-debt realization is shown to reduce lender credit consistently and order-independently."),
        L("LANE-06", "Liquidation consistency", "liquidation-consistency",
          m.PRIORITY_HIGH,
          ("liquidate", "liquidation", "seize", "lif", "maxlif", "baddebt", "maturity", "input mode"),
          "Liquidation may accept several input modes; divergent outcomes let an actor over-seize or under-repay.",
          ("INV-FCM-02", "INV-FCM-03"), ("PROMISE-FCM-07", "PROMISE-FCM-08"),
          ("Do different liquidation input modes produce materially different seized/repaid amounts?",
           "Does post-maturity liquidation still resolve debt correctly?"),
          ("differential across input modes on one position", "post-maturity liquidation resolves debt"),
          "Liquidation outcomes are shown to be consistent across input modes and valid after maturity."),
        L("LANE-07", "Gates", "gates",
          m.PRIORITY_MEDIUM,
          ("gate", "enter", "exit", "repay", "withdraw", "liquidat", "access"),
          "Gates restrict entry; a gate that also breaks exit/repay/liquidation traps value or desyncs accounting.",
          ("INV-FCM-11",), ("PROMISE-FCM-09",),
          ("Can a gated-out party still repay, withdraw collateral, and be liquidated safely?",
           "Does a gate change desync accounting for an already-entered party?"),
          ("safe exit/repay/liquidation under a gate", "accounting stays consistent across gating"),
          "Gates are shown to restrict entry without trapping safe exits or breaking accounting."),
        L("LANE-08", "Authorization / ratifier / signatures", "authorization-ratifier-signatures",
          m.PRIORITY_HIGH,
          ("ratifier", "ratifierdata", "signature", "signed", "sign", "proof", "replay", "market", "offer", "nonce"),
          "Signed intent, ratifications, and offers are bound to a market/offer identity; a binding gap enables replay or cross-market misuse.",
          ("INV-FCM-10",), ("PROMISE-FCM-14",),
          ("Can an offer/signature/ratification from one market be honored in another?",
           "Can a signed intent be replayed within or across markets?"),
          ("signed intent bound to market/offer identity", "cross-market reuse rejected"),
          "Signed intent and ratifications are shown to bind to the correct market/offer identity and reject reuse."),
        L("LANE-09", "Fee correctness", "fee-correctness",
          m.PRIORITY_MEDIUM,
          ("settlementfee", "continuousfee", "referral", "pendingfee", "claimablesettlementfee", "continuousfeecredit", "fee"),
          "Multiple fee streams must stay fully backed; a fee credited without backing mints unbacked value.",
          ("INV-FCM-01", "INV-FCM-08"), ("PROMISE-FCM-10",),
          ("Can any fee stream be credited or claimed without corresponding backing?",
           "Do fees interact with caps/targets to push amounts past intent?"),
          ("each fee stream is backed", "fee-adjusted caps/targets bind the right amount"),
          "Each fee stream is shown to be backed and to interact correctly with caps and targets."),
        L("LANE-10", "Callback temporal windows", "callback-temporal-windows",
          m.PRIORITY_HIGH,
          ("callback", "reentr", "intermediate", "compose", "bundle", "hook", "rollback"),
          "Settlement/periphery callbacks observe mid-transaction state; if final invariants do not hold, a callback can extract value.",
          ("INV-FCM-01",), ("PROMISE-FCM-13",),
          ("Can a callback observe or act on intermediate state to violate a final invariant?",
           "Do composed periphery interactions assume a rollback that does not happen?"),
          ("final invariants hold regardless of mid-tx observation", "callback caller/state checks present"),
          "Final transaction invariants are shown to hold regardless of any intermediate state a callback observes."),
    ]


# --------------------------------------------------------------------------
# Value-flow templates
# --------------------------------------------------------------------------
def _value_flow_templates() -> list[m.ValueFlowPath]:
    V = m.ValueFlowPath
    return [
        V("VF-FCM-01", "Lend / supply credit", entry="lender supplies loan token",
          movement="credit units minted against backing", exit="withdraw to loan token",
          signals=["credit", "withdrawable", "totalUnits"]),
        V("VF-FCM-02", "Borrow against collateral", entry="borrower supplies collateral",
          movement="debt units issued, loan token paid out", exit="repay / liquidation",
          signals=["debt", "collateral", "lltv"]),
        V("VF-FCM-03", "Offer settlement", entry="maker posts offer intent",
          movement="taker settles, payment reconciles credit/debt", exit="settlement payout",
          signals=["maker", "taker", "settle", "group"]),
        V("VF-FCM-04", "Periphery bundle", entry="user submits a composed bundle",
          movement="take/repay/collateral steps to a target", exit="receiver payout / collateral move",
          signals=["bundle", "targetUnits", "withdrawCollateral", "receiver"]),
        V("VF-FCM-05", "Liquidation", entry="liquidator targets an unhealthy position",
          movement="debt repaid, collateral seized, bad debt realized", exit="seized collateral payout",
          signals=["liquidate", "lif", "lossFactor"]),
    ]


class FixedCreditMarketLens(ProtocolLens):
    """Protocol lens for Fixed Credit Market (``fixed-credit-market``)."""

    def meta(self) -> m.ProtocolLensMeta:
        return m.ProtocolLensMeta(
            lens_id=LENS_ID,
            display_name="Fixed Credit Market Protocol Lens",
            protocol_family="fixed-maturity-credit-market",
            families=_FAMILIES,
            supported_languages=("solidity",),
            supported_frameworks=("foundry",),
            known_surfaces=_KNOWN_SURFACES,
            boundary_notice=_BOUNDARY,
        )

    def extraction_groups(self) -> list[m.ExtractionGroup]:
        return list(_GROUPS)

    def periphery_function_names(self) -> list[str]:
        return list(_PERIPHERY_FUNCTIONS)

    def value_flow_templates(self) -> list[m.ValueFlowPath]:
        return _value_flow_templates()

    def behavior_promises(self) -> list[m.BehaviorPromise]:
        return _promises()

    def economic_invariants(self) -> list[m.EconomicInvariant]:
        return _invariants()

    def temporal_windows(self) -> list[m.TemporalWindow]:
        return _temporal_windows()

    def review_lanes(self) -> list[m.LensLaneDef]:
        return _lanes()
