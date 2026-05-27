# Arkheionx Config

Arkheionx supports safe local configuration through `.arkheionx.json` or an
explicit `--config` path.

```sh
python3 scripts/validate_config.py --config examples/arkheionx.config.example.json
python3 scripts/pre_audit_scan.py --root . --config .arkheionx.json
```

Config is local/static only. It cannot enable RPC calls, live-chain scans,
remote cloning, private-key handling, attack modes, or exploit automation.

Start with:

- [`CONFIG_REFERENCE.md`](CONFIG_REFERENCE.md)
- [`RULE_PACK_CONFIGURATION.md`](RULE_PACK_CONFIGURATION.md)
- [`SUPPRESSIONS.md`](SUPPRESSIONS.md)
- [`CONFIG_SAFETY.md`](CONFIG_SAFETY.md)

## Stable Shape

v1.7.0 stabilizes these top-level fields:

```json
{
  "schema_version": "1.7.0",
  "protocol_type": "auto",
  "rule_packs": [],
  "min_confidence": "low",
  "output_profile": "standard",
  "scan": {},
  "reports": {},
  "test_plan": {},
  "suppressions": []
}
```

Empty `rule_packs` means Arkheionx uses the default defensive rule-pack set.

## CLI Override Behavior

CLI flags remain the strongest signal. For example, if a config says
`"protocol_type": "lending"` but the command uses `--protocol-type amm`, the
scanner uses `amm`.

When the CLI uses `--protocol-type auto`, the config protocol type can provide
the default hint.

## Legacy Compatibility

Older config fields such as `suppress_findings`, `ignore_paths`,
`report.max_top_gaps`, and `analysis.min_confidence_for_issue_plan` are still
normalized for v1.x compatibility. New configs should use `suppressions`,
`scan.extra_ignore_paths`, `reports.max_top_gaps`, and `min_confidence`.

## Generated Artifact Ignore

Generated Arkheionx reports, SARIF, issue plans, sprint plans, test plans, and
invariant skeletons are ignored by default so previous outputs do not influence
future scores.

Only set `scan.include_generated_artifacts` to `true` for scanner debugging.
Normal users should keep it `false`.
