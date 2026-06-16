# EXPECTED — B: inline assembly role getter

- `AssemblyOracleRate.oracle` getter -> evidence `ROLE_GETTER_ASSEMBLY_SLOAD`.
- `AssemblyOracleRate.updateRate` -> `ORACLE_GATED_EXTERNAL` (HIGH); NOT `UNPRIVILEGED_EXTERNAL`.
- triage.json `function_reachability` contains `ORACLE_GATED_EXTERNAL` and `ROLE_GETTER_ASSEMBLY_SLOAD`.
- Submit:NO; no normal PoC plan for the oracle-gated setter.
