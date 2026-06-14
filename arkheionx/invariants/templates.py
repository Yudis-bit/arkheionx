"""Invariant template catalog (Layer 4).

Each template encodes an actionable economic property, the conditions that make
it *suspicious*, default attacker/victim/asset framing, testability, and an
initial severity hint (the economic gate makes the real call later).

Templates are generic shapes, never protocol-specific.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import T_FORK, T_LOCAL


@dataclass
class InvariantTemplate:
    id: str
    title: str
    description: str
    assertion_form: str
    why_it_matters: str
    attacker: str
    victim: str
    asset: str
    testability: str
    severity_hint: str
    suspicious_if: tuple


DEBT_REPAYMENT_RECONCILIATION = InvariantTemplate(
    id="DEBT_REPAYMENT_RECONCILIATION",
    title="Debt reduction must reconcile with lender credit",
    description=("Debt reduction in {function} must reconcile with lender/user repayment "
                 "credit plus explicitly tracked dust. If debt is reduced before per-tranche "
                 "flooring, the loan may close while summed lender credit is below principal."),
    assertion_form=("sum(lenderCredited_i) + trackedDust == debtBefore - debtAfter; "
                    "loan.status == Repaid => lender principal fully settled or claimable"),
    why_it_matters=("Independent per-tranche rounding can under-distribute to lenders while the "
                    "loan closes on debt alone, leaving lenders short and collateral released."),
    attacker="borrower (or any repayer)",
    victim="lenders / tranche holders",
    asset="repayment principal (rounding remainder)",
    testability=T_LOCAL,
    severity_hint="VALID_BUT_LOW unless per-call loss is large for realistic decimals",
    suspicious_if=("has_division", "debt_reduced_before_distribution"),
)

LENDER_CONSENT_VALUE_AFFECTING_CALLDATA = InvariantTemplate(
    id="LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
    title="Value-affecting calldata must be bound by victim consent",
    description=("Counterparty-controlled calldata reaching a value path in {function} "
                 "(route/receiver/amount/refund/asset) must be authorized by the victim. "
                 "Here borrower-controlled swap calldata reaches a value path but the consent "
                 "hash binds only the terms, not that calldata."),
    assertion_form=("victimRefund_withHonestRoute == victimRefund_withAttackerRoute "
                    "OR consentHash binds the route/min-refund/max-input"),
    why_it_matters=("If the victim's refund/claim can decrease under a counterparty-chosen route "
                    "that consent never bound, the victim bears uncompensated loss."),
    attacker="borrower / counterparty supplying calldata",
    victim="lender / predepositor",
    asset="lender refund / predeposit buffer",
    testability=T_FORK,
    severity_hint="NEEDS_FORK_PROOF; Low unless capture + large realistic buffer proven",
    suspicious_if=("calldata_route", "route_not_in_consent_hash"),
)

BORROW_CONSERVATION = InvariantTemplate(
    id="BORROW_CONSERVATION",
    title="Borrow must conserve value and escrow collateral",
    description=("In {function}, borrower received + fees must reconcile with lender funds "
                 "consumed, and the loan may be Active only if collateral is escrowed."),
    assertion_form=("borrowerReceived + fees <= lenderFundsConsumed; "
                    "loan.active => collateral escrowed before funds released"),
    why_it_matters=("Funds released before collateral escrow, or partial deposit consumption, "
                    "breaks solvency."),
    attacker="borrower",
    victim="protocol / lenders",
    asset="lender funds / collateral",
    testability=T_LOCAL,
    severity_hint="MEDIUM if conservation truly breaks",
    suspicious_if=("ext_before_write", "funds_before_collateral"),
)

DEPOSIT_CONSUMPTION = InvariantTemplate(
    id="DEPOSIT_CONSUMPTION",
    title="A deposit must not be consumed twice",
    description=("A deposit in {function} cannot be consumed twice, after withdrawal, after "
                 "expiration, or for the wrong target/context/token/amount."),
    assertion_form=("consume(deposit) twice reverts; deposit.active cleared before any external "
                    "interaction (checks-effects-interactions)"),
    why_it_matters=("Clearing the active flag after an external transfer opens a reentrancy / "
                    "double-use window that can drain the deposit twice."),
    attacker="deposit owner / reentrant caller",
    victim="protocol / other depositors",
    asset="deposited funds",
    testability=T_LOCAL,
    severity_hint="HIGH if double-spend is reachable; depends on guard",
    suspicious_if=("ext_before_write", "key_missing_field"),
)

SWAP_ACTUAL_RECEIVED_VS_CREDITED = InvariantTemplate(
    id="SWAP_ACTUAL_RECEIVED_VS_CREDITED",
    title="Credited output must equal actual received",
    description=("In {function}, the amount credited after a swap/adapter call must equal the "
                 "actual balance delta, or be safely bounded by minOut."),
    assertion_form=("creditedOut == balanceAfter - balanceBefore; minOut protects the receiver"),
    why_it_matters=("Crediting expected output instead of measured delta lets fee-on-transfer / "
                    "rebasing / slippage mis-credit value."),
    attacker="swap initiator / token deployer",
    victim="protocol / depositor",
    asset="swap output",
    testability=T_FORK,
    severity_hint="MEDIUM; fork needed if real AMM behavior matters",
    suspicious_if=("swap_no_balance_delta",),
)

VAULT_SHARE_ASSET_RECONCILIATION = InvariantTemplate(
    id="VAULT_SHARE_ASSET_RECONCILIATION",
    title="Shares must reconcile with assets",
    description=("Shares minted/burned in {function} must reconcile with assets received/withdrawn. "
                 "Suspicious if zero-share deposits are possible, totalAssets is attacker-inflatable, "
                 "or there is no seed/dead-shares/offset."),
    assertion_form=("sharesMinted == assets * supply / totalAssets (no zero-share theft); "
                    "totalAssets not inflatable without minting shares"),
    why_it_matters=("Balance-based totalAssets plus no dead-shares lets a first depositor / donor "
                    "inflate the share price and steal a later depositor's assets."),
    attacker="first depositor / donor",
    victim="next depositor",
    asset="deposited assets",
    testability=T_LOCAL,
    severity_hint="HIGH if first-depositor theft is reachable; else MEDIUM",
    suspicious_if=("balance_based_assets", "no_zero_share_guard"),
)

COLLATERAL_STATUS_RELEASE = InvariantTemplate(
    id="COLLATERAL_STATUS_RELEASE",
    title="Collateral releases only after settlement",
    description=("Collateral in {function} may be released only to the rightful owner after "
                 "settlement/liquidation conditions are fully met."),
    assertion_form=("collateral released => debt fully settled (not just debt==0 by scaled units); "
                    "released only to rightful owner"),
    why_it_matters=("Releasing collateral on a debt counter that was reduced before lender "
                    "settlement can free collateral while lenders are still short."),
    attacker="borrower",
    victim="lenders",
    asset="escrowed collateral",
    testability=T_LOCAL,
    severity_hint="HIGH if collateral frees while lenders unpaid; else MEDIUM",
    suspicious_if=("collateral_release_on_debt_only",),
)

ORACLE_DECIMAL_NORMALIZATION = InvariantTemplate(
    id="ORACLE_DECIMAL_NORMALIZATION",
    title="Price and token decimals must normalize consistently",
    description=("Price feeds and token decimals used in {function} must be normalized "
                 "consistently, with stale-price bounds and no attacker-controlled source."),
    assertion_form=("quote = price * 10^(tokenDec - feedDec) applied consistently; price bounded/fresh"),
    why_it_matters=("Mixed feed/token decimals or hardcoded 1e18 mis-price assets, over-crediting one side."),
    attacker="price manipulator / arbitrageur",
    victim="protocol / users",
    asset="mispriced asset value",
    testability=T_LOCAL,
    severity_hint="MEDIUM/HIGH depending on mispricing magnitude",
    suspicious_if=("mixed_decimals", "hardcoded_1e18"),
)

CROSS_CHAIN_SUPPLY_CONSERVATION = InvariantTemplate(
    id="CROSS_CHAIN_SUPPLY_CONSERVATION",
    title="Cross-chain mint/burn/lock/unlock must conserve supply",
    description=("In {function}, mint/burn/lock/unlock must conserve supply across source and "
                 "destination accounting, with no message replay and a bound trusted peer."),
    assertion_form=("sum(locked) == sum(minted); messages consumed once; peer/source authorized"),
    why_it_matters=("Replay, wrong trusted peer, or decimal mismatch inflates cross-chain supply."),
    attacker="cross-chain message sender",
    victim="all token holders",
    asset="token supply",
    testability=T_FORK,
    severity_hint="HIGH if supply can inflate; fork/integration proof needed",
    suspicious_if=("replay_possible", "peer_unbound"),
)

TEMPLATES = {
    t.id: t for t in (
        DEBT_REPAYMENT_RECONCILIATION,
        LENDER_CONSENT_VALUE_AFFECTING_CALLDATA,
        BORROW_CONSERVATION,
        DEPOSIT_CONSUMPTION,
        SWAP_ACTUAL_RECEIVED_VS_CREDITED,
        VAULT_SHARE_ASSET_RECONCILIATION,
        COLLATERAL_STATUS_RELEASE,
        ORACLE_DECIMAL_NORMALIZATION,
        CROSS_CHAIN_SUPPLY_CONSERVATION,
    )
}
