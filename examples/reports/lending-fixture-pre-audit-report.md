# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/lending-fixture`
- Generated at: `2026-06-06T12:31:33+00:00`
- Protocol type: `lending`
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
- Effective protocol type: `lending`
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

Arkheionx scanned `examples/lending-fixture` as `lending` readiness context. This is a local/static pre-audit readiness report, not a formal audit.

- Readiness score: **59/100**
- Score band: **Early readiness**
- Active readiness gaps: `10`
- Suppressed readiness gaps: `0`
- Active rule packs: `access-control, amm, docs, lending, oracle, reentrancy-value-flow, rewards, testing, vault`
- Generated artifacts ignored: `0`
- Top readiness gaps:
  - **ARK-LEND-004 (High readiness gap):** Oracle-dependent borrowing/liquidation without stale-price tests - Add local oracle tests for stale prices, decimals normalization, price shocks, invalid prices, and liquidation after oracle updates.
  - **ARK-ORC-001 (High readiness gap):** Oracle-dependent logic without stale-price tests - Add local mock oracle tests for stale round rejection, heartbeat windows, answeredInRound, and updatedAt behavior.
  - **ARK-ORC-002 (High readiness gap):** Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
  - **ARK-ACC-001 (Medium readiness gap):** Privileged setters without role-boundary tests - Add tests proving unauthorized users cannot call privileged setters or role-management functions.
  - **ARK-LEND-001 (Medium readiness gap):** Collateral/debt solvency invariant not covered by tests - Add collateral/debt invariants and boundary tests for borrow, repay, deposit, withdrawal, and liquidation readiness.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
  - Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
  - Run a formal smart contract audit before mainnet launch or before handling real user funds.

## Fix First

| Rank | Finding                                                                              | Rule Family    | Why Fix First                                                                                                                          | Next Action                                                                                                                                       |
| ---- | ------------------------------------------------------------------------------------ | -------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | ARK-LEND-004 - Oracle-dependent borrowing/liquidation without stale-price tests      | lending        | higher-priority readiness blocker; high-confidence local evidence; appears across multiple files; clear defensive tests are available. | Add or review: Mock stale, invalid, and sharply moved prices and assert borrow/liquidation behavior follows documented policy.                    |
| 2    | ARK-ORC-001 - Oracle-dependent logic without stale-price tests                       | oracle         | higher-priority readiness blocker; high-confidence local evidence; appears across multiple files; clear defensive tests are available. | Add or review: Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.    |
| 3    | ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage | oracle         | higher-priority readiness blocker; appears across multiple files; clear defensive tests are available.                                 | Add or review: Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.                                   |
| 4    | ARK-ACC-001 - Privileged setters without role-boundary tests                         | access-control | high-confidence local evidence; appears across multiple files; clear defensive tests are available.                                    | Add or review: For every privileged function, assert an unprivileged caller reverts and the documented role succeeds only within intended bounds. |
| 5    | ARK-LEND-005 - Reserve/cash accounting assumptions not covered                       | lending        | high-confidence local evidence; appears across multiple files; clear defensive tests are available.                                    | Add or review: Assert borrow reverts above available liquidity and repay updates cash, debt, reserves, and utilization consistently.              |

## Finding Groups

### Findings by Rule Family

| Rule Family    | Active Findings |
| -------------- | --------------- |
| access-control | 1               |
| lending        | 5               |
| oracle         | 3               |
| testing        | 1               |

### Findings by Confidence

| Confidence | Active Findings |
| ---------- | --------------- |
| high       | 5               |
| low        | 1               |
| medium     | 4               |

## Suppression Summary

- Suppressions loaded: `0`
- Suppressions applied: `0`
- Suppressions should include a reason and be revisited before launch or external review.

## Detected Protocol Shape

- Detected protocol type: `lending`
- Confidence: `manual`
- Protocol score signals: `{"amm": 0, "lending": 149, "oracle": 37, "staking": 0, "vault": 0}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                    | Score | Max | Notes                                                                                                                                                                                                                                                                                |
| --------------------------- | ----- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Repository Structure        | 12    | 15  | Solidity sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                                                                                                                                                   |
| Test Presence               | 20    | 20  | Solidity test files detected.; Assert usage detected.; Foundry or Hardhat test environment detected.; Protocol-specific terms appear in the testable codebase.                                                                                                                       |
| Invariant Fuzz Readiness    | 0     | 20  | No positive signal detected.                                                                                                                                                                                                                                                         |
| Defi Risk Coverage          | 4     | 20  | Role or admin boundaries have some visible coverage.                                                                                                                                                                                                                                 |
| Documentation Readiness     | 8     | 10  | README detected.; Assumptions, invariants, or limitations are documented.; Deployment or role information appears in docs/code comments.                                                                                                                                             |
| Operational Admin Readiness | 15    | 15  | Access-control surface is visible.; Emergency control or incident terms detected.; Upgradeability is absent or has visible documentation/test terms.; Privileged setters or owner boundaries are visible for review.; Monitoring, incident, limitation, or emergency notes detected. |

## Top Readiness Gaps

| ID           | Priority             | Category         | Title                                                                  |
| ------------ | -------------------- | ---------------- | ---------------------------------------------------------------------- |
| ARK-LEND-004 | High readiness gap   | lending-oracle   | Oracle-dependent borrowing/liquidation without stale-price tests       |
| ARK-ORC-001  | High readiness gap   | oracle-pricing   | Oracle-dependent logic without stale-price tests                       |
| ARK-ORC-002  | High readiness gap   | oracle-pricing   | Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage |
| ARK-ACC-001  | Medium readiness gap | access-control   | Privileged setters without role-boundary tests                         |
| ARK-LEND-001 | Medium readiness gap | lending-solvency | Collateral/debt solvency invariant not covered by tests                |

## Rule Pack Coverage

| Rule Pack                                 | Detected | Findings | Docs                                    |
| ----------------------------------------- | -------- | -------- | --------------------------------------- |
| Vault Rule Pack                           | yes      | 0        | docs/VAULT_RULE_PACK.md                 |
| Oracle Rule Pack                          | yes      | 3        | docs/ORACLE_RULE_PACK.md                |
| Access Control / Upgradeability Rule Pack | yes      | 1        | docs/ACCESS_CONTROL_RULE_PACK.md        |
| Reentrancy / Value Flow Rule Pack         | no       | 0        | docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md |
| Staking / Reward Accounting Rule Pack     | yes      | 0        | docs/REWARD_ACCOUNTING_RULE_PACK.md     |
| AMM Rule Pack                             | no       | 0        | docs/AMM_RULE_PACK.md                   |
| Lending Rule Pack                         | yes      | 5        | docs/LENDING_RULE_PACK.md               |

### Vault Rule Pack

- Signals detected: `2`
- Signal terms: `debt, pause`
- Findings: `0`
- Docs: `docs/VAULT_RULE_PACK.md`
- Suggested tests:
  - totalAssets consistency
  - deposit/withdraw roundtrip
  - share conversion rounding
  - strategy gain/loss lifecycle

### Oracle Rule Pack

- Signals detected: `4`
- Signal terms: `answer, getPrice, latestRoundData, priceFeed`
- Findings: `3`
- Docs: `docs/ORACLE_RULE_PACK.md`
- Suggested tests:
  - stale price rejection
  - decimals normalization
  - price bounds
  - TWAP vs spot behavior

### Access Control / Upgradeability Rule Pack

- Signals detected: `4`
- Signal terms: `guardian, onlyOwner, owner, pause`
- Findings: `1`
- Docs: `docs/ACCESS_CONTROL_RULE_PACK.md`
- Suggested tests:
  - unauthorized setter tests
  - pause/emergency boundaries
  - initializer once
  - upgrade authorization

### Staking / Reward Accounting Rule Pack

- Signals detected: `2`
- Signal terms: `collateral, debt`
- Findings: `0`
- Docs: `docs/REWARD_ACCOUNTING_RULE_PACK.md`
- Suggested tests:
  - reward conservation
  - no overclaim
  - index monotonicity
  - stake/unstake/claim lifecycle

### Lending Rule Pack

- Signals detected: `19`
- Signal terms: `LTV, accrueInterest, borrow, borrowIndex, cash, closeFactor, collateral, collateralFactor, debt, guardian, healthFactor, interestIndex, liquidate, liquidationBonus, liquidationThreshold, ratePerSecond, repay, totalBorrows, totalReserves`
- Findings: `5`
- Docs: `docs/LENDING_RULE_PACK.md`
- Suggested tests:
  - collateral/debt invariant
  - liquidation boundary tests
  - interest index monotonicity
  - oracle shock tests

## Risk Signal Summary

### Vault Strategy

- Detected signals: `debt`
- Files with signals: `2`
- Example files: `src/ToyLendingMarket.sol, test/ToyLendingMarket.t.sol`

### Vault Pricing

- Detected signals: `getPrice, latestRoundData, priceFeed`
- Files with signals: `2`
- Example files: `src/ToyLendingMarket.sol, test/ToyLendingMarket.t.sol`

### Vault Admin Ops

- Detected signals: `pause`
- Files with signals: `2`
- Example files: `src/ToyLendingMarket.sol, test/ToyLendingMarket.t.sol`

### Oracle

- Detected signals: `answer, getPrice, latestRoundData, priceFeed`
- Files with signals: `2`
- Example files: `src/ToyLendingMarket.sol, test/ToyLendingMarket.t.sol`

### Access Control

- Detected signals: `guardian, onlyOwner, owner, pause`
- Files with signals: `2`
- Example files: `src/ToyLendingMarket.sol, test/ToyLendingMarket.t.sol`

### Accounting Complexity

- Detected signals: `collateral, debt`
- Files with signals: `2`
- Example files: `src/ToyLendingMarket.sol, test/ToyLendingMarket.t.sol`

### Lending

- Detected signals: `LTV, accrueInterest, borrow, borrowIndex, cash, closeFactor, collateral, collateralFactor, debt, guardian, healthFactor, interestIndex, liquidate, liquidationBonus, liquidationThreshold, ratePerSecond, repay, totalBorrows, totalReserves`
- Files with signals: `2`
- Example files: `src/ToyLendingMarket.sol, test/ToyLendingMarket.t.sol`

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
- Test files: `test/ToyLendingMarket.t.sol`

## Historical Exploit-Pattern Similarity

### Privileged control and operational risk review recommended

- Confidence: `medium`
- Detected signals: `guardian, onlyOwner, owner, pause`
- Why it matters: Admin setters, emergency controls, fee updates, and governance execution paths can become launch blockers if role boundaries are unclear or untested.
- Failed assumption class: Privileged actors can only perform documented, intended operations.
- Broken invariant class: Admin actions cannot silently bypass accounting, oracle, or user-safety invariants.
- Recommended defensive checks:
  - Document every privileged role and setter.
  - Add unauthorized-call tests for each privileged function.
  - Add tests showing pause/emergency controls behave as documented.
- Suggested test/invariant: Invariant: unprivileged callers cannot change fees, oracles, strategies, treasury, pause state, or upgrade target.
- Search tags: `access-control-review, admin-risk, operational-security`

### Liquidation and collateral accounting review recommended

- Confidence: `high`
- Detected signals: `LTV, accrueInterest, answer, borrow, borrowIndex, cash, closeFactor, collateral, collateralFactor, debt, getPrice, guardian, healthFactor, interestIndex, latestRoundData, liquidate, liquidationBonus, liquidationThreshold, priceFeed, ratePerSecond`
- Why it matters: Lending systems depend on collateral, debt, oracle, and liquidation assumptions staying consistent through edge cases.
- Failed assumption class: Collateral value and debt state stay aligned with liquidation and solvency rules.
- Broken invariant class: Borrowers cannot become undercollateralized without expected liquidation or protocol accounting response.
- Recommended defensive checks:
  - Test collateralization and liquidation boundaries.
  - Test oracle movement around borrow and liquidation flows.
  - Check interest index monotonicity and debt accounting.
- Suggested test/invariant: Invariant: positions below required collateralization are liquidatable and solvent positions are not incorrectly liquidated.
- Search tags: `lending, liquidation, collateral, oracle-risk`

## All Readiness Gaps

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword`
- Category: `testing-readiness`

Evidence:
- `src/ToyLendingMarket.sol:1`: Keyword signal matched this readiness finding.
- `test/ToyLendingMarket.t.sol:1`: Keyword signal matched this readiness finding.

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- scanner signal

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

What was detected:

Protocol-like value flows were detected, but no invariant/property testing signal was found.

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

Search tags: `invariant-testing, lending`

### ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage

- Priority: `High readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/ToyLendingMarket.sol:52` in `getPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,,,) = priceFeed.latestRoundData();`
- `src/ToyLendingMarket.sol:58` in `collateralValue`: Solidity function contains oracle or price-feed call evidence. Snippet: `return collateral[user] * getPrice() / 1e18;`
- `src/ToyLendingMarket.sol:94` in `liquidate`: Solidity function contains oracle or price-feed call evidence. Snippet: `uint256 seized = actualRepay * liquidationBonus / getPrice();`

Detected signals:
- scanner signal

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

What was detected:

Oracle and price-feed signals were detected without enough freshness or sanity-check language.


Suggested tests:

- Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
- Test decimals normalization across expected feed decimals.
- Test zero, negative, or invalid oracle answers if applicable.
- Assert normalized price units match accounting units.

Invariant candidates:

- Normalized oracle values remain within documented unit and decimal assumptions.

Search tags: `oracle-risk, price-assumptions`

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

- Priority: `High readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/ToyLendingMarket.sol:52` in `getPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,,,) = priceFeed.latestRoundData();`
- `src/ToyLendingMarket.sol:58` in `collateralValue`: Solidity function contains oracle or price-feed call evidence. Snippet: `return collateral[user] * getPrice() / 1e18;`
- `src/ToyLendingMarket.sol:94` in `liquidate`: Solidity function contains oracle or price-feed call evidence. Snippet: `uint256 seized = actualRepay * liquidationBonus / getPrice();`

Detected signals:
- `answer`
- `getPrice`
- `latestRoundData`
- `priceFeed`

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

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

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/ToyLendingMarket.sol:52` in `getPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,,,) = priceFeed.latestRoundData();`
- `src/ToyLendingMarket.sol:58` in `collateralValue`: Solidity function contains oracle or price-feed call evidence. Snippet: `return collateral[user] * getPrice() / 1e18;`
- `src/ToyLendingMarket.sol:94` in `liquidate`: Solidity function contains oracle or price-feed call evidence. Snippet: `uint256 seized = actualRepay * liquidationBonus / getPrice();`

Detected signals:
- `answer`
- `getPrice`
- `latestRoundData`
- `priceFeed`

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

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

### ARK-ACC-001 - Privileged setters without role-boundary tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `access-control`

Evidence:
- `src/ToyLendingMarket.sol:39` in `setGuardian`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `src/ToyLendingMarket.sol:43` in `pause`: Solidity function contains external value-flow call evidence. Snippet: `require(msg.sender == guardian, "GUARDIAN");`
- `test/documentation coverage`: No semantic-lite access control test coverage terms were detected.

Detected signals:
- `guardian`
- `onlyOwner`
- `owner`
- `pause`

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

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

Suggested tests:

- For every privileged function, assert an unprivileged caller reverts and the documented role succeeds only within intended bounds.
- Test unauthorized callers cannot change critical parameters.
- Test authorized role can perform expected setter actions.
- Document role ownership and transfer procedure.

Invariant candidates:

- Unauthorized users cannot mutate privileged configuration.

Search tags: `access-control-review, admin-risk, access-control-rule-pack`

### ARK-LEND-001 - Collateral/debt solvency invariant not covered by tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `lending-solvency`

Evidence:
- `src/ToyLendingMarket.sol:48` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `src/ToyLendingMarket.sol:58` in `collateralValue`: Solidity function contains oracle or price-feed call evidence. Snippet: `return collateral[user] * getPrice() / 1e18;`
- `src/ToyLendingMarket.sol:62` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`

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
- `healthFactor`
- `interestIndex`
- `liquidate`
- `liquidationBonus`
- `liquidationThreshold`
- `ratePerSecond`
- `repay`
- `totalBorrows`
- `totalReserves`

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

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
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `lending-liquidation`

Evidence:
- `src/ToyLendingMarket.sol:48` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `src/ToyLendingMarket.sol:58` in `collateralValue`: Solidity function contains oracle or price-feed call evidence. Snippet: `return collateral[user] * getPrice() / 1e18;`
- `src/ToyLendingMarket.sol:62` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`

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
- `healthFactor`
- `interestIndex`
- `liquidate`
- `liquidationBonus`
- `liquidationThreshold`
- `ratePerSecond`
- `repay`
- `totalBorrows`
- `totalReserves`

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

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
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `lending-interest-index`

Evidence:
- `src/ToyLendingMarket.sol:48` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `src/ToyLendingMarket.sol:58` in `collateralValue`: Solidity function contains oracle or price-feed call evidence. Snippet: `return collateral[user] * getPrice() / 1e18;`
- `src/ToyLendingMarket.sol:62` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`

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
- `healthFactor`
- `interestIndex`
- `liquidate`
- `liquidationBonus`
- `liquidationThreshold`
- `ratePerSecond`
- `repay`
- `totalBorrows`
- `totalReserves`

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

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

### ARK-LEND-004 - Oracle-dependent borrowing/liquidation without stale-price tests

- Priority: `High readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `lending-oracle`

Evidence:
- `src/ToyLendingMarket.sol:52` in `getPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,,,) = priceFeed.latestRoundData();`
- `src/ToyLendingMarket.sol:58` in `collateralValue`: Solidity function contains oracle or price-feed call evidence. Snippet: `return collateral[user] * getPrice() / 1e18;`
- `src/ToyLendingMarket.sol:94` in `liquidate`: Solidity function contains oracle or price-feed call evidence. Snippet: `uint256 seized = actualRepay * liquidationBonus / getPrice();`

Detected signals:
- `LTV`
- `accrueInterest`
- `answer`
- `borrow`
- `borrowIndex`
- `cash`
- `closeFactor`
- `collateral`
- `collateralFactor`
- `debt`
- `getPrice`
- `guardian`
- `healthFactor`
- `interestIndex`
- `latestRoundData`
- `liquidate`
- `liquidationBonus`
- `liquidationThreshold`
- `priceFeed`
- `ratePerSecond`

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

What was detected:

Borrowing, collateral valuation, health-factor, or liquidation logic appears oracle-dependent without visible stale-price or price-shock tests.

Why it matters:

Lending solvency can be distorted when collateral values depend on stale, invalid, or mis-normalized prices.

Historical pattern similarity:

Maps to oracle-dependent liquidation and collateral valuation readiness classes.

Recommended defensive checks:

- stale oracle rejection
- decimals normalization
- price shock boundary
- borrow blocked on invalid price

Related Knowledge:

- Historical patterns: pattern-oracle-stale-price, pattern-collateral-debt-invariant
- Suggested defensive tests: stale-oracle-rejection, decimals-normalization-test, price-shock-boundary-test
- Related PoCs: poc-2025-11-moonwell, poc-2020-10-harvest

Suggested tests:

- Mock stale, invalid, and sharply moved prices and assert borrow/liquidation behavior follows documented policy.
- Test stale oracle rejection for borrow and liquidation paths.
- Test decimals normalization for collateral valuation.
- Test price shock boundaries around health-factor transitions.

Invariant candidates:

- Borrowing and liquidation decisions only use oracle data that satisfies documented validity policy.

Search tags: `lending-oracle, oracle-risk, lending-rule-pack`

### ARK-LEND-005 - Reserve/cash accounting assumptions not covered

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `semantic-lite`
- Category: `lending-liquidity`

Evidence:
- `src/ToyLendingMarket.sol:48` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `src/ToyLendingMarket.sol:58` in `collateralValue`: Solidity function contains oracle or price-feed call evidence. Snippet: `return collateral[user] * getPrice() / 1e18;`
- `src/ToyLendingMarket.sol:62` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`

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
- `healthFactor`
- `interestIndex`
- `liquidate`
- `liquidationBonus`
- `liquidationThreshold`
- `ratePerSecond`
- `repay`
- `totalBorrows`
- `totalReserves`

Affected files:
- `src/ToyLendingMarket.sol`
- `test/ToyLendingMarket.t.sol`

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

- **stale price rejection** (`oracle`): Stale oracle rounds should be rejected or handled according to documented policy.
- **decimals normalization** (`oracle`): Price decimals should be normalized consistently before accounting decisions.
- **price bounds** (`oracle`): Outlier prices should hit documented bounds or review paths.
- **TWAP or sanity check** (`oracle`): Spot price dependence should be bounded by TWAP, sanity checks, or explicit assumptions.
- **oracle update access control** (`oracle`): Only authorized roles should change oracle configuration.
- **collateralization invariant** (`lending`): Borrower positions should respect collateralization requirements after every user action.
- **liquidation solvency** (`lending`): Liquidations should improve solvency and preserve accounting assumptions.
- **interest index monotonicity** (`lending`): Interest indexes should move monotonically according to configured rate logic.
- **oracle manipulation resistance** (`lending`): Borrow and liquidation paths should resist transient price manipulation.
- **borrow/repay accounting consistency** (`lending`): Debt and collateral balances should reconcile after borrow and repay sequences.
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

- No issue checklist file was requested in this run.
- To generate one: `python3 scripts/pre_audit_scan.py --root . --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md`
- Generated issue plan: `examples/reports/lending-fixture-issue-plan.json`
- Issue plan JSON can be used with `scripts/create_github_issues.py` in dry-run, create, or update mode.

## GitHub Action Outputs

- Markdown Report: `examples/reports/lending-fixture-pre-audit-report.md`
- Json Report: `examples/reports/lending-fixture-pre-audit-report.json`
- Sarif Report: `examples/reports/lending-fixture.sarif.json`
- Issue Plan: `examples/reports/lending-fixture-issue-plan.json`

## Search Tags

`access-control-review`, `arkheionx`, `audit-preparation`, `defi-security`, `foundry`, `historical-exploit-pattern`, `indie-defi`, `invariant-testing`, `oracle-risk`, `pre-audit-readiness`, `reentrancy-review`, `root-cause-analysis`, `smart-contract-security`, `solidity-security`, `vault-accounting`

## Recommended Next Steps

1. Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
2. Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
3. Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
4. Run a formal smart contract audit before mainnet launch or before handling real user funds.

## What This Report Does Not Prove

- It does not prove protocol safety.
- It does not confirm exploitability.
- It does not replace manual review.
- It does not replace a formal audit.

## Formal Audit Recommendation

Run a formal smart contract audit before mainnet deployment, before material TVL, or before handling real user funds.

