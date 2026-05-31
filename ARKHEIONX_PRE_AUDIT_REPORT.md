# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `.`
- Generated at: `2026-05-28T12:45:27+00:00`
- Protocol type: `amm`
- Protocol confidence: `medium`
- Files scanned: `330`
- Scanner version: `2.0.1`
- Output profile: `standard` (Standard)

| File class       | Count |
| ---------------- | ----- |
| Solidity sources | 22    |
| Solidity tests   | 32    |
| Docs             | 260   |
| Configs          | 11    |
| Workflows        | 5     |

## Config Summary

- Config source: `defaults`
- Effective protocol type: `amm`
- Enabled rule packs: `access-control, amm, docs, lending, oracle, reentrancy-value-flow, rewards, testing, vault`
- Minimum confidence: `low`
- Suppressions configured: `0`
- Output profile: `standard`
- Ignore generated artifacts: `True`
- Include generated artifacts: `False`

## Scan Source Summary

- Files considered: `338`
- Files scanned: `330`
- Files ignored: `8`
- Generated Arkheionx artifacts ignored: `6`
- Generated artifacts were ignored to prevent previous Arkheionx outputs from influencing this scan.

## Disclaimer

This is an automated pre-audit readiness report. It is not a formal audit, does not prove the absence or presence of vulnerabilities, does not authorize live-target testing, and should only be used on repositories you own or are authorized to review. A formal audit is recommended before handling real user funds.

## Analysis Quality

| Source                   | Status   |
| ------------------------ | -------- |
| Keyword scan             | enabled  |
| Semantic-lite extraction | enabled  |
| Semantic contracts       | 167      |
| Semantic test files      | 29       |
| Slither                  | disabled |
| Slither detectors        | 0        |
| Test coverage mapping    | enabled  |
| Negative evidence        | 2028     |

## Executive Summary

Arkheionx scanned `.` as `amm` readiness context. This is a local/static pre-audit readiness report, not a formal audit.

- Readiness score: **82/100**
- Score band: **Near audit-ready**
- Active readiness gaps: `10`
- Suppressed readiness gaps: `0`
- Active rule packs: `access-control, amm, docs, lending, oracle, reentrancy-value-flow, rewards, testing, vault`
- Generated artifacts ignored: `6`
- Top readiness gaps:
  - **ARK-AMM-002 (Medium readiness gap):** LP share accounting without mint/burn boundary tests - Add tests for first liquidity provider behavior, proportional LP minting/burning, withdrawal rounding, and dust handling.
  - **ARK-LEND-001 (Medium readiness gap):** Collateral/debt solvency invariant not covered by tests - Add collateral/debt invariants and boundary tests for borrow, repay, deposit, withdrawal, and liquidation readiness.
  - **ARK-LEND-002 (Medium readiness gap):** Liquidation boundary tests missing - Add tests for liquidation thresholds, partial liquidation, bonus bounds, and over-seizure prevention.
  - **ARK-LEND-003 (Medium readiness gap):** Interest/index accounting not covered by rounding and time-step tests - Add tests for accrual monotonicity, small-balance rounding, borrow/repay around accrual, and repeated accrual drift.
  - **ARK-LEND-005 (Medium readiness gap):** Reserve/cash accounting assumptions not covered - Add tests proving borrow cannot exceed available liquidity and repay/reserve updates keep cash and debt accounting consistent.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
  - Run a formal smart contract audit before mainnet launch or before handling real user funds.

## Fix First

| Rank | Finding                                                                | Rule Family | Why Fix First                                                                                       | Next Action                                                                                                                                                     |
| ---- | ---------------------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | ARK-RWD-001 - Reward accounting without conservation tests             | rewards     | high-confidence local evidence; appears across multiple files; clear defensive tests are available. | Add or review: Fund rewards, run multiple users through stake/claim/unstake sequences, and assert total claimed remains bounded by funded rewards.              |
| 2    | ARK-RWD-003 - Claim flow without double-claim prevention tests         | rewards     | high-confidence local evidence; appears across multiple files; clear defensive tests are available. | Add or review: Assert claim twice without new rewards returns zero or reverts according to documented policy.                                                   |
| 3    | ARK-AMM-002 - LP share accounting without mint/burn boundary tests     | amm         | appears across multiple files; clear defensive tests are available.                                 | Add or review: Test first liquidity, repeated add/remove liquidity, and tiny-liquidity burn cases to verify LP shares remain proportional.                      |
| 4    | ARK-LEND-001 - Collateral/debt solvency invariant not covered by tests | lending     | appears across multiple files; clear defensive tests are available.                                 | Add or review: Assert debt cannot exceed documented collateral constraints and collateral withdrawals cannot make a position unsafe unless intended and tested. |
| 5    | ARK-LEND-002 - Liquidation boundary tests missing                      | lending     | appears across multiple files; clear defensive tests are available.                                 | Add or review: Test a position just above threshold cannot be liquidated and a position just below threshold can be liquidated within documented bonus bounds.  |

## Finding Groups

### Findings by Rule Family

| Rule Family           | Active Findings |
| --------------------- | --------------- |
| access-control        | 1               |
| amm                   | 1               |
| lending               | 4               |
| reentrancy-value-flow | 1               |
| rewards               | 3               |

### Findings by Confidence

| Confidence | Active Findings |
| ---------- | --------------- |
| high       | 3               |
| low        | 1               |
| medium     | 6               |

## Suppression Summary

- Suppressions loaded: `0`
- Suppressions applied: `0`
- Suppressions should include a reason and be revisited before launch or external review.

## Negative Evidence

Arkheionx found coverage terms in missing/negative context. These statements are not counted as positive test coverage.

- `.github/workflows/pre-audit-ci.yml:168` `invariant` - Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests` - Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test` - Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant` - Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant` - Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

## Detected Protocol Shape

- Detected protocol type: `amm`
- Confidence: `medium`
- Protocol score signals: `{"amm": 744, "lending": 569, "oracle": 272, "staking": 132, "vault": 624}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                    | Score | Max | Notes                                                                                                                                                                                                                                                                                                                                                                                                              |
| --------------------------- | ----- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Repository Structure        | 15    | 15  | Solidity sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.; CI workflow detected.                                                                                                                                                                                                                                                                          |
| Test Presence               | 15    | 20  | Solidity test files detected.; Assert usage detected.; Foundry or Hardhat test environment detected.                                                                                                                                                                                                                                                                                                               |
| Invariant Fuzz Readiness    | 13    | 20  | Invariant tests or invariant terms detected.; Fuzz tests detected.; Edge-case testing terms detected.; Negative coverage statements detected; removed 3 readiness point(s) from this category.                                                                                                                                                                                                                     |
| Defi Risk Coverage          | 17    | 20  | Oracle assumptions have at least some documented or tested controls.; Accounting assumptions have at least some documented or tested controls.; Role or admin boundaries have some visible coverage.; Value-flow or reentrancy guard/review signals detected.; Protocol-specific checklist or property coverage detected.; Negative coverage statements detected; removed 3 readiness point(s) from this category. |
| Documentation Readiness     | 7     | 10  | README detected.; SECURITY or docs/security material detected.; Assumptions, invariants, or limitations are documented.; Deployment or role information appears in docs/code comments.; Negative coverage statements detected; removed 3 readiness point(s) from this category.                                                                                                                                    |
| Operational Admin Readiness | 15    | 15  | Access-control surface is visible.; Emergency control or incident terms detected.; Upgradeability is absent or has visible documentation/test terms.; Privileged setters or owner boundaries are visible for review.; Monitoring, incident, limitation, or emergency notes detected.                                                                                                                               |

## Top Readiness Gaps

| ID           | Priority             | Category               | Title                                                                 |
| ------------ | -------------------- | ---------------------- | --------------------------------------------------------------------- |
| ARK-AMM-002  | Medium readiness gap | amm-lp-accounting      | LP share accounting without mint/burn boundary tests                  |
| ARK-LEND-001 | Medium readiness gap | lending-solvency       | Collateral/debt solvency invariant not covered by tests               |
| ARK-LEND-002 | Medium readiness gap | lending-liquidation    | Liquidation boundary tests missing                                    |
| ARK-LEND-003 | Medium readiness gap | lending-interest-index | Interest/index accounting not covered by rounding and time-step tests |
| ARK-LEND-005 | Medium readiness gap | lending-liquidity      | Reserve/cash accounting assumptions not covered                       |

## Rule Pack Coverage

| Rule Pack                                 | Detected | Findings | Docs                                    |
| ----------------------------------------- | -------- | -------- | --------------------------------------- |
| Vault Rule Pack                           | yes      | 0        | docs/VAULT_RULE_PACK.md                 |
| Oracle Rule Pack                          | yes      | 0        | docs/ORACLE_RULE_PACK.md                |
| Access Control / Upgradeability Rule Pack | yes      | 1        | docs/ACCESS_CONTROL_RULE_PACK.md        |
| Reentrancy / Value Flow Rule Pack         | yes      | 1        | docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md |
| Staking / Reward Accounting Rule Pack     | yes      | 3        | docs/REWARD_ACCOUNTING_RULE_PACK.md     |
| AMM Rule Pack                             | yes      | 1        | docs/AMM_RULE_PACK.md                   |
| Lending Rule Pack                         | yes      | 4        | docs/LENDING_RULE_PACK.md               |

### Vault Rule Pack

- Signals detected: `61`
- Signal terms: `allocate, asset(), assets, balanceOf, cancelWithdraw, claimWithdraw, convertToAssets, convertToShares, cooldown, debt, decimals, deposit, depositFee, emergencyExit, emergencyWithdraw, feeRecipient, gain, harvest, initialize, liquidityBuffer`
- Findings: `0`
- Docs: `docs/VAULT_RULE_PACK.md`
- Suggested tests:
  - totalAssets consistency
  - deposit/withdraw roundtrip
  - share conversion rounding
  - strategy gain/loss lifecycle

### Oracle Rule Pack

- Signals detected: `27`
- Signal terms: `AggregatorV3Interface, Chainlink, Curve, LP token, UniswapV3, answer, answeredInRound, bounds, decimals, getPrice, getReserves, heartbeat, latestAnswer, latestRoundData, maxPrice, minPrice, observe, oracle, pool, priceFeed`
- Findings: `0`
- Docs: `docs/ORACLE_RULE_PACK.md`
- Suggested tests:
  - stale price rejection
  - decimals normalization
  - price bounds
  - TWAP vs spot behavior

### Access Control / Upgradeability Rule Pack

- Signals detected: `22`
- Signal terms: `DEFAULT_ADMIN_ROLE, admin, emergencyWithdraw, grantRole, guardian, hasRole, implementation, multisig, onlyOwner, operator, owner, pause, proxy, rescue, revokeRole, role, setFee, setOracle, setStrategy, setTreasury`
- Findings: `1`
- Docs: `docs/ACCESS_CONTROL_RULE_PACK.md`
- Suggested tests:
  - unauthorized setter tests
  - pause/emergency boundaries
  - initializer once
  - upgrade authorization

### Reentrancy / Value Flow Rule Pack

- Signals detected: `14`
- Signal terms: `.call(, callback, call{, claim, flashLoan, onERC1155Received, onERC721Received, redeem, safeTransfer, send, staticcall, transfer, transferFrom, withdraw`
- Findings: `1`
- Docs: `docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md`
- Suggested tests:
  - reentrant receiver mock
  - state update ordering
  - double claim prevention
  - failed external call behavior

### Staking / Reward Accounting Rule Pack

- Signals detected: `24`
- Signal terms: `accumulator, claim, claimReward, collateral, cooldown, debt, decimals, depositFee, earned, fee, index, managementFee, pendingReward, performanceFee, reward, rewardPerToken, rewards, rounding, shares, stake`
- Findings: `3`
- Docs: `docs/REWARD_ACCOUNTING_RULE_PACK.md`
- Suggested tests:
  - reward conservation
  - no overclaim
  - index monotonicity
  - stake/unstake/claim lifecycle

### AMM Rule Pack

- Signals detected: `24`
- Signal terms: `LP, addLiquidity, amountIn, amountOut, balanceOf, burn, deadline, getAmountOut, getReserves, invariant, kLast, liquidity, mint, pair, pool, quote, removeLiquidity, reserve, reserve0, reserve1`
- Findings: `1`
- Docs: `docs/AMM_RULE_PACK.md`
- Suggested tests:
  - swap invariant conservation
  - LP share proportionality
  - TWAP or reserve bounds
  - minOut enforcement

### Lending Rule Pack

- Signals detected: `24`
- Signal terms: `LTV, accrueInterest, borrow, borrowIndex, cash, closeFactor, collateral, collateralFactor, debt, guardian, health factor, healthFactor, interestIndex, liquidate, liquidation, liquidationBonus, liquidationThreshold, liquidator, principal, ratePerSecond`
- Findings: `4`
- Docs: `docs/LENDING_RULE_PACK.md`
- Suggested tests:
  - collateral/debt invariant
  - liquidation boundary tests
  - interest index monotonicity
  - oracle shock tests

## Risk Signal Summary

### Vault Erc4626

- Detected signals: `asset(), assets, balanceOf, convertToAssets, convertToShares, deposit, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, previewDeposit, previewMint, previewRedeem, previewWithdraw, redeem, shares, totalAssets, totalSupply, withdraw`
- Files with signals: `29`
- Example files: `EVM/src/interface.sol, EVM/src/tokenhelper.sol, EVM/templates/ExploitTemplate.t.sol, EVM/test/2018-04/Exploit_2018-04.t.sol, EVM/test/2020-04/Exploit_2020-04.t.sol`

### Vault Accounting

- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, deposit, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, previewDeposit, previewMint, previewRedeem, previewWithdraw, redeem, shares, strategy, totalAssets, totalSupply, withdraw`
- Files with signals: `29`
- Example files: `EVM/src/interface.sol, EVM/src/tokenhelper.sol, EVM/templates/ExploitTemplate.t.sol, EVM/test/2018-04/Exploit_2018-04.t.sol, EVM/test/2020-04/Exploit_2020-04.t.sol`

### Vault Accounting Risk

- Detected signals: `convertToAssets, convertToShares, decimals, depositFee, feeRecipient, managementFee, performanceFee, previewDeposit, previewMint, previewRedeem, previewWithdraw, rounding, totalAssets, treasury, withdrawalFee`
- Files with signals: `18`
- Example files: `EVM/src/basetest.sol, EVM/src/interface.sol, EVM/src/tokenhelper.sol, EVM/test/2020-10/Exploit_2020-10.t.sol, EVM/test/2020-11/Exploit_2020-11.t.sol`

### Vault Strategy

- Detected signals: `allocate, debt, emergencyExit, gain, harvest, loss, profit, rebalance, report, strategy, totalDebt, withdrawFromStrategy`
- Files with signals: `17`
- Example files: `EVM/src/interface.sol, EVM/templates/ExploitTemplate.t.sol, EVM/test/2020-04/Exploit_2020-04.t.sol, EVM/test/2020-06/Exploit_2020-06.t.sol, EVM/test/2020-08/Exploit_2020-08.t.sol`

### Vault Pricing

- Detected signals: `Chainlink, Curve, LP token, UniswapV3, decimals, getPrice, getReserves, heartbeat, latestAnswer, latestRoundData, oracle, priceFeed, stale`
- Files with signals: `27`
- Example files: `EVM/src/basetest.sol, EVM/src/interface.sol, EVM/src/tokenhelper.sol, EVM/templates/ExploitTemplate.t.sol, EVM/test/2020-10/Exploit_2020-10.t.sol`

### Vault Withdrawal Liquidity

- Detected signals: `cancelWithdraw, claimWithdraw, cooldown, liquidityBuffer, pendingWithdraw, requestWithdraw, withdrawalQueue`
- Files with signals: `1`
- Example files: `examples/vault-risk-fixture/src/VaultRiskFixture.sol`

### Vault Admin Ops

- Detected signals: `emergencyWithdraw, initialize, pause, rescue, setDepositLimit, setFee, setMaxLoss, setOracle, setSlippage, setStrategy, setTreasury, setWithdrawLimit, sweep, unpause`
- Files with signals: `12`
- Example files: `EVM/src/interface.sol, EVM/test/2021-02/Exploit_2021-02.t.sol, examples/generated-artifact-self-ingestion-fixture/src/SelfIngestionToy.sol, examples/lending-fixture/src/ToyLendingMarket.sol, examples/lending-fixture/test/ToyLendingMarket.t.sol`

### Oracle

- Detected signals: `AggregatorV3Interface, Chainlink, answer, answeredInRound, bounds, decimals, getPrice, getReserves, heartbeat, latestAnswer, latestRoundData, maxPrice, minPrice, observe, oracle, pool, priceFeed, reserve0, reserve1, roundId, setOracle, sqrtPriceX96, stale, updatedAt`
- Files with signals: `32`
- Example files: `EVM/src/basetest.sol, EVM/src/interface.sol, EVM/src/tokenhelper.sol, EVM/templates/ExploitTemplate.t.sol, EVM/test/2020-10/Exploit_2020-10.t.sol`

### Access Control

- Detected signals: `DEFAULT_ADMIN_ROLE, admin, emergencyWithdraw, grantRole, guardian, hasRole, implementation, multisig, onlyOwner, operator, owner, pause, proxy, rescue, revokeRole, role, setFee, setOracle, setStrategy, setTreasury, sweep, unpause`
- Files with signals: `15`
- Example files: `EVM/src/interface.sol, EVM/test/2017-07/Exploit_2017-07.t.sol, EVM/test/2017-11/Exploit_2017-11.t.sol, EVM/test/2020-04/Exploit_2020-04.t.sol, examples/generated-artifact-self-ingestion-fixture/src/SelfIngestionToy.sol`

### Reentrancy Value Flow

- Detected signals: `.call(, callback, call{, claim, flashLoan, onERC1155Received, onERC721Received, redeem, safeTransfer, send, staticcall, transfer, transferFrom, withdraw`
- Files with signals: `27`
- Example files: `EVM/src/interface.sol, EVM/src/tokenhelper.sol, EVM/test/2018-10/Exploit_2018-10.t.sol, EVM/test/2020-04/Exploit_2020-04.t.sol, EVM/test/2020-06/Exploit_2020-06.t.sol`

### Upgradeability

- Detected signals: `implementation, proxy`
- Files with signals: `1`
- Example files: `EVM/src/interface.sol`

### Accounting Complexity

- Detected signals: `accumulator, collateral, debt, decimals, depositFee, fee, index, managementFee, performanceFee, reward, rounding, withdrawalFee`
- Files with signals: `29`
- Example files: `EVM/src/basetest.sol, EVM/src/interface.sol, EVM/src/tokenhelper.sol, EVM/test/2020-08/Exploit_2020-08.t.sol, EVM/test/2020-10/Exploit_2020-10.t.sol`

### Staking Rewards

- Detected signals: `accumulator, claim, claimReward, cooldown, earned, index, pendingReward, reward, rewardPerToken, rewards, shares, stake, totalStaked, unstake, withdraw`
- Files with signals: `21`
- Example files: `EVM/src/interface.sol, EVM/test/2020-04/Exploit_2020-04.t.sol, EVM/test/2020-10/Exploit_2020-10.t.sol, EVM/test/2020-11/Exploit_2020-11.t.sol, EVM/test/2020-12/Exploit_2020-12.t.sol`

### Amm

- Detected signals: `LP, addLiquidity, amountIn, amountOut, balanceOf, burn, deadline, getAmountOut, getReserves, invariant, kLast, liquidity, mint, pair, pool, quote, removeLiquidity, reserve, reserve0, reserve1, sqrtPriceX96, swap, totalSupply, x * y`
- Files with signals: `39`
- Example files: `EVM/src/interface.sol, EVM/src/tokenhelper.sol, EVM/templates/ExploitTemplate.t.sol, EVM/test/2018-04/Exploit_2018-04.t.sol, EVM/test/2020-04/Exploit_2020-04.t.sol`

### Lending

- Detected signals: `LTV, accrueInterest, borrow, borrowIndex, cash, closeFactor, collateral, collateralFactor, debt, guardian, health factor, healthFactor, interestIndex, liquidate, liquidation, liquidationBonus, liquidationThreshold, liquidator, principal, ratePerSecond, repay, seize, totalBorrows, totalReserves`
- Files with signals: `11`
- Example files: `EVM/src/interface.sol, EVM/templates/ExploitTemplate.t.sol, EVM/test/2020-08/Exploit_2020-08.t.sol, EVM/test/2020-09/Exploit_2020-09.t.sol, EVM/test/2025-11/Exploit_2025-11.t.sol`

### Bridge Cross Chain

- Detected signals: `bridge, endpoint`
- Files with signals: `2`
- Example files: `EVM/src/interface.sol, EVM/test/2021-01/Exploit_2021-01.t.sol`

### Governance

- Detected signals: `delegate, proposal, vote`
- Files with signals: `2`
- Example files: `EVM/src/interface.sol, EVM/test/2022-02/Exploit_2022-02.t.sol`

### Testing And Documentation

- Test Directory: `True`
- Foundry Tests: `True`
- Hardhat Tests: `False`
- Test File Count: `29`
- Invariant Tests: `True`
- Fuzz Tests: `True`
- Handler Contracts: `False`
- Assert Usage: `True`
- Assert Count: `76`
- Forge Std: `True`
- Echidna: `False`
- Slither: `True`
- Ci Workflow: `True`
- Edge Case Tests: `True`
- Negative Evidence Count: `2028`
- Negative Evidence Terms: `['LP share accounting', 'access-control', 'access-control negative tests', 'borrow index', 'callback', 'collateral debt', 'constant product', 'double-claim', 'fee-on-transfer', 'fuzz', 'heartbeat', 'interest index', 'invariant', 'invariant test', 'invariant tests', 'liquidation boundary', 'oracle freshness', 'reentrancy', 'reentrancy/callback tests', 'reward conservation', 'reward conservation tests', 'role-boundary', 'share accounting', 'slippage', 'solvency', 'stale oracle', 'stale oracle tests', 'totalAssets', 'unauthorized', 'updatedAt']`
- Test files: `EVM/templates/ExploitTemplate.t.sol, EVM/test/2017-07/Exploit_2017-07.t.sol, EVM/test/2017-11/Exploit_2017-11.t.sol, EVM/test/2018-04/Exploit_2018-04.t.sol, EVM/test/2018-10/Exploit_2018-10.t.sol, EVM/test/2020-04/Exploit_2020-04.t.sol, EVM/test/2020-06/Exploit_2020-06.t.sol, EVM/test/2020-08/Exploit_2020-08.t.sol, EVM/test/2020-09/Exploit_2020-09.t.sol, EVM/test/2020-10/Exploit_2020-10.t.sol`

## Historical Exploit-Pattern Similarity

### Strategy debt/gain/loss accounting readiness gap

- Confidence: `high`
- Detected signals: `allocate, assets, balanceOf, convertToAssets, convertToShares, debt, deposit, emergencyExit, gain, harvest, loss, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint, previewDeposit, previewMint, previewRedeem, previewWithdraw`
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
- Detected signals: `DEFAULT_ADMIN_ROLE, admin, emergencyWithdraw, grantRole, guardian, hasRole, implementation, initialize, multisig, onlyOwner, operator, owner, pause, proxy, rescue, revokeRole, role, setDepositLimit, setFee, setMaxLoss`
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
- Detected signals: `.call(, accumulator, assets, balanceOf, callback, call{, claim, claimReward, convertToAssets, convertToShares, cooldown, deposit, earned, flashLoan, index, maxDeposit, maxMint, maxRedeem, maxWithdraw, mint`
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
- Detected signals: `DEFAULT_ADMIN_ROLE, admin, delegate, emergencyWithdraw, grantRole, guardian, hasRole, implementation, multisig, onlyOwner, operator, owner, pause, proposal, proxy, rescue, revokeRole, role, setFee, setOracle`
- Why it matters: Admin setters, emergency controls, fee updates, and governance execution paths can become launch blockers if role boundaries are unclear or untested.
- Failed assumption class: Privileged actors can only perform documented, intended operations.
- Broken invariant class: Admin actions cannot silently bypass accounting, oracle, or user-safety invariants.
- Recommended defensive checks:
  - Document every privileged role and setter.
  - Add unauthorized-call tests for each privileged function.
  - Add tests showing pause/emergency controls behave as documented.
- Suggested test/invariant: Invariant: unprivileged callers cannot change fees, oracles, strategies, treasury, pause state, or upgrade target.
- Search tags: `access-control-review, admin-risk, operational-security`

### Initialization and upgrade boundary review recommended

- Confidence: `low`
- Detected signals: `implementation, proxy`
- Why it matters: Upgradeable contracts can fail when initialization, authorization, storage layout, or implementation boundaries are not tested explicitly.
- Failed assumption class: Initialization and upgrade authority cannot be taken by the wrong actor.
- Broken invariant class: Storage and implementation changes preserve core accounting and access-control invariants.
- Recommended defensive checks:
  - Test initializer can only run once.
  - Test upgrade authorization boundaries.
  - Document storage layout and upgrade process.
- Suggested test/invariant: Test: unauthorized caller cannot initialize, reinitialize, or upgrade the implementation.
- Search tags: `upgradeability, initialization-bug, proxy-review`

### Reward accounting mismatch review recommended

- Confidence: `high`
- Detected signals: `accumulator, claim, claimReward, collateral, cooldown, debt, decimals, depositFee, earned, fee, index, managementFee, pendingReward, performanceFee, reward, rewardPerToken, rewards, rounding, shares, stake`
- Why it matters: Reward indexes and accumulators are common sources of overclaim, underclaim, and precision drift when supply changes across epochs.
- Failed assumption class: Reward index math always reflects actual funded rewards and stake weights.
- Broken invariant class: Claimable rewards cannot exceed funded rewards beyond documented rounding.
- Recommended defensive checks:
  - Test claim conservation across multiple users.
  - Test stake/unstake around reward updates.
  - Check precision and rounding around small balances.
- Suggested test/invariant: Invariant: total claimed plus remaining claimable never exceeds funded rewards beyond expected rounding.
- Search tags: `reward-accounting, staking, index-math, precision`

### AMM invariant manipulation review recommended

- Confidence: `high`
- Detected signals: `AggregatorV3Interface, Chainlink, LP, addLiquidity, amountIn, amountOut, answer, answeredInRound, balanceOf, bounds, burn, deadline, decimals, getAmountOut, getPrice, getReserves, heartbeat, invariant, kLast, latestAnswer`
- Why it matters: AMM integrations need invariant and reserve assumptions tested under swaps, liquidity changes, fees, and price movements.
- Failed assumption class: Pool reserves and quote functions remain representative for protocol decisions.
- Broken invariant class: Swaps and liquidity changes cannot create value outside documented fee mechanics.
- Recommended defensive checks:
  - Add invariant conservation tests.
  - Test add/remove liquidity proportionality.
  - Avoid relying on same-block spot reserves without documented controls.
- Suggested test/invariant: Invariant: swaps and liquidity operations preserve the AMM invariant within fee and rounding bounds.
- Search tags: `amm-invariant, liquidity, spot-price, reserve-manipulation`

### Liquidation and collateral accounting review recommended

- Confidence: `high`
- Detected signals: `AggregatorV3Interface, Chainlink, LTV, accrueInterest, answer, answeredInRound, borrow, borrowIndex, bounds, cash, closeFactor, collateral, collateralFactor, debt, decimals, getPrice, getReserves, guardian, health factor, healthFactor`
- Why it matters: Lending systems depend on collateral, debt, oracle, and liquidation assumptions staying consistent through edge cases.
- Failed assumption class: Collateral value and debt state stay aligned with liquidation and solvency rules.
- Broken invariant class: Borrowers cannot become undercollateralized without expected liquidation or protocol accounting response.
- Recommended defensive checks:
  - Test collateralization and liquidation boundaries.
  - Test oracle movement around borrow and liquidation flows.
  - Check interest index monotonicity and debt accounting.
- Suggested test/invariant: Invariant: positions below required collateralization are liquidatable and solvent positions are not incorrectly liquidated.
- Search tags: `lending, liquidation, collateral, oracle-risk`

### Cross-chain message validation review recommended

- Confidence: `high`
- Detected signals: `DEFAULT_ADMIN_ROLE, admin, bridge, emergencyWithdraw, endpoint, grantRole, guardian, hasRole, implementation, multisig, onlyOwner, operator, owner, pause, proxy, rescue, revokeRole, role, setFee, setOracle`
- Why it matters: Cross-chain flows need explicit source, sender, replay, and message-authentication checks before they should be considered launch-ready.
- Failed assumption class: Inbound messages are authentic, authorized, and replay-protected.
- Broken invariant class: Cross-chain state transitions cannot be triggered by an untrusted endpoint or malformed message.
- Recommended defensive checks:
  - Document trusted endpoints and relayer assumptions.
  - Test source-chain and sender validation.
  - Test replay and malformed message rejection.
- Suggested test/invariant: Test: untrusted local message sender cannot execute privileged cross-chain state transitions.
- Search tags: `cross-chain, bridge-validation, message-authentication`

## All Readiness Gaps

### ARK-UPG-001 - Upgradeable contract without initializer/upgrade tests

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Related test coverage terms were found, but conflicting missing-coverage statements require manual review.
- Detection sources: `keyword, negative-test-coverage, test-coverage`
- Category: `upgradeability-initialization`

Evidence:
- `test/documentation coverage`: Matching test coverage terms detected: owner, prank, unauthorized.
- `EVM/src/basetest.sol:1`: Keyword signal matched this readiness finding. Snippet: `DEFAULT_ADMIN_ROLE, admin, emergencyWithdraw, grantRole, guardian, hasRole, implementation, multisig`
- `EVM/src/interface.sol:1`: Keyword signal matched this readiness finding. Snippet: `DEFAULT_ADMIN_ROLE, admin, emergencyWithdraw, grantRole, guardian, hasRole, implementation, multisig`

Negative evidence:
- `.github/workflows/pre-audit-ci.yml:168` `invariant`: Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant`: Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `DEFAULT_ADMIN_ROLE`
- `admin`
- `emergencyWithdraw`
- `grantRole`
- `guardian`
- `hasRole`
- `implementation`
- `multisig`
- `onlyOwner`
- `operator`
- `owner`
- `pause`
- `proxy`
- `rescue`
- `revokeRole`
- `role`
- `setFee`
- `setOracle`
- `setStrategy`
- `setTreasury`

Affected files:
- `EVM/src/basetest.sol`
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2017-07/Exploit_2017-07.t.sol`
- `EVM/test/2017-11/Exploit_2017-11.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`
- `EVM/test/2020-10/Exploit_2020-10.t.sol`

What was detected:

Upgradeable or proxy signals were detected without visible initializer or upgrade authorization tests.

Why it matters:

Initialization and upgrade boundaries can affect every storage, accounting, and role assumption in the protocol.

Historical pattern similarity:

Maps to initialization and upgrade boundary readiness classes.

Recommended defensive checks:

- initializer once
- unauthorized upgrade rejection
- post-upgrade invariant
- implementation ownership

Related Knowledge:

- Historical patterns: pattern-unprotected-initializer, pattern-upgrade-authorization-gap
- Suggested defensive tests: initializer-cannot-run-twice, upgrade-authorization-test, storage-layout-documentation-check
- Related PoCs: poc-2017-07-parity-multisig, poc-2017-11-parity-suicide, poc-2021-03-dodo-crowdpool

Suggested tests:

- Deploy a local proxy or upgradeable instance and assert initialization and upgrade authorization match the documented process.
- Test initializer can only run once.
- Test unauthorized upgrades are rejected.
- Run a local upgrade simulation that preserves key accounting state.

Invariant candidates:

- Initialization and upgrade paths preserve documented state and access boundaries.

Search tags: `upgradeability, initializer, access-control-rule-pack`

### ARK-REENT-003 - Claim/refund flow without state-transition tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Related test coverage terms were found, but conflicting missing-coverage statements require manual review.
- Detection sources: `negative-test-coverage, semantic-lite`
- Category: `reentrancy-value-flow`

Evidence:
- `examples/amm-fixture/src/ToyAMMPool.sol:28` in `addLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amount0);`
- `examples/amm-fixture/src/ToyAMMPool.sol:47` in `removeLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transfer(msg.sender, amount0);`
- `examples/amm-fixture/src/ToyAMMPool.sol:67` in `swap`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amountIn);`

Negative evidence:
- `.github/workflows/pre-audit-ci.yml:168` `invariant`: Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant`: Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

False-positive notes:

Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding.

Detected signals:
- `.call(`
- `callback`
- `call{`
- `claim`
- `flashLoan`
- `onERC1155Received`
- `onERC721Received`
- `redeem`
- `safeTransfer`
- `send`
- `staticcall`
- `transfer`
- `transferFrom`
- `withdraw`

Affected files:
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2018-04/Exploit_2018-04.t.sol`
- `EVM/test/2018-10/Exploit_2018-10.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-06/Exploit_2020-06.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`
- `EVM/test/2020-10/Exploit_2020-10.t.sol`

What was detected:

Claim, refund, or payout signals were detected without visible state-transition or double-claim tests.

Why it matters:

Claim and refund flows often depend on one-way state transitions that should be explicit before audit intake.

Historical pattern similarity:

Maps to duplicate-claim and state-transition readiness classes.

Recommended defensive checks:

- double claim prevention
- claim/refund mutual exclusion
- failed transfer behavior


Suggested tests:

- Assert claim or refund can only happen once per entitlement and failed transfers cannot leave reusable claim state.
- Test claim/refund state transitions before and after value transfer.
- Test double-claim and repeated refund attempts.
- Assert failed external transfers do not corrupt claim state.

Invariant candidates:

- Claimable accounting decreases exactly once for each successful claim or refund.

Search tags: `reentrancy-review, claim-flow, reentrancy-rule-pack`

### ARK-RWD-001 - Reward accounting without conservation tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected, and explicit missing-test coverage statements were found.
- Detection sources: `negative-test-coverage, semantic-lite`
- Category: `reward-accounting`

Evidence:
- `examples/generated-artifact-self-ingestion-fixture/src/SelfIngestionToy.sol:48` in `claimReward`: Solidity function shape matches this readiness finding. Snippet: `rewardPerTokenStored += 1;`
- `examples/negative-evidence-fixture/src/FakeGlobalVault.sol:51` in `claimReward`: Solidity function shape matches this readiness finding. Snippet: `rewardPerTokenStored += 1;`
- `examples/oracle-staking-fixture/src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`

Negative evidence:
- `.github/workflows/pre-audit-ci.yml:168` `invariant`: Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant`: Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

False-positive notes:

Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding.

Detected signals:
- `accumulator`
- `claim`
- `claimReward`
- `cooldown`
- `earned`
- `index`
- `pendingReward`
- `reward`
- `rewardPerToken`
- `rewards`
- `shares`
- `stake`
- `totalStaked`
- `unstake`
- `withdraw`

Affected files:
- `EVM/src/basetest.sol`
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2018-04/Exploit_2018-04.t.sol`
- `EVM/test/2018-10/Exploit_2018-10.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-06/Exploit_2020-06.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`

What was detected:

Reward, stake, claim, or accounting signals were detected without visible reward conservation tests.

Why it matters:

Reward systems can silently over-distribute or under-distribute when stake weights, timing, and funding change.

Historical pattern similarity:

Maps to reward accounting mismatch readiness classes.

Recommended defensive checks:

- funded reward conservation
- multi-user distribution
- stake/unstake around reward updates

Related Knowledge:

- Historical patterns: pattern-reward-overclaim, pattern-accounting-index-drift
- Suggested defensive tests: reward-conservation-multi-user, claim-twice-reverts-or-noops, rewardPerToken-monotonicity
- Related PoCs: poc-2020-12-warp-finance, poc-2020-08-opyn, poc-2020-09-bzx-ifusdc

Suggested tests:

- Fund rewards, run multiple users through stake/claim/unstake sequences, and assert total claimed remains bounded by funded rewards.
- Assert funded rewards cover claimed plus remaining claimable amounts.
- Test stake, unstake, claim, and notify reward lifecycle.
- Cover multi-user reward distribution.

Invariant candidates:

- Claimed rewards plus remaining claimable rewards do not exceed funded rewards beyond documented rounding.

Search tags: `reward-accounting, staking-rule-pack, pre-audit-readiness`

### ARK-RWD-003 - Claim flow without double-claim prevention tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected, and explicit missing-test coverage statements were found.
- Detection sources: `negative-test-coverage, semantic-lite`
- Category: `reward-accounting`

Evidence:
- `examples/generated-artifact-self-ingestion-fixture/src/SelfIngestionToy.sol:48` in `claimReward`: Solidity function shape matches this readiness finding. Snippet: `rewardPerTokenStored += 1;`
- `examples/negative-evidence-fixture/src/FakeGlobalVault.sol:51` in `claimReward`: Solidity function shape matches this readiness finding. Snippet: `rewardPerTokenStored += 1;`
- `examples/oracle-staking-fixture/src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`

Negative evidence:
- `.github/workflows/pre-audit-ci.yml:168` `invariant`: Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant`: Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

False-positive notes:

Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding.

Detected signals:
- `accumulator`
- `claim`
- `claimReward`
- `cooldown`
- `earned`
- `index`
- `pendingReward`
- `reward`
- `rewardPerToken`
- `rewards`
- `shares`
- `stake`
- `totalStaked`
- `unstake`
- `withdraw`

Affected files:
- `EVM/src/basetest.sol`
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2018-04/Exploit_2018-04.t.sol`
- `EVM/test/2018-10/Exploit_2018-10.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-06/Exploit_2020-06.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`

What was detected:

Claim or claimReward signals were detected without visible repeated-claim or overclaim tests.

Why it matters:

Claim flows depend on updating accrued state at exactly the right time.

Historical pattern similarity:

Maps to duplicate-claim and reward accounting mismatch classes.

Recommended defensive checks:

- double claim prevention
- claim state reset
- multi-user claim ordering


Suggested tests:

- Assert claim twice without new rewards returns zero or reverts according to documented policy.
- Test repeated claim attempts after successful claim.
- Test claim after stake/unstake boundary transitions.
- Assert paid amounts update before repeatable state is exposed.

Invariant candidates:

- Each reward increment can be claimed at most once per entitled account.

Search tags: `reward-accounting, claim-flow, staking-rule-pack`

### ARK-RWD-004 - Lock/cooldown reward lifecycle not tested

- Priority: `Low readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected, and explicit missing-test coverage statements were found.
- Detection sources: `negative-test-coverage, semantic-lite`
- Category: `reward-accounting`

Evidence:
- `examples/generated-artifact-self-ingestion-fixture/src/SelfIngestionToy.sol:48` in `claimReward`: Solidity function shape matches this readiness finding. Snippet: `rewardPerTokenStored += 1;`
- `examples/negative-evidence-fixture/src/FakeGlobalVault.sol:51` in `claimReward`: Solidity function shape matches this readiness finding. Snippet: `rewardPerTokenStored += 1;`
- `examples/oracle-staking-fixture/src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`

Negative evidence:
- `.github/workflows/pre-audit-ci.yml:168` `invariant`: Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant`: Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

False-positive notes:

Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding.

Detected signals:
- `accumulator`
- `claim`
- `claimReward`
- `cooldown`
- `earned`
- `index`
- `pendingReward`
- `reward`
- `rewardPerToken`
- `rewards`
- `shares`
- `stake`
- `totalStaked`
- `unstake`
- `withdraw`

Affected files:
- `EVM/src/basetest.sol`
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2018-04/Exploit_2018-04.t.sol`
- `EVM/test/2018-10/Exploit_2018-10.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-06/Exploit_2020-06.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`

What was detected:

Lock, cooldown, epoch, or vesting signals were detected without visible lifecycle tests.

Why it matters:

Time or epoch-based reward states are easy to mis-handle around boundary transitions.

Historical pattern similarity:

Maps to reward lifecycle and state-transition readiness classes.

Recommended defensive checks:

- epoch boundaries
- cooldown transitions
- vesting claim timing


Suggested tests:

- Advance local time/epochs and assert reward and withdrawal state transitions follow documented policy.
- Test lock, cooldown, unstake, and claim ordering.
- Test early exit restrictions if applicable.
- Assert reward checkpointing around lifecycle boundaries.

Invariant candidates:

- Lifecycle transitions preserve user stake and reward checkpoints.

Search tags: `reward-accounting, staking-lifecycle, staking-rule-pack`

### ARK-AMM-002 - LP share accounting without mint/burn boundary tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Related test coverage terms were found, but conflicting missing-coverage statements require manual review.
- Detection sources: `negative-test-coverage, semantic-lite`
- Category: `amm-lp-accounting`

Evidence:
- `examples/amm-fixture/src/ToyAMMPool.sol:24` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `examples/amm-fixture/src/ToyAMMPool.sol:28` in `addLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amount0);`
- `examples/amm-fixture/src/ToyAMMPool.sol:47` in `removeLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transfer(msg.sender, amount0);`

Negative evidence:
- `.github/workflows/pre-audit-ci.yml:168` `invariant`: Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant`: Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

False-positive notes:

Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding.

Detected signals:
- `LP`
- `addLiquidity`
- `amountIn`
- `amountOut`
- `balanceOf`
- `burn`
- `deadline`
- `getAmountOut`
- `getReserves`
- `invariant`
- `kLast`
- `liquidity`
- `mint`
- `pair`
- `pool`
- `quote`
- `removeLiquidity`
- `reserve`
- `reserve0`
- `reserve1`

Affected files:
- `EVM/src/basetest.sol`
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2018-04/Exploit_2018-04.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-06/Exploit_2020-06.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`
- `EVM/test/2020-10/Exploit_2020-10.t.sol`

What was detected:

LP supply, mint, burn, or share-accounting signals were detected without visible first-provider, proportional mint/burn, or rounding boundary tests.

Why it matters:

LP share accounting controls who owns pool value; boundary mistakes can distort deposits, withdrawals, or low-liquidity behavior.

Historical pattern similarity:

Maps to share inflation and liquidity accounting readiness classes.

Recommended defensive checks:

- first liquidity provider behavior
- proportional minting
- proportional withdrawal
- dust handling

Related Knowledge:

- Historical patterns: pattern-share-inflation-donation, pattern-amm-invariant-steering
- Suggested defensive tests: first-liquidity-provider-test, proportional-minting-test, proportional-withdrawal-test
- Related PoCs: poc-2021-10-indexed-finance, poc-2025-12-yeth

Suggested tests:

- Test first liquidity, repeated add/remove liquidity, and tiny-liquidity burn cases to verify LP shares remain proportional.
- Test first liquidity provider behavior.
- Test proportional minting and proportional withdrawal.
- Cover rounding and dust handling during mint/burn.

Invariant candidates:

- LP share supply tracks pool ownership within documented rounding.

Search tags: `amm-lp-accounting, amm-rule-pack, share-accounting`

### ARK-LEND-001 - Collateral/debt solvency invariant not covered by tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Related test coverage terms were found, but conflicting missing-coverage statements require manual review.
- Detection sources: `negative-test-coverage, semantic-lite`
- Category: `lending-solvency`

Evidence:
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:37` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:41` in `collateralValue`: Solidity function shape matches this readiness finding. Snippet: `return collateral[user] * price / 1e18;`
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:46` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`

Negative evidence:
- `.github/workflows/pre-audit-ci.yml:168` `invariant`: Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant`: Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

False-positive notes:

Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding.

Detected signals:
- `LTV`
- `accrueInterest`
- `borrow`
- `borrowIndex`
- `cash`
- `closeFactor`
- `collateral`
- `collateralFactor`
- `debt`
- `guardian`
- `health factor`
- `healthFactor`
- `interestIndex`
- `liquidate`
- `liquidation`
- `liquidationBonus`
- `liquidationThreshold`
- `liquidator`
- `principal`
- `ratePerSecond`

Affected files:
- `EVM/src/basetest.sol`
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2017-07/Exploit_2017-07.t.sol`
- `EVM/test/2017-11/Exploit_2017-11.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-06/Exploit_2020-06.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`

What was detected:

Collateral, debt, borrow, repay, or health-factor signals were detected without visible solvency invariant tests.

Why it matters:

Lending systems depend on collateral and debt accounting staying aligned across every user action.

Historical pattern similarity:

Maps to collateral/debt invariant and oracle-dependent lending readiness classes. This is defensive review context, not vulnerability confirmation.

Recommended defensive checks:

- collateral debt invariant
- unsafe withdrawal rejection
- borrow limit boundary
- repay/deposit accounting

Related Knowledge:

- Historical patterns: pattern-collateral-debt-invariant, pattern-oracle-stale-price
- Suggested defensive tests: collateral-debt-invariant, borrow-limit-boundary-test, unsafe-withdrawal-rejection
- Related PoCs: poc-2025-11-moonwell, poc-2020-11-cheese-bank

Suggested tests:

- Assert debt cannot exceed documented collateral constraints and collateral withdrawals cannot make a position unsafe unless intended and tested.
- Assert solvent positions remain solvent after deposit, borrow, repay, and withdraw flows.
- Test debt cannot exceed documented collateral constraints.
- Test unsafe withdrawals are rejected or explicitly documented.

Invariant candidates:

- Collateral value and debt remain inside documented solvency constraints after allowed user actions.

Search tags: `lending-solvency, lending-rule-pack, pre-audit-readiness`

### ARK-LEND-002 - Liquidation boundary tests missing

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Related test coverage terms were found, but conflicting missing-coverage statements require manual review.
- Detection sources: `negative-test-coverage, semantic-lite`
- Category: `lending-liquidation`

Evidence:
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:37` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:41` in `collateralValue`: Solidity function shape matches this readiness finding. Snippet: `return collateral[user] * price / 1e18;`
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:46` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`

Negative evidence:
- `.github/workflows/pre-audit-ci.yml:168` `invariant`: Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant`: Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

False-positive notes:

Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding.

Detected signals:
- `LTV`
- `accrueInterest`
- `borrow`
- `borrowIndex`
- `cash`
- `closeFactor`
- `collateral`
- `collateralFactor`
- `debt`
- `guardian`
- `health factor`
- `healthFactor`
- `interestIndex`
- `liquidate`
- `liquidation`
- `liquidationBonus`
- `liquidationThreshold`
- `liquidator`
- `principal`
- `ratePerSecond`

Affected files:
- `EVM/src/basetest.sol`
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2017-07/Exploit_2017-07.t.sol`
- `EVM/test/2017-11/Exploit_2017-11.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-06/Exploit_2020-06.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`

What was detected:

Liquidation, threshold, bonus, close factor, or seize signals were detected without visible just-above/just-below boundary tests.

Why it matters:

Liquidation boundary errors can reject valid liquidations, liquidate solvent positions, or distort seized collateral accounting.

Historical pattern similarity:

Maps to liquidation boundary and collateral accounting readiness classes.

Recommended defensive checks:

- just-above threshold
- just-below threshold
- bonus bounds
- partial liquidation math

Related Knowledge:

- Historical patterns: pattern-collateral-debt-invariant, pattern-oracle-stale-price
- Suggested defensive tests: just-above-threshold-test, just-below-threshold-test, partial-liquidation-math
- Related PoCs: poc-2025-11-moonwell, poc-2020-11-cheese-bank

Suggested tests:

- Test a position just above threshold cannot be liquidated and a position just below threshold can be liquidated within documented bonus bounds.
- Test just-above-threshold positions cannot be liquidated.
- Test just-below-threshold positions can be liquidated according to policy.
- Assert liquidation bonus and close factor stay within documented bounds.

Invariant candidates:

- Liquidation eligibility changes only at documented threshold boundaries.

Search tags: `lending-liquidation, liquidation-boundary, lending-rule-pack`

### ARK-LEND-003 - Interest/index accounting not covered by rounding and time-step tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Related test coverage terms were found, but conflicting missing-coverage statements require manual review.
- Detection sources: `negative-test-coverage, semantic-lite`
- Category: `lending-interest-index`

Evidence:
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:37` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:41` in `collateralValue`: Solidity function shape matches this readiness finding. Snippet: `return collateral[user] * price / 1e18;`
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:46` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`

Negative evidence:
- `.github/workflows/pre-audit-ci.yml:168` `invariant`: Coverage term appears in negative context. Snippet: `python3 scripts/search_knowledge.py "missing invariant" --json`
- `CHANGELOG.md:459` `invariant tests`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:459` `invariant test`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`
- `CHANGELOG.md:222` `invariant`: Coverage term appears in negative context. Snippet: `- Search index includes invariant/test-plan generator surfaces.`
- `CHANGELOG.md:459` `invariant`: Coverage term appears in negative context. Snippet: `- Negative-context comments such as "missing invariant tests" are no longer`

False-positive notes:

Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding.

Detected signals:
- `LTV`
- `accrueInterest`
- `borrow`
- `borrowIndex`
- `cash`
- `closeFactor`
- `collateral`
- `collateralFactor`
- `debt`
- `guardian`
- `health factor`
- `healthFactor`
- `interestIndex`
- `liquidate`
- `liquidation`
- `liquidationBonus`
- `liquidationThreshold`
- `liquidator`
- `principal`
- `ratePerSecond`

Affected files:
- `EVM/src/basetest.sol`
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2017-07/Exploit_2017-07.t.sol`
- `EVM/test/2017-11/Exploit_2017-11.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-06/Exploit_2020-06.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`

What was detected:

Interest index, borrow index, exchange rate, utilization, or accrual signals were detected without visible rounding and time-step tests.

Why it matters:

Interest/index accounting can drift when rates, time steps, small balances, and repeated accrual interact.

Historical pattern similarity:

Maps to accounting index drift and precision readiness classes.

Recommended defensive checks:

- index monotonicity
- small-balance rounding
- borrow/repay around accrual
- drift bound

Related Knowledge:

- Historical patterns: pattern-accounting-index-drift, pattern-precision-rounding-loss
- Suggested defensive tests: interest-index-monotonicity, small-balance-rounding-test, borrow-repay-around-accrual
- Related PoCs: poc-2020-09-bzx-ifusdc, poc-2020-08-opyn

Suggested tests:

- Advance local time across multiple accrual steps and assert borrow indexes and balances remain monotonic and bounded by documented rounding.
- Test interest or borrow index monotonicity.
- Cover small balances and repeated accrual.
- Test borrow and repay before and after accrual.

Invariant candidates:

- Interest and borrow indexes move according to documented rate policy and do not drift unexpectedly.

Search tags: `lending-interest-index, precision, lending-rule-pack`

### ARK-LEND-005 - Reserve/cash accounting assumptions not covered

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Related test coverage terms were found, but conflicting missing-coverage statements require manual review.
- Detection sources: `negative-test-coverage, semantic-lite`
- Category: `lending-liquidity`

Evidence:
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:37` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:41` in `collateralValue`: Solidity function shape matches this readiness finding. Snippet: `return collateral[user] * price / 1e18;`
- `examples/amm-lending-hybrid-fixture/src/ToyHybridMarket.sol:46` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`

Negative evidence:
- `docs/LENDING_RULE_PACK.md:7` `solvency`: Coverage term appears in negative context. Snippet: `## ARK-LEND-001 - Collateral/Debt Solvency Invariant Not Covered By Tests`
- `docs/LENDING_RULE_PACK.md:24` `solvency`: Coverage term appears in negative context. Snippet: `- High confidence requires Solidity-level lending evidence plus missing solvency invariant tests.`
- `docs/LENDING_RULE_PACK.md:27` `liquidation boundary`: Coverage term appears in negative context. Snippet: `## ARK-LEND-002 - Liquidation Boundary Tests Missing`
- `docs/LENDING_RULE_PACK.md:5` `interest index`: Coverage term appears in negative context. Snippet: `Use this rule pack when a repository contains lending markets, collateral/debt accounting, borrowing, repayment, interest indexes, liquidation boundaries, or oracle-dependent health-factor logic.`
- `docs/READINESS_SCORE.md:68` `solvency`: Coverage term appears in negative context. Snippet: `- lending collateral/debt solvency without invariant tests;`

False-positive notes:

Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding.

Detected signals:
- `LTV`
- `accrueInterest`
- `borrow`
- `borrowIndex`
- `cash`
- `closeFactor`
- `collateral`
- `collateralFactor`
- `debt`
- `guardian`
- `health factor`
- `healthFactor`
- `interestIndex`
- `liquidate`
- `liquidation`
- `liquidationBonus`
- `liquidationThreshold`
- `liquidator`
- `principal`
- `ratePerSecond`

Affected files:
- `EVM/src/basetest.sol`
- `EVM/src/interface.sol`
- `EVM/src/tokenhelper.sol`
- `EVM/templates/ExploitTemplate.t.sol`
- `EVM/test/2017-07/Exploit_2017-07.t.sol`
- `EVM/test/2017-11/Exploit_2017-11.t.sol`
- `EVM/test/2020-04/Exploit_2020-04.t.sol`
- `EVM/test/2020-06/Exploit_2020-06.t.sol`
- `EVM/test/2020-08/Exploit_2020-08.t.sol`
- `EVM/test/2020-09/Exploit_2020-09.t.sol`

What was detected:

Cash, reserves, total borrows, utilization, or available-liquidity signals were detected without visible cash/debt consistency tests.

Why it matters:

Reserve and cash accounting define whether borrowers can draw liquidity and whether repayments restore accounting state.

Historical pattern similarity:

Maps to cash/debt mismatch and liquidity accounting readiness classes.

Recommended defensive checks:

- available liquidity bound
- repay updates cash/debt
- reserve withdrawal constraints
- utilization bounds

Related Knowledge:

- Historical patterns: pattern-collateral-debt-invariant, pattern-accounting-index-drift
- Suggested defensive tests: available-liquidity-bound, repay-cash-debt-consistency, reserve-withdrawal-constraints
- Related PoCs: poc-2020-11-cheese-bank

Suggested tests:

- Assert borrow reverts above available liquidity and repay updates cash, debt, reserves, and utilization consistently.
- Test borrow cannot exceed available liquidity.
- Test repay updates cash, debt, and reserves consistently.
- Assert reserves cannot be withdrawn beyond documented constraints.

Invariant candidates:

- Cash, total borrows, total reserves, and utilization remain internally consistent.

Search tags: `lending-liquidity, reserve-accounting, lending-rule-pack`

## Suppressed Readiness Gaps

No readiness gaps were suppressed in this run.

## Suggested Foundry Invariant Skeletons

- Skeleton not generated in this run.
- To generate: `python3 scripts/pre_audit_scan.py --root . --generate-invariant-skeletons`

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
- **invariant conservation** (`amm`): Swaps should preserve the AMM invariant within fee and rounding expectations.
- **swap does not create value** (`amm`): No swap sequence should create value outside documented fee mechanics.
- **liquidity add/remove proportionality** (`amm`): Liquidity mint/burn should be proportional to reserves within expected rounding.
- **fee growth consistency** (`amm`): Fee growth should be monotonic and attributable to swaps or configured fee paths.
- **collateralization invariant** (`lending`): Borrower positions should respect collateralization requirements after every user action.

## Audit Readiness Checklist

- [ ] Core user flows have deterministic unit tests.
- [ ] Accounting, oracle, reward, and role assumptions are documented.
- [ ] Foundry invariant tests cover value conservation and access boundaries.
- [ ] Fuzz tests cover edge cases, rounding, and unexpected user sequences.
- [ ] Privileged roles, upgrade controls, and emergency controls are documented and tested.
- [ ] Known limitations are written down for auditors.
- [ ] A formal audit scope names contracts, commit hash, deployment assumptions, and out-of-scope areas.

## Generated Issue Checklist

- No issue checklist file was requested in this run.
- To generate one: `python3 scripts/pre_audit_scan.py --root . --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md`

## GitHub Action Outputs

- Markdown Report: `ARKHEIONX_PRE_AUDIT_REPORT.md`

## Search Tags

`access-control-review`, `arkheionx`, `audit-preparation`, `defi-security`, `foundry`, `historical-exploit-pattern`, `indie-defi`, `invariant-testing`, `oracle-risk`, `pre-audit-readiness`, `reentrancy-review`, `root-cause-analysis`, `smart-contract-security`, `solidity-security`, `vault-accounting`

## Recommended Next Steps

1. Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
2. Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
3. Run a formal smart contract audit before mainnet launch or before handling real user funds.

## What This Report Does Not Prove

- It does not prove protocol safety.
- It does not confirm exploitability.
- It does not replace manual review.
- It does not replace a formal audit.

## Formal Audit Recommendation

Run a formal smart contract audit before mainnet deployment, before material TVL, or before handling real user funds.

