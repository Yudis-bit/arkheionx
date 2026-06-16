# Senior Triage Toy Fixture

A tiny, synthetic, target-agnostic repository used only by the senior-triage tests.

It models five situations on purpose:

- `FreshAdapter` — a fresh integration surface worth pursuing first.
- `OldVault.deposit` — a share-accounting path with prior public coverage.
- `OldVault.sweep` — a privileged path reachable only by a trusted role.
- `OldVault.redeem` — a legacy path reviewed in the prior baseline.
- `PaymentModule.fund` — a value-bearing path with no scope or prior context.

Nothing here is a real protocol. It is planning input for `arkheionx triage`, not a
finding. See `known/`, `audits/`, and `scope.md` for the rest of the context.
