# Known Issues — Toy

These are prior, already-known issues. New reports that match them are duplicates.

## OldVault deposit first-depositor inflation

- Surface: `OldVault.deposit`
- Behavior: classic first-depositor / inflation share-accounting rounding.
- Status: acknowledged, by design, won't fix.
- Note: previously reported and a known issue. Covered by the public test
  `testFirstDepositorInflationIsKnown`. Treat any new report on this share/deposit
  inflation behavior as a duplicate.

## OldVault owner sweep

- Surface: `OldVault.sweep`
- Behavior: trusted owner can move funds.
- Status: documented, trusted-role behavior, out of scope.
