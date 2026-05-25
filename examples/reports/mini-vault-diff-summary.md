# Arkheionx Pre-Audit Readiness Summary

Score: **73/100** - Improving
Protocol type: `vault`
Top readiness gaps: `2`

## Top Gaps

| ID          | Priority             | Title                                    |
| ----------- | -------------------- | ---------------------------------------- |
| ARK-VLT-001 | High readiness gap   | Vault accounting without invariant tests |
| ARK-VLT-007 | Medium readiness gap | Fee logic without fee accounting tests   |

## Counts

- Critical: `0`
- High: `1`
- Medium: `1`
- Low: `0`
- Suppressed: `0`

## Baseline Diff

- New readiness gaps: `0`
- Resolved readiness gaps: `0`
- Unchanged readiness gaps: `2`
- Changed readiness gaps: `0`
- Diff report: `examples/reports/mini-vault-diff.md`

## Outputs

- Markdown Report: `examples/reports/mini-vault-diff-report.md`
- Json Report: `examples/reports/mini-vault-diff-report.json`
- Sarif Report: `examples/reports/mini-vault-diff.sarif.json`
- Summary: `examples/reports/mini-vault-diff-summary.md`
- Comment: `examples/reports/mini-vault-diff-comment.md`
- Issue Checklist: `examples/reports/mini-vault-diff-checklist.md`
- Diff Report: `examples/reports/mini-vault-diff.md`
- Diff Json: `examples/reports/mini-vault-diff.json`

## Next Steps

- Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
- Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
- Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.
- Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
- Run a formal smart contract audit before mainnet launch or before handling real user funds.

Arkheionx is not a formal audit and not a security guarantee.
