# Schema Reference

Arkheionx v1.0.0 freezes the main public output shapes for stable use in CI,
reporting, and downstream tooling.

Schemas live in [`schemas/`](../schemas/) and use JSON Schema draft 2020-12.
They validate the main shape and required fields, not every nested future
extension.

## Stable Schemas

| Output | Schema |
|---|---|
| Pre-audit JSON report | [`schemas/pre-audit-report.schema.json`](../schemas/pre-audit-report.schema.json) |
| Issue plan JSON | [`schemas/issue-plan.schema.json`](../schemas/issue-plan.schema.json) |
| Baseline JSON | [`schemas/baseline.schema.json`](../schemas/baseline.schema.json) |
| Diff JSON | [`schemas/diff.schema.json`](../schemas/diff.schema.json) |
| Security memory graph | [`schemas/security-memory-graph.schema.json`](../schemas/security-memory-graph.schema.json) |
| Finding knowledge map | [`schemas/finding-knowledge-map.schema.json`](../schemas/finding-knowledge-map.schema.json) |
| Rule calibration matrix | [`schemas/rule-calibration-matrix.schema.json`](../schemas/rule-calibration-matrix.schema.json) |

## Versioning

The main scanner JSON includes:

```json
{
  "schema_version": "1.0.0",
  "version": "1.0.0"
}
```

Baselines, diff outputs, and issue plans also include `schema_version` in
v1.0.0.

## Compatibility Policy

Patch and minor releases may:

- add optional fields;
- add new findings or rule-pack metadata;
- add new generated artifacts;
- extend `properties` objects.

Patch and minor releases should not:

- remove required top-level fields without a major-version note;
- change existing field types without a migration note;
- reinterpret readiness findings as formal audit findings.

## Manual Validation Without Dependencies

The test suite uses Python standard-library checks so users do not need the
`jsonschema` package. Downstream users may use any JSON Schema validator that
supports draft 2020-12.
