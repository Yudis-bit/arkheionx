# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/mini-vault`
- Generated at: `2026-05-25T06:11:33+00:00`
- Protocol type: `vault`
- Protocol confidence: `high`
- Files scanned: `5`
- Scanner version: `0.1.0`

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

- Readiness score: **70/100**
- Score band: **Improving**
- Top readiness gaps:
  - **High readiness gap:** No invariant tests detected for DeFi protocol shape — Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
  - **Medium readiness gap:** External-call value flow needs reentrancy review — Review state update order and add local malicious-receiver tests where callbacks are possible.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
  - Review state update order and add malicious local receiver tests for callback-capable flows.
  - Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
  - Run a formal smart contract audit before mainnet launch or before handling real user funds.

## Detected Protocol Shape

- Detected protocol type: `vault`
- Confidence: `high`
- Protocol score signals: `{"amm": 0, "lending": 0, "oracle": 0, "staking": 0, "vault": 68}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                    | Score | Max | Notes                                                                                                                                                                                                                                                                                |
| --------------------------- | ----- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Repository Structure        | 12    | 15  | Solidity sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                                                                                                                                                   |
| Test Presence               | 20    | 20  | Solidity test files detected.; Assert usage detected.; Foundry or Hardhat test environment detected.; Protocol-specific terms appear in the testable codebase.                                                                                                                       |
| Invariant Fuzz Readiness    | 3     | 20  | Edge-case testing terms detected.                                                                                                                                                                                                                                                    |
| Defi Risk Coverage          | 12    | 20  | Accounting assumptions have at least some documented or tested controls.; Role or admin boundaries have some visible coverage.; Protocol-specific checklist or property coverage detected.                                                                                           |
| Documentation Readiness     | 8     | 10  | README detected.; Assumptions, invariants, or limitations are documented.; Deployment or role information appears in docs/code comments.                                                                                                                                             |
| Operational Admin Readiness | 15    | 15  | Access-control surface is visible.; Emergency control or incident terms detected.; Upgradeability is absent or has visible documentation/test terms.; Privileged setters or owner boundaries are visible for review.; Monitoring, incident, limitation, or emergency notes detected. |

## Risk Signal Summary

### Vault Accounting

- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, deposit, mint, shares, totalAssets, totalSupply, withdraw`
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

## Historical Exploit-Pattern Similarity

### Vault accounting invariant readiness gap

- Confidence: `high`
- Detected signals: `assets, balanceOf, convertToAssets, convertToShares, decimals, deposit, fee, mint, shares, totalAssets, totalSupply, withdraw`
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

- **High readiness gap: No invariant tests detected for DeFi protocol shape.** Protocol-like value flows were detected, but no invariant/property testing signal was found. Recommendation: Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions. Tags: `invariant-testing, vault`
- **Medium readiness gap: External-call value flow needs reentrancy review.** External call or token transfer terms were detected without guard or reentrancy-review signals. Recommendation: Review state update order and add local malicious-receiver tests where callbacks are possible. Tags: `reentrancy-review, value-flow`

## Suggested Foundry Invariant Skeletons

- Generated skeleton: `test/invariant/ArkheionxReadinessInvariants.t.sol`

- **totalAssets consistency** (`vault`): totalAssets should match local asset accounting and strategy balances within documented rounding.
- **deposit/withdraw roundtrip** (`vault`): A user should not create value by depositing and withdrawing through normal paths.
- **share price manipulation resistance** (`vault`): Donations, supply edges, or local price changes should not let one actor distort share value unexpectedly.
- **fee accounting conservation** (`vault`): Fees should be bounded, documented, and unable to overcharge beyond configured limits.
- **strategy balance drift handling** (`vault`): Strategy gains, losses, and withdrawals should remain reflected in accounting assumptions.
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

