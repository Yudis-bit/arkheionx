# Evidence Package

`arkheionx evidence` assembles a compact, structured evidence package from the
proof and trace artifacts produced by `prove --run` / `trace`, plus protocol and
hunt context.

```sh
arkheionx evidence . --target Vault.withdraw
arkheionx evidence . --from-proof .arkheionx/out/proof/Vault_withdraw/proof.json
```

## What it does

1. Resolves the fully-qualified target (rejects ambiguity).
2. Locates `proof.json` and `trace.json` for the target.
3. Pulls role / score / money-flow / likely-bug-class context from the map.
4. Records a deterministic `evidence_package_id` and additive `manifest`.
5. Writes `evidence.json` and `evidence.txt` under
   `.arkheionx/out/evidence/<target-slug>/`.
6. Prints a compact summary and the next command (`arkheionx report`).

## Evidence levels

- `HEURISTIC` — static only.
- `COMPILER_CONFIRMED` — `forge build` passed.
- `EXECUTION_CONFIRMED` — a relevant Foundry test executed.
- `EVIDENCE_READY` — execution-confirmed proof **and** a trace artifact exist and
  the evidence package was built. If uncertain, the package stays at
  `EXECUTION_CONFIRMED`, not `EVIDENCE_READY`.

In release-prep v3.5.0, the internal Protocol Intelligence Model can reference an
evidence package's existing `evidence_package_id` and link it to proof/trace
receipts and a target function ID. This is additive and internal only: the
trace-bounded evidence readiness logic, the package manifest, the
`evidence.json` / `evidence.txt` shapes, and evidence levels are unchanged.

## Statuses

`no_proof`, `scaffold_only`, `compiler_confirmed_only`, `execution_confirmed`,
`evidence_ready`.

If no proof exists, the command is honest and prints the exact
`arkheionx prove . --target <target> --run` next command.

## v3.4 package manifest

In v3.4.0, `evidence.json` includes:

- `evidence_package_id`
- `manifest.package_id`
- proof source records
- trace source records only when a real trace exists
- recorded proof and trace source paths
- readiness checks such as `trace_linked` and
  `trace_required_for_evidence_ready`
- `human_review_required`

`validate-artifacts` checks that evidence-ready packages have real linked trace
artifacts, source paths match the manifest, manifest source existence flags are
current, and manifest checks do not contradict the evidence level.

## Schema

[`../schemas/evidence.schema.json`](../schemas/evidence.schema.json).

## Limits

Severity is never final. Human review is required to determine whether a result
represents a valid vulnerability. Not a formal audit; no severity guarantee.

See also [`REPORT_DRAFTS.md`](REPORT_DRAFTS.md) and
[`EXECUTION_PROOF.md`](EXECUTION_PROOF.md). To inspect or validate artifacts
across a repo, see [`EVIDENCE_WORKFLOW_HARDENING.md`](EVIDENCE_WORKFLOW_HARDENING.md).
