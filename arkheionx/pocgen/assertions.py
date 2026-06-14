"""Action-sequence and assertion builders for PoC skeletons (Layer 6).

Assertions are written to falsify the broken invariant. They are real Foundry
assertions with explicit TODO markers where target-specific values are needed; we
do not claim they compile unmodified.
"""
from __future__ import annotations

_ACTIONS = {
    "DEBT_REPAYMENT_RECONCILIATION": [
        "uint256 debtBefore = loan.debt();",
        "uint256 creditBefore = totalLenderCredit();",
        "vm.prank(borrower); target.repay(loanId, amount); // repeat for partial repayments",
        "uint256 debtAfter = loan.debt();",
        "uint256 creditAfter = totalLenderCredit();",
    ],
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": [
        "uint256 refundHonest = runOrigination(honestRoute);",
        "vm.revertTo(snapshot);",
        "uint256 refundAttacker = runOrigination(attackerRoute); // same loan output",
    ],
    "BORROW_CONSERVATION": [
        "uint256 lenderBefore = asset.balanceOf(lender);",
        "vm.prank(borrower); target.borrow(terms, infos);",
        "uint256 borrowerRecv = asset.balanceOf(borrower);",
    ],
    "DEPOSIT_CONSUMPTION": [
        "vm.prank(depositor); target.createDeposit(key, amount);",
        "vm.prank(attacker); target.consume(key);",
        "// attempt to consume the same deposit again (or reenter during transfer)",
    ],
    "VAULT_SHARE_ASSET_RECONCILIATION": [
        "vm.prank(attacker); target.deposit(1); // first depositor mints ~1 share",
        "asset.transfer(address(target), donation); // inflate totalAssets by donation",
        "vm.prank(victim); uint256 got = target.deposit(victimAssets);",
    ],
    "COLLATERAL_STATUS_RELEASE": [
        "vm.prank(borrower); target.repay(loanId, partialAmount);",
        "// drive the status/release path while lender settlement is incomplete",
    ],
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": [
        "uint256 balBefore = tokenOut.balanceOf(address(target));",
        "uint256 credited = target.swapAndCredit(tokenIn, tokenOut, amountIn, route);",
        "uint256 actual = tokenOut.balanceOf(address(target)) - balBefore;",
    ],
    "ORACLE_DECIMAL_NORMALIZATION": [
        "uint8 feedDecimals = 8;    // TODO: set to the real price-feed decimals",
        "uint8 tokenDecimals = 18;  // TODO: set to the real collateral token decimals",
        "oracle.setAnswer(int256(2000 * 10 ** uint256(feedDecimals)), feedDecimals);",
        "collateral.mint(borrower, 1 * 10 ** uint256(tokenDecimals));",
        "uint256 protocolMax = target.maxBorrow(borrower);",
        "uint256 safeMax = (1 * 2000) * 10 ** 18 / 10 ** uint256(feedDecimals); // normalized value",
    ],
    "CROSS_CHAIN_SUPPLY_CONSERVATION": [
        "bytes32 msgId = keccak256(\"cross-chain-message-1\");",
        "uint256 supplyBefore = token.totalSupply();",
        "vm.prank(attacker); target.receiveMessage(msgId, attacker, amount);",
        "vm.prank(attacker); target.receiveMessage(msgId, attacker, amount); // replay SAME id",
        "uint256 supplyAfter = token.totalSupply();",
    ],
    "ACCESS_CONTROLLED_VALUE_MOVEMENT": [
        "vm.prank(attacker);",
        "vm.expectRevert(); // unprivileged caller must not move value",
    ],
}

_ASSERTS = {
    "DEBT_REPAYMENT_RECONCILIATION": [
        "// INVARIANT: debt reduction must reconcile with lender credit (+ tracked dust).",
        "assertEq(debtBefore - debtAfter, (creditAfter - creditBefore) + trackedDust,",
        "    \"lender credit + dust must equal debt reduction\");",
        "// If the loan closed, lenders must be fully settled (not just debt==0).",
        "if (loan.status() == REPAID) assertGe(creditAfter, principalOwed,",
        "    \"loan closed while lenders short\");",
        "// SEVERITY CAP: loss is bounded by per-tranche rounding (token base units).",
        "//   18-decimal assets are effectively immune; quantify for 6-decimal currencies.",
    ],
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": [
        "// INVARIANT: a counterparty-chosen route must not reduce the victim's refund",
        "//   unless the victim consented to it.",
        "assertEq(refundHonest, refundAttacker,",
        "    \"victim refund decreased under an unconsented attacker route\");",
        "// SEVERITY CAP: loss is bounded by the predeposit buffer; same-token path is",
        "//   immune; FORK REQUIRED because real AMM liquidity sets the actual delta.",
    ],
    "BORROW_CONSERVATION": [
        "// INVARIANT: borrower received <= lender funds consumed - fees; collateral escrowed.",
        "assertLe(borrowerRecv, lenderBefore - asset.balanceOf(lender) - fees,",
        "    \"borrower received more than lenders funded\");",
        "assertTrue(collateralEscrowed(), \"loan active without collateral escrow\");",
    ],
    "DEPOSIT_CONSUMPTION": [
        "// INVARIANT: a deposit cannot be consumed twice / after clearing.",
        "vm.expectRevert();",
        "vm.prank(attacker); target.consume(key); // second consume must revert",
        "// If a reentrant token is used, assert total paid out <= deposited amount.",
    ],
    "VAULT_SHARE_ASSET_RECONCILIATION": [
        "// INVARIANT: a later depositor must not lose assets to share-price inflation.",
        "assertGt(got, 0, \"victim minted zero shares (rounded to nothing)\");",
        "uint256 recoverable = target.previewRedeem(target.shares(victim));",
        "assertGe(recoverable, victimAssets * 99 / 100, \"victim cannot recover ~deposit\");",
    ],
    "COLLATERAL_STATUS_RELEASE": [
        "// INVARIANT: collateral releases only after full settlement, to the rightful owner.",
        "assertTrue(collateralHeld(loanId) || lendersFullySettled(loanId),",
        "    \"collateral released before settlement\");",
    ],
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": [
        "// INVARIANT: credited output must equal the measured balance delta.",
        "assertEq(credited, actual, \"credited != actual received\");",
    ],
    "ORACLE_DECIMAL_NORMALIZATION": [
        "// INVARIANT: the borrow limit must use a decimal-normalized price.",
        "assertLe(protocolMax, safeMax,",
        "    \"protocol over-credits collateral value via a mis-scaled (non-normalized) price\");",
        "// If the bug is present, protocolMax >> safeMax; an attacker over-borrows:",
        "// vm.prank(borrower); target.borrow(protocolMax); // borrows beyond safe value",
    ],
    "CROSS_CHAIN_SUPPLY_CONSERVATION": [
        "// INVARIANT: a cross-chain message must mint at most once (idempotent),",
        "//   so destination minted supply is conserved against source locked/burned.",
        "assertEq(supplyAfter - supplyBefore, amount,",
        "    \"replaying one message minted more than once (supply not conserved)\");",
        "// assertTrue(target.processed(msgId), \"message id must be marked consumed\");",
    ],
    "ACCESS_CONTROLLED_VALUE_MOVEMENT": [
        "// This candidate is expected to be KILLED: only a trusted role can move value.",
        "// The expectRevert above documents that an unprivileged caller cannot.",
    ],
}


def action_sequence(family: str) -> list:
    return list(_ACTIONS.get(family, ["// TODO: drive the entry function with attacker inputs."]))


def assertion_lines(family: str) -> list:
    return list(_ASSERTS.get(family, ["// TODO: assert the broken invariant fails here."]))
