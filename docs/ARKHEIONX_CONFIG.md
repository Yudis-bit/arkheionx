# Arkheionx Config

Arkheionx v0.3.0 supports an optional JSON config file:

```text
.arkheionx.json
```

The config is intentionally simple and dependency-free.

## Example

```json
{
  "version": "0.3.0",
  "protocol_type": "auto",
  "suppress_findings": [
    {
      "id": "ARK-ORC-001",
      "reason": "Oracle risk accepted during testnet prototype phase.",
      "expires": "2026-12-31"
    }
  ],
  "ignore_paths": [
    "lib/",
    "test/mocks/"
  ],
  "additional_search_tags": [
    "my-protocol",
    "vault"
  ],
  "report": {
    "max_top_gaps": 5
  }
}
```

See [`../examples/arkheionx.config.example.json`](../examples/arkheionx.config.example.json).

## Fields

| Field | Purpose |
|---|---|
| `version` | Config format version. |
| `protocol_type` | Optional default protocol type when CLI/action input is `auto`. |
| `suppress_findings` | Documented finding-ID suppressions. |
| `ignore_paths` | Paths excluded from scanner collection. |
| `additional_search_tags` | Extra tags added to reports. |
| `report.max_top_gaps` | Number of top gaps shown in summaries and comments. |

## Suppression Rules

Suppression works by stable finding ID:

```json
{
  "id": "ARK-VLT-001",
  "reason": "Temporarily accepted during prototype phase.",
  "expires": "2026-12-31"
}
```

Suppressed findings are not silently hidden. They appear under:

- `Suppressed Readiness Gaps` in Markdown;
- `suppressed_findings` in JSON.

Suppression is not proof of safety. It should be reviewed before launch,
fundraising, audit intake, or handling user funds.

## Ignore Paths

Use `ignore_paths` for generated code, mocks, vendored dependencies, or
fixtures that should not influence readiness output:

```json
"ignore_paths": ["lib/", "test/mocks/"]
```

The scanner already ignores common build/cache directories.

## Invalid Config Behavior

If the JSON is invalid, Arkheionx continues scanning and writes a configuration
warning to Markdown and JSON. It does not apply suppressions from invalid
config files.

## Limitations

- JSON only for v0.3.0.
- No remote policy service.
- No organization-level config inheritance.
- No guarantee that a suppressed finding is safe.
