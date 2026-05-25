# Arkheionx Baseline Diff Report

## Baseline Diff

Compared against: `examples/reports/vault-risk-fixture.baseline.json`

| Status                    | Count |
| ------------------------- | ----- |
| New readiness gaps        | 0     |
| Resolved readiness gaps   | 0     |
| Unchanged readiness gaps  | 9     |
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

### Changed readiness gaps

- None.

## Safety Note

This diff compares local/static readiness findings. It is not a formal audit and does not confirm vulnerabilities.
