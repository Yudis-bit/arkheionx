# Arkheionx Defensive Test Plan

This generated plan turns Arkheionx readiness findings into defensive local test ideas.

## Important Notice

- Generated plans are starter scaffolds for authorized local repositories; human review required.
- They are not a formal audit, not formal verification, and not proof of safety.
- Replace TODO placeholders with project-specific contracts, handlers, and assertions.
- Use local mocks or test deployments only; do not wire production credentials or deployed systems.

## Source Summary

- Source report root: `examples/amm-lending-hybrid-fixture`
- Source report version: `1.8.0`
- Protocol type: `amm`
- Readiness score: `38`
- Score band: `Not audit-ready`
- Mapped findings: `13`

## Rule-Family Plan

### amm

- Findings: `ARK-AMM-001, ARK-AMM-003, ARK-AMM-004, ARK-AMM-005`
- Suggested tests:
  - Assert swaps preserve the documented constant-product or stableswap invariant within fee and rounding bounds.
  - Test repeated swaps across small and large reserve states.
  - Document expected invariant tolerance.
  - Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.
  - Test reserve-price movement bounds.
  - Test TWAP or delay assumptions if used.
  - Document whether other accounting paths rely on spot reserve price.
  - Move reserves in a local pool test and assert dependent protocol decisions respect documented price bounds or TWAP assumptions.
  - Test actual received amount accounting with balanceBefore/balanceAfter pattern.
  - Simulate fee-on-transfer behavior with a local mock if supported.
- Invariant candidates:
  - Swaps and liquidity operations preserve documented AMM accounting within expected fee and rounding bounds.
  - Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.
  - Reserve-based price consumers respect documented bounds and delay assumptions.
  - Pool accounting uses actual received token amounts or explicitly rejects unsupported tokens.
  - Swap execution respects user-provided output bounds and documented deadline policy.

### lending

- Findings: `ARK-LEND-001, ARK-LEND-002, ARK-LEND-005, ARK-LEND-004`
- Suggested tests:
  - Assert solvent positions remain solvent after deposit, borrow, repay, and withdraw flows.
  - Test debt cannot exceed documented collateral constraints.
  - Test unsafe withdrawals are rejected or explicitly documented.
  - Assert debt cannot exceed documented collateral constraints and collateral withdrawals cannot make a position unsafe unless intended and tested.
  - Test just-above-threshold positions cannot be liquidated.
  - Test just-below-threshold positions can be liquidated according to policy.
  - Assert liquidation bonus and close factor stay within documented bounds.
  - Test a position just above threshold cannot be liquidated and a position just below threshold can be liquidated within documented bonus bounds.
  - Test borrow cannot exceed available liquidity.
  - Test repay updates cash, debt, and reserves consistently.
- Invariant candidates:
  - Collateral value and debt remain inside documented solvency constraints after allowed user actions.
  - Liquidation eligibility changes only at documented threshold boundaries.
  - Cash, total borrows, total reserves, and utilization remain internally consistent.
  - Borrowing and liquidation decisions only use oracle data that satisfies documented validity policy.

### oracle

- Findings: `ARK-ORC-002, ARK-ORC-001, ARK-ORC-003, ARK-ORC-005`
- Suggested tests:
  - Test decimals normalization across expected feed decimals.
  - Test zero, negative, or invalid oracle answers if applicable.
  - Assert normalized price units match accounting units.
  - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
  - Reject stale oracle rounds or document fallback behavior.
  - Test updatedAt or heartbeat boundaries.
  - Test borrow, liquidation, vault, or reward flows when oracle data is stale.
  - Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.
  - Test spot-price movement bounds.
  - Test TWAP or delay assumptions when used.
- Invariant candidates:
  - Normalized oracle values remain within documented unit and decimal assumptions.
  - Accounting decisions only use oracle data that satisfies documented freshness policy.
  - Price-dependent accounting does not rely on an undocumented instantaneous reserve ratio.
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

### ARK-AMM-001 - AMM invariant assumptions not covered by tests

- Rule family: `amm`
- Priority: `High readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyHybridMarket.sol in `getReserves`: Solidity function shape matches this readiness finding.
- Suggested tests:
  - Assert swaps preserve the documented constant-product or stableswap invariant within fee and rounding bounds.
  - Test repeated swaps across small and large reserve states.
  - Document expected invariant tolerance.
  - Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.
- Invariant candidates:
  - Swaps and liquidity operations preserve documented AMM accounting within expected fee and rounding bounds.
  - Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.
- Project bindings to fill in:
  - AMM pool
  - Token0 and token1 mocks
  - Swap handler
- Manual review notes:
  - Review exact AMM curve before choosing assertion tolerance.

### ARK-AMM-003 - Spot-price or reserve-price dependency without manipulation-resistance tests

- Rule family: `amm`
- Priority: `High readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyHybridMarket.sol in `getReserves`: Solidity function shape matches this readiness finding.
- Suggested tests:
  - Test reserve-price movement bounds.
  - Test TWAP or delay assumptions if used.
  - Document whether other accounting paths rely on spot reserve price.
  - Move reserves in a local pool test and assert dependent protocol decisions respect documented price bounds or TWAP assumptions.
- Invariant candidates:
  - Reserve-based price consumers respect documented bounds and delay assumptions.
- Project bindings to fill in:
  - AMM price function
  - Price consumer
- Manual review notes:
  - Review whether price output is advisory or used for critical accounting.

### ARK-AMM-004 - Fee-on-transfer or non-standard token assumptions not documented

- Rule family: `amm`
- Priority: `Medium readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyHybridMarket.sol in `getReserves`: Solidity function shape matches this readiness finding.
- Suggested tests:
  - Test actual received amount accounting with balanceBefore/balanceAfter pattern.
  - Simulate fee-on-transfer behavior with a local mock if supported.
  - Document unsupported token types if not handled.
  - Use a local fee-on-transfer token mock or document that such tokens are unsupported and guarded by configuration.
- Invariant candidates:
  - Pool accounting uses actual received token amounts or explicitly rejects unsupported tokens.
- Project bindings to fill in:
  - Transfer path
  - Token mock with configurable received amount
- Manual review notes:
  - Review token support policy before adding mocks.

### ARK-AMM-005 - Slippage/min-output constraints missing or unclear

- Rule family: `amm`
- Priority: `Medium readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyHybridMarket.sol in `getReserves`: Solidity function shape matches this readiness finding.
- Suggested tests:
  - Test minOut enforcement.
  - Test stale quote or deadline behavior if supported.
  - Assert user-provided slippage bounds are respected.
  - Assert swaps revert or follow documented policy when amountOut falls below a user-provided bound or quote is stale.
- Invariant candidates:
  - Swap execution respects user-provided output bounds and documented deadline policy.
- Project bindings to fill in:
  - Swap function
  - Slippage or deadline inputs
- Manual review notes:
  - Review whether slippage is enforced by a router outside this repository.

### ARK-LEND-001 - Collateral/debt solvency invariant not covered by tests

- Rule family: `lending`
- Priority: `Medium readiness gap`
- Confidence: `medium`
- Source evidence summary: src/ToyHybridMarket.sol in `depositCollateral`: Solidity function contains external value-flow call evidence.
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
- Source evidence summary: src/ToyHybridMarket.sol in `depositCollateral`: Solidity function contains external value-flow call evidence.
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

### ARK-LEND-005 - Reserve/cash accounting assumptions not covered

- Rule family: `lending`
- Priority: `Medium readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyHybridMarket.sol in `depositCollateral`: Solidity function contains external value-flow call evidence.
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
- Source evidence summary: src/ToyHybridMarket.sol: Keyword signal matched this readiness finding.
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

### ARK-ORC-002 - Oracle decimals or normalization not covered by tests

- Rule family: `oracle`
- Priority: `Low readiness gap`
- Confidence: `low`
- Source evidence summary: : No semantic-lite oracle test coverage terms were detected.
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
- Priority: `Low readiness gap`
- Confidence: `low`
- Source evidence summary: : No semantic-lite oracle test coverage terms were detected.
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

### ARK-ORC-003 - Spot or reserve-based pricing without manipulation-resistance tests

- Rule family: `oracle`
- Priority: `Low readiness gap`
- Confidence: `low`
- Source evidence summary: : No semantic-lite oracle test coverage terms were detected.
- Suggested tests:
  - Test spot-price movement bounds.
  - Test TWAP or delay assumptions when used.
  - Document reserve-price dependency and expected safeguards.
  - Use a local pool mock to move reserves or price and assert protocol actions respect documented bounds.
- Invariant candidates:
  - Price-dependent accounting does not rely on an undocumented instantaneous reserve ratio.
- Project bindings to fill in:
  - AMM or price source mock
  - Price consumer
- Manual review notes:
  - Review whether price source is advisory or authoritative.

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Rule family: `oracle`
- Priority: `Low readiness gap`
- Confidence: `low`
- Source evidence summary: : No semantic-lite oracle test coverage terms were detected.
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

### ARK-LEND-004 - Oracle-dependent borrowing/liquidation without stale-price tests

- Rule family: `lending`
- Priority: `Low readiness gap`
- Confidence: `low`
- Source evidence summary: : No semantic-lite oracle test coverage terms were detected.
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

## Foundry Skeleton

- Suggested output: `examples/reports/ArkheionxHybridInvariants.t.sol`
- Contract name: `ArkheionxHybridInvariants`
- Skeleton functions:
  - `invariant_ammAccountingPreservesDocumentedInvariant`
  - `invariant_reservePriceConsumersRespectBounds`
  - `invariant_poolUsesActualReceivedAmounts`
  - `invariant_swapsRespectUserOutputBounds`
  - `invariant_collateralDebtSolvencyHolds`
  - `invariant_liquidationBoundaryMatchesPolicy`
  - `invariant_lendingCashAndDebtAccountingConsistent`
  - `invariant_coreAccountingRelationshipsHold`
  - `invariant_privilegedActionsRespectDocumentedAssumptions`
  - `invariant_oracleNormalizationMatchesAccountingUnits`
  - `invariant_oracleFreshnessPolicyIsRespected`
  - `invariant_reservePriceDependencyIsBounded`
  - `invariant_invalidPricesDoNotDriveCriticalAccounting`
  - `invariant_lendingOracleValidityPolicyIsRespected`

## What To Do Next

1. Wire TODO bindings to local project contracts and mocks.
2. Replace placeholder assertions with project-specific properties.
3. Run the project test suite locally.
4. Re-run Arkheionx and compare the readiness report or baseline.

## Limitations

- This plan is generated from heuristic readiness findings.
- Manual review is required before relying on any generated property.
- A formal smart contract audit remains recommended before handling real user funds.
