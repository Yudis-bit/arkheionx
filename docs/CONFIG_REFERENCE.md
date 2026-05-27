# Config Reference

This page documents the stable Arkheionx v1.7.0 config surface.

The machine-readable schema lives at
[`schemas/arkheionx_config.schema.json`](../schemas/arkheionx_config.schema.json).
Runtime validation uses Python standard library checks through
[`scripts/validate_config.py`](../scripts/validate_config.py).

## Top-Level Fields

| Field | Default | Purpose |
|---|---|---|
| `schema_version` | `1.7.0` | Config schema version. |
| `protocol_type` | `auto` | Protocol hint for scanner behavior. |
| `rule_packs` | `[]` | Enabled rule packs. Empty means default enabled packs. |
| `min_confidence` | `low` | Minimum confidence preference for issue planning. |
| `output_profile` | `standard` | Report verbosity profile: `concise`, `standard`, `full`, or `ci`. |
| `scan` | object | Source file handling and generated artifact controls. |
| `reports` | object | Report content preferences. |
| `test_plan` | object | Test-plan generator preferences. |
| `suppressions` | `[]` | Documented finding suppressions. |

## Protocol Types

Supported values:

- `auto`
- `generic`
- `vault`
- `oracle`
- `access-control`
- `rewards`
- `staking`
- `amm`
- `lending`
- `hybrid`

Use `auto` unless the repository has a known dominant protocol shape.

## Scan Fields

| Field | Default | Purpose |
|---|---|---|
| `ignore_generated_artifacts` | `true` | Ignore Arkheionx outputs as source evidence. |
| `include_generated_artifacts` | `false` | Advanced/debug override. |
| `extra_ignore_paths` | `[]` | Additional path prefixes to ignore. |
| `extra_ignore_globs` | `[]` | Additional relative path globs to ignore. |
| `max_file_size_kb` | `null` | Optional maximum file size to read. |
| `include_tests` | `true` | Include tests in readiness evidence. |
| `include_docs` | `true` | Include Markdown docs in readiness evidence. |

## Report Fields

| Field | Default | Purpose |
|---|---|---|
| `include_related_knowledge` | `true` | Include security memory context. |
| `include_evidence_snippets` | `true` | Include compact evidence snippets. |
| `include_suggested_tests` | `true` | Include suggested tests. |
| `include_issue_plan` | `true` | Include issue-plan-oriented metadata. |
| `include_executive_summary` | `true` | Include executive summary sections where supported. |
| `max_top_gaps` | `5` | Top gap count in summaries. |

## Test Plan Fields

| Field | Default | Purpose |
|---|---|---|
| `include_foundry_skeletons` | `true` | Allow safe Foundry skeleton output in generated test plans. |
| `group_by_rule_family` | `true` | Group suggestions by rule family. |
| `include_low_confidence` | `false` | Include low-confidence findings in test plans. |
| `output_profile` | `standard` | `concise`, `standard`, or `full`. |

## Validation

```sh
python3 scripts/validate_config.py --config examples/configs/minimal.config.json
python3 scripts/validate_config.py --config examples/configs/minimal.config.json --json
```

Invalid configs fail clearly. Dangerous keys are rejected.
