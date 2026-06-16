# EXPECTED — J: auth bypass candidate

- `BypassCandidate.setValue` -> `OWNER_GATED_EXTERNAL` (HIGH); trusted-role-only by itself.
- `BypassCandidate.initialize` -> `UNPRIVILEGED_EXTERNAL` with warning `UNGUARDED_INITIALIZER_SETS_ROLE` (it is the attacker-reachable surface / takeover hypothesis).
- The owner-gated setter is not pursued directly; the reachable lead is the unguarded initializer takeover.
