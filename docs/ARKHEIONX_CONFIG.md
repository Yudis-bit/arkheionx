# Arkheionx Config

Arkheionx supports an optional JSON config file:

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
  },
  "analysis": {
    "semantic_lite": true,
    "slither": false,
    "min_confidence_for_issue_plan": "medium",
    "downgrade_keyword_only": true,
    "max_evidence_per_finding": 5
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
| `analysis.semantic_lite` | Enable semantic-lite Solidity structure extraction. Defaults to `true`. |
| `analysis.slither` | Enable optional local Slither integration. Defaults to `false`. |
| `analysis.min_confidence_for_issue_plan` | Minimum finding confidence included in generated issue plans. Defaults to `medium`. |
| `analysis.downgrade_keyword_only` | Downgrade weak keyword-only findings. Defaults to `true`. |
| `analysis.max_evidence_per_finding` | Maximum evidence records shown per finding. Defaults to `5`. |

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

## Baseline And Diff Interaction

Suppressed findings are excluded from active SARIF results and active diff
findings, but they remain visible in Markdown and JSON. Suppression can affect
explicit gates such as `--fail-on-unsuppressed-high`; it should never be used
to hide launch-critical work without a written reason.

## Analysis Tuning

Semantic-lite extraction is enabled by default because it improves evidence,
affected-function reporting, SARIF locations, and false-positive reduction.
Slither is disabled by default because it is an optional local dependency.

Low-confidence findings remain visible in reports. If
`min_confidence_for_issue_plan` is set to `medium`, Arkheionx keeps
keyword-only findings out of generated issue plans and lists them as excluded
low-confidence findings in the issue-plan JSON.

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

- JSON only.
- No remote policy service.
- No organization-level config inheritance.
- No guarantee that a suppressed finding is safe.
