# Review Package

`arkheionx review-package` assembles a local, reviewer-ready package from the
artifacts Arkheionx already wrote under `.arkheionx/out/`. It collects them into
one folder, builds a manifest with checksums, validates the package, generates a
reviewer README and limitations note, optionally includes a Protocol
Intelligence Model sidecar with cross-reference checks, and can write a
deterministic local ZIP archive.

It is review guidance only. It is local and static, requires human review, and
is never ready for submission.

## 1. What is an Arkheionx Review Package?

A review package is a single, self-describing local folder a reviewer can read
offline. It does not run analysis itself — it gathers existing local artifacts
(`review-map`, value paths, assumptions, test gaps, proof plan, proof/trace,
evidence packages, report drafts, evidence-links, and the artifact index),
records their checksums, validates them, and adds reviewer-facing context. It
connects those artifacts, their validation, an optional protocol-model sidecar,
and an optional export bundle into one place.

## 2. What it includes

- `manifest.json` — the artifact inventory, checksums, schema versions, and
  package id.
- `validation.json` — per-check results, errors, and warnings.
- `README.md` — the reviewer-facing summary and safety boundary.
- `limitations.md` — what the package is and is not.
- `artifacts/` — copied artifacts in their original relative layout.
- `checksums/SHA256SUMS` — sha256 of each packaged file.
- `exports/*.zip` — a deterministic archive, only when `--export zip` is used.
- `artifacts/intelligence/protocol-model.json` — the Protocol Intelligence Model
  sidecar, when buildable.

## 3. What it does not claim

- It is not a formal audit.
- It is not a vulnerability confirmation.
- It does not assign a final severity.
- It makes no audit-passed claim.
- It does not establish bounty eligibility.
- It is not ready for submission; `ready_for_submission` is false.
- Manual review is required before any use.

## 4. Package layout

```text
.arkheionx/out/review-package/
  manifest.json
  validation.json
  README.md
  limitations.md
  artifacts/
    review-map/...
    proofs/ traces/ evidence/ reports/ ...
    intelligence/protocol-model.json   # when buildable
  checksums/SHA256SUMS
  exports/
    arkheionx-review-package-<id>.zip  # only with --export zip
```

All recorded paths are repo-relative or package-relative; no absolute path is
written into any package file.

## 5. Build command

```sh
arkheionx review-package .
```

This writes the package folder under `.arkheionx/out/review-package/`, copies
artifacts, builds the manifest and checksums, validates, and writes the reviewer
README and limitations note.

## 6. No-write mode

```sh
arkheionx review-package . --no-write --json
```

No-write builds the manifest, checksums, validation, and (in memory) the
protocol model without creating the package folder or writing any file. JSON
reports `written: false` and `no_write: true`.

## 7. Strict mode

```sh
arkheionx review-package . --strict --json
```

Strict mode exits non-zero (`1`) when validation is invalid or reports errors,
and blocks an export archive when validation is invalid. JSON is still emitted.

## 8. Export ZIP

```sh
arkheionx review-package . --export zip --json
```

`--export zip` writes a deterministic archive under `review-package/exports/`
(`--export-output PATH` overrides the location). The archive uses a stable
`arkheionx-review-package/` root, lexicographically sorted entries, fixed
timestamps, and excludes the `exports/` directory, caches, and VCS metadata. It
is local only — Arkheionx never transmits it.

## 9. Protocol Intelligence Model sidecar

By default the package includes `artifacts/intelligence/protocol-model.json`
when it can be built from existing `review-map` output (or an existing local
protocol-model artifact). The sidecar is built additively, with the absolute
repo path scrubbed and no added timestamp.

- `--include-protocol-model` — include the sidecar when buildable (default on).
- `--no-protocol-model` — skip the sidecar and cross-reference checks.

When no `review-map` artifact exists to build from, the sidecar is omitted and a
warning is recorded — it is never a build failure.

## 10. Cross-reference validation

When the protocol-model sidecar is present, the package validates the IDs that
artifacts reference (function, contract, value-path, assumption, test-gap,
proof-suggestion, receipt, evidence-package, report, and evidence-link IDs, plus
legacy target aliases) against the model.

- Resolution is by exact ID match or an explicit alias only.
- There is no fuzzy matching and no substring matching.
- Unresolved references are warnings, never invented or fabricated links.
- A missing protocol model is a warning, not an error.

## 11. JSON output fields

`--json` prints only JSON. Build fields: `command`, `package_root`,
`manifest_path`, `validation_path`, `readme_path`, `limitations_path`,
`checksums_path`, `artifact_count`, `validation_status`,
`manual_review_required`, `ready_for_submission`, `written`, `no_write`,
`copied_artifacts`, `warnings`, `errors`. Export fields: `export_requested`,
`export_format`, `export_path`, `export_id`, `export_status`,
`export_file_count`, `export_size_bytes`, `export_checksum_sha256`,
`export_written`. Protocol-model and cross-reference fields:
`protocol_model_requested`, `protocol_model_included`, `protocol_model_path`,
`protocol_model_id`, `crossref_check_count`, `crossref_warning_count`,
`crossref_error_count`.

## 12. Manual review requirements

Every package keeps `manual_review_required` true and `ready_for_submission`
false. A reviewer must read `validation.json`, `README.md`, and `limitations.md`
and inspect the artifacts before drawing any conclusion or sharing the package.

## 13. Safety boundaries

- Local and static only.
- No RPC and no live-chain calls.
- No private keys and no seed phrases.
- No transaction broadcasting.
- No exploit automation.
- No auto-submit.
- No automatic human-reviewed status.
- No confirmed vulnerabilities.
- No final severity.
- No audit-passed claim.
- No bounty eligibility.
- Manual review required; not ready for submission.

## 14. Troubleshooting

- Missing required artifacts: the validation status is `PACKAGE_PARTIAL` and the
  missing kinds are listed in `missing_required_artifacts`. Run `review-map`
  first to generate them.
- Validation warnings: warnings do not block a build; read `validation.json` and
  resolve them before relying on the package.
- Strict invalid: with `--strict`, an invalid package exits `1` and no archive is
  written. Fix the reported errors and rebuild.
- Export blocked: an export is blocked when a required file is missing, a safety
  failure is recorded, or (with `--strict`) validation is invalid.
- Protocol model missing: if there is no `review-map` artifact to build from, the
  sidecar is omitted with a warning. Run `review-map` to enable it.
- Cross-reference warnings: unresolved references are expected when the model is
  built from `review-map` only; they are guidance, never errors.

## 15. Example workflows

Dry run, then build, then export:

```sh
arkheionx review-package . --no-write --json
arkheionx review-package .
arkheionx review-package . --export zip --json
```

See [`REVIEW_PACKAGE_WORKFLOW.md`](REVIEW_PACKAGE_WORKFLOW.md) for the full
step-by-step guide and [`REVIEW_PACKAGE_SMOKE_TEST.md`](REVIEW_PACKAGE_SMOKE_TEST.md)
for a local smoke run.

## 16. Limitations

The package is assembled from local artifacts only; it does not re-derive
analysis or raise evidence levels. The protocol-model sidecar is built from
`review-map` output, so receipt-level references resolve through evidence-link
IDs rather than dedicated receipt nodes. Cross-reference checks are warnings by
design. The package is local and is never published by Arkheionx.

## 17. Related docs

- [`CLI_REFERENCE.md`](CLI_REFERENCE.md) — full flag and JSON reference.
- [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md) — public command surface.
- [`REVIEW_MAP.md`](REVIEW_MAP.md) — the review-map artifacts the package
  collects.
- [`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md) — evidence packages included when
  present.
- [`REPORT_DRAFTS.md`](REPORT_DRAFTS.md) — report drafts included when present.

## Local Validation Artifacts (v3.7, in progress)

When `arkheionx local-validate` has written `.arkheionx/out/local-validation/`
artifacts, the review package includes them automatically. This is additive v3.7
branch work, not a finalized release.

- The collector discovers local-validation artifacts when present; they are
  **optional and never required**, and a missing `local-validation/` folder is
  not an error.
- Six optional kinds are recognized: `local_validation_summary`,
  `local_validation_run`, `local_test_result`, `local_trace_receipt`,
  `local_validation_artifacts_index`, and `local_validation_checksums`.
- They are included in the manifest, the checksum map, and the deterministic ZIP
  export alongside the existing artifacts.
- Validation checks that the local-validation JSON parses, the `SHA256SUMS` file
  is well-formed and matches, paths are safe and repo-relative, and there is no
  overclaim (a `ready_for_submission: true` or a human-reviewed marker is a
  safety failure that invalidates the package).
- Cross-reference checks resolve local-validation linked IDs
  (`linked_function_ids`, `linked_value_path_ids`, `linked_assumption_ids`,
  `linked_test_gap_ids`) against the protocol-model sidecar by exact ID or
  explicit alias only; an unresolved reference is a warning, never a fabricated
  link.
- Including local-validation artifacts does not finalize any evidence or report
  conclusion: `manual_review_required` stays true and `ready_for_submission`
  stays false.

See [`LOCAL_VALIDATION.md`](LOCAL_VALIDATION.md) and
[`LOCAL_VALIDATION_WORKFLOW.md`](LOCAL_VALIDATION_WORKFLOW.md).

## Protocol Graph Artifacts (v3.8, in progress)

When optional protocol-graph artifacts already exist under
`.arkheionx/out/protocol-graph/`, the review package includes them
automatically. This is additive v3.8 branch work, not a finalized release. The
Protocol Intelligence Core ships no public graph writer; the review package only
packages graph artifacts that are already present (see
[`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md)).

Optional layout:

```text
.arkheionx/out/protocol-graph/
  graph.json
  nodes/*.json
  edges/*.json
  checks/*.json
  coverage-summary.json
  artifacts-index.json
  checksums/SHA256SUMS
```

- The collector discovers these when present; they are **optional and never
  required**, and a missing `protocol-graph/` folder is not an error.
- Seven optional kinds are recognized: `protocol_graph`, `protocol_graph_node`,
  `protocol_graph_edge`, `protocol_graph_check`,
  `protocol_graph_coverage_summary`, `protocol_graph_artifacts_index`, and
  `protocol_graph_checksums`. The required kinds (`review_map`, `evidence_links`,
  `artifacts_index`) are unchanged. The protocol-graph `artifacts-index.json` is
  classified as `protocol_graph_artifacts_index`, never as the global
  `artifacts_index`, and the extension-less `SHA256SUMS` is collected, not
  ignored.
- They are included in the manifest, the checksum map, and the deterministic ZIP
  export alongside the existing artifacts. Adding or removing graph artifacts
  changes the package id deterministically; a repeated export over unchanged
  inputs is byte-identical.
- **Validation** checks that each known graph JSON parses, that no embedded path
  value is absolute / uses backslashes / contains a `..` traversal segment, that
  the `SHA256SUMS` file is well-formed and matches, and that there is no
  overclaim. A `ready_for_submission: true` flag, a `HUMAN_REVIEWED` token, or
  forbidden finality wording (confirmed vulnerability, final severity, audit
  passed, bounty-eligibility, graph-proves-safety, warning-proves-vulnerability)
  is a safety failure that invalidates the package. A missing optional file is a
  warning, never a failure.
- **Cross-reference** checks resolve graph IDs by exact ID / explicit alias only:
  internal node/edge/check/graph/coverage IDs against the packaged graph
  artifacts, function / value-path / assumption / test-gap IDs against the
  protocol-model sidecar, and local-validation / trace-receipt IDs against
  included local-validation artifacts. There is no fuzzy or substring matching
  and no invented link; an unresolved reference is a warning, never a failure,
  and a missing protocol model is a warning, not an error.
- Including protocol-graph artifacts does not finalize any conclusion: graph
  consistency does not prove safety, a graph warning does not prove a
  vulnerability, `manual_review_required` stays true, and `ready_for_submission`
  stays false.

See [`PROTOCOL_INTELLIGENCE_CORE.md`](PROTOCOL_INTELLIGENCE_CORE.md),
[`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md), and
[`PROTOCOL_GRAPH_SMOKE_TEST.md`](PROTOCOL_GRAPH_SMOKE_TEST.md).
