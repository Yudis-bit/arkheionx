# Local Validation Workflow (v3.7, in progress)

> Status: active v3.7.0 branch work, not a finalized release. Local/static only.
> Not an audit; does not replace a human auditor; manual review is always
> required. See [`LOCAL_VALIDATION.md`](LOCAL_VALIDATION.md).

This guide walks the saved-output local-validation workflow end to end. Arkheionx
never runs `forge` and never spawns a subprocess; it ingests a saved Foundry
output file you produce separately.

## 1. Produce or obtain a saved Foundry output (external step)

Outside Arkheionx, on a repository you own or are authorized to review, produce a
saved Foundry test output and write it to a file — for example a structured
`forge test --json` document or saved text output. This creation step is
**external** to Arkheionx v3.7 saved-output ingestion; Arkheionx only reads the
file. No RPC, no fork-url behavior, no private keys, and no seed phrases are
involved.

## 2. Dry run with `--no-write`

```sh
arkheionx local-validate ./protocol --input foundry-output.json --json --no-write
```

Nothing is written. The JSON shows `no_write` true, `written` false, the parsed
test counts, `validation_status`, `manual_review_required` true, and
`ready_for_submission` false.

## 3. Inspect the JSON result

Confirm `input_format`, the test counts, and any `warnings` (for example
unresolved test lines). A failing test is reported as context that needs manual
review, never as a confirmed vulnerability.

## 4. Write the local-validation artifacts

```sh
arkheionx local-validate ./protocol --input foundry-output.json --json
```

This writes `.arkheionx/out/local-validation/` (or your `--output` path, which
must be inside the repo).

## 5. Inspect the artifacts

```text
.arkheionx/out/local-validation/summary.json
.arkheionx/out/local-validation/run.json
.arkheionx/out/local-validation/results/<test_result_id>.json
.arkheionx/out/local-validation/traces/<trace_receipt_id>.json   (if present)
.arkheionx/out/local-validation/artifacts-index.json
.arkheionx/out/local-validation/checksums/SHA256SUMS
```

`summary.json` and `artifacts-index.json` keep `manual_review_required` true and
`ready_for_submission` false. Paths are repo-relative; no absolute path or secret
value appears.

## 6. Build a review package

```sh
arkheionx review-package ./protocol --json
```

The review package discovers the local-validation artifacts automatically when
they are present, classifies them into optional kinds, includes them in the
manifest and checksums, and (with `--export zip`) in the deterministic archive.
They are optional and never required.

```sh
arkheionx review-package ./protocol --export zip --json
```

## 7. Inspect the manifest and validation

The package `artifact_count` increases when local-validation artifacts are
present. Validation checks that the local-validation JSON parses, the checksum
file matches, paths are safe, and there is no overclaim; cross-reference checks
resolve linked IDs against the protocol-model sidecar by exact ID or explicit
alias only (unresolved references are warnings).

## 8. Build evidence / report drafts (optional)

```sh
arkheionx evidence ./protocol --target Contract.function
arkheionx report ./protocol --target Contract.function
```

When local-validation artifacts exist, the evidence package can carry an optional
`local_validation_support` block and the report draft can summarize a "Local
Validation Context" section.

## 9. Inspect the support context

Support is `SUPPORT_TESTED` for a passing test, `SUPPORT_TRACE_BOUND` only when an
explicit local trace receipt links it, and otherwise manual-review-needed
context. The evidence readiness ladder is unchanged: a tested-only local signal
does not create `EVIDENCE_READY`, which still requires an execution-confirmed
proof plus a linked trace artifact.

## 10. Keep human review required

Every output keeps `manual_review_required` true and `ready_for_submission`
false, emits no human-reviewed status, and makes no confirmed-vulnerability,
final-severity, audit-passed, or bounty-eligibility claim. A human reviewer
decides whether anything here is meaningful.
