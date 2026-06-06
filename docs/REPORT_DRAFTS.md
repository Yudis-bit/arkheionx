# Report Drafts

`arkheionx report` turns an evidence package into a responsible local report
draft. It never auto-submits and never claims final severity.

```sh
arkheionx report . --target Vault.withdraw
arkheionx report . --from-evidence .arkheionx/out/evidence/Vault_withdraw/evidence.json
```

## What it does

1. Loads (or builds) the evidence package for the target.
2. Writes `report.md` and `report.json` under
   `.arkheionx/out/reports/<target-slug>/`.
3. Prints a compact summary; the next step is always manual review.

## Report structure

`Summary`, `Evidence Level`, `Affected Components`, `Proof Artifacts`,
`Reproduction` (local-only), `Trace Summary`, `Impact Reasoning`, `Assumptions`,
`Limitations`, `Suggested Next Steps`, `Safety Notice`.

In v3.4.0, report JSON also includes:

- `evidence_context`
- `receipt_references`
- `report_readiness`
- `claim_references`

In release-prep v3.5.0, the internal Protocol Intelligence Model can link a
report draft to its evidence package and target function via stable IDs
(`ReportDraftNode`). This is additive and internal only: report drafts remain
draft/manual-review only, `review_status` stays `NEEDS_HUMAN_REVIEW`,
`ready_for_submission` stays false, `HUMAN_REVIEWED` is never emitted
automatically, and the `report.md` / `report.json` shapes are unchanged.

These fields link the draft back to existing local evidence, proof, and trace
receipts. They do not mark the report as reviewed or ready to submit.

## Responsible language

- A failing test → "Observed a failing local test. Human review is required to
  determine whether this represents a valid vulnerability."
- A passing test → "Observed a passing local test. This does not prove absence
  of bugs."
- Impact is always framed as a candidate review surface, never a final severity.

## Safety

- No auto-submit.
- No final severity claim, no bounty guarantee.
- No live-chain reproduction, no private keys, no broadcast.
- Local defensive security research only; not a formal audit.
- `ready_for_submission` stays false and `HUMAN_REVIEWED` is not emitted
  automatically.

## Review-map linkage

When a local report draft exists under `.arkheionx/out/reports/<target-slug>/`,
`arkheionx review-map` and `arkheionx evidence-links` may surface the report
JSON/Markdown paths alongside proof, trace, and evidence package references.
Those links remain draft/manual-review context only; `evidence-links` is
read-only and does not create evidence, confirm vulnerabilities, assign final
severity, or submit reports.

## Schema

[`../schemas/report-draft.schema.json`](../schemas/report-draft.schema.json).

See also [`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md) and
[`EVIDENCE_WORKFLOW_HARDENING.md`](EVIDENCE_WORKFLOW_HARDENING.md).
