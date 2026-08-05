# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/amm-fixture`
- Generated at: `2026-08-05T18:37:05+00:00`
- Protocol type: `amm`
- Protocol confidence: `manual`
- Files scanned: `4`
- Scanner version: `2.0.1`
- Output profile: `standard` (Standard)

| File class       | Count |
| ---------------- | ----- |
| Solidity sources | 1     |
| Solidity tests   | 1     |
| Docs             | 1     |
| Configs          | 1     |
| Workflows        | 0     |

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

- Files considered: `4`
- Files scanned: `4`
- Files ignored: `0`
- Generated Arkheionx artifacts ignored: `0`

## Disclaimer

This is an automated pre-audit readiness report. It is not a formal audit, does not prove the absence or presence of vulnerabilities, does not authorize live-target testing, and should only be used on repositories you own or are authorized to review. A formal audit is recommended before handling real user funds.

## Analysis Quality

| Source                   | Status   |
| ------------------------ | -------- |
| Keyword scan             | enabled  |
| Semantic-lite extraction | enabled  |
| Semantic contracts       | 2        |
| Semantic test files      | 1        |
| Slither                  | disabled |
| Slither detectors        | 0        |
| Test coverage mapping    | enabled  |
| Negative evidence        | 0        |

## Executive Summary

Arkheionx scanned `examples/amm-fixture` as `amm` readiness context. This is a local/static pre-audit readiness report, not a formal audit.

- Readiness score: **43/100**
- Score band: **Early readiness**
- Active readiness gaps: `12`
- Suppressed readiness gaps: `0`
- Active rule packs: `access-control, amm, docs, lending, oracle, reentrancy-value-flow, rewards, testing, vault`
- Generated artifacts ignored: `0`
- Top readiness gaps:
  - **ARK-AMM-002 (High readiness gap):** LP share accounting without mint/burn boundary tests - Add tests for first liquidity provider behavior, proportional LP minting/burning, withdrawal rounding, and dust handling.
  - **ARK-AMM-003 (High readiness gap):** Spot-price or reserve-price dependency without manipulation-resistance tests - Add local reserve-movement tests and document whether spot, TWAP, or external oracle assumptions are intended.
  - **ARK-AMM-001 (Medium readiness gap):** AMM invariant assumptions not covered by tests - Add local tests or invariants showing swaps and liquidity operations preserve documented AMM accounting within fee and rounding bounds.
  - **ARK-AMM-004 (Medium readiness gap):** Fee-on-transfer or non-standard token assumptions not documented - Document supported token assumptions or add balanceBefore/balanceAfter accounting tests for fee-on-transfer and non-standard token behavior.
  - **ARK-AMM-005 (Medium readiness gap):** Slippage/min-output constraints missing or unclear - Add user-provided min-output and stale-quote tests, or document why swaps are not user-facing and how price movement is bounded.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
  - Review state update order and add malicious local receiver tests for callback-capable flows.
  - Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
  - Run a formal smart contract audit before mainnet launch or before handling real user funds.

## Fix First

| Rank | Finding                                                                                    | Rule Family | Why Fix First                                                                                                                          | Next Action                                                                                                                                    |
| ---- | ------------------------------------------------------------------------------------------ | ----------- | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | ARK-AMM-002 - LP share accounting without mint/burn boundary tests                         | amm         | higher-priority readiness blocker; high-confidence local evidence; appears across multiple files; clear defensive tests are available. | Add or review: Test first liquidity, repeated add/remove liquidity, and tiny-liquidity burn cases to verify LP shares remain proportional.     |
| 2    | ARK-AMM-003 - Spot-price or reserve-price dependency without manipulation-resistance tests | amm         | higher-priority readiness blocker; high-confidence local evidence; appears across multiple files; clear defensive tests are available. | Add or review: Move reserves in a local pool test and assert dependent protocol decisions respect documented price bounds or TWAP assumptions. |
| 3    | ARK-AMM-001 - AMM invariant assumptions not covered by tests                               | amm         | appears across multiple files; clear defensive tests are available.                                                                    | Add or review: Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.          |
| 4    | ARK-AMM-004 - Fee-on-transfer or non-standard token assumptions not documented             | amm         | appears across multiple files; clear defensive tests are available.                                                                    | Add or review: Use a local fee-on-transfer token mock or document that such tokens are unsupported and guarded by configuration.               |
| 5    | ARK-AMM-005 - Slippage/min-output constraints missing or unclear                           | amm         | appears across multiple files; clear defensive tests are available.                                                                    | Add or review: Assert swaps revert or follow documented policy when amountOut falls below a user-provided bound or quote is stale.             |

## Finding Groups

### Findings by Rule Family

| Rule Family           | Active Findings |
| --------------------- | --------------- |
| amm                   | 5               |
| oracle                | 4               |
| reentrancy-value-flow | 2               |
| testing               | 1               |

### Findings by Confidence

| Confidence | Active Findings |
| ---------- | --------------- |
| high       | 2               |
| low        | 5               |
| medium     | 5               |

## Suppression Summary

- Suppressions loaded: `0`
- Suppressions applied: `0`
- Suppressions should include a reason and be revisited before launch or external review.

## Detected Protocol Shape

- Detected protocol type: `amm`
- Confidence: `manual`
- Protocol score signals: `{"amm": 163, "lending": 0, "oracle": 0, "staking": 0, "vault": 0}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                    | Score | Max | Notes                                                                                                                                                          |
| --------------------------- | ----- | --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository Structure        | 12    | 15  | Solidity sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                             |
| Test Presence               | 20    | 20  | Solidity test files detected.; Assert usage detected.; Foundry or Hardhat test environment detected.; Protocol-specific terms appear in the testable codebase. |
| Invariant Fuzz Readiness    | 0     | 20  | No positive signal detected.                                                                                                                                   |
| Defi Risk Coverage          | 5     | 20  | Accounting assumptions have at least some documented or tested controls.                                                                                       |
| Documentation Readiness     | 3     | 10  | README detected.                                                                                                                                               |
| Operational Admin Readiness | 3     | 15  | Upgradeability is absent or has visible documentation/test terms.                                                                                              |

## Top Readiness Gaps

| ID          | Priority             | Category              | Title                                                                        |
| ----------- | -------------------- | --------------------- | ---------------------------------------------------------------------------- |
| ARK-AMM-002 | High readiness gap   | amm-lp-accounting     | LP share accounting without mint/burn boundary tests                         |
| ARK-AMM-003 | High readiness gap   | amm-pricing           | Spot-price or reserve-price dependency without manipulation-resistance tests |
| ARK-AMM-001 | Medium readiness gap | amm-invariant         | AMM invariant assumptions not covered by tests                               |
| ARK-AMM-004 | Medium readiness gap | amm-token-assumptions | Fee-on-transfer or non-standard token assumptions not documented             |
| ARK-AMM-005 | Medium readiness gap | amm-slippage          | Slippage/min-output constraints missing or unclear                           |

## Rule Pack Coverage

| Rule Pack                                 | Detected | Findings | Docs                                    |
| ----------------------------------------- | -------- | -------- | --------------------------------------- |
| Vault Rule Pack                           | yes      | 0        | docs/VAULT_RULE_PACK.md                 |
| Oracle Rule Pack                          | yes      | 4        | docs/ORACLE_RULE_PACK.md                |
| Access Control / Upgradeability Rule Pack | no       | 0        | docs/ACCESS_CONTROL_RULE_PACK.md        |
| Reentrancy / Value Flow Rule Pack         | yes      | 2        | docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md |
| Staking / Reward Accounting Rule Pack     | yes      | 0        | docs/REWARD_ACCOUNTING_RULE_PACK.md     |
| AMM Rule Pack                             | yes      | 5        | docs/AMM_RULE_PACK.md                   |
| Lending Rule Pack                         | no       | 0        | docs/LENDING_RULE_PACK.md               |

### Vault Rule Pack

- Signals detected: `4`
- Signal terms: `balanceOf, mint, shares, totalSupply`
- Findings: `0`
- Docs: `docs/VAULT_RULE_PACK.md`
- Suggested tests:
  - totalAssets consistency
  - deposit/withdraw roundtrip
  - share conversion rounding
  - strategy gain/loss lifecycle

### Oracle Rule Pack

- Signals detected: `4`
- Signal terms: `getReserves, pool, reserve0, reserve1`
- Findings: `4`
- Docs: `docs/ORACLE_RULE_PACK.md`
- Suggested tests:
  - stale price rejection
  - decimals normalization
  - price bounds
  - TWAP vs spot behavior

### Reentrancy / Value Flow Rule Pack

- Signals detected: `2`
- Signal terms: `transfer, transferFrom`
- Findings: `2`
- Docs: `docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md`
- Suggested tests:
  - reentrant receiver mock
  - state update ordering
  - double claim prevention
  - failed external call behavior

### Staking / Reward Accounting Rule Pack

- Signals detected: `1`
- Signal terms: `shares`
- Findings: `0`
- Docs: `docs/REWARD_ACCOUNTING_RULE_PACK.md`
- Suggested tests:
  - reward conservation
  - no overclaim
  - index monotonicity
  - stake/unstake/claim lifecycle

### AMM Rule Pack

- Signals detected: `14`
- Signal terms: `addLiquidity, amountIn, amountOut, balanceOf, getAmountOut, getReserves, kLast, mint, pool, removeLiquidity, reserve0, reserve1, swap, totalSupply`
- Findings: `5`
- Docs: `docs/AMM_RULE_PACK.md`
- Suggested tests:
  - swap invariant conservation
  - LP share proportionality
  - TWAP or reserve bounds
  - minOut enforcement

## Risk Signal Summary

### Vault Erc4626

- Detected signals: `balanceOf, mint, shares, totalSupply`
- Files with signals: `2`
- Example files: `src/ToyAMMPool.sol, test/ToyAMMPool.t.sol`

### Vault Accounting

- Detected signals: `balanceOf, mint, shares, totalSupply`
- Files with signals: `2`
- Example files: `src/ToyAMMPool.sol, test/ToyAMMPool.t.sol`

### Vault Pricing

- Detected signals: `getReserves`
- Files with signals: `1`
- Example files: `src/ToyAMMPool.sol`

### Oracle

- Detected signals: `getReserves, pool, reserve0, reserve1`
- Files with signals: `2`
- Example files: `src/ToyAMMPool.sol, test/ToyAMMPool.t.sol`

### Reentrancy Value Flow

- Detected signals: `transfer, transferFrom`
- Files with signals: `2`
- Example files: `src/ToyAMMPool.sol, test/ToyAMMPool.t.sol`

### Staking Rewards

- Detected signals: `shares`
- Files with signals: `1`
- Example files: `src/ToyAMMPool.sol`

### Amm

- Detected signals: `addLiquidity, amountIn, amountOut, balanceOf, getAmountOut, getReserves, kLast, mint, pool, removeLiquidity, reserve0, reserve1, swap, totalSupply`
- Files with signals: `2`
- Example files: `src/ToyAMMPool.sol, test/ToyAMMPool.t.sol`

### Testing And Documentation

- Test Directory: `True`
- Foundry Tests: `True`
- Hardhat Tests: `False`
- Test File Count: `1`
- Invariant Tests: `False`
- Fuzz Tests: `False`
- Handler Contracts: `False`
- Assert Usage: `True`
- Assert Count: `2`
- Forge Std: `True`
- Echidna: `False`
- Slither: `False`
- Ci Workflow: `False`
- Edge Case Tests: `False`
- Negative Evidence Count: `0`
- Negative Evidence Terms: `[]`
- Test files: `test/ToyAMMPool.t.sol`

## Historical Exploit-Pattern Similarity

### Harvest/Yearn-style oracle or pool price readiness gap

- Confidence: `high`
- Detected signals: `balanceOf, getReserves, mint, pool, reserve0, reserve1, shares, totalSupply`
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

- Confidence: `medium`
- Detected signals: `balanceOf, mint, shares, totalSupply`
- Why it matters: Vaults need explicit conservation and roundtrip properties because share math, fees, donations, and rounding can break user-value assumptions.
- Failed assumption class: Shares and assets remain exchangeable according to documented accounting rules.
- Broken invariant class: Deposits, withdrawals, redemptions, and fee paths conserve value within expected rounding bounds.
- Recommended defensive checks:
  - Add totalAssets consistency tests.
  - Add deposit-withdraw roundtrip tests across small and large amounts.
  - Test donation, zero-supply, rounding, and fee paths.
- Suggested test/invariant: Invariant: deposit followed by withdraw does not create value and does not strand assets beyond expected rounding.
- Search tags: `vault-security, share-accounting, totalAssets, audit-readiness`

### Reentrancy-sensitive value flow review recommended

- Confidence: `medium`
- Detected signals: `balanceOf, mint, shares, totalSupply, transfer, transferFrom`
- Why it matters: External calls around withdrawals, claims, callbacks, or token transfers have repeatedly exposed state-ordering assumptions.
- Failed assumption class: External receivers cannot re-enter before internal accounting reaches a safe state.
- Broken invariant class: Value flow remains single-entry and accounting is updated before control leaves the contract.
- Recommended defensive checks:
  - Review checks-effects-interactions order.
  - Add reentrancy tests using local receiver mocks.
  - Use guards where the protocol design requires them.
- Suggested test/invariant: Test: malicious local receiver cannot withdraw, claim, or redeem twice through a callback.
- Search tags: `reentrancy-review, value-flow, checks-effects-interactions`

### Reward accounting mismatch review recommended

- Confidence: `low`
- Detected signals: `shares`
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
- Detected signals: `addLiquidity, amountIn, amountOut, balanceOf, getAmountOut, getReserves, kLast, mint, pool, removeLiquidity, reserve0, reserve1, swap, totalSupply`
- Why it matters: AMM integrations need invariant and reserve assumptions tested under swaps, liquidity changes, fees, and price movements.
- Failed assumption class: Pool reserves and quote functions remain representative for protocol decisions.
- Broken invariant class: Swaps and liquidity changes cannot create value outside documented fee mechanics.
- Recommended defensive checks:
  - Add invariant conservation tests.
  - Test add/remove liquidity proportionality.
  - Avoid relying on same-block spot reserves without documented controls.
- Suggested test/invariant: Invariant: swaps and liquidity operations preserve the AMM invariant within fee and rounding bounds.
- Search tags: `amm-invariant, liquidity, spot-price, reserve-manipulation`

## All Readiness Gaps

### ARK-AMM-002 - LP share accounting without mint/burn boundary tests

- Priority: `High readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `semantic-lite`
- Category: `amm-lp-accounting`

Evidence:
- `src/ToyAMMPool.sol:24` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `src/ToyAMMPool.sol:28` in `addLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amount0);`
- `src/ToyAMMPool.sol:47` in `removeLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transfer(msg.sender, amount0);`

Detected signals:
- `addLiquidity`
- `amountIn`
- `amountOut`
- `balanceOf`
- `getAmountOut`
- `getReserves`
- `kLast`
- `mint`
- `pool`
- `removeLiquidity`
- `reserve0`
- `reserve1`
- `swap`
- `totalSupply`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

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

### ARK-AMM-003 - Spot-price or reserve-price dependency without manipulation-resistance tests

- Priority: `High readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `semantic-lite`
- Category: `amm-pricing`

Evidence:
- `src/ToyAMMPool.sol:24` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `src/ToyAMMPool.sol:28` in `addLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amount0);`
- `src/ToyAMMPool.sol:47` in `removeLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transfer(msg.sender, amount0);`

Detected signals:
- `addLiquidity`
- `amountIn`
- `amountOut`
- `balanceOf`
- `getAmountOut`
- `getReserves`
- `kLast`
- `mint`
- `pool`
- `removeLiquidity`
- `reserve0`
- `reserve1`
- `swap`
- `totalSupply`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

Reserve-ratio, quote, getAmountOut, or spot-price signals were detected without visible TWAP, delay, bounds, or manipulation-resistance tests.

Why it matters:

Same-block reserve prices and spot quotes can be poor readiness evidence unless manipulation boundaries are tested or explicitly documented.

Historical pattern similarity:

Maps to spot-price and pool-price accounting readiness classes.

Recommended defensive checks:

- TWAP or delay assumption
- reserve manipulation sanity test
- price movement bounds

Related Knowledge:

- Historical patterns: pattern-spot-price-manipulation, pattern-pool-price-accounting
- Suggested defensive tests: twap-vs-spot-behavior, reserve-manipulation-sanity-test, price-movement-bounds
- Related PoCs: poc-2020-10-harvest, poc-2021-01-saddle, poc-2025-12-yeth

Suggested tests:

- Move reserves in a local pool test and assert dependent protocol decisions respect documented price bounds or TWAP assumptions.
- Test reserve-price movement bounds.
- Test TWAP or delay assumptions if used.
- Document whether other accounting paths rely on spot reserve price.

Invariant candidates:

- Reserve-based price consumers respect documented bounds and delay assumptions.

Search tags: `amm-pricing, spot-price, oracle-risk, amm-rule-pack`

### ARK-AMM-001 - AMM invariant assumptions not covered by tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `amm-invariant`

Evidence:
- `src/ToyAMMPool.sol:24` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `src/ToyAMMPool.sol:28` in `addLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amount0);`
- `src/ToyAMMPool.sol:47` in `removeLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transfer(msg.sender, amount0);`

Detected signals:
- `addLiquidity`
- `amountIn`
- `amountOut`
- `balanceOf`
- `getAmountOut`
- `getReserves`
- `kLast`
- `mint`
- `pool`
- `removeLiquidity`
- `reserve0`
- `reserve1`
- `swap`
- `totalSupply`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

AMM reserve, swap, or liquidity signals were detected without visible invariant or reserve-accounting tests.

Why it matters:

AMM correctness depends on reserve accounting, swap bounds, and invariant preservation staying true under fees, rounding, and repeated operations.

Historical pattern similarity:

Maps to historical AMM invariant and pool-price accounting readiness classes. This is defensive test inspiration, not vulnerability confirmation.

Recommended defensive checks:

- swap invariant conservation
- reserve accounting
- add/remove liquidity consistency
- fee and rounding bounds

Related Knowledge:

- Historical patterns: pattern-amm-invariant-steering, pattern-spot-price-manipulation
- Suggested defensive tests: swap-invariant-conservation, reserve-accounting-test, liquidity-proportionality
- Related PoCs: poc-2021-01-saddle, poc-2021-10-indexed-finance, poc-2025-12-yeth

Suggested tests:

- Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.
- Assert swaps preserve the documented constant-product or stableswap invariant within fee and rounding bounds.
- Test repeated swaps across small and large reserve states.
- Document expected invariant tolerance.

Invariant candidates:

- Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.
- Swaps and liquidity operations preserve documented AMM accounting within expected fee and rounding bounds.

Search tags: `amm-invariant, amm-rule-pack, pre-audit-readiness`

### ARK-AMM-004 - Fee-on-transfer or non-standard token assumptions not documented

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `amm-token-assumptions`

Evidence:
- `src/ToyAMMPool.sol:24` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `src/ToyAMMPool.sol:28` in `addLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amount0);`
- `src/ToyAMMPool.sol:47` in `removeLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transfer(msg.sender, amount0);`

Detected signals:
- `addLiquidity`
- `amountIn`
- `amountOut`
- `balanceOf`
- `getAmountOut`
- `getReserves`
- `kLast`
- `mint`
- `pool`
- `removeLiquidity`
- `reserve0`
- `reserve1`
- `swap`
- `totalSupply`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

Token transfer and amountIn accounting signals were detected without clear received-amount tests or non-standard token assumptions.

Why it matters:

AMM pools that assume amountIn equals tokens received may mis-account non-standard tokens unless explicitly unsupported or handled.

Historical pattern similarity:

Maps to fee-on-transfer and token accounting assumption readiness classes.

Recommended defensive checks:

- actual received amount accounting
- fee-on-transfer simulation
- unsupported token documentation

Related Knowledge:

- Historical patterns: pattern-pool-price-accounting, pattern-precision-rounding-loss
- Suggested defensive tests: balance-before-after-accounting, fee-on-transfer-token-simulation, unsupported-token-documentation
- Related PoCs: poc-2020-06-balancer-deflationary

Suggested tests:

- Use a local fee-on-transfer token mock or document that such tokens are unsupported and guarded by configuration.
- Test actual received amount accounting with balanceBefore/balanceAfter pattern.
- Simulate fee-on-transfer behavior with a local mock if supported.
- Document unsupported token types if not handled.

Invariant candidates:

- Pool accounting uses actual received token amounts or explicitly rejects unsupported tokens.

Search tags: `amm-token-assumptions, fee-on-transfer, amm-rule-pack`

### ARK-AMM-005 - Slippage/min-output constraints missing or unclear

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `amm-slippage`

Evidence:
- `src/ToyAMMPool.sol:24` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `src/ToyAMMPool.sol:28` in `addLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amount0);`
- `src/ToyAMMPool.sol:47` in `removeLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transfer(msg.sender, amount0);`

Detected signals:
- `addLiquidity`
- `amountIn`
- `amountOut`
- `balanceOf`
- `getAmountOut`
- `getReserves`
- `kLast`
- `mint`
- `pool`
- `removeLiquidity`
- `reserve0`
- `reserve1`
- `swap`
- `totalSupply`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

Swap path signals were detected without clear minOut, deadline, slippage, or stale-quote constraints.

Why it matters:

Slippage and stale quote controls help users and integrations bound expected outcomes around swaps.

Historical pattern similarity:

Maps to price boundary and quote freshness readiness classes.

Recommended defensive checks:

- minOut enforcement
- deadline behavior
- stale quote handling

Related Knowledge:

- Historical patterns: pattern-spot-price-manipulation, pattern-assumption-not-encoded-in-tests
- Suggested defensive tests: min-out-enforcement, deadline-or-stale-quote-test, slippage-boundary-test
- Related PoCs: poc-2020-10-harvest, poc-2021-01-saddle

Suggested tests:

- Assert swaps revert or follow documented policy when amountOut falls below a user-provided bound or quote is stale.
- Test minOut enforcement.
- Test stale quote or deadline behavior if supported.
- Assert user-provided slippage bounds are respected.

Invariant candidates:

- Swap execution respects user-provided output bounds and documented deadline policy.

Search tags: `amm-slippage, min-output, amm-rule-pack`

### ARK-REENT-001 - External-call value flow needs reentrancy review

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `reentrancy-value-flow`

Evidence:
- `src/ToyAMMPool.sol:28` in `addLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amount0);`
- `src/ToyAMMPool.sol:47` in `removeLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transfer(msg.sender, amount0);`
- `src/ToyAMMPool.sol:67` in `swap`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amountIn);`

Detected signals:
- `transfer`
- `transferFrom`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

External call or token transfer terms were detected without guard or reentrancy-review signals.

Why it matters:

External calls around value flow can expose state-ordering assumptions if internal accounting is not finalized before control leaves the contract.

Recommended defensive checks:

- checks-effects-interactions ordering
- local malicious-receiver callback test
- double-withdraw or double-claim prevention

Related Knowledge:

- Historical patterns: pattern-external-call-before-state-update, pattern-callback-capable-token
- Suggested defensive tests: reentrant-receiver-mock, state-update-before-external-call-test, double-claim-prevention
- Related PoCs: poc-2018-10-spankchain, poc-2020-04-uniswap-imbtc, poc-2021-03-dodo-crowdpool

Suggested tests:

- Review state update order and add local malicious-receiver tests where callbacks are possible.
- Add a benign callback-capable receiver stub.
- Assert state updates happen before external value transfer where required.
- Test withdraw, claim, refund, or swap flows for accounting consistency.

Invariant candidates:

- External-call flows cannot observe or preserve inconsistent accounting state.

Search tags: `reentrancy-review, value-flow`

### ARK-REENT-004 - External call path without documented ordering assumptions

- Priority: `Low readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `reentrancy-value-flow`

Evidence:
- `src/ToyAMMPool.sol:28` in `addLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amount0);`
- `src/ToyAMMPool.sol:47` in `removeLiquidity`: Solidity function contains external value-flow call evidence. Snippet: `token0.transfer(msg.sender, amount0);`
- `src/ToyAMMPool.sol:67` in `swap`: Solidity function contains external value-flow call evidence. Snippet: `token0.transferFrom(msg.sender, address(this), amountIn);`

Detected signals:
- `transfer`
- `transferFrom`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

External call/value-flow signals were detected without clear ordering or reentrancy assumption documentation.

Why it matters:

Reviewers need clear state-ordering assumptions to evaluate external call safety.

Historical pattern similarity:

Maps to checks-effects-interactions and callback boundary readiness classes.

Recommended defensive checks:

- ordering documentation
- callback assumptions
- external call failure behavior


Suggested tests:

- Pair ordering documentation with a local receiver test that exercises the documented boundary.
- Document checks-effects-interactions or guard assumptions.
- Test state before and after external calls.
- Assert failure paths preserve accounting state.

Invariant candidates:

- External call ordering follows documented state-transition policy.

Search tags: `reentrancy-review, documentation-readiness, reentrancy-rule-pack`

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyAMMPool.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`
- `test/ToyAMMPool.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `getReserves`
- `pool`
- `reserve0`
- `reserve1`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

Oracle or price-feed signals were detected, but tests do not visibly cover stale rounds, heartbeat, or timestamp behavior.

Why it matters:

Oracle-dependent accounting and control flows can be wrong when price data is stale, incomplete, or outside documented assumptions.

Historical pattern similarity:

Maps to historical oracle and pricing failure classes where stale or manipulated price state broke protocol assumptions.

Recommended defensive checks:

- stale round rejection
- heartbeat checks
- updatedAt validation
- answeredInRound handling

Related Knowledge:

- Historical patterns: pattern-oracle-stale-price, pattern-spot-price-manipulation, pattern-pool-price-accounting
- Suggested defensive tests: stale-round-rejection, heartbeat-bound-test, decimal-normalization-test
- Related PoCs: poc-2025-11-moonwell, poc-2020-10-harvest, poc-2021-02-yearn-v1-dai

Suggested tests:

- Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.
- Reject stale oracle rounds or document fallback behavior.
- Test updatedAt or heartbeat boundaries.
- Test borrow, liquidation, vault, or reward flows when oracle data is stale.

Invariant candidates:

- Accounting decisions only use oracle data that satisfies documented freshness policy.

Search tags: `oracle-risk, oracle-rule-pack, pre-audit-readiness`

### ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyAMMPool.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`
- `test/ToyAMMPool.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `getReserves`
- `pool`
- `reserve0`
- `reserve1`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

Oracle and price-feed signals were detected without enough freshness or sanity-check language.

Why it matters:

Price-dependent accounting can be wrong when oracle data is stale, out of bounds, or mis-normalized and no freshness or sanity check is visible to a reviewer.

Recommended defensive checks:

- stale-round and heartbeat handling
- decimals normalization to accounting units
- documented price bounds, TWAP, or fallback policy


Suggested tests:

- Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
- Test decimals normalization across expected feed decimals.
- Test zero, negative, or invalid oracle answers if applicable.
- Assert normalized price units match accounting units.

Invariant candidates:

- Normalized oracle values remain within documented unit and decimal assumptions.

Search tags: `oracle-risk, price-assumptions`

### ARK-ORC-003 - Spot or reserve-based pricing without manipulation-resistance tests

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyAMMPool.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`
- `test/ToyAMMPool.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `getReserves`
- `pool`
- `reserve0`
- `reserve1`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

Spot, reserve, pool, or sqrtPriceX96 pricing signals were detected without visible manipulation-resistance tests.

Why it matters:

Same-block spot or reserve-based pricing can drift from fair value unless bounded by the protocol design.

Historical pattern similarity:

Maps to historical price-manipulation readiness classes.

Recommended defensive checks:

- TWAP vs spot behavior
- reserve movement bounds
- price sanity checks
- local pool mocks

Related Knowledge:

- Historical patterns: pattern-spot-price-manipulation, pattern-amm-invariant-steering
- Suggested defensive tests: twap-vs-spot-behavior, reserve-manipulation-sanity-test, price-bounds-test
- Related PoCs: poc-2020-10-harvest, poc-2021-01-saddle, poc-2025-12-yeth

Suggested tests:

- Use a local pool mock to move reserves or price and assert protocol actions respect documented bounds.
- Test spot-price movement bounds.
- Test TWAP or delay assumptions when used.
- Document reserve-price dependency and expected safeguards.

Invariant candidates:

- Price-dependent accounting does not rely on an undocumented instantaneous reserve ratio.

Search tags: `oracle-risk, spot-price, reserve-pricing, oracle-rule-pack`

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyAMMPool.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`
- `test/ToyAMMPool.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `getReserves`
- `pool`
- `reserve0`
- `reserve1`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

Oracle pricing signals were detected without clear documentation for bounds, fallback behavior, or stale price assumptions.

Why it matters:

Auditors and maintainers need explicit pricing assumptions to review whether the design handles oracle failure modes.

Historical pattern similarity:

Maps to failed assumption classes where oracle behavior was implied but not enforced or documented.

Recommended defensive checks:

- price bounds
- fallback policy
- stale-price policy
- sequencer downtime notes


Suggested tests:

- Add documentation plus local tests showing fallback and out-of-bounds price behavior.
- Test documented price bounds.
- Test invalid answer fallback behavior.
- Add documentation for price shock and fallback assumptions.

Invariant candidates:

- Invalid or out-of-bound price inputs cannot silently drive critical accounting decisions.

Search tags: `oracle-risk, documentation-readiness, oracle-rule-pack`

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword`
- Category: `testing-readiness`

Evidence:
- `src/ToyAMMPool.sol:1`: Keyword signal matched this readiness finding. Snippet: `invariant_tests_missing, fuzz_tests_missing, handler_contracts_missing`
- `test/ToyAMMPool.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `invariant_tests_missing, fuzz_tests_missing, handler_contracts_missing`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `invariant_tests_missing`
- `fuzz_tests_missing`
- `handler_contracts_missing`

Affected files:
- `src/ToyAMMPool.sol`
- `test/ToyAMMPool.t.sol`

What was detected:

Protocol-like value flows were detected, but no invariant/property testing signal was found.

Why it matters:

Protocol-like value flows without invariant or property tests leave core accounting assumptions unverified under fees, rounding, and unexpected action sequences.

Recommended defensive checks:

- stateful invariant suite for the core lifecycle
- handler actions for normal and edge-case user flows
- conservation properties for value-bearing state

Related Knowledge:

- Historical patterns: pattern-missing-invariant-coverage, pattern-assumption-not-encoded-in-tests
- Suggested defensive tests: foundry-invariant-skeleton, stateful-fuzz-sequence, roundtrip-or-conservation-invariant
- Related PoCs: poc-2020-08-opyn, poc-2020-09-bzx-ifusdc, poc-2021-10-indexed-finance

Suggested tests:

- Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
- Add a stateful invariant suite for the core protocol lifecycle.
- Add handler actions for normal user flows and documented edge cases.
- Add conservation properties for assets, shares, rewards, debt, or reserves as applicable.

Invariant candidates:

- Core accounting relationships hold after any allowed user action.
- Privileged actions cannot silently bypass documented accounting assumptions.

Search tags: `invariant-testing, amm`

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
- **reward conservation** (`staking`): Total claimed plus remaining claimable should not exceed funded rewards beyond rounding.

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
- Generated issue plan: `examples/reports/amm-fixture-issue-plan.json`
- Issue plan JSON can be used with `scripts/create_github_issues.py` in dry-run, create, or update mode.

## GitHub Action Outputs

- Markdown Report: `examples/reports/amm-fixture-pre-audit-report.md`
- Json Report: `examples/reports/amm-fixture-pre-audit-report.json`
- Sarif Report: `examples/reports/amm-fixture.sarif.json`
- Issue Plan: `examples/reports/amm-fixture-issue-plan.json`

## Search Tags

`access-control-review`, `arkheionx`, `audit-preparation`, `defi-security`, `foundry`, `historical-exploit-pattern`, `indie-defi`, `invariant-testing`, `oracle-risk`, `pre-audit-readiness`, `reentrancy-review`, `root-cause-analysis`, `smart-contract-security`, `solidity-security`, `vault-accounting`

## Recommended Next Steps

1. Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
2. Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
3. Review state update order and add malicious local receiver tests for callback-capable flows.
4. Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
5. Run a formal smart contract audit before mainnet launch or before handling real user funds.

## What This Report Does Not Prove

- It does not prove protocol safety.
- It does not confirm exploitability.
- It does not replace manual review.
- It does not replace a formal audit.

## Formal Audit Recommendation

Run a formal smart contract audit before mainnet deployment, before material TVL, or before handling real user funds.

