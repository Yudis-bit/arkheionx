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

## Schema

[`../schemas/report-draft.schema.json`](../schemas/report-draft.schema.json).

See also [`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md).
