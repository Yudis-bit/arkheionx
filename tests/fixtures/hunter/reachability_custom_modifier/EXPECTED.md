# EXPECTED — A: custom onlyOracle modifier

- `OracleRate.updateRate` -> `ORACLE_GATED_EXTERNAL` (HIGH); NOT `UNPRIVILEGED_EXTERNAL`.
- `OracleRate.pushPayout` -> `ORACLE_GATED_EXTERNAL` (HIGH).
- Reason: `onlyOracle` modifier compares `msg.sender` to `oracle`.
- Decision: TRUSTED_ROLE_ONLY -> KILL_TRUSTED_ROLE; Submit:NO; no PoC plan unless a separate oracle-bypass hypothesis exists.
