# EXPECTED — D: non-auth modifier

- `NonAuthOnly.setValue` / `NonAuthOnly.withdraw` -> `UNPRIVILEGED_EXTERNAL` (HIGH).
- Reason: `whenNotPaused` is a known non-auth modifier; it does not restrict the caller.
- The lead must remain attacker-reachable (NOT killed as trusted-role, NOT PARK_REACHABILITY).
