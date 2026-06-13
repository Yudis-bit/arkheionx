# Prior Audit Report — Toy

Audit performed by Spearbit on the legacy contracts. This is the prior review
baseline. Anything reviewed here is considered stale / over-audited unless it
changed afterwards.

## Scope of this audit

- `OldVault.deposit` — reviewed. First-depositor / inflation share accounting was
  identified and acknowledged as an accepted risk (by design).
- `OldVault.redeem` — reviewed. Redeem accounting verified; no issue found.
- `OldVault` access control — reviewed. Owner is a trusted role.

## Not covered by this audit

- The newly wired external yield-source integration was added after this audit and
  was not in scope here.

## Findings

- F-1: OldVault deposit inflation — acknowledged, by design. No fix required.
