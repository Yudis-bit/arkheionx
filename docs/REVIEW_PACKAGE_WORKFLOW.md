# Review Package Workflow

A practical, local-only guide to producing a reviewer-ready Arkheionx review
package. Every step runs on your own machine against a repository you own or are
authorized to review. The package is review guidance only: manual review is
required, and it is never ready for submission.

## Overview

The flow is: generate the review-map artifacts, dry-run the package, build the
package folder, inspect it, review the protocol-model sidecar and
cross-reference warnings, optionally export a deterministic ZIP, and only share
it locally after a human has reviewed it.

## 1. Generate or refresh project artifacts

The package collects existing local artifacts, so generate them first.

```sh
arkheionx review-map .
arkheionx value-paths .
arkheionx assumptions .
arkheionx test-gap-map .
arkheionx proof-plan .
arkheionx evidence-links .
```

These write artifacts under `.arkheionx/out/review-map/`. Proof, trace,
evidence, and report artifacts are included automatically when they already
exist under `.arkheionx/out/`.

## 2. Build the review package as a dry run

```sh
arkheionx review-package . --no-write --json
```

This builds the manifest, checksums, validation, and the in-memory protocol
model without writing anything. Confirm `written` is false and check
`validation_status`, `missing_required_artifacts`, and `crossref_warning_count`.

## 3. Build the review package folder

```sh
arkheionx review-package .
```

This writes `.arkheionx/out/review-package/` with `manifest.json`,
`validation.json`, `README.md`, `limitations.md`, copied `artifacts/`,
`checksums/SHA256SUMS`, and (when buildable) the protocol-model sidecar.

## 4. Inspect `manifest.json`

Read `.arkheionx/out/review-package/manifest.json`. Confirm the included
artifacts, their checksums, `protocol_model_id` (when present),
`manual_review_required` is true, and `ready_for_submission` is false.

## 5. Inspect `validation.json`

Read `.arkheionx/out/review-package/validation.json`. Review `status`, `errors`,
`warnings`, `missing_required_artifacts`, and any `crossref.*` checks. Warnings
are guidance; resolve them before relying on the package.

## 6. Inspect `README.md` and `limitations.md`

Read the reviewer `README.md` and `limitations.md` in the package folder. They
state the package status and the local/static, manual-review-required boundary.

## 7. Include the protocol-model sidecar

By default the package includes `artifacts/intelligence/protocol-model.json`
when buildable from `review-map` output. Use `--no-protocol-model` to skip it,
or `--include-protocol-model` to make the intent explicit.

## 8. Review cross-reference warnings

When the sidecar is present, cross-reference checks resolve referenced IDs
against the model by exact match or explicit alias only. Unresolved references
are warnings, never invented links. Read them as guidance about which artifacts
do not yet connect to the model.

## 9. Export a deterministic ZIP

```sh
arkheionx review-package . --export zip --json
```

This writes `review-package/exports/arkheionx-review-package-<id>.zip`, a
deterministic local archive (stable entry order, fixed timestamps). Confirm
`export_written` is true and `export_status` is `created`. The archive is local;
Arkheionx does not transmit it.

## 10. Share locally only, after human review

The archive is a local file. Manual review is required before any external
sharing. Arkheionx does not upload, submit, publish, or send the package
anywhere — moving or sharing it is a manual decision you make after review, and
the package remains not ready for submission.

## Safety boundary

Local and static only: no RPC, no private keys, no seed phrases, no live-chain
calls, no transaction broadcasting, no exploit automation, and no auto-submit.
No confirmed vulnerabilities, no final severity, no audit-passed claim, and no
bounty eligibility. Manual review is required; `ready_for_submission` stays
false.

## Related docs

- [`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md)
- [`REVIEW_PACKAGE_SMOKE_TEST.md`](REVIEW_PACKAGE_SMOKE_TEST.md)
- [`CLI_REFERENCE.md`](CLI_REFERENCE.md)

## Optional: include local validation (v3.7, in progress)

If you have a saved Foundry test output for the repository, you can ingest it
**before** building the review package so the package includes the resulting
local-validation artifacts. Arkheionx never runs `forge`; it reads the saved file
only.

```sh
arkheionx local-validate . --input foundry-output.json --json
arkheionx review-package . --json
```

The review package then discovers the `.arkheionx/out/local-validation/`
artifacts automatically. They are optional and never required, are added to the
manifest, checksums, and export, and never change the package's readiness:
`manual_review_required` stays true and `ready_for_submission` stays false.
Manual review remains required. See
[`LOCAL_VALIDATION_WORKFLOW.md`](LOCAL_VALIDATION_WORKFLOW.md).

## Optional: include protocol graph artifacts (v3.8, in progress)

If optional protocol-graph artifacts already exist under
`.arkheionx/out/protocol-graph/`, the review package includes them automatically
when you build it — no extra flag and no new command:

```sh
arkheionx review-package . --json
```

- Graph artifacts are **optional and never required**; a missing
  `protocol-graph/` folder is not an error and the package still builds.
- When present, they are added to the manifest (as the optional
  `protocol_graph*` kinds), the checksum map, and the deterministic export, and
  `artifact_count` increases accordingly.
- Their JSON, paths, and `SHA256SUMS` are validated, and graph IDs are
  cross-referenced by exact ID / explicit alias only. **Unresolved references are
  warnings**, never failures or invented links; a missing protocol model is a
  warning, not an error.
- Any overclaim (a `ready_for_submission: true` flag, a `HUMAN_REVIEWED` token,
  or forbidden finality wording) is a safety failure that invalidates the
  package. Graph consistency does not prove safety and a graph warning does not
  prove a vulnerability.
- Readiness is unchanged: `manual_review_required` stays true and
  `ready_for_submission` stays false. **Human review remains required.**

See [`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md) and
[`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md).
