# Evidence Workflow Hardening

v2.4.0 hardens the local evidence workflow so a researcher always knows what
exists, what is missing, and what to run next.

```text
hunt → prove --run → trace → evidence → report → manual review
```

## evidence-status

```sh
arkheionx evidence-status .
arkheionx evidence-status . --target Vault.withdraw
arkheionx evidence-status . --json
```

Shows, per target, which artifacts exist (proof / trace / evidence / report),
the review status, and the next command. With no artifacts it points to
`arkheionx hunt`. It never crashes on an empty `.arkheionx/` and reports
malformed artifacts as invalid rather than ignoring them.

## Review statuses

`NO_PROOF` → `PROOF_ONLY` → `TRACE_READY` → `EVIDENCE_READY` → `REPORT_DRAFTED`.
A drafted report is always `NEEDS_HUMAN_REVIEW`. There is no "ready to submit".

## Artifact index

`prove`, `trace`, `evidence`, and `report` refresh
`.arkheionx/out/artifacts-index.json` after writing. `evidence-status` rebuilds
it by scanning when missing or stale, so it is always a cache — never a
dependency. Schema: [`../schemas/artifacts-index.schema.json`](../schemas/artifacts-index.schema.json).

## Next-command chain

| After | Next |
|---|---|
| hunt | `prove . --target <t> --run` |
| prove (executed) | `trace . --target <t>` |
| trace (execution-confirmed) | `evidence . --target <t>` |
| evidence (ready) | `report . --target <t>` |
| report | manual review |
| evidence-status (no artifacts) | `hunt . --top 5` |
| validate-artifacts (issues) | regenerate the affected artifacts |

See also [`ARTIFACT_VALIDATION.md`](ARTIFACT_VALIDATION.md),
[`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md), and
[`REPORT_DRAFTS.md`](REPORT_DRAFTS.md).
