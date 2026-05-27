# Config Safety

Arkheionx config is intentionally local/static. It must not enable unsafe
behavior.

Dangerous config keys are rejected, including:

- `rpc_url`
- `private_key`
- `mnemonic`
- `live_target`
- `exploit_mode`
- `attack_mode`
- `drain_mode`
- `profit_mode`
- `clone_url`
- `remote_target`
- `bypass_safety`
- `disable_safety`

Arkheionx does not support RPC calls, live-chain calls, deployed-contract
scanning, transaction execution, target enumeration, private-key handling,
remote cloning, exploit automation, or bounty-farming workflows.

Use configs only for local repository readiness controls:

- protocol type hints;
- enabled rule packs;
- minimum confidence preferences;
- documented suppressions;
- generated artifact ignore behavior;
- report verbosity;
- test-plan preferences;
- local ignore paths and globs.
