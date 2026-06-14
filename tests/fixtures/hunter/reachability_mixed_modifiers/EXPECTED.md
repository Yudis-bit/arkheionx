# EXPECTED — H: mixed modifiers

- `MixedModifiers.setValue` / `MixedModifiers.withdraw` -> `OWNER_GATED_EXTERNAL` (HIGH).
- The auth modifier (`onlyOwner`) dominates the non-auth modifier (`whenNotPaused`).
- Warning: MIXED_AUTH_AND_NON_AUTH_MODIFIERS. Decision: KILL_TRUSTED_ROLE; Submit:NO.
