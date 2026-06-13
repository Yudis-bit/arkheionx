# Core workflow — `arkheionx review`

`arkheionx review` is the primary, "start here" command. It turns a local
repository (plus an optional scope note and an optional generic protocol-family
lens) into one review pack: numbered human-readable Markdown plus machine-readable
`review.json` and `manifest.json`.

```bash
# One-command review pack:
arkheionx review . --scope-file scope.md --out .arkheionx/review

# Protocol-aware deep dive (adds lens artifacts):
arkheionx review . --scope-file scope.md --lens fixed-credit-market --out .arkheionx/review
```

The pipeline:

> scope → value flow → interaction map → assumptions → review lanes → evidence tasks → evidence rubric → report filter → human review

`arkheionx review` orchestrates the existing layers (the review map, scope-aware
orchestration, and — when `--lens` is given — a protocol lens). It adds no new
analysis and makes no vulnerability or severity claim.

## What the pack contains

Core artifacts (always written):

- `00-run-context.md` — version, repo, scope, lens, counts, read order, exit codes.
- `01-scope-map.md` — the scope turned into structured review rules.
- `02-value-flow-map.md` — where value enters, moves, and exits.
- `03-interaction-map.md` — cross-contract and external-call interactions.
- `04-assumptions.md` — the trust each value path appears to rely on.
- `05-review-lanes.md` — review lanes selected for this scope (review order, not severity).
- `06-evidence-tasks.md` — precise, bounded tasks, each with a **kill condition**.
- `07-evidence-rubric.md` — how local-test evidence is graded.
- `08-report-filter.md` — how candidates are classified before submission.
- `09-agent-input.md` — model-agnostic instructions for an AI-assisted reviewer.
- `review.json` — the consolidated machine-readable pack (see [`SCHEMAS.md`](SCHEMAS.md)).
- `manifest.json` — the pack manifest (counts, safety flags, exit-code semantics).

With `--lens`, the pack also includes `10-protocol-model.md`,
`11-behavior-promises.md`, `12-economic-invariants.md`, `13-temporal-windows.md`,
`14-lens-review-lanes.md`, and `15-lens-evidence-tasks.md`. See
[`PROTOCOL_LENS_PACKS.md`](PROTOCOL_LENS_PACKS.md).

## Kill conditions

Every evidence task carries a **kill condition**: the practical signal that the
hypothesis is dead and should be abandoned (the invariant holds for realistic
actors, the path is out of scope / known / accepted / trusted-role-only, or there
is no material impact). Kill conditions exist so a reviewer or agent stops a weak
hypothesis quickly.

## Then what

1. Read `00-run-context.md`, then `01-scope-map.md` and `04-assumptions.md`.
2. Give `09-agent-input.md` plus `06-evidence-tasks.md` to a reviewer or agent.
3. Write local Foundry tests; grade them with `07-evidence-rubric.md`
   ([`EVIDENCE_JUDGE.md`](EVIDENCE_JUDGE.md)).
4. Classify candidates with `08-report-filter.md` ([`REPORT_FILTER.md`](REPORT_FILTER.md)).
5. A human makes the security call.

## Exit codes

See [`SAFETY_BOUNDARIES.md`](SAFETY_BOUNDARIES.md#exit-codes) and
[`CLI_REFERENCE.md`](CLI_REFERENCE.md). Analysis commands may return `1` when the
output is heuristic and needs human review — a warning-style code, not a crash.

## Boundary

Local/static only. No RPC, no live-chain scanning, no exploit automation, no
auto-submit. A review pack is a planning artifact, not a finding. A review lane is
not a vulnerability. Evidence quality is not vulnerability validity. Human review is
required.
