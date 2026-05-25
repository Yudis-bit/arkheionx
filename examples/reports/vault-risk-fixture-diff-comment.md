<!-- arkheionx-pre-audit-comment -->

## Arkheionx Pre-Audit Readiness

Score: **58/100** - Early readiness
Protocol type: `vault`

Top readiness gaps:

| ID          | Priority           | Gap                                                                   |
| ----------- | ------------------ | --------------------------------------------------------------------- |
| ARK-ORC-001 | High readiness gap | Oracle-dependent vault without stale-price or bounds tests            |
| ARK-VLT-001 | High readiness gap | Vault accounting without invariant tests                              |
| ARK-VLT-002 | High readiness gap | ERC4626-like interface without preview function tests                 |
| ARK-VLT-003 | High readiness gap | Shares/assets conversion without rounding tests                       |
| ARK-VLT-004 | High readiness gap | totalAssets external dependency without manipulation-resistance tests |

Full report: `examples/reports/vault-risk-fixture-diff-report.md`
Issue checklist: `examples/reports/vault-risk-fixture-diff-checklist.md`

Diff vs baseline:
- New: `0`
- Resolved: `0`
- Unchanged: `9`
- Changed: `0`
Diff report: `examples/reports/vault-risk-fixture-diff.md`

Arkheionx is not a formal audit and not a security guarantee.
