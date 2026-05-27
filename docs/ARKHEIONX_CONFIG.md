# Arkheionx Config

Arkheionx supports an optional JSON config file:

```text
.arkheionx.json
```

The config is intentionally simple and dependency-free.

## Example

```json
{
  "version": "1.4.0",
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
    "vault",
    "amm",
    "lending"
  ],
  "report": {
    "max_top_gaps": 5
  },
  "scan": {
    "ignore_generated_artifacts": true,
    "include_generated_artifacts": false,
    "extra_ignore_paths": [],
    "extra_ignore_globs": []
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
| `scan.ignore_generated_artifacts` | Ignore Arkheionx generated reports/artifacts as source evidence. Defaults to `true`. |
| `scan.include_generated_artifacts` | Advanced/debug override to include generated artifacts. Defaults to `false`. |
| `scan.extra_ignore_paths` | Additional path-prefix ignores. |
| `scan.extra_ignore_globs` | Additional glob ignores. |
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

Protocol type can be set to `auto`, `vault`, `amm`, `lending`, `staking`,
`oracle`, or `generic`. Use `auto` unless a repository has a known dominant
shape. Hybrid repositories can still emit multiple rule-pack findings through
source signals.

AMM and lending suppressions use the same format:

```json
{
  "id": "ARK-AMM-003",
  "reason": "Spot-price assumptions are documented in the scoped audit package.",
  "expires": "2026-12-31"
}
```

```json
{
  "id": "ARK-LEND-002",
  "reason": "Liquidation boundary tests are tracked in an active remediation issue.",
  "expires": "2026-12-31"
}
```

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

Delivery artifacts such as Launch Reports, sprint plans, contest readiness
reports, executive summaries, and remediation roadmaps inherit the same active
and suppressed finding model. Suppression remains visible and should be
explained before any client-facing handoff.

## Ignore Paths

Use `ignore_paths` for generated code, mocks, vendored dependencies, or
fixtures that should not influence readiness output:

```json
"ignore_paths": ["lib/", "test/mocks/"]
```

The scanner already ignores common build/cache directories.

## Generated Artifact Ignore

Arkheionx ignores its own generated reports and artifacts by default. This
prevents files such as `reports/*-pre-audit-report.md`,
`reports/*-issue-plan.json`, `arkheionx.sarif.json`, and
`ARKHEIONX_PR_COMMENT.md` from affecting future scans.

Reports include `scan_sources` so users can see how many generated artifacts
were ignored. Only set `scan.include_generated_artifacts` to `true` for
debugging scanner behavior; it can make previous reports influence the current
score.

See [`GENERATED_ARTIFACT_IGNORE.md`](GENERATED_ARTIFACT_IGNORE.md).

## Invalid Config Behavior

If the JSON is invalid, Arkheionx continues scanning and writes a configuration
warning to Markdown and JSON. It does not apply suppressions from invalid
config files.

## Limitations

- JSON only.
- No remote policy service.
- No organization-level config inheritance.
- No guarantee that a suppressed finding is safe.
