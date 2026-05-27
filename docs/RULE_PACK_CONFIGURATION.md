# Rule Pack Configuration

Arkheionx rule packs are defensive readiness heuristics. Config can enable a
subset of packs for focused local review.

```json
{
  "schema_version": "1.7.0",
  "protocol_type": "hybrid",
  "rule_packs": [
    "oracle",
    "access-control",
    "reentrancy-value-flow",
    "testing",
    "docs",
    "amm",
    "lending"
  ]
}
```

Supported rule-pack keys:

| Key | Finding IDs | Docs |
|---|---|---|
| `vault` | `ARK-VLT-*` | [`VAULT_RULE_PACK.md`](VAULT_RULE_PACK.md) |
| `oracle` | `ARK-ORC-*` | [`ORACLE_RULE_PACK.md`](ORACLE_RULE_PACK.md) |
| `access-control` | `ARK-ACC-*`, `ARK-UPG-*` | [`ACCESS_CONTROL_RULE_PACK.md`](ACCESS_CONTROL_RULE_PACK.md) |
| `reentrancy-value-flow` | `ARK-REENT-*` | [`REENTRANCY_VALUE_FLOW_RULE_PACK.md`](REENTRANCY_VALUE_FLOW_RULE_PACK.md) |
| `rewards` | `ARK-RWD-*` | [`REWARD_ACCOUNTING_RULE_PACK.md`](REWARD_ACCOUNTING_RULE_PACK.md) |
| `testing` | `ARK-TST-*` | [`READINESS_SCORE.md`](READINESS_SCORE.md) |
| `docs` | `ARK-DOC-*` | [`READINESS_SCORE.md`](READINESS_SCORE.md) |
| `amm` | `ARK-AMM-*` | [`AMM_RULE_PACK.md`](AMM_RULE_PACK.md) |
| `lending` | `ARK-LEND-*` | [`LENDING_RULE_PACK.md`](LENDING_RULE_PACK.md) |

Empty `rule_packs` means default enabled packs.

Disabling a rule pack is useful for scoped triage, but it should not be used to
claim the repository is safe. Arkheionx findings are readiness signals, not
formal audit findings.
