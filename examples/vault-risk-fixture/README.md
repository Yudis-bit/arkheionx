# Vault Risk Fixture

This is a toy vault-like fixture for the Arkheionx v0.2.0 Vault Rule Pack.
It is not production code and must not be deployed.

The fixture exists only to demonstrate pre-audit readiness reporting for
ERC4626-like vaults and strategy vaults. It intentionally includes signals
that should produce defensive readiness prompts:

- ERC4626-like deposit, mint, withdraw, redeem, preview, and conversion terms;
- totalAssets dependence on a strategy balance;
- fee and treasury terms;
- strategy, harvest, gain, loss, debt, and migration vocabulary;
- oracle and LP pricing vocabulary;
- withdrawal queue and cooldown vocabulary;
- pause and admin setter vocabulary.

It does not include exploit logic, live addresses, RPC configuration, or
deployed-contract testing.

Run from the repository root:

```sh
python3 scripts/pre_audit_scan.py \
  --root examples/vault-risk-fixture \
  --protocol-type vault \
  --output examples/reports/vault-risk-fixture-pre-audit-report.md \
  --json-output examples/reports/vault-risk-fixture-pre-audit-report.json \
  --generate-invariant-skeletons
```

The output is a pre-audit readiness report, not a formal audit and not a
security guarantee.
