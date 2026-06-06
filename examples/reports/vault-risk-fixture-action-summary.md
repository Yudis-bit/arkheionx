# Arkheionx Pre-Audit Readiness Summary

Score: **58/100** - Early readiness
Protocol type: `vault`
Top readiness gaps: `5`

## Top Gaps

| ID            | Priority             | Title                                                      |
| ------------- | -------------------- | ---------------------------------------------------------- |
| ARK-REENT-001 | High readiness gap   | Value flow with external calls needs reentrancy review     |
| ARK-ACC-001   | Medium readiness gap | Privileged setters without role-boundary tests             |
| ARK-ORC-001   | Medium readiness gap | Oracle-dependent vault without stale-price or bounds tests |
| ARK-ORC-002   | Medium readiness gap | Oracle decimals or normalization not covered by tests      |
| ARK-ORC-004   | Medium readiness gap | Oracle setter/admin path without role-boundary tests       |

## Counts

- Critical: `0`
- High: `1`
- Medium: `12`
- Low: `3`
- Suppressed: `0`

## Outputs

- Markdown Report: `examples/reports/vault-risk-fixture-pre-audit-report.md`
- Json Report: `examples/reports/vault-risk-fixture-pre-audit-report.json`
- Sarif Report: `examples/reports/vault-risk-fixture.sarif.json`
- Summary: `examples/reports/vault-risk-fixture-action-summary.md`
- Comment: `examples/reports/vault-risk-fixture-pr-comment.md`
- Issue Checklist: `examples/reports/vault-risk-fixture-issue-checklist.md`
- Issue Plan: `examples/reports/vault-risk-fixture-issue-plan.json`
- Baseline: `examples/reports/vault-risk-fixture.baseline.json`

## Next Steps

- Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
- Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
- Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
- Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
- Add local mock strategy tests for gain, loss, debt, harvest, and migration accounting.

Arkheionx is not a formal audit and not a security guarantee.
