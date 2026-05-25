# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/vault-risk-fixture`
- Generated at: `2026-05-25T13:23:41+00:00`
- Protocol type: `vault`
- Protocol confidence: `manual`
- Files scanned: `5`
- Scanner version: `0.4.0`

| File class       | Count |
| ---------------- | ----- |
| Solidity sources | 1     |
| Solidity tests   | 2     |
| Docs             | 1     |
| Configs          | 1     |
| Workflows        | 0     |

## Disclaimer

This is an automated pre-audit readiness report. It is not a formal audit, does not prove the absence or presence of vulnerabilities, does not authorize live-target testing, and should only be used on repositories you own or are authorized to review. A formal audit is recommended before handling real user funds.

## Executive Summary

- Readiness score: **58/100**
- Score band: **Early readiness**
- Active readiness gaps: `9`
- Suppressed readiness gaps: `0`
- Top readiness gaps:
  - **ARK-ORC-001 (High readiness gap):** Oracle-dependent vault without stale-price or bounds tests - Add local mock price tests for stale rounds, decimals normalization, price bounds, and fallback behavior.
  - **ARK-VLT-001 (High readiness gap):** Vault accounting without invariant tests - Add Foundry invariants for share/accounting conservation across deposit, withdraw, donation, fee, and emergency scenarios.
  - **ARK-VLT-002 (High readiness gap):** ERC4626-like interface without preview function tests - Add tests that preview functions match actual state-changing outcomes within documented rounding bounds.
  - **ARK-VLT-003 (High readiness gap):** Shares/assets conversion without rounding tests - Add tests for rounding direction, small values, decimals mismatch, and conversion reversibility.
  - **ARK-VLT-004 (High readiness gap):** totalAssets external dependency without manipulation-resistance tests - Test totalAssets under donated assets, mocked strategy gain/loss, and mocked stale or bounded pricing where relevant.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
  - Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
  - Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
  - Add local mock strategy tests for gain, loss, debt, harvest, and migration accounting.

## Detected Protocol Shape

- Detected protocol type: `vault`
- Confidence: `manual`
- Protocol score signals: `{"amm": 0, "lending": 0, "oracle": 34, "staking": 0, "vault": 143}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                                | Score | Max | Notes                                                                                                                                                                                                             |
| --------------------------------------- | ----- | --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository Structure                    | 8     | 10  | Solidity vault-like sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                                                                     |
| Test Presence                           | 15    | 15  | Solidity tests detected.; Assert usage detected.; Foundry or Hardhat environment detected.; Deposit and withdraw/redeem test signals detected.; Mint or preview function test signals detected.                   |
| Vault Accounting Coverage               | 12    | 20  | Vault/ERC4626 share-accounting surface detected.; totalAssets test signal detected.; Shares/assets conversion test signal detected.                                                                               |
| Invariant Fuzz Readiness                | 2     | 20  | Edge-case test signal detected.                                                                                                                                                                                   |
| Oracle Pricing Readiness                | 5     | 10  | Oracle/pool pricing controls are documented or tested.; Oracle update role boundary signal detected.                                                                                                              |
| Strategy Withdrawal Lifecycle Readiness | 2     | 10  | Lifecycle operational boundary signal detected.                                                                                                                                                                   |
| Admin Operational Readiness             | 9     | 10  | Vault admin/operational surface is visible.; Role or unauthorized-call coverage signal detected.; Pause or emergency control signal detected.; Upgradeability is absent or initializer/upgrade terms are visible. |
| Documentation Readiness                 | 5     | 5   | README detected.; Vault assumptions or limitations are documented.; Role, treasury, owner, or deployment terms are documented.                                                                                    |

## Top Readiness Gaps

| ID          | Priority           | Category         | Title                                                                 |
| ----------- | ------------------ | ---------------- | --------------------------------------------------------------------- |
| ARK-ORC-001 | High readiness gap | oracle-pricing   | Oracle-dependent vault without stale-price or bounds tests            |
| ARK-VLT-001 | High readiness gap | vault-accounting | Vault accounting without invariant tests                              |
| ARK-VLT-002 | High readiness gap | vault-accounting | ERC4626-like interface without preview function tests                 |
| ARK-VLT-003 | High readiness gap | vault-accounting | Shares/assets conversion without rounding tests                       |
| ARK-VLT-004 | High readiness gap | vault-accounting | totalAssets external dependency without manipulation-resistance tests |

## Risk Signal Summary

### Vault Erc4626

- Detected signals: `asset(), assets, balanceOf, convertToAssets, convertToShares, deposit, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, previewDeposit, previewMint, previewRedeem, previewWithdraw, redeem, shares, totalAssets, totalSupply, withdraw`
- Files with signals: `2`
- Example files: `src/VaultRiskFixture.sol, test/VaultRiskFixture.t.sol`

### Vault Accounting

- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, deposit, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, previewDeposit, previewMint, previewRedeem, previewWithdraw, redeem, shares, strategy, totalAssets, totalSupply, withdraw`
- Files with signals: `2`
- Example files: `src/VaultRiskFixture.sol, test/VaultRiskFixture.t.sol`

### Vault Accounting Risk

- Detected signals: `convertToAssets, convertToShares, depositFee, feeRecipient, managementFee, performanceFee, previewDeposit, previewMint, previewRedeem, previewWithdraw, totalAssets, treasury, withdrawalFee`
- Files with signals: `2`
- Example files: `src/VaultRiskFixture.sol, test/VaultRiskFixture.t.sol`

### Vault Strategy

- Detected signals: `allocate, emergencyExit, gain, harvest, loss, profit, rebalance, report, strategy, totalDebt, withdrawFromStrategy`
- Files with signals: `1`
- Example files: `src/VaultRiskFixture.sol`

### Vault Pricing

- Detected signals: `getPrice, latestRoundData, priceFeed`
- Files with signals: `2`
- Example files: `src/VaultRiskFixture.sol, test/VaultRiskFixture.t.sol`

### Vault Withdrawal Liquidity

- Detected signals: `cancelWithdraw, claimWithdraw, cooldown, liquidityBuffer, pendingWithdraw, requestWithdraw, withdrawalQueue`
- Files with signals: `1`
- Example files: `src/VaultRiskFixture.sol`

### Vault Admin Ops

- Detected signals: `emergencyWithdraw, pause, rescue, setDepositLimit, setFee, setMaxLoss, setOracle, setSlippage, setStrategy, setTreasury, setWithdrawLimit, sweep, unpause`
- Files with signals: `1`
- Example files: `src/VaultRiskFixture.sol`

### Oracle

- Detected signals: `latestRoundData, priceFeed, setOracle`
- Files with signals: `2`
- Example files: `src/VaultRiskFixture.sol, test/VaultRiskFixture.t.sol`

### Access Control

- Detected signals: `emergencyWithdraw, onlyOwner, owner, pause, setFee, setOracle, setStrategy, setTreasury, unpause`
- Files with signals: `1`
- Example files: `src/VaultRiskFixture.sol`

### Reentrancy Value Flow

- Detected signals: `transfer(, transferFrom`
- Files with signals: `2`
- Example files: `src/VaultRiskFixture.sol, test/VaultRiskFixture.t.sol`

### Accounting Complexity

- Detected signals: `depositFee, managementFee, performanceFee, withdrawalFee`
- Files with signals: `1`
- Example files: `src/VaultRiskFixture.sol`

### Testing And Documentation

- Test Directory: `True`
- Foundry Tests: `True`
- Hardhat Tests: `False`
- Test File Count: `1`
- Invariant Tests: `False`
- Fuzz Tests: `False`
- Handler Contracts: `False`
- Assert Usage: `True`
- Assert Count: `5`
- Forge Std: `True`
- Echidna: `False`
- Slither: `False`
- Ci Workflow: `False`
- Edge Case Tests: `True`
- Test files: `test/VaultRiskFixture.t.sol`

## Vault Rule Pack Coverage

The v0.2.0 vault rule pack checks ERC4626-like share accounting, totalAssets assumptions, conversion rounding, fee logic, strategies, withdrawal lifecycle, oracle/pricing assumptions, admin controls, and pause/emergency behavior.

| Vault check          | Covered | Matched terms |
| -------------------- | ------- | ------------- |
| decimals rounding    | no      | -             |
| deposit              | yes     | deposit       |
| donation inflation   | no      | -             |
| emergency pause      | no      | -             |
| fee                  | no      | -             |
| fuzz                 | no      | -             |
| invariant            | no      | -             |
| mint                 | yes     | mint          |
| oracle pricing       | no      | -             |
| preview functions    | no      | -             |
| roundtrip            | no      | -             |
| share conversion     | yes     | shares        |
| strategy loss        | no      | -             |
| total assets         | yes     | totalAssets   |
| withdraw             | yes     | withdraw      |
| withdrawal lifecycle | no      | -             |

## Historical Exploit-Pattern Similarity

### Harvest/Yearn-style oracle or pool price readiness gap

- Confidence: `high`
- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, deposit, getPrice, latestRoundData, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, previewDeposit, previewMint, previewRedeem, previewWithdraw, priceFeed, redeem, setOracle, shares`
- Why it matters: Vault accounting that depends on oracle, pool, LP, or reserve pricing needs explicit tests for stale, spot, and manipulated local price assumptions.
- Failed assumption class: Price source remains representative during deposits, withdrawals, and share conversions.
- Broken invariant class: Share/accounting value cannot be moved by transient price state.
- Recommended defensive checks:
  - Document oracle freshness, bounds, and fallback behavior.
  - Test deposit, withdraw, and totalAssets under mocked stale and bounded prices.
  - Prefer TWAP, sanity bounds, or explicit staleness checks where the design depends on external prices.
- Suggested test/invariant: Invariant: share price and totalAssets cannot be inflated by a single mocked price or pool-state movement.
- Search tags: `vault-accounting, oracle-risk, pool-pricing, historical-vault-pattern, invariant-testing`

### Vault accounting invariant readiness gap

- Confidence: `high`
- Detected signals: `asset(), assets, balanceOf, convertToAssets, convertToShares, deposit, depositFee, feeRecipient, managementFee, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, performanceFee, previewDeposit, previewMint, previewRedeem, previewWithdraw, redeem`
- Why it matters: Vaults need explicit conservation and roundtrip properties because share math, fees, donations, and rounding can break user-value assumptions.
- Failed assumption class: Shares and assets remain exchangeable according to documented accounting rules.
- Broken invariant class: Deposits, withdrawals, redemptions, and fee paths conserve value within expected rounding bounds.
- Recommended defensive checks:
  - Add totalAssets consistency tests.
  - Add deposit-withdraw roundtrip tests across small and large amounts.
  - Test donation, zero-supply, rounding, and fee paths.
- Suggested test/invariant: Invariant: deposit followed by withdraw does not create value and does not strand assets beyond expected rounding.
- Search tags: `vault-security, share-accounting, totalAssets, audit-readiness`

### Strategy debt/gain/loss accounting readiness gap

- Confidence: `high`
- Detected signals: `allocate, assets, balanceOf, convertToAssets, convertToShares, deposit, emergencyExit, gain, harvest, loss, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, previewDeposit, previewMint, previewRedeem, previewWithdraw, profit`
- Why it matters: Strategy vaults need explicit tests for gain, loss, debt, harvest, report, and migration lifecycle assumptions.
- Failed assumption class: Strategy-reported balances, gains, losses, and debt remain aligned with vault accounting.
- Broken invariant class: Strategy lifecycle events cannot silently break totalAssets, share price, or withdrawal accounting.
- Recommended defensive checks:
  - Test harvest/report gain and loss paths with local mocks.
  - Test strategy withdrawal and migration accounting.
  - Document trusted strategy roles and loss-handling assumptions.
- Suggested test/invariant: Invariant: strategy gain/loss reports update totalAssets and share accounting according to documented policy.
- Search tags: `strategy-accounting, vault-lifecycle, gain-loss, audit-readiness`

### Withdrawal liquidity and queue lifecycle readiness gap

- Confidence: `high`
- Detected signals: `assets, balanceOf, cancelWithdraw, claimWithdraw, convertToAssets, convertToShares, cooldown, deposit, liquidityBuffer, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, pendingWithdraw, previewDeposit, previewMint, previewRedeem, previewWithdraw, redeem`
- Why it matters: Withdrawal queues, cooldowns, epochs, and liquidity buffers need lifecycle tests because user exits depend on state transitions over time.
- Failed assumption class: Requested, pending, claimable, and cancelled withdrawals move through documented states only.
- Broken invariant class: Withdrawal lifecycle preserves shares/assets accounting and available liquidity assumptions.
- Recommended defensive checks:
  - Test request, cancel, claim, cooldown, and epoch transitions.
  - Test available liquidity and buffer boundaries.
  - Document delayed withdrawal assumptions for auditors.
- Suggested test/invariant: Test: withdrawal lifecycle conserves shares and assets across request, cooldown, claim, and cancellation.
- Search tags: `withdrawal-queue, liquidity-buffer, vault-lifecycle, audit-readiness`

### Privileged vault controls and emergency operation readiness gap

- Confidence: `high`
- Detected signals: `emergencyWithdraw, onlyOwner, owner, pause, rescue, setDepositLimit, setFee, setMaxLoss, setOracle, setSlippage, setStrategy, setTreasury, setWithdrawLimit, sweep, unpause`
- Why it matters: Vault admin operations can change strategy, oracle, fee, limits, slippage, pause state, or upgrade targets and should be tested as launch-critical boundaries.
- Failed assumption class: Privileged operations are limited to documented roles and cannot bypass accounting assumptions silently.
- Broken invariant class: Emergency and configuration changes preserve the user-facing safety properties the protocol claims.
- Recommended defensive checks:
  - Test unauthorized calls for each setter and emergency function.
  - Test pause and emergency controls against deposit, withdraw, redeem, and strategy paths.
  - Document trusted-role powers and operational limits.
- Suggested test/invariant: Invariant: admin operations cannot bypass vault accounting without explicit, documented trust assumptions.
- Search tags: `vault-admin, emergency-controls, access-control-review, operational-readiness`

### Reentrancy-sensitive value flow review recommended

- Confidence: `high`
- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, deposit, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, previewDeposit, previewMint, previewRedeem, previewWithdraw, redeem, shares, strategy, totalAssets, totalSupply, transfer(`
- Why it matters: External calls around withdrawals, claims, callbacks, or token transfers have repeatedly exposed state-ordering assumptions.
- Failed assumption class: External receivers cannot re-enter before internal accounting reaches a safe state.
- Broken invariant class: Value flow remains single-entry and accounting is updated before control leaves the contract.
- Recommended defensive checks:
  - Review checks-effects-interactions order.
  - Add reentrancy tests using local receiver mocks.
  - Use guards where the protocol design requires them.
- Suggested test/invariant: Test: malicious local receiver cannot withdraw, claim, or redeem twice through a callback.
- Search tags: `reentrancy-review, value-flow, checks-effects-interactions`

### Privileged control and operational risk review recommended

- Confidence: `high`
- Detected signals: `emergencyWithdraw, onlyOwner, owner, pause, setFee, setOracle, setStrategy, setTreasury, unpause`
- Why it matters: Admin setters, emergency controls, fee updates, and governance execution paths can become launch blockers if role boundaries are unclear or untested.
- Failed assumption class: Privileged actors can only perform documented, intended operations.
- Broken invariant class: Admin actions cannot silently bypass accounting, oracle, or user-safety invariants.
- Recommended defensive checks:
  - Document every privileged role and setter.
  - Add unauthorized-call tests for each privileged function.
  - Add tests showing pause/emergency controls behave as documented.
- Suggested test/invariant: Invariant: unprivileged callers cannot change fees, oracles, strategies, treasury, pause state, or upgrade target.
- Search tags: `access-control-review, admin-risk, operational-security`

## All Readiness Gaps

### ARK-VLT-001 - Vault accounting without invariant tests

- Priority: `High readiness gap`
- Confidence: `high`
- Category: `vault-accounting`

Detected signals:
- `asset()`
- `assets`
- `balanceOf`
- `convertToAssets`
- `convertToShares`
- `deposit`
- `maxDeposit`
- `maxMint`
- `maxRedeem`
- `maxWithdraw`
- `mint`
- `previewDeposit`
- `previewMint`
- `previewRedeem`
- `previewWithdraw`
- `redeem`
- `shares`
- `strategy`
- `totalAssets`
- `totalSupply`

Affected files:
- `src/VaultRiskFixture.sol`
- `test/VaultRiskFixture.t.sol`

What was detected:

Vault/ERC4626-like accounting signals were detected, but no non-placeholder invariant/property testing signal was found.

Why it matters:

Vault bugs often appear when shares, assets, totalSupply, totalAssets, and external balances drift from assumptions used during deposits and withdrawals.

Historical pattern similarity:

Maps to historical vault/accounting failure classes where broken share valuation or manipulated accounting state caused loss.

Recommended defensive checks:

- deposit/withdraw roundtrip
- convertToShares/convertToAssets consistency
- donation/inflation resistance
- rounding direction tests
- totalAssets external dependency tests

Suggested tests:

- Add a Foundry invariant that checks totalAssets and share accounting conservation across deposit, withdraw, donation, and fee scenarios.

Search tags: `vault-accounting, invariant-testing, erc4626`

### ARK-VLT-002 - ERC4626-like interface without preview function tests

- Priority: `High readiness gap`
- Confidence: `high`
- Category: `vault-accounting`

Detected signals:
- `asset()`
- `assets`
- `balanceOf`
- `convertToAssets`
- `convertToShares`
- `deposit`
- `maxDeposit`
- `maxMint`
- `maxRedeem`
- `maxWithdraw`
- `mint`
- `previewDeposit`
- `previewMint`
- `previewRedeem`
- `previewWithdraw`
- `redeem`
- `shares`
- `totalAssets`
- `totalSupply`
- `withdraw`

Affected files:
- `src/VaultRiskFixture.sol`
- `test/VaultRiskFixture.t.sol`

What was detected:

Preview function signals were detected, but test files do not visibly cover previewDeposit, previewMint, previewWithdraw, or previewRedeem.

Why it matters:

ERC4626 integrations often rely on preview functions for quotes and UX; inconsistent previews can create user and integration risk.

Historical pattern similarity:

Maps to share/accounting mismatch classes where quoted and realized vault state diverge.

Recommended defensive checks:

- preview/action equivalence
- rounding direction tests
- max function boundary tests

Suggested tests:

- For each preview function, compare the previewed shares/assets with the actual deposit, mint, withdraw, or redeem result.

Search tags: `erc4626, preview-functions, vault-accounting`

### ARK-VLT-003 - Shares/assets conversion without rounding tests

- Priority: `High readiness gap`
- Confidence: `high`
- Category: `vault-accounting`

Detected signals:
- `asset()`
- `assets`
- `balanceOf`
- `convertToAssets`
- `convertToShares`
- `deposit`
- `depositFee`
- `feeRecipient`
- `managementFee`
- `maxDeposit`
- `maxMint`
- `maxRedeem`
- `maxWithdraw`
- `mint`
- `performanceFee`
- `previewDeposit`
- `previewMint`
- `previewRedeem`
- `previewWithdraw`
- `redeem`

Affected files:
- `src/VaultRiskFixture.sol`
- `test/VaultRiskFixture.t.sol`

What was detected:

Shares/assets conversion signals were detected without visible decimals, precision, mulDiv, or rounding test coverage.

Why it matters:

Small rounding mistakes in conversion functions can compound into unfair share issuance, redemption drift, or stranded assets.

Historical pattern similarity:

Maps to historical arithmetic and accounting mismatch classes where precision assumptions failed.

Recommended defensive checks:

- small amount tests
- decimals normalization
- mulDiv/precision review
- conversion reversibility

Suggested tests:

- Fuzz assets and shares across small, large, and decimal-edge values and assert conversion error stays within documented bounds.

Search tags: `share-accounting, rounding, precision`

### ARK-VLT-004 - totalAssets external dependency without manipulation-resistance tests

- Priority: `High readiness gap`
- Confidence: `high`
- Category: `vault-accounting`

Detected signals:
- `allocate`
- `assets`
- `balanceOf`
- `convertToAssets`
- `convertToShares`
- `deposit`
- `emergencyExit`
- `gain`
- `getPrice`
- `harvest`
- `latestRoundData`
- `loss`
- `maxDeposit`
- `maxMint`
- `maxRedeem`
- `maxWithdraw`
- `mint`
- `previewDeposit`
- `previewMint`
- `previewRedeem`

Affected files:
- `src/VaultRiskFixture.sol`
- `test/VaultRiskFixture.t.sol`

What was detected:

totalAssets appears connected to external strategy, pricing, or balance assumptions without visible manipulation-resistance test coverage.

Why it matters:

Vault share value often depends on totalAssets; external balances, strategies, or prices can make the accounting view drift from user expectations.

Historical pattern similarity:

Maps to Harvest/Yearn-style vault readiness classes where pricing or strategy state influenced share accounting.

Recommended defensive checks:

- donation tests
- mock strategy gain/loss
- stale/bounded oracle tests
- share price drift checks

Suggested tests:

- Mock external strategy or price state and assert totalAssets, share price, and withdrawal accounting remain within documented policy.

Search tags: `totalAssets, strategy-accounting, oracle-risk`

### ARK-VLT-005 - Strategy accounting without gain/loss tests

- Priority: `High readiness gap`
- Confidence: `high`
- Category: `vault-strategy`

Detected signals:
- `allocate`
- `emergencyExit`
- `gain`
- `harvest`
- `loss`
- `profit`
- `rebalance`
- `report`
- `strategy`
- `totalDebt`
- `withdrawFromStrategy`

Affected files:
- `src/VaultRiskFixture.sol`
- `test/VaultRiskFixture.t.sol`

What was detected:

Strategy, harvest, debt, gain, loss, or migration signals were detected without visible strategy lifecycle tests.

Why it matters:

Strategy vaults can look solvent until gain/loss, debt, or migration paths update accounting in unexpected ways.

Historical pattern similarity:

Maps to strategy debt/gain/loss accounting readiness classes.

Recommended defensive checks:

- gain report
- loss report
- debt update
- withdrawFromStrategy
- strategy migration

Suggested tests:

- Use a local mock strategy that reports gain and loss, then assert totalAssets and share accounting follow documented policy.

Search tags: `strategy-accounting, gain-loss, vault-lifecycle`

### ARK-VLT-006 - Withdrawal queue/cooldown without lifecycle tests

- Priority: `High readiness gap`
- Confidence: `medium`
- Category: `vault-withdrawal`

Detected signals:
- `cancelWithdraw`
- `claimWithdraw`
- `cooldown`
- `liquidityBuffer`
- `pendingWithdraw`
- `requestWithdraw`
- `withdrawalQueue`

Affected files:
- `src/VaultRiskFixture.sol`

What was detected:

Withdrawal queue, cooldown, epoch, pending withdrawal, or liquidity-buffer signals were detected without visible lifecycle tests.

Why it matters:

Delayed withdrawals create state machines; audit preparation should prove shares and assets are conserved through each state.

Historical pattern similarity:

Maps to vault lifecycle readiness classes where exit accounting or liquidity assumptions can break.

Recommended defensive checks:

- requestWithdraw
- claimWithdraw
- cancelWithdraw
- cooldown
- available liquidity

Suggested tests:

- Test the full withdrawal lifecycle and assert shares/assets are conserved across request, cooldown, claim, and cancellation.

Search tags: `withdrawal-queue, liquidity, vault-lifecycle`

### ARK-ORC-001 - Oracle-dependent vault without stale-price or bounds tests

- Priority: `High readiness gap`
- Confidence: `medium`
- Category: `oracle-pricing`

Detected signals:
- `getPrice`
- `latestRoundData`
- `priceFeed`
- `setOracle`

Affected files:
- `src/VaultRiskFixture.sol`
- `test/VaultRiskFixture.t.sol`

What was detected:

Oracle, price-feed, pool-price, reserve, TWAP, or LP pricing signals were detected without enough stale-price, bounds, or sanity-check coverage.

Why it matters:

Vaults that price assets, LP tokens, or strategies through external sources need explicit assumptions around stale, spot, and bounded prices.

Historical pattern similarity:

Maps to historical vault/oracle and pool-price manipulation readiness classes.

Recommended defensive checks:

- stale price rejection
- decimals normalization
- TWAP/sanity check
- bounds
- oracle setter roles

Suggested tests:

- Use local mock oracles/pools to test stale, out-of-bounds, decimals, and spot-price scenarios without live-chain calls.

Search tags: `oracle-risk, vault-pricing, pool-price`

### ARK-VLT-007 - Fee logic without fee accounting tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Category: `vault-accounting`

Detected signals:
- `depositFee`
- `feeRecipient`
- `managementFee`
- `performanceFee`
- `withdrawalFee`

Affected files:
- `src/VaultRiskFixture.sol`
- `test/VaultRiskFixture.t.sol`

What was detected:

Fee terms were detected without visible tests for fee accounting, recipient balances, or conservation around fee paths.

Why it matters:

Fee logic changes share issuance, redemption value, and treasury balances; missing tests make audit review slower and riskier.

Historical pattern similarity:

Maps to accounting mismatch classes where protocol fees changed conservation assumptions.

Recommended defensive checks:

- fee bounds
- recipient accounting
- share conservation
- rounding with fees

Suggested tests:

- Assert user shares, treasury shares/assets, and totalAssets remain consistent before and after fee-bearing operations.

Search tags: `fee-accounting, vault-accounting`

### ARK-VLT-008 - Pause/emergency controls without operational tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Category: `vault-operations`

Detected signals:
- `emergencyWithdraw`
- `pause`
- `rescue`
- `setDepositLimit`
- `setFee`
- `setMaxLoss`
- `setOracle`
- `setSlippage`
- `setStrategy`
- `setTreasury`
- `setWithdrawLimit`
- `sweep`
- `unpause`

Affected files:
- `src/VaultRiskFixture.sol`
- `test/VaultRiskFixture.t.sol`

What was detected:

Pause or emergency signals were detected without visible tests for blocked flows and documented recovery behavior.

Why it matters:

Emergency controls are launch-critical; they should behave predictably under stress without bypassing accounting assumptions.

Historical pattern similarity:

Maps to operational readiness classes where emergency behavior changes core state transitions.

Recommended defensive checks:

- pause blocks deposit
- pause blocks withdraw/redeem if intended
- emergency exit behavior
- role boundary

Suggested tests:

- Assert pause and emergency states block or allow each vault flow exactly as documented.

Search tags: `pause, emergency-controls, vault-operations`


## Suppressed Readiness Gaps

No readiness gaps were suppressed in this run.

## Suggested Foundry Invariant Skeletons

- Generated skeleton: `test/invariant/ArkheionxReadinessInvariants.t.sol`

- **totalAssets consistency** (`vault`): totalAssets should match local asset accounting and strategy balances within documented rounding.
- **deposit/withdraw roundtrip** (`vault`): A user should not create value by depositing and withdrawing through normal paths.
- **convertToShares/convertToAssets consistency** (`vault`): Conversion functions should be mutually consistent within documented rounding across supply states.
- **share price donation resistance** (`vault`): Donations, low supply, and external balances should not let one actor distort share value unexpectedly.
- **fee accounting conservation** (`vault`): Fees should be bounded, documented, and unable to overcharge beyond configured limits.
- **strategy balance drift handling** (`vault`): Strategy gains, losses, and withdrawals should remain reflected in accounting assumptions.
- **withdrawal lifecycle conservation** (`vault`): Queued or delayed withdrawals should conserve shares/assets through request, cooldown, claim, and cancellation.
- **pause behavior** (`vault`): Pause should block risky flows while preserving documented emergency exits.
- **stale price rejection** (`oracle`): Stale oracle rounds should be rejected or handled according to documented policy.
- **decimals normalization** (`oracle`): Price decimals should be normalized consistently before accounting decisions.
- **price bounds** (`oracle`): Outlier prices should hit documented bounds or review paths.
- **TWAP or sanity check** (`oracle`): Spot price dependence should be bounded by TWAP, sanity checks, or explicit assumptions.
- **oracle update access control** (`oracle`): Only authorized roles should change oracle configuration.
- **unauthorized role rejection** (`access control`): Unauthorized users cannot call privileged setters or emergency functions.
- **admin cannot bypass accounting** (`access control`): Owner/admin operations cannot silently break accounting invariants unless explicitly trusted and documented.
- **pause blocks risky flows** (`access control`): Pause blocks documented risky flows and preserves expected recovery paths.
- **upgrade authorization** (`access control`): Upgrade authorization works as intended and cannot be triggered by untrusted callers.

## Audit Readiness Checklist

- [ ] Core user flows have deterministic unit tests.
- [ ] Accounting, oracle, reward, and role assumptions are documented.
- [ ] Foundry invariant tests cover value conservation and access boundaries.
- [ ] Fuzz tests cover edge cases, rounding, and unexpected user sequences.
- [ ] Privileged roles, upgrade controls, and emergency controls are documented and tested.
- [ ] Known limitations are written down for auditors.
- [ ] A formal audit scope names contracts, commit hash, deployment assumptions, and out-of-scope areas.

## Generated Issue Checklist

- Generated checklist: `examples/reports/vault-risk-fixture-issue-checklist.md`
- Use this as a copyable GitHub Issue body or as a remediation tracker.

## GitHub Action Outputs

- Markdown Report: `examples/reports/vault-risk-fixture-pre-audit-report.md`
- Json Report: `examples/reports/vault-risk-fixture-pre-audit-report.json`
- Sarif Report: `examples/reports/vault-risk-fixture.sarif.json`
- Summary: `examples/reports/vault-risk-fixture-action-summary.md`
- Comment: `examples/reports/vault-risk-fixture-pr-comment.md`
- Issue Checklist: `examples/reports/vault-risk-fixture-issue-checklist.md`
- Baseline: `examples/reports/vault-risk-fixture.baseline.json`

## Search Tags

`access-control-review`, `arkheionx`, `audit-preparation`, `defi-security`, `foundry`, `historical-exploit-pattern`, `indie-defi`, `invariant-testing`, `oracle-risk`, `pre-audit-readiness`, `reentrancy-review`, `root-cause-analysis`, `smart-contract-security`, `solidity-security`, `vault-accounting`

## Recommended Next Steps

1. Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
2. Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
3. Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
4. Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
5. Add local mock strategy tests for gain, loss, debt, harvest, and migration accounting.

## What This Report Does Not Prove

- It does not prove protocol safety.
- It does not confirm exploitability.
- It does not replace manual review.
- It does not replace a formal audit.

## Formal Audit Recommendation

Run a formal smart contract audit before mainnet deployment, before material TVL, or before handling real user funds.

