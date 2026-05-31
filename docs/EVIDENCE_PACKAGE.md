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
4. Writes `evidence.json` and `evidence.txt` under
   `.arkheionx/out/evidence/<target-slug>/`.
5. Prints a compact summary and the next command (`arkheionx report`).

## Evidence levels

- `HEURISTIC` — static only.
- `COMPILER_CONFIRMED` — `forge build` passed.
- `EXECUTION_CONFIRMED` — a relevant Foundry test executed.
- `EVIDENCE_READY` — execution-confirmed proof **and** a trace artifact exist and
  the evidence package was built. If uncertain, the package stays at
  `EXECUTION_CONFIRMED`, not `EVIDENCE_READY`.

## Statuses

`no_proof`, `scaffold_only`, `compiler_confirmed_only`, `execution_confirmed`,
`evidence_ready`.

If no proof exists, the command is honest and prints the exact
`arkheionx prove . --target <target> --run` next command.

## Schema

[`../schemas/evidence.schema.json`](../schemas/evidence.schema.json).

## Limits

Severity is never final. Human review is required to determine whether a result
represents a valid vulnerability. Not a formal audit; no severity guarantee.

See also [`REPORT_DRAFTS.md`](REPORT_DRAFTS.md) and
[`EXECUTION_PROOF.md`](EXECUTION_PROOF.md). To inspect or validate artifacts
across a repo, see [`EVIDENCE_WORKFLOW_HARDENING.md`](EVIDENCE_WORKFLOW_HARDENING.md).
