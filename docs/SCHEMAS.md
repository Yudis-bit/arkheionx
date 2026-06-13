# Schemas

Arkheionx ships JSON schemas under [`schemas/`](../schemas) and installs them with
the package (under `share/arkheionx/schemas/`). They describe the machine-readable
artifacts so CI and downstream tools can validate output without guessing the shape.

Every major JSON artifact carries `schema_version`, `arkheionx_version`,
`artifact_type` (or `kind`), and `generated_at`.

## Review pack (v8)

- [`manifest.schema.json`](../schemas/manifest.schema.json) — the review pack
  `manifest.json`: `artifact_type` `review-pack-manifest`, `command`, `repo_path`,
  `scope_file`, `lens`, `artifact_count`, `artifact_paths`, `counts`,
  `safety_flags`, `exit_code_semantics`, `human_review_required`, `safety_boundary`.
- [`review-pack.schema.json`](../schemas/review-pack.schema.json) — the consolidated
  `review.json`: `artifact_type` `review-pack` plus an embedded `data` block with the
  scope map, value-flow map, interaction map, assumptions, review lanes, evidence
  tasks, evidence judge, and report filter.

## Scope-aware and lens artifacts

- [`scope-map.schema.json`](../schemas/scope-map.schema.json),
  [`scope-lanes.schema.json`](../schemas/scope-lanes.schema.json),
  [`scope-tasks.schema.json`](../schemas/scope-tasks.schema.json) — scope-aware
  orchestration. Each scope task requires a `kill_condition`.
- [`evidence-judge.schema.json`](../schemas/evidence-judge.schema.json),
  [`report-filter.schema.json`](../schemas/report-filter.schema.json) — grading and
  candidate classification.
- [`lens-pack.schema.json`](../schemas/lens-pack.schema.json),
  [`lens-map.schema.json`](../schemas/lens-map.schema.json),
  [`lens-lanes.schema.json`](../schemas/lens-lanes.schema.json),
  [`lens-tasks.schema.json`](../schemas/lens-tasks.schema.json),
  [`lens-evidence.schema.json`](../schemas/lens-evidence.schema.json),
  [`lens-report-filter.schema.json`](../schemas/lens-report-filter.schema.json) —
  the protocol-lens layer. Each lens task also requires a `kill_condition`.

## Validating in CI

The artifacts are plain JSON, so any draft-07 validator works. The test suite uses a
small recursive validator (no extra dependency) to keep the artifacts honest; see
`tests/test_v8_schemas.py`, `tests/test_v7_scope_schemas.py`, and
`tests/test_lens_schemas.py`. In CI, prefer inspecting decision fields in the JSON
over treating a non-zero analysis exit code as fatal — see
[`SAFETY_BOUNDARIES.md`](SAFETY_BOUNDARIES.md#exit-codes).
