# Arkheionx Defensive Test Plan

This generated plan turns Arkheionx readiness findings into defensive local test ideas.

## Important Notice

- Generated plans are starter scaffolds for authorized local repositories; human review required.
- They are not a formal audit, not formal verification, and not proof of safety.
- Replace TODO placeholders with project-specific contracts, handlers, and assertions.
- Use local mocks or test deployments only; do not wire production credentials or deployed systems.

## Source Summary

- Source report root: `examples/amm-fixture`
- Source report version: `1.5.0`
- Protocol type: `amm`
- Readiness score: `43`
- Score band: `Early readiness`
- Mapped findings: `12`

## Rule-Family Plan

### amm

- Findings: `ARK-AMM-002, ARK-AMM-003, ARK-AMM-001, ARK-AMM-004, ARK-AMM-005`
- Suggested tests:
  - Test first liquidity provider behavior.
  - Test proportional minting and proportional withdrawal.
  - Cover rounding and dust handling during mint/burn.
  - Test first liquidity, repeated add/remove liquidity, and tiny-liquidity burn cases to verify LP shares remain proportional.
  - Test reserve-price movement bounds.
  - Test TWAP or delay assumptions if used.
  - Document whether other accounting paths rely on spot reserve price.
  - Move reserves in a local pool test and assert dependent protocol decisions respect documented price bounds or TWAP assumptions.
  - Assert swaps preserve the documented constant-product or stableswap invariant within fee and rounding bounds.
  - Test repeated swaps across small and large reserve states.
- Invariant candidates:
  - LP share supply tracks pool ownership within documented rounding.
  - Reserve-based price consumers respect documented bounds and delay assumptions.
  - Swaps and liquidity operations preserve documented AMM accounting within expected fee and rounding bounds.
  - Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.
  - Pool accounting uses actual received token amounts or explicitly rejects unsupported tokens.
  - Swap execution respects user-provided output bounds and documented deadline policy.

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

### reentrancy-value-flow

- Findings: `ARK-REENT-001, ARK-REENT-004`
- Suggested tests:
  - Add a benign callback-capable receiver stub.
  - Assert state updates happen before external value transfer where required.
  - Test withdraw, claim, refund, or swap flows for accounting consistency.
  - Review state update order and add local malicious-receiver tests where callbacks are possible.
  - Document checks-effects-interactions or guard assumptions.
  - Test state before and after external calls.
  - Assert failure paths preserve accounting state.
  - Pair ordering documentation with a local receiver test that exercises the documented boundary.
- Invariant candidates:
  - External-call flows cannot observe or preserve inconsistent accounting state.
  - External call ordering follows documented state-transition policy.

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

### ARK-AMM-002 - LP share accounting without mint/burn boundary tests

- Rule family: `amm`
- Priority: `High readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyAMMPool.sol in `getReserves`: Solidity function shape matches this readiness finding.
- Suggested tests:
  - Test first liquidity provider behavior.
  - Test proportional minting and proportional withdrawal.
  - Cover rounding and dust handling during mint/burn.
  - Test first liquidity, repeated add/remove liquidity, and tiny-liquidity burn cases to verify LP shares remain proportional.
- Invariant candidates:
  - LP share supply tracks pool ownership within documented rounding.
- Project bindings to fill in:
  - AMM pool
  - LP share accounting
  - Liquidity actors
- Manual review notes:
  - Review minimum-liquidity and initial-share policy.

### ARK-AMM-003 - Spot-price or reserve-price dependency without manipulation-resistance tests

- Rule family: `amm`
- Priority: `High readiness gap`
- Confidence: `high`
- Source evidence summary: src/ToyAMMPool.sol in `getReserves`: Solidity function shape matches this readiness finding.
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

### ARK-REENT-001 - Value flow with external calls needs reentrancy review

- Rule family: `reentrancy-value-flow`
- Priority: `Medium readiness gap`
- Confidence: `medium`
- Source evidence summary: src/ToyAMMPool.sol in `addLiquidity`: Solidity function contains external value-flow call evidence.
- Suggested tests:
  - Add a benign callback-capable receiver stub.
  - Assert state updates happen before external value transfer where required.
  - Test withdraw, claim, refund, or swap flows for accounting consistency.
  - Review state update order and add local malicious-receiver tests where callbacks are possible.
- Invariant candidates:
  - External-call flows cannot observe or preserve inconsistent accounting state.
- Project bindings to fill in:
  - External-call flow
  - Local receiver stub
- Manual review notes:
  - Review inherited guards and pull-payment patterns.

### ARK-AMM-001 - AMM invariant assumptions not covered by tests

- Rule family: `amm`
- Priority: `Medium readiness gap`
- Confidence: `medium`
- Source evidence summary: src/ToyAMMPool.sol in `getReserves`: Solidity function shape matches this readiness finding.
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

### ARK-AMM-004 - Fee-on-transfer or non-standard token assumptions not documented

- Rule family: `amm`
- Priority: `Medium readiness gap`
- Confidence: `medium`
- Source evidence summary: src/ToyAMMPool.sol in `getReserves`: Solidity function shape matches this readiness finding.
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
- Confidence: `medium`
- Source evidence summary: src/ToyAMMPool.sol in `getReserves`: Solidity function shape matches this readiness finding.
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

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Rule family: `testing`
- Priority: `Low readiness gap`
- Confidence: `low`
- Source evidence summary: src/ToyAMMPool.sol: Keyword signal matched this readiness finding.
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

### ARK-REENT-004 - External call path without documented ordering assumptions

- Rule family: `reentrancy-value-flow`
- Priority: `Low readiness gap`
- Confidence: `medium`
- Source evidence summary: src/ToyAMMPool.sol in `addLiquidity`: Solidity function contains external value-flow call evidence.
- Suggested tests:
  - Document checks-effects-interactions or guard assumptions.
  - Test state before and after external calls.
  - Assert failure paths preserve accounting state.
  - Pair ordering documentation with a local receiver test that exercises the documented boundary.
- Invariant candidates:
  - External call ordering follows documented state-transition policy.
- Project bindings to fill in:
  - External call path
  - Failure-mode stub
- Manual review notes:
  - Review code paths manually before deciding severity.

## Foundry Skeleton

- Suggested output: `examples/reports/ArkheionxAMMInvariants.t.sol`
- Contract name: `ArkheionxAMMInvariants`
- Skeleton functions:
  - `invariant_lpSharesTrackPoolOwnership`
  - `invariant_reservePriceConsumersRespectBounds`
  - `invariant_externalCallFlowsPreserveAccountingState`
  - `invariant_ammAccountingPreservesDocumentedInvariant`
  - `invariant_poolUsesActualReceivedAmounts`
  - `invariant_swapsRespectUserOutputBounds`
  - `invariant_coreAccountingRelationshipsHold`
  - `invariant_privilegedActionsRespectDocumentedAssumptions`
  - `invariant_oracleNormalizationMatchesAccountingUnits`
  - `invariant_oracleFreshnessPolicyIsRespected`
  - `invariant_reservePriceDependencyIsBounded`
  - `invariant_invalidPricesDoNotDriveCriticalAccounting`
  - `invariant_externalCallOrderingMatchesPolicy`

## What To Do Next

1. Wire TODO bindings to local project contracts and mocks.
2. Replace placeholder assertions with project-specific properties.
3. Run the project test suite locally.
4. Re-run Arkheionx and compare the readiness report or baseline.

## Limitations

- This plan is generated from heuristic readiness findings.
- Manual review is required before relying on any generated property.
- A formal smart contract audit remains recommended before handling real user funds.
