# Arkheionx Mini Vault Fixture

This is a minimal toy protocol fixture for Arkheionx scanner demonstrations.
It is not production code and must not be deployed.

The fixture exists so contributors and indie builders can see how the
pre-audit readiness scanner reacts to a small vault-shaped Solidity project.
It intentionally stays simple:

- local Solidity source only;
- no live addresses;
- no RPC configuration;
- no deployed-contract testing;
- no exploit workflow.

Run the scanner from the repository root:

```sh
python3 scripts/pre_audit_scan.py \
  --root examples/mini-vault \
  --protocol-type auto \
  --output examples/reports/mini-vault-pre-audit-report.md \
  --json-output examples/reports/mini-vault-pre-audit-report.json \
  --generate-invariant-skeletons
```

The generated report should be read as pre-audit readiness guidance, not as a
formal audit and not as a claim that the toy vault is safe.
