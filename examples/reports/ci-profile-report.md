# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/amm-lending-hybrid-fixture`
- Generated at: `2026-05-27T09:51:55+00:00`
- Protocol type: `amm`
- Protocol confidence: `medium`
- Files scanned: `4`
- Scanner version: `1.9.0`
- Output profile: `ci` (CI)

| File class       | Count |
| ---------------- | ----- |
| Solidity sources | 1     |
| Solidity tests   | 1     |
| Docs             | 1     |
| Configs          | 1     |
| Workflows        | 0     |

## Config Summary

- Config source: `examples/configs/ci.config.json`
- Effective protocol type: `amm`
- Enabled rule packs: `access-control, amm, docs, lending, oracle, reentrancy-value-flow, rewards, testing, vault`
- Minimum confidence: `medium`
- Suppressions configured: `0`
- Output profile: `ci`
- Ignore generated artifacts: `True`
- Include generated artifacts: `False`

## Scan Source Summary

- Files considered: `4`
- Files scanned: `4`
- Files ignored: `0`
- Generated Arkheionx artifacts ignored: `0`

## Disclaimer

This is an automated pre-audit readiness report. It is not a formal audit, does not prove the absence or presence of vulnerabilities, does not authorize live-target testing, and should only be used on repositories you own or are authorized to review. A formal audit is recommended before handling real user funds.

## Executive Summary

Arkheionx scanned `examples/amm-lending-hybrid-fixture` as `amm` readiness context. This is a local/static pre-audit readiness report, not a formal audit.

- Readiness score: **38/100**
- Score band: **Not audit-ready**
- Active readiness gaps: `13`
- Suppressed readiness gaps: `0`
- Active rule packs: `access-control, amm, docs, lending, oracle, reentrancy-value-flow, rewards, testing, vault`
- Generated artifacts ignored: `0`
- Top readiness gaps:
  - **ARK-AMM-001 (High readiness gap):** AMM invariant assumptions not covered by tests - Add local tests or invariants showing swaps and liquidity operations preserve documented AMM accounting within fee and rounding bounds.
  - **ARK-AMM-003 (High readiness gap):** Spot-price or reserve-price dependency without manipulation-resistance tests - Add local reserve-movement tests and document whether spot, TWAP, or external oracle assumptions are intended.
  - **ARK-AMM-004 (Medium readiness gap):** Fee-on-transfer or non-standard token assumptions not documented - Document supported token assumptions or add balanceBefore/balanceAfter accounting tests for fee-on-transfer and non-standard token behavior.
  - **ARK-AMM-005 (Medium readiness gap):** Slippage/min-output constraints missing or unclear - Add user-provided min-output and stale-quote tests, or document why swaps are not user-facing and how price movement is bounded.
  - **ARK-LEND-001 (Medium readiness gap):** Collateral/debt solvency invariant not covered by tests - Add collateral/debt invariants and boundary tests for borrow, repay, deposit, withdrawal, and liquidation readiness.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
  - Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
  - Run a formal smart contract audit before mainnet launch or before handling real user funds.

## Fix First

| Rank | Finding                                                                                    | Rule Family | Why Fix First                                                                                                                          | Next Action                                                                                                                                    |
| ---- | ------------------------------------------------------------------------------------------ | ----------- | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | ARK-AMM-001 - AMM invariant assumptions not covered by tests                               | amm         | higher-priority readiness blocker; high-confidence local evidence; appears across multiple files; clear defensive tests are available. | Add or review: Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.          |
| 2    | ARK-AMM-003 - Spot-price or reserve-price dependency without manipulation-resistance tests | amm         | higher-priority readiness blocker; high-confidence local evidence; appears across multiple files; clear defensive tests are available. | Add or review: Move reserves in a local pool test and assert dependent protocol decisions respect documented price bounds or TWAP assumptions. |
| 3    | ARK-AMM-004 - Fee-on-transfer or non-standard token assumptions not documented             | amm         | high-confidence local evidence; appears across multiple files; clear defensive tests are available.                                    | Add or review: Use a local fee-on-transfer token mock or document that such tokens are unsupported and guarded by configuration.               |
| 4    | ARK-AMM-005 - Slippage/min-output constraints missing or unclear                           | amm         | high-confidence local evidence; appears across multiple files; clear defensive tests are available.                                    | Add or review: Assert swaps revert or follow documented policy when amountOut falls below a user-provided bound or quote is stale.             |
| 5    | ARK-LEND-005 - Reserve/cash accounting assumptions not covered                             | lending     | high-confidence local evidence; appears across multiple files; clear defensive tests are available.                                    | Add or review: Assert borrow reverts above available liquidity and repay updates cash, debt, reserves, and utilization consistently.           |

## Finding Groups

### Findings by Rule Family

| Rule Family | Active Findings |
| ----------- | --------------- |
| amm         | 4               |
| lending     | 4               |
| oracle      | 4               |
| testing     | 1               |

### Findings by Confidence

| Confidence | Active Findings |
| ---------- | --------------- |
| high       | 5               |
| low        | 6               |
| medium     | 2               |

## Suppression Summary

- Suppressions loaded: `0`
- Suppressions applied: `0`
- Suppressions should include a reason and be revisited before launch or external review.

## Readiness Score Breakdown

| Category                    | Score | Max | Notes                                                                                                                                                          |
| --------------------------- | ----- | --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository Structure        | 12    | 15  | Solidity sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                             |
| Test Presence               | 20    | 20  | Solidity test files detected.; Assert usage detected.; Foundry or Hardhat test environment detected.; Protocol-specific terms appear in the testable codebase. |
| Invariant Fuzz Readiness    | 0     | 20  | No positive signal detected.                                                                                                                                   |
| Defi Risk Coverage          | 0     | 20  | No positive signal detected.                                                                                                                                   |
| Documentation Readiness     | 3     | 10  | README detected.                                                                                                                                               |
| Operational Admin Readiness | 3     | 15  | Upgradeability is absent or has visible documentation/test terms.                                                                                              |

## Top Readiness Gaps

| ID           | Priority             | Category              | Title                                                                        |
| ------------ | -------------------- | --------------------- | ---------------------------------------------------------------------------- |
| ARK-AMM-001  | High readiness gap   | amm-invariant         | AMM invariant assumptions not covered by tests                               |
| ARK-AMM-003  | High readiness gap   | amm-pricing           | Spot-price or reserve-price dependency without manipulation-resistance tests |
| ARK-AMM-004  | Medium readiness gap | amm-token-assumptions | Fee-on-transfer or non-standard token assumptions not documented             |
| ARK-AMM-005  | Medium readiness gap | amm-slippage          | Slippage/min-output constraints missing or unclear                           |
| ARK-LEND-001 | Medium readiness gap | lending-solvency      | Collateral/debt solvency invariant not covered by tests                      |

## Rule Pack Coverage

| Rule Pack                                 | Detected | Findings | Docs                                    |
| ----------------------------------------- | -------- | -------- | --------------------------------------- |
| Vault Rule Pack                           | yes      | 0        | docs/VAULT_RULE_PACK.md                 |
| Oracle Rule Pack                          | yes      | 4        | docs/ORACLE_RULE_PACK.md                |
| Access Control / Upgradeability Rule Pack | no       | 0        | docs/ACCESS_CONTROL_RULE_PACK.md        |
| Reentrancy / Value Flow Rule Pack         | no       | 0        | docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md |
| Staking / Reward Accounting Rule Pack     | yes      | 0        | docs/REWARD_ACCOUNTING_RULE_PACK.md     |
| AMM Rule Pack                             | yes      | 4        | docs/AMM_RULE_PACK.md                   |
| Lending Rule Pack                         | yes      | 4        | docs/LENDING_RULE_PACK.md               |

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
- Test files: `test/ToyHybridMarket.t.sol`

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
- **invariant conservation** (`amm`): Swaps should preserve the AMM invariant within fee and rounding expectations.
- **swap does not create value** (`amm`): No swap sequence should create value outside documented fee mechanics.
- **liquidity add/remove proportionality** (`amm`): Liquidity mint/burn should be proportional to reserves within expected rounding.
- **fee growth consistency** (`amm`): Fee growth should be monotonic and attributable to swaps or configured fee paths.
- **collateralization invariant** (`lending`): Borrower positions should respect collateralization requirements after every user action.
- **liquidation solvency** (`lending`): Liquidations should improve solvency and preserve accounting assumptions.
- **interest index monotonicity** (`lending`): Interest indexes should move monotonically according to configured rate logic.
- **oracle manipulation resistance** (`lending`): Borrow and liquidation paths should resist transient price manipulation.
- **borrow/repay accounting consistency** (`lending`): Debt and collateral balances should reconcile after borrow and repay sequences.

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

- Markdown Report: `examples/reports/ci-profile-report.md`
- Json Report: `examples/reports/ci-profile-report.json`
- Sarif Report: `examples/reports/ci-profile.sarif.json`

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

