# Local Validation (v3.7, in progress)

> Status: active v3.7.0 branch work, not a finalized or published release. Local
> Validation is local/static review tooling. It is not an audit, does not replace
> a human auditor, and makes no confirmed-vulnerability, final-severity,
> audit-passed, or bounty-eligibility claim.

Local Validation lets Arkheionx ingest a **saved** Foundry test output file and
turn it into structured, deterministic local-validation artifacts that connect to
the existing Arkheionx evidence graph. Foundry proves local execution; Arkheionx
structures, validates, links, and packages the evidence; the human reviewer
decides.

## What Local Validation Is

- A reader of a **saved** `forge test` output file (structured JSON or text) that
  you already produced separately.
- A normalizer that builds deterministic run, test-result, optional trace-receipt,
  and summary records with stable IDs.
- A linker that connects results to the Protocol Intelligence Model by exact
  match only.
- A packager that writes local-validation artifacts and lets the review package,
  evidence, and report layers reference them as supporting context.

## What Local Validation Is Not

- It does **not** run `forge` and does **not** spawn a subprocess.
- It does **not** require Foundry to be installed to ingest saved output.
- It uses no RPC, no fork-url behavior, and no live-chain calls.
- It reads no private keys and no seed phrases, and it broadcasts no transactions.
- It performs no exploit automation and no auto-submit.
- It never emits a human-reviewed status automatically.
- It makes no confirmed-vulnerability, final-severity, audit-passed, or
  bounty-eligibility claim, and it keeps `ready_for_submission` false.
- It is not an audit and does not replace a human auditor.

Creating the Foundry output itself (for example by running `forge test --json`)
is **external** to Arkheionx v3.7 saved-output ingestion; Arkheionx only reads the
file you provide.

## Architecture

```text
saved Foundry output  (you produce this separately)
  -> parser            (structured JSON first, conservative text fallback)
  -> builder           (deterministic run / test-result / summary IDs; exact links)
  -> writer            (.arkheionx/out/local-validation/ artifacts)
  -> review package    (optional, additive inclusion)
  -> evidence support  (optional supporting context)
  -> report draft      (optional supporting context)
  -> human review      (always required)
```

## Command

```sh
arkheionx local-validate <repo> --input <path>
```

- `<repo>` — authorized local repository root (required).
- `--input <path>` — a saved Foundry test output file (required).

Flags:

- `--json` — print one machine-readable JSON object to stdout only (no human text).
- `--no-write` — parse and build in memory only; write no artifacts.
- `--output <path>` — output directory; it must resolve inside the repo
  (default: `<repo>/.arkheionx/out/local-validation/`).
- `--format auto|foundry-json|foundry-text` — saved-output format (default `auto`).
- `--tool foundry` — the local validation tool label recorded in artifacts.
- `--command <text>` — a command string recorded for provenance only; it is
  **never** executed.

Exit codes: `0` success, `2` invalid repo / input / format / output, `1` an
unexpected build or write error.

## Output Layout

```text
.arkheionx/out/local-validation/
  summary.json
  run.json
  results/<test_result_id>.json
  traces/<trace_receipt_id>.json     (only when trace metadata is present)
  artifacts-index.json
  checksums/SHA256SUMS
```

All generated metadata records repo-relative POSIX paths only, with no absolute
path and no secret value. Output is deterministic: repeating a run over the same
input yields byte-identical files and an identical checksum map.

## JSON Fields

The `--json` object includes `command`, `repo_path`, `input_path`,
`input_format`, `tool`, `no_write`, `written`, `output_root`, `summary_path`,
`run_path`, `artifacts_index_path`, `checksums_path`, the test counts
(`total_tests`, `passed_tests`, `failed_tests`, `skipped_tests`, `errored_tests`,
`unknown_tests`), `validation_status`, `run_id`, `summary_id`,
`test_result_count`, `trace_receipt_count`, `artifact_count`,
`written_file_count`, `manual_review_required` (true), `ready_for_submission`
(false), `warnings`, and `errors`.

`validation_status` is one of `LOCAL_VALIDATION_PASSED`, `LOCAL_VALIDATION_FAILED`,
`LOCAL_VALIDATION_PARTIAL`, `LOCAL_VALIDATION_ERROR`, `LOCAL_VALIDATION_SKIPPED`,
or `LOCAL_VALIDATION_NOT_RUN`.

## Support Semantics

Local validation can record supporting context; it cannot finalize a security
conclusion.

- A passing local test can be recorded as `SUPPORT_TESTED` supporting context.
- A passing local test with an explicit, linked local trace receipt can be
  recorded as `SUPPORT_TRACE_BOUND` supporting context.
- A failing local test is recorded as manual-review-needed context, never as a
  confirmed vulnerability.
- Skipped and errored local tests are context and warnings only.
- No local-validation signal raises the evidence ladder by itself. The
  trace-bounded `EVIDENCE_READY` rule is unchanged: it still requires an
  execution-confirmed proof plus a linked trace artifact, and a tested-only local
  signal does not create it.

## Linking

Local-validation results link to the Protocol Intelligence Model by exact match
only: an exact function signature, an exact selector, an exact contract plus
function, or an explicit alias already recorded on the model. There is no fuzzy
or substring matching and no invented link. An unresolved reference is a warning,
never a fabricated edge.

## Safety Boundary

Every local-validation artifact declares, all true: local/static only, no RPC,
no fork-url behavior, no live-chain calls, no private keys, no seed phrases, no
transaction broadcasting, no exploit automation, no auto-submit, no automatic
human-reviewed status, no confirmed vulnerabilities, no final severity, no
audit-passed claim, no bounty eligibility, and manual review required;
`ready_for_submission` is false.

## Protocol Graph Coverage Correlation (v3.8, in progress)

On the v3.8 branch, the internal Protocol Intelligence Core can correlate
explicitly linked local-validation result IDs and trace-receipt IDs to protocol
graph **test gaps** (and, through them, to function roles, value paths, and
assumptions) as **supporting context only**. This is additive and internal: it
introduces no new public command and does not change local-validation semantics.

- `COVERAGE_TESTED` means a local-validation result ID was explicitly linked to a
  test gap; **tested does not mean safe**.
- `COVERAGE_TRACE_BOUND` means a trace-receipt ID was explicitly linked;
  **trace-bound does not mean proven**.
- Correlation is exact-ID / explicit-alias only — no fuzzy or substring matching
  and no invented coverage. An unresolved reference is a warning, never a
  fabricated link.
- No coverage signal raises the evidence ladder, confirms a vulnerability, or
  assigns a severity. Missing coverage does not prove a vulnerability. Manual
  review is required and `ready_for_submission` stays false.

See [`PROTOCOL_INTELLIGENCE_CORE.md`](PROTOCOL_INTELLIGENCE_CORE.md) and
[`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md).

## Related Docs

- [`LOCAL_VALIDATION_WORKFLOW.md`](LOCAL_VALIDATION_WORKFLOW.md) — a step-by-step
  workflow.
- [`LOCAL_VALIDATION_SMOKE_TEST.md`](LOCAL_VALIDATION_SMOKE_TEST.md) — a local,
  network-free smoke test.
- [`CLI_REFERENCE.md`](CLI_REFERENCE.md) and [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md)
  — the command contract.
- [`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md) — how the review package includes
  local-validation artifacts.
