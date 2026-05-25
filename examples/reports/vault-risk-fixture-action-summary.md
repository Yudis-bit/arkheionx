# Arkheionx Pre-Audit Readiness Summary

Score: **58/100** - Early readiness
Protocol type: `vault`
Top readiness gaps: `5`

## Top Gaps

| ID          | Priority           | Title                                                                 |
| ----------- | ------------------ | --------------------------------------------------------------------- |
| ARK-ORC-001 | High readiness gap | Oracle-dependent vault without stale-price or bounds tests            |
| ARK-VLT-001 | High readiness gap | Vault accounting without invariant tests                              |
| ARK-VLT-002 | High readiness gap | ERC4626-like interface without preview function tests                 |
| ARK-VLT-003 | High readiness gap | Shares/assets conversion without rounding tests                       |
| ARK-VLT-004 | High readiness gap | totalAssets external dependency without manipulation-resistance tests |

## Counts

- Critical: `0`
- High: `7`
- Medium: `2`
- Low: `0`
- Suppressed: `0`

## Outputs

- Markdown Report: `examples/reports/vault-risk-fixture-pre-audit-report.md`
- Json Report: `examples/reports/vault-risk-fixture-pre-audit-report.json`
- Summary: `examples/reports/vault-risk-fixture-action-summary.md`
- Comment: `examples/reports/vault-risk-fixture-pr-comment.md`
- Issue Checklist: `examples/reports/vault-risk-fixture-issue-checklist.md`

## Next Steps

- Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
- Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
- Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
- Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
- Add local mock strategy tests for gain, loss, debt, harvest, and migration accounting.

Arkheionx is not a formal audit and not a security guarantee.
