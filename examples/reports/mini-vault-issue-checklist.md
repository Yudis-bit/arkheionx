# Arkheionx Generated Issue Checklist

Generated from: pre-audit readiness scan
Protocol type: `vault`
Score: `73/100`

## High priority readiness gaps

- [ ] ARK-VLT-001 - Add Foundry invariants for share/accounting conservation across deposit, withdraw, donation, fee, and emergency scenarios.
  - Suggested tests:
    - Add a Foundry invariant that checks totalAssets and share accounting conservation across deposit, withdraw, donation, and fee scenarios.
    - deposit/withdraw roundtrip
    - convertToShares/convertToAssets consistency
    - donation/inflation resistance
    - rounding direction tests
    - totalAssets external dependency tests

## Medium priority readiness gaps

- [ ] ARK-VLT-007 - Add deposit, withdrawal, management, and performance fee tests where relevant.
  - Suggested tests:
    - Assert user shares, treasury shares/assets, and totalAssets remain consistent before and after fee-bearing operations.
    - fee bounds
    - recipient accounting
    - share conservation
    - rounding with fees

## Documentation Tasks

- [ ] Document admin role boundaries.
- [ ] Document oracle and pricing assumptions.
- [ ] Document known limitations and formal audit scope.

## Notes

This checklist is generated from static/local readiness signals. It is not a formal audit.
