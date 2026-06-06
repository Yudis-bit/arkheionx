# Artifact Validation

`arkheionx validate-artifacts` checks the generated proof/evidence/report
artifacts locally, with no third-party dependencies.

```sh
arkheionx validate-artifacts .
arkheionx validate-artifacts . --json
```

## What it checks

- Required fields in `proof.json`, `trace.json`, `evidence.json`, `report.json`.
- Legal evidence-level transitions:
  - `EXECUTION_CONFIRMED` proof must have at least one executed test.
  - `EVIDENCE_READY` evidence must reference an existing trace artifact.
- Referenced paths (e.g. `evidence.json` → `trace.json`) exist.
- Report drafts include a `safety_notice` and contain no disallowed phrasing
  ("ready to submit", bounty or exploit promises) and no live-chain reproduction
  steps (`--fork-url`, `rpc_url`, "deploy to mainnet").
- Malformed JSON is reported as invalid, not silently ignored.

## Exit codes

- `0` — all checked artifacts are valid.
- `1` — validation issues or review attention were found. This can include
  malformed JSON, missing required fields, broken artifact references, unknown
  evidence levels, or report-draft safety wording issues.
- `2` — command/input failure (for example, the path is not a directory).

v3.2.0 keeps this 0/1/2 behavior for compatibility. A dedicated
artifact-validation failure code or strict exit-code mode is deferred to a later
release.

## Output

Compact terminal by default; `--json` for machine-readable output. Lists how
many of each artifact type were checked and any issues found, then the next
command (regenerate affected artifacts, or proceed to manual review).

For strict CI in v3.2.0, use `arkheionx validate-artifacts . --json` and fail
on `status != "ok"` until a dedicated strict mode exists.

See also [`EVIDENCE_WORKFLOW_HARDENING.md`](EVIDENCE_WORKFLOW_HARDENING.md).
