# Arkheionx Generated Issue Checklist

Generated from: pre-audit readiness scan
Protocol type: `oracle`
Score: `58/100`

## Medium priority readiness gaps

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

- [ ] ARK-TST-002 - Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
  - Suggested issue title: `[Arkheionx][Low] ARK-TST-002 - No invariant tests detected for DeFi protocol shape`
  - Suggested labels: `arkheionx, invariant-testing, low-confidence, low-readiness-gap, oracle, pre-audit-readiness, testing-readiness`
  - Suggested tests:
    - Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
- [ ] ARK-RWD-001 - Add reward conservation and no-overclaim tests across multiple users and timing boundaries.
  - Suggested issue title: `[Arkheionx][Low] ARK-RWD-001 - Reward accounting needs conservation coverage`
  - Suggested labels: `arkheionx, low-confidence, low-readiness-gap, pre-audit-readiness, precision, reward-accounting`
  - Suggested tests:
    - Add reward conservation and no-overclaim tests across multiple users and timing boundaries.
- [ ] ARK-ACC-003 - Document who can change critical configuration and whether controls use a multisig, timelock, guardian, or single owner.
  - Suggested issue title: `[Arkheionx][Low] ARK-ACC-003 - Admin role concentration not documented`
  - Suggested labels: `access-control, access-control-review, access-control-rule-pack, arkheionx, documentation-readiness, low-readiness-gap, pre-audit-readiness`
  - Suggested tests:
    - Add a role matrix to docs and unit tests for critical roles.
    - role matrix
    - owner powers
    - timelock assumptions
    - multisig assumptions
- [ ] ARK-RWD-002 - Add precision, dust, rounding, and small-balance tests for accumulator or index logic.
  - Suggested issue title: `[Arkheionx][Low] ARK-RWD-002 - Accumulator/index logic without precision/rounding tests`
  - Suggested labels: `arkheionx, low-confidence, low-readiness-gap, pre-audit-readiness, precision, reward-accounting, staking-rule-pack`
  - Suggested tests:
    - Fuzz stake sizes and reward amounts and assert reward indexes are monotonic and bounded by funded rewards.
    - index monotonicity
    - rounding dust
    - small balance behavior
    - multi-user precision

## Documentation Tasks

- [ ] Document admin role boundaries.
- [ ] Document oracle and pricing assumptions.
- [ ] Document known limitations and formal audit scope.

## Convert This Checklist Into GitHub Issues

Issue plan: `examples/reports/semantic-lite-fixture-issue-plan.json`

Dry run:

```sh
python3 scripts/create_github_issues.py --issue-plan examples/reports/semantic-lite-fixture-issue-plan.json --mode dry-run
```

Create issues:

```sh
python3 scripts/create_github_issues.py --issue-plan examples/reports/semantic-lite-fixture-issue-plan.json --mode create --max-issues 5
```

Only run issue creation in repositories you own or are authorized to manage.

## Notes

This checklist is generated from static/local readiness signals. It is not a formal audit.
