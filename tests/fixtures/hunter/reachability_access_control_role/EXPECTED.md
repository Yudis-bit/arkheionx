# EXPECTED — F: AccessControl role

- `AccessControlled.mint` -> `MINTER_GATED_EXTERNAL` (HIGH) — role from `onlyRole(MINTER_ROLE)`.
- Evidence includes `ACCESS_CONTROL_ONLY_ROLE` and a role-mapping membership check.
- NOT `UNPRIVILEGED_EXTERNAL`. Decision: KILL_TRUSTED_ROLE; Submit:NO.
