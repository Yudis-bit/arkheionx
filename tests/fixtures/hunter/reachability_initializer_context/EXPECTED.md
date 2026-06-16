# EXPECTED — I: initializer context

- `InitContext.initialize` -> `INITIALIZER_CONTEXT_EXTERNAL` (MEDIUM); NOT ordinary `UNPRIVILEGED_EXTERNAL`.
- Decision: PARK_DEPLOYMENT (initialization/deployment state) unless deployed state proves an uninitialized attacker path.
