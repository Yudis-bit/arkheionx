# Arkheionx Generated Issue Checklist

Generated from: pre-audit readiness scan
Protocol type: `vault`
Score: `58/100`

## High priority readiness gaps

- [ ] ARK-REENT-001 - Review state ordering and add local reentrant receiver tests around every value-flow path.
  - Suggested issue title: `[Arkheionx][High] ARK-REENT-001 - Value flow with external calls needs reentrancy review`
  - Suggested labels: `arkheionx, high-readiness-gap, pre-audit-readiness, reentrancy-review, reentrancy-rule-pack, reentrancy-value-flow, value-flow`
  - Suggested tests:
    - Use a local malicious receiver mock and assert withdraw/redeem/claim cannot be executed twice through reentry.
    - state update before external call
    - reentrant receiver mock
    - failed external call behavior
    - single-claim guarantees

## Medium priority readiness gaps

- [ ] ARK-VLT-001 - Add Foundry invariants for share/accounting conservation across deposit, withdraw, donation, fee, and emergency scenarios.
  - Suggested issue title: `[Arkheionx][Medium] ARK-VLT-001 - Vault accounting without invariant tests`
  - Suggested labels: `arkheionx, erc4626, invariant-testing, medium-readiness-gap, pre-audit-readiness, vault-accounting`
  - Suggested tests:
    - Add a Foundry invariant that checks totalAssets and share accounting conservation across deposit, withdraw, donation, and fee scenarios.
    - deposit/withdraw roundtrip
    - convertToShares/convertToAssets consistency
    - donation/inflation resistance
    - rounding direction tests
    - totalAssets external dependency tests
- [ ] ARK-VLT-002 - Add tests that preview functions match actual state-changing outcomes within documented rounding bounds.
  - Suggested issue title: `[Arkheionx][Medium] ARK-VLT-002 - ERC4626-like interface without preview function tests`
  - Suggested labels: `arkheionx, erc4626, medium-readiness-gap, pre-audit-readiness, preview-functions, vault-accounting`
  - Suggested tests:
    - For each preview function, compare the previewed shares/assets with the actual deposit, mint, withdraw, or redeem result.
    - preview/action equivalence
    - rounding direction tests
    - max function boundary tests
- [ ] ARK-VLT-003 - Add tests for rounding direction, small values, decimals mismatch, and conversion reversibility.
  - Suggested issue title: `[Arkheionx][Medium] ARK-VLT-003 - Shares/assets conversion without rounding tests`
  - Suggested labels: `arkheionx, medium-readiness-gap, pre-audit-readiness, precision, rounding, share-accounting, vault-accounting`
  - Suggested tests:
    - Fuzz assets and shares across small, large, and decimal-edge values and assert conversion error stays within documented bounds.
    - small amount tests
    - decimals normalization
    - mulDiv/precision review
    - conversion reversibility
- [ ] ARK-VLT-004 - Test totalAssets under donated assets, mocked strategy gain/loss, and mocked stale or bounded pricing where relevant.
  - Suggested issue title: `[Arkheionx][Medium] ARK-VLT-004 - totalAssets external dependency without manipulation-resistance tests`
  - Suggested labels: `arkheionx, medium-readiness-gap, oracle-risk, pre-audit-readiness, strategy-accounting, totalAssets, vault-accounting`
  - Suggested tests:
    - Mock external strategy or price state and assert totalAssets, share price, and withdrawal accounting remain within documented policy.
    - donation tests
    - mock strategy gain/loss
    - stale/bounded oracle tests
    - share price drift checks
- [ ] ARK-VLT-005 - Add tests for strategy report, harvest, gain, loss, debt changes, withdrawals, and migration or emergency exit if present.
  - Suggested issue title: `[Arkheionx][Medium] ARK-VLT-005 - Strategy accounting without gain/loss tests`
  - Suggested labels: `arkheionx, gain-loss, medium-readiness-gap, pre-audit-readiness, strategy-accounting, vault-lifecycle, vault-strategy`
  - Suggested tests:
    - Use a local mock strategy that reports gain and loss, then assert totalAssets and share accounting follow documented policy.
    - gain report
    - loss report
    - debt update
    - withdrawFromStrategy
    - strategy migration
- [ ] ARK-VLT-006 - Add tests for request, cooldown/epoch movement, claim, cancellation, and insufficient-liquidity behavior.
  - Suggested issue title: `[Arkheionx][Medium] ARK-VLT-006 - Withdrawal queue/cooldown without lifecycle tests`
  - Suggested labels: `arkheionx, liquidity, medium-readiness-gap, pre-audit-readiness, vault-lifecycle, vault-withdrawal, withdrawal-queue`
  - Suggested tests:
    - Test the full withdrawal lifecycle and assert shares/assets are conserved across request, cooldown, claim, and cancellation.
    - requestWithdraw
    - claimWithdraw
    - cancelWithdraw
    - cooldown
    - available liquidity
- [ ] ARK-ORC-001 - Add local mock price tests for stale rounds, decimals normalization, price bounds, and fallback behavior.
  - Suggested issue title: `[Arkheionx][Medium] ARK-ORC-001 - Oracle-dependent vault without stale-price or bounds tests`
  - Suggested labels: `arkheionx, medium-readiness-gap, oracle-pricing, oracle-risk, pool-price, pre-audit-readiness, vault-pricing`
  - Suggested tests:
    - Use local mock oracles/pools to test stale, out-of-bounds, decimals, and spot-price scenarios without live-chain calls.
    - stale price rejection
    - decimals normalization
    - TWAP/sanity check
    - bounds
    - oracle setter roles
- [ ] ARK-VLT-007 - Add deposit, withdrawal, management, and performance fee tests where relevant.
  - Suggested issue title: `[Arkheionx][Medium] ARK-VLT-007 - Fee logic without fee accounting tests`
  - Suggested labels: `arkheionx, fee-accounting, medium-readiness-gap, pre-audit-readiness, vault-accounting`
  - Suggested tests:
    - Assert user shares, treasury shares/assets, and totalAssets remain consistent before and after fee-bearing operations.
    - fee bounds
    - recipient accounting
    - share conservation
    - rounding with fees
- [ ] ARK-VLT-008 - Add tests showing pause/emergency controls block risky flows and preserve documented exit or recovery paths.
  - Suggested issue title: `[Arkheionx][Medium] ARK-VLT-008 - Pause/emergency controls without operational tests`
  - Suggested labels: `arkheionx, emergency-controls, medium-readiness-gap, pause, pre-audit-readiness, vault-operations`
  - Suggested tests:
    - Assert pause and emergency states block or allow each vault flow exactly as documented.
    - pause blocks deposit
    - pause blocks withdraw/redeem if intended
    - emergency exit behavior
    - role boundary
- [ ] ARK-ORC-002 - Add tests for decimals normalization, precision scaling, and mixed-decimal asset assumptions.
  - Suggested issue title: `[Arkheionx][Medium] ARK-ORC-002 - Oracle decimals or normalization not covered by tests`
  - Suggested labels: `arkheionx, decimals, medium-readiness-gap, oracle-pricing, oracle-risk, oracle-rule-pack, pre-audit-readiness, precision`
  - Suggested tests:
    - Mock price feeds with different decimals and assert protocol accounting normalizes every value before use.
    - decimals normalization
    - mixed asset decimals
    - precision scaling
    - rounding bounds
- [ ] ARK-ORC-004 - Add tests proving only documented roles can update oracle configuration.
  - Suggested issue title: `[Arkheionx][Medium] ARK-ORC-004 - Oracle setter/admin path without role-boundary tests`
  - Suggested labels: `access-control-review, arkheionx, medium-readiness-gap, oracle-pricing, oracle-risk, oracle-rule-pack, pre-audit-readiness`
  - Suggested tests:
    - Assert unprivileged callers cannot change oracle or fallback oracle configuration.
    - unauthorized setOracle reverts
    - trusted role documentation
    - fallback oracle controls
- [ ] ARK-ACC-001 - Add tests proving unauthorized users cannot call privileged setters or role-management functions.
  - Suggested issue title: `[Arkheionx][Medium] ARK-ACC-001 - Privileged setters without role-boundary tests`
  - Suggested labels: `access-control, access-control-review, access-control-rule-pack, admin-risk, arkheionx, medium-readiness-gap, pre-audit-readiness`
  - Suggested tests:
    - For every privileged function, assert an unprivileged caller reverts and the documented role succeeds only within intended bounds.
    - unauthorized setter tests
    - role grant/revoke tests
    - pause role tests
    - timelock/multisig assumptions

## Low priority readiness gaps

- [ ] ARK-ACC-003 - Document who can change critical configuration and whether controls use a multisig, timelock, guardian, or single owner.
  - Suggested issue title: `[Arkheionx][Low] ARK-ACC-003 - Admin role concentration not documented`
  - Suggested labels: `access-control, access-control-review, access-control-rule-pack, arkheionx, documentation-readiness, low-readiness-gap, pre-audit-readiness`
  - Suggested tests:
    - Add a role matrix to docs and unit tests for critical roles.
    - role matrix
    - owner powers
    - timelock assumptions
    - multisig assumptions
- [ ] ARK-REENT-004 - Document state-update ordering, callback assumptions, and why any unguarded external calls are safe by design.
  - Suggested issue title: `[Arkheionx][Low] ARK-REENT-004 - External call path without documented ordering assumptions`
  - Suggested labels: `arkheionx, documentation-readiness, low-readiness-gap, pre-audit-readiness, reentrancy-review, reentrancy-rule-pack, reentrancy-value-flow`
  - Suggested tests:
    - Pair ordering documentation with a local receiver test that exercises the documented boundary.
    - ordering documentation
    - callback assumptions
    - external call failure behavior
- [ ] ARK-RWD-004 - Add tests for stake, lock/cooldown, reward accrual, claim, and unstake lifecycle transitions.
  - Suggested issue title: `[Arkheionx][Low] ARK-RWD-004 - Lock/cooldown reward lifecycle not tested`
  - Suggested labels: `arkheionx, low-readiness-gap, pre-audit-readiness, reward-accounting, staking-lifecycle, staking-rule-pack`
  - Suggested tests:
    - Advance local time/epochs and assert reward and withdrawal state transitions follow documented policy.
    - epoch boundaries
    - cooldown transitions
    - vesting claim timing

## Documentation Tasks

- [ ] Document admin role boundaries.
- [ ] Document oracle and pricing assumptions.
- [ ] Document known limitations and formal audit scope.

## Convert This Checklist Into GitHub Issues

Issue plan: `examples/reports/vault-risk-fixture-issue-plan.json`

Dry run:

```sh
python3 scripts/create_github_issues.py --issue-plan examples/reports/vault-risk-fixture-issue-plan.json --mode dry-run
```

Create issues:

```sh
python3 scripts/create_github_issues.py --issue-plan examples/reports/vault-risk-fixture-issue-plan.json --mode create --max-issues 5
```

Only run issue creation in repositories you own or are authorized to manage.

## Notes

This checklist is generated from static/local readiness signals. It is not a formal audit.
