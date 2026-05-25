# Arkheionx Generated Issue Checklist

Generated from: pre-audit readiness scan
Protocol type: `vault`
Score: `73/100`

## High priority readiness gaps

- [ ] ARK-VLT-001 - Add Foundry invariants for share/accounting conservation across deposit, withdraw, donation, fee, and emergency scenarios.
  - Suggested issue title: `[Arkheionx][High] ARK-VLT-001 - Vault accounting without invariant tests`
  - Suggested labels: `arkheionx, erc4626, high-readiness-gap, invariant-testing, pre-audit-readiness, vault-accounting`
  - Suggested tests:
    - Add a Foundry invariant that checks totalAssets and share accounting conservation across deposit, withdraw, donation, and fee scenarios.
    - deposit/withdraw roundtrip
    - convertToShares/convertToAssets consistency
    - donation/inflation resistance
    - rounding direction tests
    - totalAssets external dependency tests
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

- [ ] ARK-VLT-007 - Add deposit, withdrawal, management, and performance fee tests where relevant.
  - Suggested issue title: `[Arkheionx][Medium] ARK-VLT-007 - Fee logic without fee accounting tests`
  - Suggested labels: `arkheionx, fee-accounting, medium-readiness-gap, pre-audit-readiness, vault-accounting`
  - Suggested tests:
    - Assert user shares, treasury shares/assets, and totalAssets remain consistent before and after fee-bearing operations.
    - fee bounds
    - recipient accounting
    - share conservation
    - rounding with fees

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

## Documentation Tasks

- [ ] Document admin role boundaries.
- [ ] Document oracle and pricing assumptions.
- [ ] Document known limitations and formal audit scope.

## Convert This Checklist Into GitHub Issues

Issue plan: `examples/reports/mini-vault-issue-plan.json`

Dry run:

```sh
python3 scripts/create_github_issues.py --issue-plan examples/reports/mini-vault-issue-plan.json --mode dry-run
```

Create issues:

```sh
python3 scripts/create_github_issues.py --issue-plan examples/reports/mini-vault-issue-plan.json --mode create --max-issues 5
```

Only run issue creation in repositories you own or are authorized to manage.

## Notes

This checklist is generated from static/local readiness signals. It is not a formal audit.
