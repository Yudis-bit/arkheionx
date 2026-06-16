# EXPECTED — G: direct body auth

- `BodyAuth.setValue` / `BodyAuth.withdraw` -> `OWNER_GATED_EXTERNAL` (HIGH).
- Evidence: `DIRECT_BODY_MSG_SENDER_CHECK` (`msg.sender == owner`).
- Decision: KILL_TRUSTED_ROLE; Submit:NO.
