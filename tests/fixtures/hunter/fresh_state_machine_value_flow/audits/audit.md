# Prior Audit — Generic Staking Program

Audit by an independent firm. Baseline review of the legacy core.

## Scope of this audit
- `LegacyVault.deposit` — reviewed, no issue.
- `LegacyVault.withdraw` — reviewed, accounting verified.

## Not covered
- The new `WithdrawalQueue` request/claim state machine was added after this audit and
  was not in scope here.
