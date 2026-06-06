# Arkheionx Defensive Test Plan

This generated plan turns Arkheionx readiness findings into defensive local test ideas.

## Important Notice

- Generated plans are starter scaffolds for authorized local repositories; human review required.
- They are not a formal audit, not formal verification, and not proof of safety.
- Replace TODO placeholders with project-specific contracts, handlers, and assertions.
- Use local mocks or test deployments only; do not wire production credentials or deployed systems.

## Source Summary

- Source report root: `examples/lending-fixture`
- Source report version: `2.0.1`
- Protocol type: `lending`
- Readiness score: `59`
- Score band: `Early readiness`
- Mapped findings: `10`

## Rule-Family Plan

### access-control

- Findings: `ARK-ACC-001`
- Suggested tests:
  - Test unauthorized callers cannot change critical parameters.
  - Test authorized role can perform expected setter actions.
  - Document role ownership and transfer procedure.
  - For every privileged function, assert an unprivileged caller reverts and the documented role succeeds only within intended bounds.
- Invariant candidates:
  - Unauthorized users cannot mutate privileged configuration.

### lending

- Findings: `ARK-LEND-004, ARK-LEND-001, ARK-LEND-002, ARK-LEND-003, ARK-LEND-005`
- Suggested tests:
  - Test stale oracle rejection for borrow and liquidation paths.
  - Test decimals normalization for collateral valuation.
  - Test price shock boundaries around health-factor transitions.
  - Mock stale, invalid, and sharply moved prices and assert borrow/liquidation behavior follows documented policy.
  - Assert solvent positions remain solvent after deposit, borrow, repay, and withdraw flows.
  - Test debt cannot exceed documented collateral constraints.
  - Test unsafe withdrawals are rejected or explicitly documented.
  - Assert debt cannot exceed documented collateral constraints and collateral withdrawals cannot make a position unsafe unless intended and tested.
  - Test just-above-threshold positions cannot be liquidated.
  - Test just-below-threshold positions can be liquidated according to policy.
- Invariant candidates:
  - Borrowing and liquidation decisions only use oracle data that satisfies documented validity policy.
  - Collateral value and debt remain inside documented solvency constraints after allowed user actions.
  - Liquidation eligibility changes only at documented threshold boundaries.
  - Interest and borrow indexes move according to documented rate policy and do not drift unexpectedly.
  - Cash, total borrows, total reserves, and utilization remain internally consistent.

### oracle

- Findings: `ARK-ORC-002, ARK-ORC-001, ARK-ORC-005`
- Suggested tests:
  - Test decimals normalization across expected feed decimals.
  - Test zero, negative, or invalid oracle answers if applicable.
  - Assert normalized price units match accounting units.
  - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
  - Reject stale oracle rounds or document fallback behavior.
  - Test updatedAt or heartbeat boundaries.
  - Test borrow, liquidation, vault, or reward flows when oracle data is stale.
  - Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.
  - Test documented price bounds.
  - Test invalid answer fallback behavior.
- Invariant candidates:
  - Normalized oracle values remain within documented unit and decimal assumptions.
  - Accounting decisions only use oracle data that satisfies documented freshness policy.
  - Invalid or out-of-bound price inputs cannot silently drive critical accounting decisions.

### testing

- Findings: `ARK-TST-002`
- Suggested tests:
  - Add a stateful invariant suite for the core protocol lifecycle.
  - Add handler actions for normal user flows and documented edge cases.
  - Add conservation properties for assets, shares, rewards, debt, or reserves as applicable.
  - Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
- Invariant candidates:
  - Core accounting relationships hold after any allowed user action.
  - Privileged actions cannot silently bypass documented accounting assumptions.

## Finding Details

### ARK-ORC-002 - Oracle decimals or normalization not covered by tests

- Rule family: `oracle`
- Priority: `High readiness gap`
- Confidence: `medium`
- Source evidence summary: src/ToyLendingMarket.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Suggested tests:
  - Test decimals normalization across expected feed decimals.
  - Test zero, negative, or invalid oracle answers if applicable.
  - Assert normalized price units match accounting units.
  - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
- Invariant candidates:
  - Normalized oracle values remain within documented unit and decimal assumptions.
- Project bindings to fill in:
  - Oracle adapter
  - Accounting consumer
- Manual review notes:
  - Review whether feed decimals are fixed at deployment.

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

- Rule family: `oracle`
- Priority: `High readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyLendingMarket.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Suggested tests:
  - Reject stale oracle rounds or document fallback behavior.
  - Test updatedAt or heartbeat boundaries.
  - Test borrow, liquidation, vault, or reward flows when oracle data is stale.
  - Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.
- Invariant candidates:
  - Accounting decisions only use oracle data that satisfies documented freshness policy.
- Project bindings to fill in:
  - Oracle adapter or mock feed
  - Consumer contract
- Manual review notes:
  - Check whether freshness validation is implemented in an imported adapter.

### ARK-LEND-004 - Oracle-dependent borrowing/liquidation without stale-price tests

- Rule family: `lending`
- Priority: `High readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyLendingMarket.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Suggested tests:
  - Test stale oracle rejection for borrow and liquidation paths.
  - Test decimals normalization for collateral valuation.
  - Test price shock boundaries around health-factor transitions.
  - Mock stale, invalid, and sharply moved prices and assert borrow/liquidation behavior follows documented policy.
- Invariant candidates:
  - Borrowing and liquidation decisions only use oracle data that satisfies documented validity policy.
- Project bindings to fill in:
  - Lending market
  - Oracle mock
  - Health-factor logic
- Manual review notes:
  - Review fallback behavior and collateral-specific feed assumptions.

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Rule family: `oracle`
- Priority: `Medium readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyLendingMarket.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Suggested tests:
  - Test documented price bounds.
  - Test invalid answer fallback behavior.
  - Add documentation for price shock and fallback assumptions.
  - Add documentation plus local tests showing fallback and out-of-bounds price behavior.
- Invariant candidates:
  - Invalid or out-of-bound price inputs cannot silently drive critical accounting decisions.
- Project bindings to fill in:
  - Oracle adapter
  - Consumer path
- Manual review notes:
  - Review whether fallback behavior is intentionally unavailable.

### ARK-ACC-001 - Privileged setters without role-boundary tests

- Rule family: `access-control`
- Priority: `Medium readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyLendingMarket.sol in `setGuardian`: Solidity function contains access-control or lifecycle modifier evidence.
- Suggested tests:
  - Test unauthorized callers cannot change critical parameters.
  - Test authorized role can perform expected setter actions.
  - Document role ownership and transfer procedure.
  - For every privileged function, assert an unprivileged caller reverts and the documented role succeeds only within intended bounds.
- Invariant candidates:
  - Unauthorized users cannot mutate privileged configuration.
- Project bindings to fill in:
  - Privileged setter functions
  - Owner or role accounts
- Manual review notes:
  - Review role inheritance and deployment ownership transfer.

### ARK-LEND-001 - Collateral/debt solvency invariant not covered by tests

- Rule family: `lending`
- Priority: `Medium readiness gap`
- Confidence: `medium`
- Source evidence summary: src/ToyLendingMarket.sol in `depositCollateral`: Solidity function contains external value-flow call evidence.
- Suggested tests:
  - Assert solvent positions remain solvent after deposit, borrow, repay, and withdraw flows.
  - Test debt cannot exceed documented collateral constraints.
  - Test unsafe withdrawals are rejected or explicitly documented.
  - Assert debt cannot exceed documented collateral constraints and collateral withdrawals cannot make a position unsafe unless intended and tested.
- Invariant candidates:
  - Collateral value and debt remain inside documented solvency constraints after allowed user actions.
- Project bindings to fill in:
  - Lending market
  - Collateral token mock
  - Borrow token mock
  - Oracle mock
- Manual review notes:
  - Review collateral factor and price-unit assumptions.

### ARK-LEND-002 - Liquidation boundary tests missing

- Rule family: `lending`
- Priority: `Medium readiness gap`
- Confidence: `medium`
- Source evidence summary: src/ToyLendingMarket.sol in `depositCollateral`: Solidity function contains external value-flow call evidence.
- Suggested tests:
  - Test just-above-threshold positions cannot be liquidated.
  - Test just-below-threshold positions can be liquidated according to policy.
  - Assert liquidation bonus and close factor stay within documented bounds.
  - Test a position just above threshold cannot be liquidated and a position just below threshold can be liquidated within documented bonus bounds.
- Invariant candidates:
  - Liquidation eligibility changes only at documented threshold boundaries.
- Project bindings to fill in:
  - Liquidation function
  - Health factor calculation
  - Price mock
- Manual review notes:
  - Review rounding around exact threshold values.

### ARK-LEND-003 - Interest/index accounting not covered by rounding and time-step tests

- Rule family: `lending`
- Priority: `Medium readiness gap`
- Confidence: `medium`
- Source evidence summary: src/ToyLendingMarket.sol in `depositCollateral`: Solidity function contains external value-flow call evidence.
- Suggested tests:
  - Test interest or borrow index monotonicity.
  - Cover small balances and repeated accrual.
  - Test borrow and repay before and after accrual.
  - Advance local time across multiple accrual steps and assert borrow indexes and balances remain monotonic and bounded by documented rounding.
- Invariant candidates:
  - Interest and borrow indexes move according to documented rate policy and do not drift unexpectedly.
- Project bindings to fill in:
  - Interest accrual function
  - Borrow index state
  - Debt state
- Manual review notes:
  - Review whether index math is inherited from a shared library.

### ARK-LEND-005 - Reserve/cash accounting assumptions not covered

- Rule family: `lending`
- Priority: `Medium readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyLendingMarket.sol in `depositCollateral`: Solidity function contains external value-flow call evidence.
- Suggested tests:
  - Test borrow cannot exceed available liquidity.
  - Test repay updates cash, debt, and reserves consistently.
  - Assert reserves cannot be withdrawn beyond documented constraints.
  - Assert borrow reverts above available liquidity and repay updates cash, debt, reserves, and utilization consistently.
- Invariant candidates:
  - Cash, total borrows, total reserves, and utilization remain internally consistent.
- Project bindings to fill in:
  - Market cash state
  - Borrow/repay functions
  - Reserve accounting
- Manual review notes:
  - Review reserve factor and protocol fee accounting.

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Rule family: `testing`
- Priority: `Low readiness gap`
- Confidence: `low`
- Source evidence summary: src/ToyLendingMarket.sol: Keyword signal matched this readiness finding.
- Suggested tests:
  - Add a stateful invariant suite for the core protocol lifecycle.
  - Add handler actions for normal user flows and documented edge cases.
  - Add conservation properties for assets, shares, rewards, debt, or reserves as applicable.
  - Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
- Invariant candidates:
  - Core accounting relationships hold after any allowed user action.
  - Privileged actions cannot silently bypass documented accounting assumptions.
- Project bindings to fill in:
  - Target contracts
  - Allowed action handler
  - Local mocks for assets and oracle inputs
- Manual review notes:
  - Review whether the protocol uses another property-testing framework outside Foundry.

## Foundry Skeleton

- Suggested output: `not requested`
- Contract name: `ArkheionxLendingInvariants`
- Skeleton functions:
  - `invariant_oracleNormalizationMatchesAccountingUnits`
  - `invariant_oracleFreshnessPolicyIsRespected`
  - `invariant_lendingOracleValidityPolicyIsRespected`
  - `invariant_invalidPricesDoNotDriveCriticalAccounting`
  - `invariant_unauthorizedUsersCannotChangeCriticalParams`
  - `invariant_collateralDebtSolvencyHolds`
  - `invariant_liquidationBoundaryMatchesPolicy`
  - `invariant_interestIndexesAreMonotonic`
  - `invariant_lendingCashAndDebtAccountingConsistent`
  - `invariant_coreAccountingRelationshipsHold`
  - `invariant_privilegedActionsRespectDocumentedAssumptions`

## What To Do Next

1. Wire TODO bindings to local project contracts and mocks.
2. Replace placeholder assertions with project-specific properties.
3. Run the project test suite locally.
4. Re-run Arkheionx and compare the readiness report or baseline.

## Limitations

- This plan is generated from heuristic readiness findings.
- Manual review is required before relying on any generated property.
- A formal smart contract audit remains recommended before handling real user funds.
