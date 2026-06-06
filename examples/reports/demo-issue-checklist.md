# Arkheionx Generated Issue Checklist

Generated from: pre-audit readiness scan
Protocol type: `staking`
Score: `52/100`

## High priority readiness gaps

- [ ] ARK-TST-002 - Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
  - Suggested issue title: `[Arkheionx][High] ARK-TST-002 - No invariant tests detected for DeFi protocol shape`
  - Suggested labels: `arkheionx, high-readiness-gap, invariant-testing, negative-evidence, pre-audit-readiness, staking, testing-readiness`
  - Suggested tests:
    - Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
- [ ] ARK-ORC-002 - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
  - Suggested issue title: `[Arkheionx][High] ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage`
  - Suggested labels: `arkheionx, high-readiness-gap, oracle-pricing, oracle-risk, pre-audit-readiness, price-assumptions`
  - Suggested tests:
    - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
- [ ] ARK-ORC-001 - Add local mock oracle tests for stale round rejection, heartbeat windows, answeredInRound, and updatedAt behavior.
  - Suggested issue title: `[Arkheionx][High] ARK-ORC-001 - Oracle-dependent logic without stale-price tests`
  - Suggested labels: `arkheionx, high-readiness-gap, negative-evidence, oracle-pricing, oracle-risk, oracle-rule-pack, pre-audit-readiness`
  - Suggested tests:
    - Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.
    - stale round rejection
    - heartbeat checks
    - updatedAt validation
    - answeredInRound handling

## Medium priority readiness gaps

- [ ] ARK-REENT-001 - Review state update order and add local malicious-receiver tests where callbacks are possible.
  - Suggested issue title: `[Arkheionx][Medium] ARK-REENT-001 - External-call value flow needs reentrancy review`
  - Suggested labels: `arkheionx, medium-readiness-gap, pre-audit-readiness, reentrancy-review, reentrancy-value-flow, value-flow`
  - Suggested tests:
    - Review state update order and add local malicious-receiver tests where callbacks are possible.
- [ ] ARK-RWD-001 - Add reward conservation and no-overclaim tests across multiple users and timing boundaries.
  - Suggested issue title: `[Arkheionx][Medium] ARK-RWD-001 - Reward accounting needs conservation coverage`
  - Suggested labels: `arkheionx, medium-readiness-gap, pre-audit-readiness, precision, reward-accounting`
  - Suggested tests:
    - Add reward conservation and no-overclaim tests across multiple users and timing boundaries.
- [ ] ARK-ORC-004 - Add tests proving only documented roles can update oracle configuration.
  - Suggested issue title: `[Arkheionx][Medium] ARK-ORC-004 - Oracle setter/admin path without role-boundary tests`
  - Suggested labels: `access-control-review, arkheionx, medium-readiness-gap, negative-evidence, oracle-pricing, oracle-risk, oracle-rule-pack, pre-audit-readiness`
  - Suggested tests:
    - Assert unprivileged callers cannot change oracle or fallback oracle configuration.
    - unauthorized setOracle reverts
    - trusted role documentation
    - fallback oracle controls
- [ ] ARK-ORC-005 - Document min/max bounds, fallback oracle behavior, stale-price policy, and L2 sequencer assumptions if relevant.
  - Suggested issue title: `[Arkheionx][Medium] ARK-ORC-005 - Missing price bounds or fallback assumptions documentation`
  - Suggested labels: `arkheionx, documentation-readiness, medium-readiness-gap, oracle-pricing, oracle-risk, oracle-rule-pack, pre-audit-readiness`
  - Suggested tests:
    - Add documentation plus local tests showing fallback and out-of-bounds price behavior.
    - price bounds
    - fallback policy
    - stale-price policy
    - sequencer downtime notes
- [ ] ARK-ACC-001 - Add tests proving unauthorized users cannot call privileged setters or role-management functions.
  - Suggested issue title: `[Arkheionx][Medium] ARK-ACC-001 - Privileged setters without role-boundary tests`
  - Suggested labels: `access-control, access-control-review, access-control-rule-pack, admin-risk, arkheionx, medium-readiness-gap, negative-evidence, pre-audit-readiness`
  - Suggested tests:
    - For every privileged function, assert an unprivileged caller reverts and the documented role succeeds only within intended bounds.
    - unauthorized setter tests
    - role grant/revoke tests
    - pause role tests
    - timelock/multisig assumptions
- [ ] ARK-RWD-002 - Add precision, dust, rounding, and small-balance tests for accumulator or index logic.
  - Suggested issue title: `[Arkheionx][Medium] ARK-RWD-002 - Accumulator/index logic without precision/rounding tests`
  - Suggested labels: `arkheionx, medium-readiness-gap, negative-evidence, pre-audit-readiness, precision, reward-accounting, staking-rule-pack`
  - Suggested tests:
    - Fuzz stake sizes and reward amounts and assert reward indexes are monotonic and bounded by funded rewards.
    - index monotonicity
    - rounding dust
    - small balance behavior
    - multi-user precision
- [ ] ARK-RWD-003 - Add tests proving users cannot claim the same reward entitlement twice.
  - Suggested issue title: `[Arkheionx][Medium] ARK-RWD-003 - Claim flow without double-claim prevention tests`
  - Suggested labels: `arkheionx, claim-flow, medium-readiness-gap, negative-evidence, pre-audit-readiness, reward-accounting, staking-rule-pack`
  - Suggested tests:
    - Assert claim twice without new rewards returns zero or reverts according to documented policy.
    - double claim prevention
    - claim state reset
    - multi-user claim ordering

## Low priority readiness gaps

- [ ] ARK-VLT-009 - Add deposit/withdraw roundtrip tests and totalAssets/share accounting invariants.
  - Suggested issue title: `[Arkheionx][Low] ARK-VLT-009 - Vault accounting lacks visible roundtrip or conservation coverage`
  - Suggested labels: `arkheionx, low-confidence, low-readiness-gap, negative-evidence, pre-audit-readiness, share-accounting, vault-accounting`
  - Suggested tests:
    - Add deposit/withdraw roundtrip tests and totalAssets/share accounting invariants.
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

## Documentation Tasks

- [ ] Document admin role boundaries.
- [ ] Document oracle and pricing assumptions.
- [ ] Document known limitations and formal audit scope.

## Convert This Checklist Into GitHub Issues

Issue plan: `examples/reports/demo-issue-plan.json`

Dry run:

```sh
python3 scripts/create_github_issues.py --issue-plan examples/reports/demo-issue-plan.json --mode dry-run
```

Create issues:

```sh
python3 scripts/create_github_issues.py --issue-plan examples/reports/demo-issue-plan.json --mode create --max-issues 5
```

Only run issue creation in repositories you own or are authorized to manage.

## Notes

This checklist is generated from static/local readiness signals. It is not a formal audit.
