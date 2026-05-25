# Arkheionx Generated Issue Checklist

Generated from: pre-audit readiness scan
Protocol type: `vault`
Score: `58/100`

## High priority readiness gaps

- [ ] ARK-VLT-002 - Add tests that preview functions match actual state-changing outcomes within documented rounding bounds.
  - Suggested tests:
    - For each preview function, compare the previewed shares/assets with the actual deposit, mint, withdraw, or redeem result.
    - preview/action equivalence
    - rounding direction tests
    - max function boundary tests
- [ ] ARK-VLT-003 - Add tests for rounding direction, small values, decimals mismatch, and conversion reversibility.
  - Suggested tests:
    - Fuzz assets and shares across small, large, and decimal-edge values and assert conversion error stays within documented bounds.
    - small amount tests
    - decimals normalization
    - mulDiv/precision review
    - conversion reversibility
- [ ] ARK-VLT-004 - Test totalAssets under donated assets, mocked strategy gain/loss, and mocked stale or bounded pricing where relevant.
  - Suggested tests:
    - Mock external strategy or price state and assert totalAssets, share price, and withdrawal accounting remain within documented policy.
    - donation tests
    - mock strategy gain/loss
    - stale/bounded oracle tests
    - share price drift checks
- [ ] ARK-VLT-005 - Add tests for strategy report, harvest, gain, loss, debt changes, withdrawals, and migration or emergency exit if present.
  - Suggested tests:
    - Use a local mock strategy that reports gain and loss, then assert totalAssets and share accounting follow documented policy.
    - gain report
    - loss report
    - debt update
    - withdrawFromStrategy
    - strategy migration
- [ ] ARK-VLT-006 - Add tests for request, cooldown/epoch movement, claim, cancellation, and insufficient-liquidity behavior.
  - Suggested tests:
    - Test the full withdrawal lifecycle and assert shares/assets are conserved across request, cooldown, claim, and cancellation.
    - requestWithdraw
    - claimWithdraw
    - cancelWithdraw
    - cooldown
    - available liquidity
- [ ] ARK-ORC-001 - Add local mock price tests for stale rounds, decimals normalization, price bounds, and fallback behavior.
  - Suggested tests:
    - Use local mock oracles/pools to test stale, out-of-bounds, decimals, and spot-price scenarios without live-chain calls.
    - stale price rejection
    - decimals normalization
    - TWAP/sanity check
    - bounds
    - oracle setter roles

## Medium priority readiness gaps

- [ ] ARK-VLT-007 - Add deposit, withdrawal, management, and performance fee tests where relevant.
  - Suggested tests:
    - Assert user shares, treasury shares/assets, and totalAssets remain consistent before and after fee-bearing operations.
    - fee bounds
    - recipient accounting
    - share conservation
    - rounding with fees
- [ ] ARK-VLT-008 - Add tests showing pause/emergency controls block risky flows and preserve documented exit or recovery paths.
  - Suggested tests:
    - Assert pause and emergency states block or allow each vault flow exactly as documented.
    - pause blocks deposit
    - pause blocks withdraw/redeem if intended
    - emergency exit behavior
    - role boundary

## Documentation Tasks

- [ ] Document admin role boundaries.
- [ ] Document oracle and pricing assumptions.
- [ ] Document known limitations and formal audit scope.

## Notes

This checklist is generated from static/local readiness signals. It is not a formal audit.
