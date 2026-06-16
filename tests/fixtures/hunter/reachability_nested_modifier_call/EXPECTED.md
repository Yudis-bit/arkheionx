# EXPECTED — E: nested helper

- `NestedRole.setValue` / `NestedRole.withdraw` -> `ADMIN_GATED_EXTERNAL` (HIGH).
- Evidence: `onlyAdmin` -> helper `_checkAdmin` -> `msg.sender == admin` (`HELPER_MSG_SENDER_CHECK`).
- Decision: KILL_TRUSTED_ROLE; Submit:NO.
