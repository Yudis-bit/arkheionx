# Lending Rule Pack

Arkheionx lending findings are defensive pre-audit readiness signals for authorized repositories. They are not formal audit findings, vulnerability confirmations, liquidation strategy, or bounty guidance.

Use this rule pack when a repository contains lending markets, collateral/debt accounting, borrowing, repayment, interest indexes, liquidation boundaries, or oracle-dependent health-factor logic.

## ARK-LEND-001 - Collateral/Debt Solvency Invariant Not Covered By Tests

Signals:
- `collateral`, `debt`, `borrow`, `repay`
- `healthFactor`, `LTV`, `loan-to-value`
- `liquidationThreshold`, `collateralFactor`

Why it matters:
Lending readiness depends on collateral value and debt state staying aligned through deposits, withdrawals, borrow, repay, and liquidation paths.

Suggested tests:
- Solvent positions remain solvent after repay/deposit.
- Debt cannot exceed documented collateral constraints.
- Collateral withdrawals cannot make a position unsafe unless intended and tested.
- Total debt/accounting consistency.

Calibration:
- High confidence requires Solidity-level lending evidence plus missing solvency invariant tests.
- Downgrade when collateral/debt invariant, borrow-limit, and unsafe-withdrawal tests are present.

## ARK-LEND-002 - Liquidation Boundary Tests Missing

Signals:
- `liquidate`, `liquidation`
- `liquidationBonus`, `closeFactor`, `seize`
- `healthFactor` or threshold logic

Why it matters:
Liquidation boundaries need precise testing around the exact point where positions move from safe to liquidatable.

Suggested tests:
- Just-above threshold cannot be liquidated.
- Just-below threshold can be liquidated.
- Liquidation bonus bounded.
- Partial liquidation math.
- No over-seizure beyond debt plus allowed bonus.

Calibration:
- High confidence requires liquidation evidence plus missing threshold boundary tests.
- Downgrade when just-above/just-below, close factor, bonus, and over-seizure tests are visible.

## ARK-LEND-003 - Interest/Index Accounting Not Covered By Rounding And Time-Step Tests

Signals:
- `interestIndex`, `borrowIndex`, `exchangeRate`
- `utilization`, `accrueInterest`, `ratePerSecond`
- `index`, `principal`, `scaledBalance`

Why it matters:
Interest and index accounting can drift under repeated accrual, small balances, rounding, and borrow/repay timing.

Suggested tests:
- Interest accrual monotonicity.
- Index rounding under small balances.
- Borrow/repay before and after accrual.
- Repeated accrual does not create accounting drift.

Calibration:
- Medium confidence when lending index terms appear without rounding/time-step tests.
- Downgrade when monotonicity, accrual, small-balance, and repeated-step tests are present.

## ARK-LEND-004 - Oracle-Dependent Borrowing/Liquidation Without Stale-Price Tests

Signals:
- `oracle`, `price`, `getPrice`, `latestRoundData`
- `healthFactor`, `collateralValue`
- borrow or liquidation paths using price data

Why it matters:
Borrow and liquidation decisions can depend on price freshness, normalization, and bounds.

Suggested tests:
- Stale oracle rejection.
- Decimals normalization.
- Price shock boundary.
- Liquidation after oracle update.
- Borrow blocked when price invalid.

Calibration:
- High confidence requires oracle-dependent lending evidence plus missing stale/freshness or price-shock tests.
- Downgrade when stale price, decimals, price shock, and invalid-price tests are present.

## ARK-LEND-005 - Reserve/Cash Accounting Assumptions Not Covered

Signals:
- `cash`, `reserves`, `totalBorrows`, `totalReserves`
- `liquidity`, `utilization`, `available liquidity`

Why it matters:
Cash and reserve accounting define whether a market can satisfy borrows, repayments, and reserve withdrawals consistently.

Suggested tests:
- Borrow cannot exceed available liquidity.
- Repay updates cash/debt consistently.
- Reserves cannot be withdrawn beyond documented constraints.
- Utilization stays bounded.

Calibration:
- Medium confidence when reserve/cash accounting appears without liquidity and reconciliation tests.
- Downgrade when cash/debt, utilization, reserve, and repay consistency tests are visible.

## ARK-LEND-006 - Liquidation/Access-Control Interaction Not Documented

Signals:
- `liquidator`, `keeper`, `owner`, `guardian`
- `pause`, `whitelist`
- liquidation role boundary terms

Why it matters:
Liquidation and emergency controls affect who can act during stressed market states and should be documented before external review.

Suggested tests:
- Unauthorized liquidator restrictions if applicable.
- Paused-market behavior.
- Liquidation cannot bypass documented role rules.
- Emergency controls documented.

Calibration:
- Low or medium confidence depending on role surface and missing documentation.
- Downgrade when role-boundary tests or clear liquidation role documentation are present.

## False-Positive Notes

Lending terms in docs, interfaces, or imported adapters may be noisy. Arkheionx uses semantic-lite function context where possible and downgrades weak keyword-only signals. Manual review remains required.

## Related Search Queries

```sh
python3 scripts/search_knowledge.py "collateral debt invariant"
python3 scripts/search_knowledge.py "liquidation boundary"
python3 scripts/search_knowledge.py "interest index"
python3 scripts/search_knowledge.py "lending oracle"
```

## Test Plan Generation

Lending findings map to local defensive test ideas in
`metadata/finding_test_plan_map.json`.

```sh
python3 scripts/generate_test_plan.py \
  --report examples/reports/lending-fixture-pre-audit-report.json \
  --output examples/reports/lending-fixture-test-plan.md \
  --foundry-output examples/reports/ArkheionxLendingInvariants.t.sol
```

Generated lending skeletons include TODOs for local lending markets, token
mocks, price mocks, borrower actors, liquidation boundaries, and accounting
properties.
