# Arkheionx Pre-Audit Readiness Summary

Score: **73/100** - Improving
Protocol type: `vault`
Top readiness gaps: `5`

## Top Gaps

| ID            | Priority             | Title                                                      |
| ------------- | -------------------- | ---------------------------------------------------------- |
| ARK-REENT-001 | High readiness gap   | Value flow with external calls needs reentrancy review     |
| ARK-VLT-001   | Medium readiness gap | Vault accounting without invariant tests                   |
| ARK-VLT-007   | Medium readiness gap | Fee logic without fee accounting tests                     |
| ARK-ACC-003   | Low readiness gap    | Admin role concentration not documented                    |
| ARK-REENT-004 | Low readiness gap    | External call path without documented ordering assumptions |

## Counts

- Critical: `0`
- High: `1`
- Medium: `2`
- Low: `2`
- Suppressed: `0`

## Outputs

- Markdown Report: `examples/reports/mini-vault-pre-audit-report.md`
- Json Report: `examples/reports/mini-vault-pre-audit-report.json`
- Sarif Report: `examples/reports/mini-vault.sarif.json`
- Summary: `examples/reports/mini-vault-action-summary.md`
- Comment: `examples/reports/mini-vault-pr-comment.md`
- Issue Checklist: `examples/reports/mini-vault-issue-checklist.md`
- Issue Plan: `examples/reports/mini-vault-issue-plan.json`
- Baseline: `examples/reports/mini-vault.baseline.json`

## Next Steps

- Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
- Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
- Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
- Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
- Run a formal smart contract audit before mainnet launch or before handling real user funds.

Arkheionx is not a formal audit and not a security guarantee.
