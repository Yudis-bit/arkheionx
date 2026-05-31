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
  ("ready to submit", "guaranteed bounty/exploit") and no live-chain reproduction
  steps (`--fork-url`, `rpc_url`, "deploy to mainnet").
- Malformed JSON is reported as invalid, not silently ignored.

## Exit codes

- `0` — all checked artifacts valid.
- `1` — warnings/invalid artifacts found.
- `2` — command failure (e.g. path is not a directory).

## Output

Compact terminal by default; `--json` for machine-readable output. Lists how
many of each artifact type were checked and any issues found, then the next
command (regenerate affected artifacts, or proceed to manual review).

See also [`EVIDENCE_WORKFLOW_HARDENING.md`](EVIDENCE_WORKFLOW_HARDENING.md).
