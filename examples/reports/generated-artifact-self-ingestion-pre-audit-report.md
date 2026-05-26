# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/generated-artifact-self-ingestion-fixture`
- Generated at: `2026-05-26T15:11:21+00:00`
- Protocol type: `oracle`
- Protocol confidence: `high`
- Files scanned: `4`
- Scanner version: `0.9.2`

| File class       | Count |
| ---------------- | ----- |
| Solidity sources | 1     |
| Solidity tests   | 1     |
| Docs             | 1     |
| Configs          | 1     |
| Workflows        | 0     |

## Scan Source Summary

- Files considered: `5`
- Files scanned: `4`
- Files ignored: `1`
- Generated Arkheionx artifacts ignored: `1`
- Generated artifacts were ignored to prevent previous Arkheionx outputs from influencing this scan.

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

- Readiness score: **55/100**
- Score band: **Early readiness**
- Active readiness gaps: `10`
- Suppressed readiness gaps: `0`
- Top readiness gaps:
  - **ARK-ORC-001 (High readiness gap):** Oracle-dependent logic without stale-price tests - Add local mock oracle tests for stale round rejection, heartbeat windows, answeredInRound, and updatedAt behavior.
  - **ARK-ORC-002 (High readiness gap):** Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
  - **ARK-ACC-001 (Medium readiness gap):** Privileged setters without role-boundary tests - Add tests proving unauthorized users cannot call privileged setters or role-management functions.
  - **ARK-ORC-004 (Medium readiness gap):** Oracle setter/admin path without role-boundary tests - Add tests proving only documented roles can update oracle configuration.
  - **ARK-ORC-005 (Medium readiness gap):** Missing price bounds or fallback assumptions documentation - Document min/max bounds, fallback oracle behavior, stale-price policy, and L2 sequencer assumptions if relevant.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
  - Review state update order and add malicious local receiver tests for callback-capable flows.
  - Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
  - Run a formal smart contract audit before mainnet launch or before handling real user funds.

## Detected Protocol Shape

- Detected protocol type: `oracle`
- Confidence: `high`
- Protocol score signals: `{"amm": 0, "lending": 0, "oracle": 30, "staking": 0, "vault": 21}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                    | Score | Max | Notes                                                                                                                                                                 |
| --------------------------- | ----- | --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository Structure        | 12    | 15  | Solidity sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                                    |
| Test Presence               | 20    | 20  | Solidity test files detected.; Assert usage detected.; Foundry or Hardhat test environment detected.; Protocol-specific terms appear in the testable codebase.        |
| Invariant Fuzz Readiness    | 0     | 20  | No positive signal detected.                                                                                                                                          |
| Defi Risk Coverage          | 9     | 20  | Accounting assumptions have at least some documented or tested controls.; Role or admin boundaries have some visible coverage.                                        |
| Documentation Readiness     | 5     | 10  | README detected.; Deployment or role information appears in docs/code comments.                                                                                       |
| Operational Admin Readiness | 9     | 15  | Access-control surface is visible.; Upgradeability is absent or has visible documentation/test terms.; Privileged setters or owner boundaries are visible for review. |

## Top Readiness Gaps

| ID          | Priority             | Category       | Title                                                                  |
| ----------- | -------------------- | -------------- | ---------------------------------------------------------------------- |
| ARK-ORC-001 | High readiness gap   | oracle-pricing | Oracle-dependent logic without stale-price tests                       |
| ARK-ORC-002 | High readiness gap   | oracle-pricing | Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage |
| ARK-ACC-001 | Medium readiness gap | access-control | Privileged setters without role-boundary tests                         |
| ARK-ORC-004 | Medium readiness gap | oracle-pricing | Oracle setter/admin path without role-boundary tests                   |
| ARK-ORC-005 | Medium readiness gap | oracle-pricing | Missing price bounds or fallback assumptions documentation             |

## Rule Pack Coverage

| Rule Pack                                 | Detected | Findings | Docs                                    |
| ----------------------------------------- | -------- | -------- | --------------------------------------- |
| Vault Rule Pack                           | yes      | 0        | docs/VAULT_RULE_PACK.md                 |
| Oracle Rule Pack                          | yes      | 4        | docs/ORACLE_RULE_PACK.md                |
| Access Control / Upgradeability Rule Pack | yes      | 2        | docs/ACCESS_CONTROL_RULE_PACK.md        |
| Reentrancy / Value Flow Rule Pack         | yes      | 2        | docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md |
| Staking / Reward Accounting Rule Pack     | yes      | 1        | docs/REWARD_ACCOUNTING_RULE_PACK.md     |

### Vault Rule Pack

- Signals detected: `6`
- Signal terms: `assets, balanceOf, deposit, setOracle, totalAssets, withdraw`
- Findings: `0`
- Docs: `docs/VAULT_RULE_PACK.md`
- Suggested tests:
  - totalAssets consistency
  - deposit/withdraw roundtrip
  - share conversion rounding
  - strategy gain/loss lifecycle

### Oracle Rule Pack

- Signals detected: `8`
- Signal terms: `AggregatorV3Interface, answer, answeredInRound, latestRoundData, priceFeed, roundId, setOracle, updatedAt`
- Findings: `4`
- Docs: `docs/ORACLE_RULE_PACK.md`
- Suggested tests:
  - stale price rejection
  - decimals normalization
  - price bounds
  - TWAP vs spot behavior

### Access Control / Upgradeability Rule Pack

- Signals detected: `3`
- Signal terms: `onlyOwner, owner, setOracle`
- Findings: `2`
- Docs: `docs/ACCESS_CONTROL_RULE_PACK.md`
- Suggested tests:
  - unauthorized setter tests
  - pause/emergency boundaries
  - initializer once
  - upgrade authorization

### Reentrancy / Value Flow Rule Pack

- Signals detected: `2`
- Signal terms: `call{, withdraw`
- Findings: `2`
- Docs: `docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md`
- Suggested tests:
  - reentrant receiver mock
  - state update ordering
  - double claim prevention
  - failed external call behavior

### Staking / Reward Accounting Rule Pack

- Signals detected: `2`
- Signal terms: `claimReward, withdraw`
- Findings: `1`
- Docs: `docs/REWARD_ACCOUNTING_RULE_PACK.md`
- Suggested tests:
  - reward conservation
  - no overclaim
  - index monotonicity
  - stake/unstake/claim lifecycle

## Risk Signal Summary

### Vault Erc4626

- Detected signals: `assets, balanceOf, deposit, totalAssets, withdraw`
- Files with signals: `1`
- Example files: `src/SelfIngestionToy.sol`

### Vault Accounting

- Detected signals: `assets, balanceOf, deposit, totalAssets, withdraw`
- Files with signals: `1`
- Example files: `src/SelfIngestionToy.sol`

### Vault Accounting Risk

- Detected signals: `totalAssets`
- Files with signals: `1`
- Example files: `src/SelfIngestionToy.sol`

### Vault Pricing

- Detected signals: `latestRoundData, priceFeed`
- Files with signals: `1`
- Example files: `src/SelfIngestionToy.sol`

### Vault Admin Ops

- Detected signals: `setOracle`
- Files with signals: `1`
- Example files: `src/SelfIngestionToy.sol`

### Oracle

- Detected signals: `AggregatorV3Interface, answer, answeredInRound, latestRoundData, priceFeed, roundId, setOracle, updatedAt`
- Files with signals: `1`
- Example files: `src/SelfIngestionToy.sol`

### Access Control

- Detected signals: `onlyOwner, owner, setOracle`
- Files with signals: `1`
- Example files: `src/SelfIngestionToy.sol`

### Reentrancy Value Flow

- Detected signals: `call{, withdraw`
- Files with signals: `1`
- Example files: `src/SelfIngestionToy.sol`

### Staking Rewards

- Detected signals: `claimReward, withdraw`
- Files with signals: `1`
- Example files: `src/SelfIngestionToy.sol`

### Testing And Documentation

- Test Directory: `True`
- Foundry Tests: `True`
- Hardhat Tests: `False`
- Test File Count: `1`
- Invariant Tests: `False`
- Fuzz Tests: `False`
- Handler Contracts: `False`
- Assert Usage: `True`
- Assert Count: `1`
- Forge Std: `True`
- Echidna: `False`
- Slither: `False`
- Ci Workflow: `False`
- Edge Case Tests: `False`
- Negative Evidence Count: `0`
- Negative Evidence Terms: `[]`
- Test files: `test/SelfIngestionToy.t.sol`

## Historical Exploit-Pattern Similarity

### Harvest/Yearn-style oracle or pool price readiness gap

- Confidence: `high`
- Detected signals: `AggregatorV3Interface, answer, answeredInRound, assets, balanceOf, deposit, latestRoundData, priceFeed, roundId, setOracle, totalAssets, updatedAt, withdraw`
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
- Detected signals: `assets, balanceOf, deposit, totalAssets, withdraw`
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
- Detected signals: `onlyOwner, owner, setOracle`
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

- Confidence: `medium`
- Detected signals: `assets, balanceOf, call{, claimReward, deposit, totalAssets, withdraw`
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
- Detected signals: `onlyOwner, owner, setOracle`
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

- Confidence: `low`
- Detected signals: `claimReward, withdraw`
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

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword`
- Category: `testing-readiness`

Evidence:
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding.

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- scanner signal

Affected files:
- `src/SelfIngestionToy.sol`

What was detected:

Protocol-like value flows were detected, but no invariant/property testing signal was found.

Related Knowledge:

- Historical patterns: pattern-missing-invariant-coverage, pattern-assumption-not-encoded-in-tests
- Suggested defensive tests: foundry-invariant-skeleton, stateful-fuzz-sequence, roundtrip-or-conservation-invariant
- Related PoCs: poc-2020-08-opyn, poc-2020-09-bzx-ifusdc, poc-2021-10-indexed-finance
- Docs: docs/READINESS_SCORE.md, templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol

Suggested tests:

- Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.

Search tags: `invariant-testing, oracle`

### ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage

- Priority: `High readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/SelfIngestionToy.sol:43` in `latestPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,,,) = priceFeed.latestRoundData();`
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding.

Detected signals:
- scanner signal

Affected files:
- `src/SelfIngestionToy.sol`

What was detected:

Oracle and price-feed signals were detected without enough freshness or sanity-check language.

Suggested tests:

- Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.

Search tags: `oracle-risk, price-assumptions`

### ARK-REENT-001 - External-call value flow needs reentrancy review

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `reentrancy-value-flow`

Evidence:
- `src/SelfIngestionToy.sol:32` in `deposit`: Solidity function contains external value-flow call evidence. Snippet: `balanceOf[msg.sender] += assets;`
- `src/SelfIngestionToy.sol:37` in `withdraw`: Solidity function contains external value-flow call evidence. Snippet: `balanceOf[msg.sender] -= assets;`
- `test/documentation coverage`: No semantic-lite reentrancy test coverage terms were detected.
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding.

Detected signals:
- scanner signal

Affected files:
- `src/SelfIngestionToy.sol`

What was detected:

External call or token transfer terms were detected without guard or reentrancy-review signals.

Related Knowledge:

- Historical patterns: pattern-external-call-before-state-update, pattern-callback-capable-token
- Suggested defensive tests: reentrant-receiver-mock, state-update-before-external-call-test, double-claim-prevention
- Related PoCs: poc-2018-10-spankchain, poc-2020-04-uniswap-imbtc, poc-2021-03-dodo-crowdpool
- Docs: docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md, docs/RULE_PACKS.md

Suggested tests:

- Review state update order and add local malicious-receiver tests where callbacks are possible.

Search tags: `reentrancy-review, value-flow`

### ARK-RWD-001 - Reward accounting needs conservation coverage

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `reward-accounting`

Evidence:
- `src/SelfIngestionToy.sol:48` in `claimReward`: Solidity function shape matches this readiness finding. Snippet: `rewardPerTokenStored += 1;`
- `test/documentation coverage`: No semantic-lite reward test coverage terms were detected.
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding.

Detected signals:
- scanner signal

Affected files:
- `src/SelfIngestionToy.sol`

What was detected:

Reward/index/claim signals were detected without invariant testing.

Related Knowledge:

- Historical patterns: pattern-reward-overclaim, pattern-accounting-index-drift
- Suggested defensive tests: reward-conservation-multi-user, claim-twice-reverts-or-noops, rewardPerToken-monotonicity
- Related PoCs: poc-2020-12-warp-finance, poc-2020-08-opyn, poc-2020-09-bzx-ifusdc
- Docs: docs/REWARD_ACCOUNTING_RULE_PACK.md, docs/RULE_PACKS.md

Suggested tests:

- Add reward conservation and no-overclaim tests across multiple users and timing boundaries.

Search tags: `reward-accounting, precision`

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

- Priority: `High readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/SelfIngestionToy.sol:43` in `latestPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,,,) = priceFeed.latestRoundData();`
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, latestRoundData, priceFeed, roundId, setOracle, updatedAt`

Detected signals:
- `AggregatorV3Interface`
- `answer`
- `answeredInRound`
- `latestRoundData`
- `priceFeed`
- `roundId`
- `setOracle`
- `updatedAt`

Affected files:
- `src/SelfIngestionToy.sol`

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
- Docs: docs/ORACLE_RULE_PACK.md, docs/RULE_PACKS.md, docs/SEARCH_GUIDE.md

Suggested tests:

- Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.

Search tags: `oracle-risk, oracle-rule-pack, pre-audit-readiness`

### ARK-ORC-004 - Oracle setter/admin path without role-boundary tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/SelfIngestionToy.sol:43` in `latestPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,,,) = priceFeed.latestRoundData();`
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, latestRoundData, priceFeed, roundId, setOracle, updatedAt`

Detected signals:
- `AggregatorV3Interface`
- `answer`
- `answeredInRound`
- `latestRoundData`
- `priceFeed`
- `roundId`
- `setOracle`
- `updatedAt`

Affected files:
- `src/SelfIngestionToy.sol`

What was detected:

Oracle setter or fallback oracle signals were detected without visible unauthorized-call tests.

Why it matters:

Oracle configuration changes can alter all downstream accounting assumptions.

Historical pattern similarity:

Maps to privileged control and oracle configuration readiness classes.

Recommended defensive checks:

- unauthorized setOracle reverts
- trusted role documentation
- fallback oracle controls

Suggested tests:

- Assert unprivileged callers cannot change oracle or fallback oracle configuration.

Search tags: `oracle-risk, access-control-review, oracle-rule-pack`

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/SelfIngestionToy.sol:43` in `latestPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,,,) = priceFeed.latestRoundData();`
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, latestRoundData, priceFeed, roundId, setOracle, updatedAt`

Detected signals:
- `AggregatorV3Interface`
- `answer`
- `answeredInRound`
- `latestRoundData`
- `priceFeed`
- `roundId`
- `setOracle`
- `updatedAt`

Affected files:
- `src/SelfIngestionToy.sol`

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

### ARK-ACC-001 - Privileged setters without role-boundary tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `access-control`

Evidence:
- `src/SelfIngestionToy.sol:28` in `setOracle`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `test/documentation coverage`: No semantic-lite access control test coverage terms were detected.
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding. Snippet: `onlyOwner, owner, setOracle`

Detected signals:
- `onlyOwner`
- `owner`
- `setOracle`

Affected files:
- `src/SelfIngestionToy.sol`

What was detected:

Privileged setter or role-management signals were detected without visible unauthorized-call coverage.

Why it matters:

Privileged setters can alter fees, oracles, strategies, treasury, roles, pause state, or accounting assumptions.

Historical pattern similarity:

Maps to access-control failure classes where privileged paths were under-specified or incorrectly guarded.

Recommended defensive checks:

- unauthorized setter tests
- role grant/revoke tests
- pause role tests
- timelock/multisig assumptions

Related Knowledge:

- Historical patterns: pattern-unprotected-initializer, pattern-privileged-operation-boundary
- Suggested defensive tests: unauthorized-setter-reverts, role-boundary-negative-tests, admin-change-event-and-bounds-test
- Related PoCs: poc-2017-07-parity-multisig, poc-2020-06-balancer-deflationary, poc-2022-02-dexible
- Docs: docs/ACCESS_CONTROL_RULE_PACK.md, docs/RULE_PACKS.md

Suggested tests:

- For every privileged function, assert an unprivileged caller reverts and the documented role succeeds only within intended bounds.

Search tags: `access-control-review, admin-risk, access-control-rule-pack`

### ARK-ACC-003 - Admin role concentration not documented

- Priority: `Low readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `access-control`

Evidence:
- `src/SelfIngestionToy.sol:28` in `setOracle`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `test/documentation coverage`: No semantic-lite access control test coverage terms were detected.
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding. Snippet: `onlyOwner, owner, setOracle`

Detected signals:
- `onlyOwner`
- `owner`
- `setOracle`

Affected files:
- `src/SelfIngestionToy.sol`

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
- `src/SelfIngestionToy.sol:32` in `deposit`: Solidity function contains external value-flow call evidence. Snippet: `balanceOf[msg.sender] += assets;`
- `src/SelfIngestionToy.sol:37` in `withdraw`: Solidity function contains external value-flow call evidence. Snippet: `balanceOf[msg.sender] -= assets;`
- `test/documentation coverage`: No semantic-lite reentrancy test coverage terms were detected.
- `src/SelfIngestionToy.sol:1`: Keyword signal matched this readiness finding. Snippet: `call{, withdraw`

Detected signals:
- `call{`
- `withdraw`

Affected files:
- `src/SelfIngestionToy.sol`

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

- No issue checklist file was requested in this run.
- To generate one: `python3 scripts/pre_audit_scan.py --root . --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md`

## GitHub Action Outputs

- Markdown Report: `examples/reports/generated-artifact-self-ingestion-pre-audit-report.md`
- Json Report: `examples/reports/generated-artifact-self-ingestion-pre-audit-report.json`

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

