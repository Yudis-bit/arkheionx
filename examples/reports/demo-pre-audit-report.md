# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/oracle-staking-fixture`
- Generated at: `2026-05-26T10:41:58+00:00`
- Protocol type: `staking`
- Protocol confidence: `medium`
- Files scanned: `4`
- Scanner version: `0.8.0`

| File class       | Count |
| ---------------- | ----- |
| Solidity sources | 1     |
| Solidity tests   | 1     |
| Docs             | 1     |
| Configs          | 1     |
| Workflows        | 0     |

## Disclaimer

This is an automated pre-audit readiness report. It is not a formal audit, does not prove the absence or presence of vulnerabilities, does not authorize live-target testing, and should only be used on repositories you own or are authorized to review. A formal audit is recommended before handling real user funds.

## Analysis Quality

| Source                   | Status   |
| ------------------------ | -------- |
| Keyword scan             | enabled  |
| Semantic-lite extraction | enabled  |
| Semantic contracts       | 3        |
| Semantic test files      | 1        |
| Slither                  | disabled |
| Slither detectors        | 0        |
| Test coverage mapping    | enabled  |

## Executive Summary

- Readiness score: **65/100**
- Score band: **Improving**
- Active readiness gaps: `11`
- Suppressed readiness gaps: `0`
- Top readiness gaps:
  - **ARK-TST-002 (High readiness gap):** No invariant tests detected for DeFi protocol shape - Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
  - **ARK-ORC-001 (Medium readiness gap):** Oracle-dependent logic without stale-price tests - Add local mock oracle tests for stale round rejection, heartbeat windows, answeredInRound, and updatedAt behavior.
  - **ARK-ORC-002 (Medium readiness gap):** Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
  - **ARK-ORC-005 (Medium readiness gap):** Missing price bounds or fallback assumptions documentation - Document min/max bounds, fallback oracle behavior, stale-price policy, and L2 sequencer assumptions if relevant.
  - **ARK-REENT-001 (Medium readiness gap):** External-call value flow needs reentrancy review - Review state update order and add local malicious-receiver tests where callbacks are possible.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
  - Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
  - Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
  - Review state update order and add malicious local receiver tests for callback-capable flows.

## Detected Protocol Shape

- Detected protocol type: `staking`
- Confidence: `medium`
- Protocol score signals: `{"amm": 0, "lending": 0, "oracle": 38, "staking": 43, "vault": 0}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                    | Score | Max | Notes                                                                                                                                                                                                                                                                                |
| --------------------------- | ----- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Repository Structure        | 12    | 15  | Solidity sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                                                                                                                                                   |
| Test Presence               | 20    | 20  | Solidity test files detected.; Assert usage detected.; Foundry or Hardhat test environment detected.; Protocol-specific terms appear in the testable codebase.                                                                                                                       |
| Invariant Fuzz Readiness    | 3     | 20  | Edge-case testing terms detected.                                                                                                                                                                                                                                                    |
| Defi Risk Coverage          | 7     | 20  | Role or admin boundaries have some visible coverage.; Protocol-specific checklist or property coverage detected.                                                                                                                                                                     |
| Documentation Readiness     | 8     | 10  | README detected.; Assumptions, invariants, or limitations are documented.; Deployment or role information appears in docs/code comments.                                                                                                                                             |
| Operational Admin Readiness | 15    | 15  | Access-control surface is visible.; Emergency control or incident terms detected.; Upgradeability is absent or has visible documentation/test terms.; Privileged setters or owner boundaries are visible for review.; Monitoring, incident, limitation, or emergency notes detected. |

## Top Readiness Gaps

| ID            | Priority             | Category              | Title                                                                  |
| ------------- | -------------------- | --------------------- | ---------------------------------------------------------------------- |
| ARK-TST-002   | High readiness gap   | testing-readiness     | No invariant tests detected for DeFi protocol shape                    |
| ARK-ORC-001   | Medium readiness gap | oracle-pricing        | Oracle-dependent logic without stale-price tests                       |
| ARK-ORC-002   | Medium readiness gap | oracle-pricing        | Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage |
| ARK-ORC-005   | Medium readiness gap | oracle-pricing        | Missing price bounds or fallback assumptions documentation             |
| ARK-REENT-001 | Medium readiness gap | reentrancy-value-flow | External-call value flow needs reentrancy review                       |

## Rule Pack Coverage

| Rule Pack                                 | Detected | Findings | Docs                                    |
| ----------------------------------------- | -------- | -------- | --------------------------------------- |
| Vault Rule Pack                           | yes      | 1        | docs/VAULT_RULE_PACK.md                 |
| Oracle Rule Pack                          | yes      | 3        | docs/ORACLE_RULE_PACK.md                |
| Access Control / Upgradeability Rule Pack | yes      | 1        | docs/ACCESS_CONTROL_RULE_PACK.md        |
| Reentrancy / Value Flow Rule Pack         | yes      | 2        | docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md |
| Staking / Reward Accounting Rule Pack     | yes      | 3        | docs/REWARD_ACCOUNTING_RULE_PACK.md     |

### Vault Rule Pack

- Signals detected: `7`
- Signal terms: `balanceOf, decimals, pause, setOracle, setTreasury, treasury, unpause`
- Findings: `1`
- Docs: `docs/VAULT_RULE_PACK.md`
- Suggested tests:
  - totalAssets consistency
  - deposit/withdraw roundtrip
  - share conversion rounding
  - strategy gain/loss lifecycle

### Oracle Rule Pack

- Signals detected: `11`
- Signal terms: `AggregatorV3Interface, answer, answeredInRound, decimals, getPrice, latestAnswer, latestRoundData, priceFeed, roundId, setOracle, updatedAt`
- Findings: `3`
- Docs: `docs/ORACLE_RULE_PACK.md`
- Suggested tests:
  - stale price rejection
  - decimals normalization
  - price bounds
  - TWAP vs spot behavior

### Access Control / Upgradeability Rule Pack

- Signals detected: `6`
- Signal terms: `onlyOwner, owner, pause, setOracle, setTreasury, unpause`
- Findings: `1`
- Docs: `docs/ACCESS_CONTROL_RULE_PACK.md`
- Suggested tests:
  - unauthorized setter tests
  - pause/emergency boundaries
  - initializer once
  - upgrade authorization

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

- Signals detected: `10`
- Signal terms: `accumulator, claimReward, decimals, earned, pendingReward, reward, rewardPerToken, stake, totalStaked, unstake`
- Findings: `3`
- Docs: `docs/REWARD_ACCOUNTING_RULE_PACK.md`
- Suggested tests:
  - reward conservation
  - no overclaim
  - index monotonicity
  - stake/unstake/claim lifecycle

## Risk Signal Summary

### Vault Erc4626

- Detected signals: `balanceOf`
- Files with signals: `1`
- Example files: `src/OracleRewardFixture.sol`

### Vault Accounting

- Detected signals: `balanceOf`
- Files with signals: `1`
- Example files: `src/OracleRewardFixture.sol`

### Vault Accounting Risk

- Detected signals: `decimals, treasury`
- Files with signals: `1`
- Example files: `src/OracleRewardFixture.sol`

### Vault Pricing

- Detected signals: `decimals, getPrice, latestAnswer, latestRoundData, priceFeed`
- Files with signals: `2`
- Example files: `src/OracleRewardFixture.sol, test/OracleRewardFixture.t.sol`

### Vault Admin Ops

- Detected signals: `pause, setOracle, setTreasury, unpause`
- Files with signals: `1`
- Example files: `src/OracleRewardFixture.sol`

### Oracle

- Detected signals: `AggregatorV3Interface, answer, answeredInRound, decimals, getPrice, latestAnswer, latestRoundData, priceFeed, roundId, setOracle, updatedAt`
- Files with signals: `2`
- Example files: `src/OracleRewardFixture.sol, test/OracleRewardFixture.t.sol`

### Access Control

- Detected signals: `onlyOwner, owner, pause, setOracle, setTreasury, unpause`
- Files with signals: `1`
- Example files: `src/OracleRewardFixture.sol`

### Reentrancy Value Flow

- Detected signals: `transfer, transferFrom`
- Files with signals: `1`
- Example files: `src/OracleRewardFixture.sol`

### Accounting Complexity

- Detected signals: `accumulator, decimals, reward`
- Files with signals: `1`
- Example files: `src/OracleRewardFixture.sol`

### Staking Rewards

- Detected signals: `accumulator, claimReward, earned, pendingReward, reward, rewardPerToken, stake, totalStaked, unstake`
- Files with signals: `2`
- Example files: `src/OracleRewardFixture.sol, test/OracleRewardFixture.t.sol`

### Testing And Documentation

- Test Directory: `True`
- Foundry Tests: `True`
- Hardhat Tests: `False`
- Test File Count: `1`
- Invariant Tests: `False`
- Fuzz Tests: `False`
- Handler Contracts: `False`
- Assert Usage: `True`
- Assert Count: `3`
- Forge Std: `True`
- Echidna: `False`
- Slither: `False`
- Ci Workflow: `False`
- Edge Case Tests: `True`
- Test files: `test/OracleRewardFixture.t.sol`

## Historical Exploit-Pattern Similarity

### Harvest/Yearn-style oracle or pool price readiness gap

- Confidence: `high`
- Detected signals: `AggregatorV3Interface, answer, answeredInRound, balanceOf, decimals, getPrice, latestAnswer, latestRoundData, priceFeed, roundId, setOracle, updatedAt`
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
- Detected signals: `accumulator, balanceOf, decimals, reward, treasury`
- Why it matters: Vaults need explicit conservation and roundtrip properties because share math, fees, donations, and rounding can break user-value assumptions.
- Failed assumption class: Shares and assets remain exchangeable according to documented accounting rules.
- Broken invariant class: Deposits, withdrawals, redemptions, and fee paths conserve value within expected rounding bounds.
- Recommended defensive checks:
  - Add totalAssets consistency tests.
  - Add deposit-withdraw roundtrip tests across small and large amounts.
  - Test donation, zero-supply, rounding, and fee paths.
- Suggested test/invariant: Invariant: deposit followed by withdraw does not create value and does not strand assets beyond expected rounding.
- Search tags: `vault-security, share-accounting, totalAssets, audit-readiness`

### Privileged vault controls and emergency operation readiness gap

- Confidence: `medium`
- Detected signals: `onlyOwner, owner, pause, setOracle, setTreasury, unpause`
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
- Detected signals: `accumulator, balanceOf, claimReward, earned, pendingReward, reward, rewardPerToken, stake, totalStaked, transfer, transferFrom, unstake`
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

- Confidence: `medium`
- Detected signals: `onlyOwner, owner, pause, setOracle, setTreasury, unpause`
- Why it matters: Admin setters, emergency controls, fee updates, and governance execution paths can become launch blockers if role boundaries are unclear or untested.
- Failed assumption class: Privileged actors can only perform documented, intended operations.
- Broken invariant class: Admin actions cannot silently bypass accounting, oracle, or user-safety invariants.
- Recommended defensive checks:
  - Document every privileged role and setter.
  - Add unauthorized-call tests for each privileged function.
  - Add tests showing pause/emergency controls behave as documented.
- Suggested test/invariant: Invariant: unprivileged callers cannot change fees, oracles, strategies, treasury, pause state, or upgrade target.
- Search tags: `access-control-review, admin-risk, operational-security`

### Reward accounting mismatch review recommended

- Confidence: `high`
- Detected signals: `accumulator, claimReward, decimals, earned, pendingReward, reward, rewardPerToken, stake, totalStaked, unstake`
- Why it matters: Reward indexes and accumulators are common sources of overclaim, underclaim, and precision drift when supply changes across epochs.
- Failed assumption class: Reward index math always reflects actual funded rewards and stake weights.
- Broken invariant class: Claimable rewards cannot exceed funded rewards beyond documented rounding.
- Recommended defensive checks:
  - Test claim conservation across multiple users.
  - Test stake/unstake around reward updates.
  - Check precision and rounding around small balances.
- Suggested test/invariant: Invariant: total claimed plus remaining claimable never exceeds funded rewards beyond expected rounding.
- Search tags: `reward-accounting, staking, index-math, precision`

## All Readiness Gaps

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Priority: `High readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `semantic-lite`
- Category: `testing-readiness`

Evidence:
- `src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`
- `src/OracleRewardFixture.sol:81` in `earned`: Solidity function shape matches this readiness finding. Snippet: `+ ((balanceOf[account] * (rewardPerToken() - userRewardPerTokenPaid[account])) / 1e18);`
- `src/OracleRewardFixture.sol:86` in `stake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transferFrom(msg.sender, address(this), amount), "transferFrom");`
- `src/OracleRewardFixture.sol:94` in `unstake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, amount), "transfer");`
- `src/OracleRewardFixture.sol:101` in `claimReward`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, reward), "reward transfer");`

Detected signals:
- scanner signal

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

What was detected:

Protocol-like value flows were detected, but no invariant/property testing signal was found.

Suggested tests:

- Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.

Search tags: `invariant-testing, staking`

### ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/OracleRewardFixture.sol:67` in `getPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,, uint256 updatedAt,) = priceFeed.latestRoundData();`
- `src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`
- `test/documentation coverage`: Matching test coverage terms detected: oracle.
- `src/OracleRewardFixture.sol:1`: Keyword signal matched this readiness finding.
- `test/OracleRewardFixture.t.sol:1`: Keyword signal matched this readiness finding.

Detected signals:
- scanner signal

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

What was detected:

Oracle and price-feed signals were detected without enough freshness or sanity-check language.

Suggested tests:

- Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.

Search tags: `oracle-risk, price-assumptions`

### ARK-VLT-009 - Vault accounting lacks visible roundtrip or conservation coverage

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `vault-accounting`

Evidence:
- `test/documentation coverage`: No semantic-lite vault test coverage terms were detected.
- `src/OracleRewardFixture.sol:1`: Keyword signal matched this readiness finding.
- `test/OracleRewardFixture.t.sol:1`: Keyword signal matched this readiness finding.

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- scanner signal

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

What was detected:

Vault/share/accounting terms were detected without enough explicit conservation or roundtrip testing language.

Suggested tests:

- Add deposit/withdraw roundtrip tests and totalAssets/share accounting invariants.

Search tags: `vault-accounting, share-accounting`

### ARK-REENT-001 - External-call value flow needs reentrancy review

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `reentrancy-value-flow`

Evidence:
- `src/OracleRewardFixture.sol:86` in `stake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transferFrom(msg.sender, address(this), amount), "transferFrom");`
- `src/OracleRewardFixture.sol:94` in `unstake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, amount), "transfer");`
- `src/OracleRewardFixture.sol:101` in `claimReward`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, reward), "reward transfer");`
- `test/documentation coverage`: No semantic-lite reentrancy test coverage terms were detected.
- `src/OracleRewardFixture.sol:1`: Keyword signal matched this readiness finding.

Detected signals:
- scanner signal

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

What was detected:

External call or token transfer terms were detected without guard or reentrancy-review signals.

Suggested tests:

- Review state update order and add local malicious-receiver tests where callbacks are possible.

Search tags: `reentrancy-review, value-flow`

### ARK-RWD-001 - Reward accounting needs conservation coverage

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `semantic-lite`
- Category: `reward-accounting`

Evidence:
- `src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`
- `src/OracleRewardFixture.sol:81` in `earned`: Solidity function shape matches this readiness finding. Snippet: `+ ((balanceOf[account] * (rewardPerToken() - userRewardPerTokenPaid[account])) / 1e18);`
- `src/OracleRewardFixture.sol:86` in `stake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transferFrom(msg.sender, address(this), amount), "transferFrom");`
- `src/OracleRewardFixture.sol:94` in `unstake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, amount), "transfer");`
- `src/OracleRewardFixture.sol:101` in `claimReward`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, reward), "reward transfer");`

Detected signals:
- scanner signal

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

What was detected:

Reward/index/claim signals were detected without invariant testing.

Suggested tests:

- Add reward conservation and no-overclaim tests across multiple users and timing boundaries.

Search tags: `reward-accounting, precision`

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/OracleRewardFixture.sol:67` in `getPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,, uint256 updatedAt,) = priceFeed.latestRoundData();`
- `src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`
- `test/documentation coverage`: Matching test coverage terms detected: oracle.
- `src/OracleRewardFixture.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, decimals, getPrice, latestAnswer, latestRoundData, priceFeed`
- `test/OracleRewardFixture.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, decimals, getPrice, latestAnswer, latestRoundData, priceFeed`

Detected signals:
- `AggregatorV3Interface`
- `answer`
- `answeredInRound`
- `decimals`
- `getPrice`
- `latestAnswer`
- `latestRoundData`
- `priceFeed`
- `roundId`
- `setOracle`
- `updatedAt`

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

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

Suggested tests:

- Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.

Search tags: `oracle-risk, oracle-rule-pack, pre-audit-readiness`

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/OracleRewardFixture.sol:67` in `getPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,, uint256 updatedAt,) = priceFeed.latestRoundData();`
- `src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`
- `test/documentation coverage`: Matching test coverage terms detected: oracle.
- `src/OracleRewardFixture.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, decimals, getPrice, latestAnswer, latestRoundData, priceFeed`
- `test/OracleRewardFixture.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, decimals, getPrice, latestAnswer, latestRoundData, priceFeed`

Detected signals:
- `AggregatorV3Interface`
- `answer`
- `answeredInRound`
- `decimals`
- `getPrice`
- `latestAnswer`
- `latestRoundData`
- `priceFeed`
- `roundId`
- `setOracle`
- `updatedAt`

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

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

Search tags: `oracle-risk, documentation-readiness, oracle-rule-pack`

### ARK-ACC-003 - Admin role concentration not documented

- Priority: `Low readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `semantic-lite`
- Category: `access-control`

Evidence:
- `src/OracleRewardFixture.sol:47` in `setOracle`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `src/OracleRewardFixture.sol:51` in `setEmissionRate`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `src/OracleRewardFixture.sol:55` in `setTreasury`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `src/OracleRewardFixture.sol:59` in `pause`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `src/OracleRewardFixture.sol:63` in `unpause`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`

Detected signals:
- `onlyOwner`
- `owner`
- `pause`
- `setOracle`
- `setTreasury`
- `unpause`

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

What was detected:

Admin, owner, guardian, operator, role, multisig, or timelock signals were detected without clear role-concentration documentation.

Why it matters:

Role concentration affects operational risk and audit scope even when access control code is syntactically correct.

Historical pattern similarity:

Maps to operational control readiness classes.

Recommended defensive checks:

- role matrix
- owner powers
- timelock assumptions
- multisig assumptions

Suggested tests:

- Add a role matrix to docs and unit tests for critical roles.

Search tags: `access-control-review, documentation-readiness, access-control-rule-pack`

### ARK-REENT-004 - External call path without documented ordering assumptions

- Priority: `Low readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `reentrancy-value-flow`

Evidence:
- `src/OracleRewardFixture.sol:86` in `stake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transferFrom(msg.sender, address(this), amount), "transferFrom");`
- `src/OracleRewardFixture.sol:94` in `unstake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, amount), "transfer");`
- `src/OracleRewardFixture.sol:101` in `claimReward`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, reward), "reward transfer");`
- `test/documentation coverage`: No semantic-lite reentrancy test coverage terms were detected.
- `src/OracleRewardFixture.sol:1`: Keyword signal matched this readiness finding. Snippet: `transfer, transferFrom`

Detected signals:
- `transfer`
- `transferFrom`

Affected files:
- `src/OracleRewardFixture.sol`

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

Search tags: `reentrancy-review, documentation-readiness, reentrancy-rule-pack`

### ARK-RWD-002 - Accumulator/index logic without precision/rounding tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `semantic-lite`
- Category: `reward-accounting`

Evidence:
- `src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`
- `src/OracleRewardFixture.sol:81` in `earned`: Solidity function shape matches this readiness finding. Snippet: `+ ((balanceOf[account] * (rewardPerToken() - userRewardPerTokenPaid[account])) / 1e18);`
- `src/OracleRewardFixture.sol:86` in `stake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transferFrom(msg.sender, address(this), amount), "transferFrom");`
- `src/OracleRewardFixture.sol:94` in `unstake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, amount), "transfer");`
- `src/OracleRewardFixture.sol:101` in `claimReward`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, reward), "reward transfer");`

Detected signals:
- `accumulator`
- `claimReward`
- `earned`
- `pendingReward`
- `reward`
- `rewardPerToken`
- `stake`
- `totalStaked`
- `unstake`

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

What was detected:

Accumulator, index, rewardPerToken, precision, or share signals were detected without visible precision/rounding tests.

Why it matters:

Index and accumulator math can leak value or strand rewards through rounding across many users.

Historical pattern similarity:

Maps to precision and accounting mismatch readiness classes.

Recommended defensive checks:

- index monotonicity
- rounding dust
- small balance behavior
- multi-user precision

Suggested tests:

- Fuzz stake sizes and reward amounts and assert reward indexes are monotonic and bounded by funded rewards.

Search tags: `reward-accounting, precision, staking-rule-pack`

### ARK-RWD-003 - Claim flow without double-claim prevention tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `semantic-lite`
- Category: `reward-accounting`

Evidence:
- `src/OracleRewardFixture.sol:74` in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence. Snippet: `return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;`
- `src/OracleRewardFixture.sol:81` in `earned`: Solidity function shape matches this readiness finding. Snippet: `+ ((balanceOf[account] * (rewardPerToken() - userRewardPerTokenPaid[account])) / 1e18);`
- `src/OracleRewardFixture.sol:86` in `stake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transferFrom(msg.sender, address(this), amount), "transferFrom");`
- `src/OracleRewardFixture.sol:94` in `unstake`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, amount), "transfer");`
- `src/OracleRewardFixture.sol:101` in `claimReward`: Solidity function contains external value-flow call evidence. Snippet: `require(stakingToken.transfer(msg.sender, reward), "reward transfer");`

Detected signals:
- `accumulator`
- `claimReward`
- `earned`
- `pendingReward`
- `reward`
- `rewardPerToken`
- `stake`
- `totalStaked`
- `unstake`

Affected files:
- `src/OracleRewardFixture.sol`
- `test/OracleRewardFixture.t.sol`

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

Search tags: `reward-accounting, claim-flow, staking-rule-pack`


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
- **reward conservation** (`staking`): Total claimed plus remaining claimable should not exceed funded rewards beyond rounding.
- **no overclaim** (`staking`): Users should not claim more than their funded and accrued share.
- **index monotonicity** (`staking`): Reward indexes should be monotonic and supply-aware.
- **stake/unstake roundtrip** (`staking`): Stake and unstake flows should preserve balances and reward accounting.
- **reward accounting precision** (`staking`): Small balances and precision edges should not create systematic reward drift.

## Audit Readiness Checklist

- [ ] Core user flows have deterministic unit tests.
- [ ] Accounting, oracle, reward, and role assumptions are documented.
- [ ] Foundry invariant tests cover value conservation and access boundaries.
- [ ] Fuzz tests cover edge cases, rounding, and unexpected user sequences.
- [ ] Privileged roles, upgrade controls, and emergency controls are documented and tested.
- [ ] Known limitations are written down for auditors.
- [ ] A formal audit scope names contracts, commit hash, deployment assumptions, and out-of-scope areas.

## Generated Issue Checklist

- Generated checklist: `examples/reports/demo-issue-checklist.md`
- Use this as a copyable GitHub Issue body or as a remediation tracker.
- Generated issue plan: `examples/reports/demo-issue-plan.json`
- Issue plan JSON can be used with `scripts/create_github_issues.py` in dry-run, create, or update mode.

## GitHub Action Outputs

- Markdown Report: `examples/reports/demo-pre-audit-report.md`
- Json Report: `examples/reports/demo-report.json`
- Sarif Report: `examples/reports/demo.sarif.json`
- Issue Checklist: `examples/reports/demo-issue-checklist.md`
- Issue Plan: `examples/reports/demo-issue-plan.json`
- Baseline: `examples/reports/demo.baseline.json`
- Launch Report: `examples/reports/demo-launch-report.md`
- Sprint Plan: `examples/reports/demo-sprint-plan.md`
- Contest Readiness: `examples/reports/demo-contest-readiness.md`
- Executive Summary: `examples/reports/demo-executive-summary.md`
- Remediation Roadmap: `examples/reports/demo-remediation-roadmap.md`

## Search Tags

`access-control-review`, `arkheionx`, `audit-preparation`, `defi-security`, `foundry`, `historical-exploit-pattern`, `indie-defi`, `invariant-testing`, `oracle-risk`, `pre-audit-readiness`, `reentrancy-review`, `root-cause-analysis`, `smart-contract-security`, `solidity-security`, `vault-accounting`

## Recommended Next Steps

1. Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
2. Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
3. Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
4. Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
5. Review state update order and add malicious local receiver tests for callback-capable flows.

## What This Report Does Not Prove

- It does not prove protocol safety.
- It does not confirm exploitability.
- It does not replace manual review.
- It does not replace a formal audit.

## Formal Audit Recommendation

Run a formal smart contract audit before mainnet deployment, before material TVL, or before handling real user funds.

