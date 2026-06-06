# Assertion Standard

A PoC's value comes from its assertions, not its `console.log` output.
Logs explain; assertions prove. This document lists the assertion
families required by the archive and which categories require which.

---

## Why logs are insufficient

`console.log("attacker drained 1278 ETH")` is a claim. The same line
will print whether the exploit succeeded, partially succeeded, or
emitted a number that looks plausible but is wrong. A maintainer
re-reading a log a year later cannot distinguish "the PoC works" from
"the PoC compiled and didn't revert".

`assertGt(attackerBalanceAfter, attackerBalanceBefore + EXPECTED_PROFIT,
"attacker did not net the expected profit")` is a check that fails the
test if reality has drifted. That is the only artifact worth carrying
forward.

Every PoC must end with at least one assertion in the **profit /
success** family and at least one in the **victim impact** family. The
specific assertions required by category are listed below.

---

## Assertion families

### F1. Attacker profit assertion

The attacker's own balance increased by an amount consistent with the
incident, in a stable accounting unit (the "profit token", usually ETH,
WETH, USDC, or the protocol's native value asset).

```solidity
assertGt(
    profitToken.balanceOf(attacker) - attackerBalanceBefore,
    EXPECTED_PROFIT_LOWER_BOUND,
    "attacker profit below expected"
);
```

Required for any incident where the attacker took value.

### F2. Victim loss assertion

The victim contract / pool / vault holds less of the affected asset
than it did pre-attack, by an amount consistent with the incident.

```solidity
assertLt(
    asset.balanceOf(victim),
    victimBalanceBefore - EXPECTED_LOSS_LOWER_BOUND,
    "victim loss below expected"
);
```

Required for any incident with on-chain value movement.

### F3. Invariant break assertion

A protocol-defined invariant is observably violated post-attack.
Examples: `totalSupply` does not equal sum of holder balances, AMM
constant-product `k` decreased without a fee, vault `totalAssets`
exceeds sum of strategy balances, sum of debts exceeds sum of
collateral.

```solidity
assertLt(post_k, pre_k, "AMM invariant decreased without fee accrual");
```

Required for AMM-invariant, vault-strategy, and bad-debt incidents.

### F4. Unauthorized state transition assertion

A state variable that should only change under authorized code paths
has changed.

```solidity
assertEq(target.owner(), attacker, "owner not seized");
```

Required for access-control and initialization incidents.

### F5. Oracle deviation assertion

The price the protocol read at the moment of the exploit differs from
a reference price (a TWAP, a signed feed, a sister pool) by at least
the manipulation amount the attack relied on.

```solidity
assertGt(
    _abs(reportedPrice - referencePrice),
    EXPECTED_DEVIATION_BPS * referencePrice / 10_000,
    "oracle deviation below threshold"
);
```

Required for oracle-manipulation, flash-loan-price-manipulation,
read-only-reentrancy.

### F6. Debt / accounting mismatch assertion

The protocol's internal accounting and the actual token reality differ.

```solidity
assertNotEq(
    pool.internalBalance(token),
    IERC20(token).balanceOf(address(pool)),
    "internal vs real balance not diverged"
);
```

Required for accounting-mismatch, fee-on-transfer, share-price, and
donation-inflation incidents.

### F7. Ownership / control assertion

Specifically: a privileged role has been transferred to the attacker.

```solidity
assertEq(target.admin(), attacker, "admin not seized");
```

Required for governance, access-control, init, and proxy-upgrade
incidents.

### F8. Liquidation result assertion

A liquidation either (a) executed against a position that was healthy
at fair prices, or (b) failed when it should have executed.

```solidity
assertGt(
    liquidatorProfit,
    0,
    "liquidator did not extract value from healthy position"
);
```

Required for liquidation-logic-flaw incidents.

### F9. Share price manipulation assertion

The vault's `pricePerShare` (or equivalent) moved between two attacker
operations by at least the targeted delta.

```solidity
assertLt(
    sharePriceMid,
    sharePricePre - TARGET_DELTA,
    "share price did not collapse"
);
assertGt(
    sharePricePost,
    sharePriceMid + TARGET_DELTA,
    "share price did not recover"
);
```

Required for share-price-manipulation and donation-inflation incidents.

---

## Required families per category

| Category                              | Required assertion families      |
| ------------------------------------- | -------------------------------- |
| oracle-manipulation                   | F1, F2, F5                       |
| flash-loan-price-manipulation         | F1, F2, F5                       |
| reentrancy                            | F1, F2                           |
| read-only-reentrancy                  | F1, F5                           |
| access-control-failure                | F4 or F7, plus F1 if value moved |
| arithmetic-precision-rounding         | F1 or F3                         |
| accounting-mismatch                   | F6, plus F1 if value moved       |
| share-price-manipulation              | F1, F9                           |
| donation-inflation                    | F1, F9, F6                       |
| governance-attack                     | F7, plus F1 if treasury drained  |
| signature-permit-misuse               | F4 or F1                         |
| bridge-validation-failure             | F1, F2                           |
| liquidation-logic-flaw                | F8, plus F1                      |
| vault-strategy-accounting-flaw        | F3, F6                           |
| amm-invariant-manipulation            | F3, F1                           |
| fee-on-transfer-rebasing-assumption   | F6, F1                           |
| callback-misuse                       | F4 or F1                         |
| initialization-bug                    | F4, F7                           |
| proxy-upgradeability-issue            | F4, F7                           |
| unsafe-external-call                  | F4 or F1                         |
| bad-debt-creation                     | F3                               |
| invariant-bypass                      | F3, F4                           |
| economic-design-flaw                  | F1                               |

A PoC missing a required family is at most
`deterministic-likely-but-unverified`. A PoC with all required families
asserted and passing on the declared fork is a candidate for
`deterministic-confirmed` after a verification report.

---

## Assertion hygiene

- **Bound, don't equal.** Profit / loss numbers drift between block
  state and library updates. Prefer `assertGt(profit, LOWER_BOUND)` to
  `assertEq(profit, EXACT)`.
- **Anchor to pre-state.** Take a snapshot before the exploit and
  assert against deltas, not absolute balances.
- **Name the failure.** Every assertion should have a message string
  describing what failed.
- **Don't assert side effects you didn't reproduce.** If your PoC does
  not touch a particular asset, do not assert its balance.
- **Prefer multiple narrow assertions over one wide one.** Each
  assertion should fail for one reason.

---

## Anti-patterns

These do not count as proof:

- `console.log` only.
- `vm.assertTrue(true)` placeholders.
- Assertions that are tautologically true given the setup.
- Asserting that a function reverted without asserting *what* it
  reverted with — for negative tests, use `vm.expectRevert(selector)`.
- `assertGt(profit, 0)` with no lower bound for incidents whose public
  loss figure is in the millions.

A PoC that satisfies the letter of the standard with cosmetic
assertions does not satisfy the spirit. Reviewers should reject
cosmetic assertions and ask for category-appropriate ones.
