# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/mini-vault`
- Generated at: `2026-05-25T19:28:59+00:00`
- Protocol type: `vault`
- Protocol confidence: `high`
- Files scanned: `5`
- Scanner version: `0.6.0`

| File class       | Count |
| ---------------- | ----- |
| Solidity sources | 1     |
| Solidity tests   | 2     |
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
| Semantic contracts       | 2        |
| Semantic test files      | 1        |
| Slither                  | disabled |
| Slither detectors        | 0        |
| Test coverage mapping    | enabled  |

## Executive Summary

- Readiness score: **73/100**
- Score band: **Improving**
- Active readiness gaps: `5`
- Suppressed readiness gaps: `0`
- Top readiness gaps:
  - **ARK-REENT-001 (High readiness gap):** Value flow with external calls needs reentrancy review - Review state ordering and add local reentrant receiver tests around every value-flow path.
  - **ARK-VLT-001 (Medium readiness gap):** Vault accounting without invariant tests - Add Foundry invariants for share/accounting conservation across deposit, withdraw, donation, fee, and emergency scenarios.
  - **ARK-VLT-007 (Medium readiness gap):** Fee logic without fee accounting tests - Add deposit, withdrawal, management, and performance fee tests where relevant.
  - **ARK-ACC-003 (Low readiness gap):** Admin role concentration not documented - Document who can change critical configuration and whether controls use a multisig, timelock, guardian, or single owner.
  - **ARK-REENT-004 (Low readiness gap):** External call path without documented ordering assumptions - Document state-update ordering, callback assumptions, and why any unguarded external calls are safe by design.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
  - Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
  - Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
  - Run a formal smart contract audit before mainnet launch or before handling real user funds.

## Detected Protocol Shape

- Detected protocol type: `vault`
- Confidence: `high`
- Protocol score signals: `{"amm": 0, "lending": 0, "oracle": 0, "staking": 0, "vault": 68}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                                | Score | Max | Notes                                                                                                                                                                                                             |
| --------------------------------------- | ----- | --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository Structure                    | 8     | 10  | Solidity vault-like sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                                                                     |
| Test Presence                           | 13    | 15  | Solidity tests detected.; Assert usage detected.; Foundry or Hardhat environment detected.; Mint or preview function test signals detected.                                                                       |
| Vault Accounting Coverage               | 16    | 20  | Vault/ERC4626 share-accounting surface detected.; totalAssets test signal detected.; Shares/assets conversion test signal detected.; Donation, inflation, decimals, or rounding test signal detected.             |
| Invariant Fuzz Readiness                | 2     | 20  | Edge-case test signal detected.                                                                                                                                                                                   |
| Oracle Pricing Readiness                | 10    | 10  | No explicit oracle or pool-pricing dependency detected.                                                                                                                                                           |
| Strategy Withdrawal Lifecycle Readiness | 10    | 10  | No strategy or queued-withdrawal lifecycle surface detected.                                                                                                                                                      |
| Admin Operational Readiness             | 9     | 10  | Vault admin/operational surface is visible.; Role or unauthorized-call coverage signal detected.; Pause or emergency control signal detected.; Upgradeability is absent or initializer/upgrade terms are visible. |
| Documentation Readiness                 | 5     | 5   | README detected.; Vault assumptions or limitations are documented.; Role, treasury, owner, or deployment terms are documented.                                                                                    |

## Top Readiness Gaps

| ID            | Priority             | Category              | Title                                                      |
| ------------- | -------------------- | --------------------- | ---------------------------------------------------------- |
| ARK-REENT-001 | High readiness gap   | reentrancy-value-flow | Value flow with external calls needs reentrancy review     |
| ARK-VLT-001   | Medium readiness gap | vault-accounting      | Vault accounting without invariant tests                   |
| ARK-VLT-007   | Medium readiness gap | vault-accounting      | Fee logic without fee accounting tests                     |
| ARK-ACC-003   | Low readiness gap    | access-control        | Admin role concentration not documented                    |
| ARK-REENT-004 | Low readiness gap    | reentrancy-value-flow | External call path without documented ordering assumptions |

## Rule Pack Coverage

| Rule Pack                                 | Detected | Findings | Docs                                    |
| ----------------------------------------- | -------- | -------- | --------------------------------------- |
| Vault Rule Pack                           | yes      | 2        | docs/VAULT_RULE_PACK.md                 |
| Oracle Rule Pack                          | yes      | 0        | docs/ORACLE_RULE_PACK.md                |
| Access Control / Upgradeability Rule Pack | yes      | 1        | docs/ACCESS_CONTROL_RULE_PACK.md        |
| Reentrancy / Value Flow Rule Pack         | yes      | 2        | docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md |
| Staking / Reward Accounting Rule Pack     | yes      | 0        | docs/REWARD_ACCOUNTING_RULE_PACK.md     |

### Vault Rule Pack

- Signals detected: `15`
- Signal terms: `assets, balanceOf, convertToAssets, convertToShares, decimals, deposit, mint, pause, setFee, shares, totalAssets, totalSupply, treasury, unpause, withdraw`
- Findings: `2`
- Docs: `docs/VAULT_RULE_PACK.md`
- Suggested tests:
  - totalAssets consistency
  - deposit/withdraw roundtrip
  - share conversion rounding
  - strategy gain/loss lifecycle

### Oracle Rule Pack

- Signals detected: `1`
- Signal terms: `decimals`
- Findings: `0`
- Docs: `docs/ORACLE_RULE_PACK.md`
- Suggested tests:
  - stale price rejection
  - decimals normalization
  - price bounds
  - TWAP vs spot behavior

### Access Control / Upgradeability Rule Pack

- Signals detected: `5`
- Signal terms: `onlyOwner, owner, pause, setFee, unpause`
- Findings: `1`
- Docs: `docs/ACCESS_CONTROL_RULE_PACK.md`
- Suggested tests:
  - unauthorized setter tests
  - pause/emergency boundaries
  - initializer once
  - upgrade authorization

### Reentrancy / Value Flow Rule Pack

- Signals detected: `3`
- Signal terms: `transfer, transferFrom, withdraw`
- Findings: `2`
- Docs: `docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md`
- Suggested tests:
  - reentrant receiver mock
  - state update ordering
  - double claim prevention
  - failed external call behavior

### Staking / Reward Accounting Rule Pack

- Signals detected: `4`
- Signal terms: `decimals, fee, shares, withdraw`
- Findings: `0`
- Docs: `docs/REWARD_ACCOUNTING_RULE_PACK.md`
- Suggested tests:
  - reward conservation
  - no overclaim
  - index monotonicity
  - stake/unstake/claim lifecycle

## Risk Signal Summary

### Vault Erc4626

- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, deposit, mint, shares, totalAssets, totalSupply, withdraw`
- Files with signals: `2`
- Example files: `src/MiniVault.sol, test/MiniVault.t.sol`

### Vault Accounting

- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, deposit, mint, shares, totalAssets, totalSupply, withdraw`
- Files with signals: `2`
- Example files: `src/MiniVault.sol, test/MiniVault.t.sol`

### Vault Accounting Risk

- Detected signals: `convertToAssets, convertToShares, decimals, totalAssets, treasury`
- Files with signals: `2`
- Example files: `src/MiniVault.sol, test/MiniVault.t.sol`

### Vault Pricing

- Detected signals: `decimals`
- Files with signals: `1`
- Example files: `test/MiniVault.t.sol`

### Vault Admin Ops

- Detected signals: `pause, setFee, unpause`
- Files with signals: `2`
- Example files: `src/MiniVault.sol, test/MiniVault.t.sol`

### Oracle

- Detected signals: `decimals`
- Files with signals: `1`
- Example files: `test/MiniVault.t.sol`

### Access Control

- Detected signals: `onlyOwner, owner, pause, setFee, unpause`
- Files with signals: `2`
- Example files: `src/MiniVault.sol, test/MiniVault.t.sol`

### Reentrancy Value Flow

- Detected signals: `transfer, transferFrom, withdraw`
- Files with signals: `2`
- Example files: `src/MiniVault.sol, test/MiniVault.t.sol`

### Accounting Complexity

- Detected signals: `decimals, fee`
- Files with signals: `2`
- Example files: `src/MiniVault.sol, test/MiniVault.t.sol`

### Staking Rewards

- Detected signals: `shares, withdraw`
- Files with signals: `2`
- Example files: `src/MiniVault.sol, test/MiniVault.t.sol`

### Testing And Documentation

- Test Directory: `True`
- Foundry Tests: `True`
- Hardhat Tests: `False`
- Test File Count: `1`
- Invariant Tests: `False`
- Fuzz Tests: `False`
- Handler Contracts: `False`
- Assert Usage: `True`
- Assert Count: `4`
- Forge Std: `True`
- Echidna: `False`
- Slither: `False`
- Ci Workflow: `False`
- Edge Case Tests: `True`
- Test files: `test/MiniVault.t.sol`

## Vault Rule Pack Coverage

The v0.2.0 vault rule pack checks ERC4626-like share accounting, totalAssets assumptions, conversion rounding, fee logic, strategies, withdrawal lifecycle, oracle/pricing assumptions, admin controls, and pause/emergency behavior.

| Vault check          | Covered | Matched terms |
| -------------------- | ------- | ------------- |
| decimals rounding    | yes     | decimals      |
| deposit              | yes     | deposit       |
| donation inflation   | no      | -             |
| emergency pause      | yes     | pause         |
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
| withdraw             | no      | -             |
| withdrawal lifecycle | no      | -             |

## Historical Exploit-Pattern Similarity

### Vault accounting invariant readiness gap

- Confidence: `high`
- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, decimals, deposit, fee, mint, shares, totalAssets, totalSupply, treasury, withdraw`
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
- Detected signals: `onlyOwner, owner, pause, setFee, unpause`
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
- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, deposit, mint, shares, totalAssets, totalSupply, transfer, transferFrom, withdraw`
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
- Detected signals: `onlyOwner, owner, pause, setFee, unpause`
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

- Confidence: `medium`
- Detected signals: `decimals, fee, shares, withdraw`
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

### ARK-VLT-001 - Vault accounting without invariant tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `vault-accounting`

Evidence:
- `src/MiniVault.sol:43` in `totalAssets`: Solidity function shape matches this readiness finding. Snippet: `totalAssets`
- `src/MiniVault.sol:47` in `convertToShares`: Solidity function shape matches this readiness finding. Snippet: `if (totalSupply == 0 || totalAssets() == 0) {`
- `src/MiniVault.sol:54` in `convertToAssets`: Solidity function shape matches this readiness finding. Snippet: `if (totalSupply == 0) {`
- `src/MiniVault.sol:61` in `deposit`: Solidity function contains external value-flow call evidence. Snippet: `require(asset.transferFrom(msg.sender, address(this), assets), "TRANSFER_FROM_FAILED");`
- `src/MiniVault.sol:80` in `withdraw`: Solidity function contains external value-flow call evidence. Snippet: `require(asset.transfer(receiver, assets), "TRANSFER_FAILED");`

Detected signals:
- `assets`
- `balanceOf`
- `convertToAssets`
- `convertToShares`
- `deposit`
- `mint`
- `shares`
- `totalAssets`
- `totalSupply`
- `withdraw`

Affected files:
- `src/MiniVault.sol`
- `test/MiniVault.t.sol`

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

### ARK-VLT-007 - Fee logic without fee accounting tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `vault-accounting`

Evidence:
- `src/MiniVault.sol:43` in `totalAssets`: Solidity function shape matches this readiness finding. Snippet: `totalAssets`
- `src/MiniVault.sol:47` in `convertToShares`: Solidity function shape matches this readiness finding. Snippet: `if (totalSupply == 0 || totalAssets() == 0) {`
- `src/MiniVault.sol:54` in `convertToAssets`: Solidity function shape matches this readiness finding. Snippet: `if (totalSupply == 0) {`
- `src/MiniVault.sol:61` in `deposit`: Solidity function contains external value-flow call evidence. Snippet: `require(asset.transferFrom(msg.sender, address(this), assets), "TRANSFER_FROM_FAILED");`
- `src/MiniVault.sol:80` in `withdraw`: Solidity function contains external value-flow call evidence. Snippet: `require(asset.transfer(receiver, assets), "TRANSFER_FAILED");`

Detected signals:
- `fee`

Affected files:
- `src/MiniVault.sol`
- `test/MiniVault.t.sol`

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

### ARK-ACC-003 - Admin role concentration not documented

- Priority: `Low readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `access-control`

Evidence:
- `src/MiniVault.sol:95` in `setFee`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `src/MiniVault.sol:101` in `pause`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `src/MiniVault.sol:106` in `unpause`: Solidity function contains access-control or lifecycle modifier evidence. Snippet: `onlyOwner`
- `test/documentation coverage`: Matching test coverage terms detected: owner, prank.
- `src/MiniVault.sol:1`: Keyword signal matched this readiness finding. Snippet: `onlyOwner, owner, pause, setFee, unpause`

Detected signals:
- `onlyOwner`
- `owner`
- `pause`
- `setFee`
- `unpause`

Affected files:
- `src/MiniVault.sol`
- `test/MiniVault.t.sol`

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

### ARK-REENT-001 - Value flow with external calls needs reentrancy review

- Priority: `High readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `reentrancy-value-flow`

Evidence:
- `src/MiniVault.sol:61` in `deposit`: Solidity function contains external value-flow call evidence. Snippet: `require(asset.transferFrom(msg.sender, address(this), assets), "TRANSFER_FROM_FAILED");`
- `src/MiniVault.sol:80` in `withdraw`: Solidity function contains external value-flow call evidence. Snippet: `require(asset.transfer(receiver, assets), "TRANSFER_FAILED");`
- `test/documentation coverage`: No semantic-lite reentrancy test coverage terms were detected.
- `src/MiniVault.sol:1`: Keyword signal matched this readiness finding. Snippet: `transfer, transferFrom, withdraw`
- `test/MiniVault.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `transfer, transferFrom, withdraw`

Detected signals:
- `transfer`
- `transferFrom`
- `withdraw`

Affected files:
- `src/MiniVault.sol`
- `test/MiniVault.t.sol`

What was detected:

Withdraw, redeem, claim, transfer, callback, or low-level call signals were detected without a visible reentrancy guard signal.

Why it matters:

External calls can hand control to untrusted code before accounting reaches a safe state.

Historical pattern similarity:

Maps to reentrancy and callback-driven value-flow readiness classes.

Recommended defensive checks:

- state update before external call
- reentrant receiver mock
- failed external call behavior
- single-claim guarantees

Suggested tests:

- Use a local malicious receiver mock and assert withdraw/redeem/claim cannot be executed twice through reentry.

Search tags: `reentrancy-review, value-flow, reentrancy-rule-pack`

### ARK-REENT-004 - External call path without documented ordering assumptions

- Priority: `Low readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `reentrancy-value-flow`

Evidence:
- `src/MiniVault.sol:61` in `deposit`: Solidity function contains external value-flow call evidence. Snippet: `require(asset.transferFrom(msg.sender, address(this), assets), "TRANSFER_FROM_FAILED");`
- `src/MiniVault.sol:80` in `withdraw`: Solidity function contains external value-flow call evidence. Snippet: `require(asset.transfer(receiver, assets), "TRANSFER_FAILED");`
- `test/documentation coverage`: No semantic-lite reentrancy test coverage terms were detected.
- `src/MiniVault.sol:1`: Keyword signal matched this readiness finding. Snippet: `transfer, transferFrom, withdraw`
- `test/MiniVault.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `transfer, transferFrom, withdraw`

Detected signals:
- `transfer`
- `transferFrom`
- `withdraw`

Affected files:
- `src/MiniVault.sol`
- `test/MiniVault.t.sol`

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

- Generated skeleton: `test/invariant/ArkheionxReadinessInvariants.t.sol`

- **totalAssets consistency** (`vault`): totalAssets should match local asset accounting and strategy balances within documented rounding.
- **deposit/withdraw roundtrip** (`vault`): A user should not create value by depositing and withdrawing through normal paths.
- **convertToShares/convertToAssets consistency** (`vault`): Conversion functions should be mutually consistent within documented rounding across supply states.
- **share price donation resistance** (`vault`): Donations, low supply, and external balances should not let one actor distort share value unexpectedly.
- **fee accounting conservation** (`vault`): Fees should be bounded, documented, and unable to overcharge beyond configured limits.
- **strategy balance drift handling** (`vault`): Strategy gains, losses, and withdrawals should remain reflected in accounting assumptions.
- **withdrawal lifecycle conservation** (`vault`): Queued or delayed withdrawals should conserve shares/assets through request, cooldown, claim, and cancellation.
- **pause behavior** (`vault`): Pause should block risky flows while preserving documented emergency exits.
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

- Generated checklist: `examples/reports/mini-vault-issue-checklist.md`
- Use this as a copyable GitHub Issue body or as a remediation tracker.
- Generated issue plan: `examples/reports/mini-vault-issue-plan.json`
- Issue plan JSON can be used with `scripts/create_github_issues.py` in dry-run, create, or update mode.

## GitHub Action Outputs

- Markdown Report: `examples/reports/mini-vault-pre-audit-report.md`
- Json Report: `examples/reports/mini-vault-pre-audit-report.json`
- Sarif Report: `examples/reports/mini-vault.sarif.json`
- Summary: `examples/reports/mini-vault-action-summary.md`
- Comment: `examples/reports/mini-vault-pr-comment.md`
- Issue Checklist: `examples/reports/mini-vault-issue-checklist.md`
- Issue Plan: `examples/reports/mini-vault-issue-plan.json`
- Baseline: `examples/reports/mini-vault.baseline.json`

## Search Tags

`access-control-review`, `arkheionx`, `audit-preparation`, `defi-security`, `foundry`, `historical-exploit-pattern`, `indie-defi`, `invariant-testing`, `oracle-risk`, `pre-audit-readiness`, `reentrancy-review`, `root-cause-analysis`, `smart-contract-security`, `solidity-security`, `vault-accounting`

## Recommended Next Steps

1. Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
2. Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
3. Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
4. Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
5. Run a formal smart contract audit before mainnet launch or before handling real user funds.

## What This Report Does Not Prove

- It does not prove protocol safety.
- It does not confirm exploitability.
- It does not replace manual review.
- It does not replace a formal audit.

## Formal Audit Recommendation

Run a formal smart contract audit before mainnet deployment, before material TVL, or before handling real user funds.

