# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/semantic-lite-fixture`
- Generated at: `2026-05-25T19:28:59+00:00`
- Protocol type: `oracle`
- Protocol confidence: `high`
- Files scanned: `5`
- Scanner version: `0.6.0`

| File class       | Count |
| ---------------- | ----- |
| Solidity sources | 2     |
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

- Readiness score: **58/100**
- Score band: **Early readiness**
- Active readiness gaps: `6`
- Suppressed readiness gaps: `0`
- Top readiness gaps:
  - **ARK-ACC-001 (Medium readiness gap):** Privileged setters without role-boundary tests - Add tests proving unauthorized users cannot call privileged setters or role-management functions.
  - **ARK-ORC-004 (Medium readiness gap):** Oracle setter/admin path without role-boundary tests - Add tests proving only documented roles can update oracle configuration.
  - **ARK-ACC-003 (Low readiness gap):** Admin role concentration not documented - Document who can change critical configuration and whether controls use a multisig, timelock, guardian, or single owner.
  - **ARK-RWD-001 (Low readiness gap):** Reward accounting needs conservation coverage - Add reward conservation and no-overclaim tests across multiple users and timing boundaries.
  - **ARK-RWD-002 (Low readiness gap):** Accumulator/index logic without precision/rounding tests - Add precision, dust, rounding, and small-balance tests for accumulator or index logic.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
  - Run a formal smart contract audit before mainnet launch or before handling real user funds.

## Detected Protocol Shape

- Detected protocol type: `oracle`
- Confidence: `high`
- Protocol score signals: `{"amm": 0, "lending": 0, "oracle": 34, "staking": 3, "vault": 4}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                    | Score | Max | Notes                                                                                                                                                                 |
| --------------------------- | ----- | --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository Structure        | 12    | 15  | Solidity sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                                    |
| Test Presence               | 20    | 20  | Solidity test files detected.; Assert usage detected.; Foundry or Hardhat test environment detected.; Protocol-specific terms appear in the testable codebase.        |
| Invariant Fuzz Readiness    | 0     | 20  | No positive signal detected.                                                                                                                                          |
| Defi Risk Coverage          | 9     | 20  | Oracle assumptions have at least some documented or tested controls.; Role or admin boundaries have some visible coverage.                                            |
| Documentation Readiness     | 8     | 10  | README detected.; Assumptions, invariants, or limitations are documented.; Deployment or role information appears in docs/code comments.                              |
| Operational Admin Readiness | 9     | 15  | Access-control surface is visible.; Upgradeability is absent or has visible documentation/test terms.; Privileged setters or owner boundaries are visible for review. |

## Top Readiness Gaps

| ID          | Priority             | Category          | Title                                                    |
| ----------- | -------------------- | ----------------- | -------------------------------------------------------- |
| ARK-ACC-001 | Medium readiness gap | access-control    | Privileged setters without role-boundary tests           |
| ARK-ORC-004 | Medium readiness gap | oracle-pricing    | Oracle setter/admin path without role-boundary tests     |
| ARK-ACC-003 | Low readiness gap    | access-control    | Admin role concentration not documented                  |
| ARK-RWD-001 | Low readiness gap    | reward-accounting | Reward accounting needs conservation coverage            |
| ARK-RWD-002 | Low readiness gap    | reward-accounting | Accumulator/index logic without precision/rounding tests |

## Rule Pack Coverage

| Rule Pack                                 | Detected | Findings | Docs                                    |
| ----------------------------------------- | -------- | -------- | --------------------------------------- |
| Vault Rule Pack                           | yes      | 0        | docs/VAULT_RULE_PACK.md                 |
| Oracle Rule Pack                          | yes      | 1        | docs/ORACLE_RULE_PACK.md                |
| Access Control / Upgradeability Rule Pack | yes      | 2        | docs/ACCESS_CONTROL_RULE_PACK.md        |
| Reentrancy / Value Flow Rule Pack         | no       | 0        | docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md |
| Staking / Reward Accounting Rule Pack     | yes      | 2        | docs/REWARD_ACCOUNTING_RULE_PACK.md     |

### Vault Rule Pack

- Signals detected: `2`
- Signal terms: `decimals, setOracle`
- Findings: `0`
- Docs: `docs/VAULT_RULE_PACK.md`
- Suggested tests:
  - totalAssets consistency
  - deposit/withdraw roundtrip
  - share conversion rounding
  - strategy gain/loss lifecycle

### Oracle Rule Pack

- Signals detected: `12`
- Signal terms: `AggregatorV3Interface, answer, answeredInRound, decimals, latestRoundData, maxPrice, minPrice, oracle, priceFeed, roundId, setOracle, updatedAt`
- Findings: `1`
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

### Staking / Reward Accounting Rule Pack

- Signals detected: `2`
- Signal terms: `decimals, reward`
- Findings: `2`
- Docs: `docs/REWARD_ACCOUNTING_RULE_PACK.md`
- Suggested tests:
  - reward conservation
  - no overclaim
  - index monotonicity
  - stake/unstake/claim lifecycle

## Risk Signal Summary

### Vault Accounting Risk

- Detected signals: `decimals`
- Files with signals: `1`
- Example files: `test/RealOracleConsumer.t.sol`

### Vault Pricing

- Detected signals: `decimals, latestRoundData, oracle, priceFeed`
- Files with signals: `3`
- Example files: `src/DocsOnlyPlanning.sol, src/RealOracleConsumer.sol, test/RealOracleConsumer.t.sol`

### Vault Admin Ops

- Detected signals: `setOracle`
- Files with signals: `1`
- Example files: `src/RealOracleConsumer.sol`

### Oracle

- Detected signals: `AggregatorV3Interface, answer, answeredInRound, decimals, latestRoundData, maxPrice, minPrice, oracle, priceFeed, roundId, setOracle, updatedAt`
- Files with signals: `3`
- Example files: `src/DocsOnlyPlanning.sol, src/RealOracleConsumer.sol, test/RealOracleConsumer.t.sol`

### Access Control

- Detected signals: `onlyOwner, owner, setOracle`
- Files with signals: `1`
- Example files: `src/RealOracleConsumer.sol`

### Accounting Complexity

- Detected signals: `decimals, reward`
- Files with signals: `2`
- Example files: `src/DocsOnlyPlanning.sol, test/RealOracleConsumer.t.sol`

### Staking Rewards

- Detected signals: `reward`
- Files with signals: `1`
- Example files: `src/DocsOnlyPlanning.sol`

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
- Edge Case Tests: `False`
- Test files: `test/RealOracleConsumer.t.sol`

## Historical Exploit-Pattern Similarity

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
- Detected signals: `decimals, reward`
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
- `src/DocsOnlyPlanning.sol:1`: Keyword signal matched this readiness finding.
- `src/RealOracleConsumer.sol:1`: Keyword signal matched this readiness finding.
- `test/RealOracleConsumer.t.sol:1`: Keyword signal matched this readiness finding.

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- scanner signal

Affected files:
- `src/DocsOnlyPlanning.sol`
- `src/RealOracleConsumer.sol`
- `test/RealOracleConsumer.t.sol`

What was detected:

Protocol-like value flows were detected, but no invariant/property testing signal was found.

Suggested tests:

- Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.

Search tags: `invariant-testing, oracle`

### ARK-RWD-001 - Reward accounting needs conservation coverage

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `reward-accounting`

Evidence:
- `test/documentation coverage`: No semantic-lite reward test coverage terms were detected.
- `src/DocsOnlyPlanning.sol:1`: Keyword signal matched this readiness finding.
- `src/RealOracleConsumer.sol:1`: Keyword signal matched this readiness finding.
- `test/RealOracleConsumer.t.sol:1`: Keyword signal matched this readiness finding.

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- scanner signal

Affected files:
- `src/DocsOnlyPlanning.sol`
- `src/RealOracleConsumer.sol`
- `test/RealOracleConsumer.t.sol`

What was detected:

Reward/index/claim signals were detected without invariant testing.

Suggested tests:

- Add reward conservation and no-overclaim tests across multiple users and timing boundaries.

Search tags: `reward-accounting, precision`

### ARK-ORC-004 - Oracle setter/admin path without role-boundary tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `src/RealOracleConsumer.sol:29` in `readPrice`: Solidity function contains oracle or price-feed call evidence. Snippet: `(, int256 answer,, uint256 updatedAt,) = priceFeed.latestRoundData();`
- `test/documentation coverage`: Matching test coverage terms detected: bounds, decimals, oracle, price, stale, updatedat.
- `src/DocsOnlyPlanning.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, decimals, latestRoundData, maxPrice, minPrice, oracle`
- `src/RealOracleConsumer.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, decimals, latestRoundData, maxPrice, minPrice, oracle`
- `test/RealOracleConsumer.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `AggregatorV3Interface, answer, answeredInRound, decimals, latestRoundData, maxPrice, minPrice, oracle`

Detected signals:
- `AggregatorV3Interface`
- `answer`
- `answeredInRound`
- `decimals`
- `latestRoundData`
- `maxPrice`
- `minPrice`
- `oracle`
- `priceFeed`
- `roundId`
- `setOracle`
- `updatedAt`

Affected files:
- `src/DocsOnlyPlanning.sol`
- `src/RealOracleConsumer.sol`
- `test/RealOracleConsumer.t.sol`

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

### ARK-ACC-001 - Privileged setters without role-boundary tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `access-control`

Evidence:
- `src/RealOracleConsumer.sol:25` in `setOracle`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `test/documentation coverage`: No semantic-lite access control test coverage terms were detected.
- `src/DocsOnlyPlanning.sol:1`: Keyword signal matched this readiness finding. Snippet: `onlyOwner, owner, setOracle`
- `src/RealOracleConsumer.sol:1`: Keyword signal matched this readiness finding. Snippet: `onlyOwner, owner, setOracle`
- `test/RealOracleConsumer.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `onlyOwner, owner, setOracle`

Detected signals:
- `onlyOwner`
- `owner`
- `setOracle`

Affected files:
- `src/DocsOnlyPlanning.sol`
- `src/RealOracleConsumer.sol`
- `test/RealOracleConsumer.t.sol`

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
- `src/RealOracleConsumer.sol:25` in `setOracle`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `test/documentation coverage`: No semantic-lite access control test coverage terms were detected.
- `src/DocsOnlyPlanning.sol:1`: Keyword signal matched this readiness finding. Snippet: `onlyOwner, owner, setOracle`
- `src/RealOracleConsumer.sol:1`: Keyword signal matched this readiness finding. Snippet: `onlyOwner, owner, setOracle`
- `test/RealOracleConsumer.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `onlyOwner, owner, setOracle`

Detected signals:
- `onlyOwner`
- `owner`
- `setOracle`

Affected files:
- `src/DocsOnlyPlanning.sol`
- `src/RealOracleConsumer.sol`
- `test/RealOracleConsumer.t.sol`

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

### ARK-RWD-002 - Accumulator/index logic without precision/rounding tests

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `reward-accounting`

Evidence:
- `test/documentation coverage`: No semantic-lite reward test coverage terms were detected.
- `src/DocsOnlyPlanning.sol:1`: Keyword signal matched this readiness finding. Snippet: `reward`
- `test/RealOracleConsumer.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `reward`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `reward`

Affected files:
- `src/DocsOnlyPlanning.sol`
- `test/RealOracleConsumer.t.sol`

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
- **reward conservation** (`staking`): Total claimed plus remaining claimable should not exceed funded rewards beyond rounding.
- **no overclaim** (`staking`): Users should not claim more than their funded and accrued share.
- **index monotonicity** (`staking`): Reward indexes should be monotonic and supply-aware.
- **stake/unstake roundtrip** (`staking`): Stake and unstake flows should preserve balances and reward accounting.
- **reward accounting precision** (`staking`): Small balances and precision edges should not create systematic reward drift.
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

- Generated checklist: `examples/reports/semantic-lite-fixture-issue-checklist.md`
- Use this as a copyable GitHub Issue body or as a remediation tracker.
- Generated issue plan: `examples/reports/semantic-lite-fixture-issue-plan.json`
- Issue plan JSON can be used with `scripts/create_github_issues.py` in dry-run, create, or update mode.

## GitHub Action Outputs

- Markdown Report: `examples/reports/semantic-lite-fixture-pre-audit-report.md`
- Json Report: `examples/reports/semantic-lite-fixture-pre-audit-report.json`
- Sarif Report: `examples/reports/semantic-lite-fixture.sarif.json`
- Issue Checklist: `examples/reports/semantic-lite-fixture-issue-checklist.md`
- Issue Plan: `examples/reports/semantic-lite-fixture-issue-plan.json`
- Baseline: `examples/reports/semantic-lite-fixture.baseline.json`

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

