# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/mini-vault`
- Generated at: `2026-05-25T08:16:43+00:00`
- Protocol type: `vault`
- Protocol confidence: `high`
- Files scanned: `5`
- Scanner version: `0.2.0`

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

- Readiness score: **73/100**
- Score band: **Improving**
- Top readiness gaps:
  - **High readiness gap:** Vault accounting without invariant tests — Add Foundry invariants for share/accounting conservation across deposit, withdraw, donation, fee, and emergency scenarios.
  - **Medium readiness gap:** Fee logic without fee accounting tests — Add deposit, withdrawal, management, and performance fee tests where relevant.
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

- Detected signals: `transfer(, transferFrom`
- Files with signals: `2`
- Example files: `src/MiniVault.sol, test/MiniVault.t.sol`

### Accounting Complexity

- Detected signals: `decimals, fee`
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
- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, deposit, mint, shares, totalAssets, totalSupply, transfer(, transferFrom, withdraw`
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

## Missing Invariant And Test Coverage

### High readiness gap: Vault accounting without invariant tests

- Priority: `High`
- Detected: `assets, balanceOf, convertToAssets, convertToShares, deposit, mint, shares, totalAssets, totalSupply, withdraw`
- What was detected: Vault/ERC4626-like accounting signals were detected, but no non-placeholder invariant/property testing signal was found.
- Why it matters: Vault bugs often appear when shares, assets, totalSupply, totalAssets, and external balances drift from assumptions used during deposits and withdrawals.
- Historical pattern similarity: Maps to historical vault/accounting failure classes where broken share valuation or manipulated accounting state caused loss.
- Recommended defensive checks:
  - deposit/withdraw roundtrip
  - convertToShares/convertToAssets consistency
  - donation/inflation resistance
  - rounding direction tests
  - totalAssets external dependency tests
- Suggested test: Add a Foundry invariant that checks totalAssets and share accounting conservation across deposit, withdraw, donation, and fee scenarios.
- Search tags: `vault-accounting, invariant-testing, erc4626`

### Medium readiness gap: Fee logic without fee accounting tests

- Priority: `Medium`
- Detected: `fee`
- What was detected: Fee terms were detected without visible tests for fee accounting, recipient balances, or conservation around fee paths.
- Why it matters: Fee logic changes share issuance, redemption value, and treasury balances; missing tests make audit review slower and riskier.
- Historical pattern similarity: Maps to accounting mismatch classes where protocol fees changed conservation assumptions.
- Recommended defensive checks:
  - fee bounds
  - recipient accounting
  - share conservation
  - rounding with fees
- Suggested test: Assert user shares, treasury shares/assets, and totalAssets remain consistent before and after fee-bearing operations.
- Search tags: `fee-accounting, vault-accounting`


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

## Search Tags

`arkheionx`, `pre-audit-readiness`, `indie-defi`, `defi-security`, `smart-contract-security`, `solidity-security`, `foundry`, `invariant-testing`, `oracle-risk`, `vault-accounting`, `reentrancy-review`, `access-control-review`, `historical-exploit-pattern`, `root-cause-analysis`, `audit-preparation`

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

