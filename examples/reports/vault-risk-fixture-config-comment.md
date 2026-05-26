<!-- arkheionx-pre-audit-comment -->

## Arkheionx Pre-Audit Readiness

Score: **58/100** - Early readiness
Protocol type: `vault`

Top readiness gaps:

| ID            | Priority             | Gap                                                        |
| ------------- | -------------------- | ---------------------------------------------------------- |
| ARK-REENT-001 | High readiness gap   | Value flow with external calls needs reentrancy review     |
| ARK-ACC-001   | Medium readiness gap | Privileged setters without role-boundary tests             |
| ARK-ORC-001   | Medium readiness gap | Oracle-dependent vault without stale-price or bounds tests |
| ARK-ORC-002   | Medium readiness gap | Oracle decimals or normalization not covered by tests      |
| ARK-ORC-004   | Medium readiness gap | Oracle setter/admin path without role-boundary tests       |

Full report: `examples/reports/vault-risk-fixture-config-report.md`
Issue checklist: `examples/reports/vault-risk-fixture-config-checklist.md`

Arkheionx is not a formal audit and not a security guarantee.
