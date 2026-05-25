# Arkheionx Baseline Diff Report

## Baseline Diff

Compared against: `examples/reports/vault-risk-fixture.baseline.json`

| Status                    | Count |
| ------------------------- | ----- |
| New readiness gaps        | 0     |
| Resolved readiness gaps   | 0     |
| Unchanged readiness gaps  | 16    |
| Changed readiness gaps    | 0     |
| Suppressed readiness gaps | 0     |

### New readiness gaps

- None.

### Resolved readiness gaps

- None.

### Unchanged readiness gaps

- `ARK-VLT-001` - Vault accounting without invariant tests
- `ARK-VLT-002` - ERC4626-like interface without preview function tests
- `ARK-VLT-003` - Shares/assets conversion without rounding tests
- `ARK-VLT-004` - totalAssets external dependency without manipulation-resistance tests
- `ARK-VLT-005` - Strategy accounting without gain/loss tests
- `ARK-VLT-006` - Withdrawal queue/cooldown without lifecycle tests
- `ARK-ORC-001` - Oracle-dependent vault without stale-price or bounds tests
- `ARK-VLT-007` - Fee logic without fee accounting tests
- `ARK-VLT-008` - Pause/emergency controls without operational tests
- `ARK-ORC-002` - Oracle decimals or normalization not covered by tests
- `ARK-ORC-004` - Oracle setter/admin path without role-boundary tests
- `ARK-ACC-001` - Privileged setters without role-boundary tests
- `ARK-ACC-003` - Admin role concentration not documented
- `ARK-REENT-001` - Value flow with external calls needs reentrancy review
- `ARK-REENT-004` - External call path without documented ordering assumptions
- `ARK-RWD-004` - Lock/cooldown reward lifecycle not tested

### Changed readiness gaps

- None.

## Safety Note

This diff compares local/static readiness findings. It is not a formal audit and does not confirm vulnerabilities.
