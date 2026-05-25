# Arkheionx Generated Issue Checklist

Generated from: pre-audit readiness scan
Protocol type: `vault`
Score: `58/100`

## Existing Findings From Baseline

- [ ] ARK-VLT-001 - Add Foundry invariants for share/accounting conservation across deposit, withdraw, donation, fee, and emergency scenarios.
- [ ] ARK-VLT-002 - Add tests that preview functions match actual state-changing outcomes within documented rounding bounds.
- [ ] ARK-VLT-003 - Add tests for rounding direction, small values, decimals mismatch, and conversion reversibility.
- [ ] ARK-VLT-004 - Test totalAssets under donated assets, mocked strategy gain/loss, and mocked stale or bounded pricing where relevant.
- [ ] ARK-VLT-005 - Add tests for strategy report, harvest, gain, loss, debt changes, withdrawals, and migration or emergency exit if present.
- [ ] ARK-VLT-006 - Add tests for request, cooldown/epoch movement, claim, cancellation, and insufficient-liquidity behavior.
- [ ] ARK-ORC-001 - Add local mock price tests for stale rounds, decimals normalization, price bounds, and fallback behavior.
- [ ] ARK-VLT-007 - Add deposit, withdrawal, management, and performance fee tests where relevant.
- [ ] ARK-VLT-008 - Add tests showing pause/emergency controls block risky flows and preserve documented exit or recovery paths.
- [ ] ARK-ORC-002 - Add tests for decimals normalization, precision scaling, and mixed-decimal asset assumptions.
- [ ] ARK-ORC-004 - Add tests proving only documented roles can update oracle configuration.
- [ ] ARK-ACC-001 - Add tests proving unauthorized users cannot call privileged setters or role-management functions.
- [ ] ARK-ACC-003 - Document who can change critical configuration and whether controls use a multisig, timelock, guardian, or single owner.
- [ ] ARK-REENT-001 - Review state ordering and add local reentrant receiver tests around every value-flow path.
- [ ] ARK-REENT-004 - Document state-update ordering, callback assumptions, and why any unguarded external calls are safe by design.
- [ ] ARK-RWD-004 - Add tests for stake, lock/cooldown, reward accrual, claim, and unstake lifecycle transitions.

## Documentation Tasks

- [ ] Document admin role boundaries.
- [ ] Document oracle and pricing assumptions.
- [ ] Document known limitations and formal audit scope.

## Convert This Checklist Into GitHub Issues

No issue plan path was provided for this run.

## Notes

This checklist is generated from static/local readiness signals. It is not a formal audit.
