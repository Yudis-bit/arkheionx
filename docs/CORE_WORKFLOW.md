# Core Review Workflow

`arkheionx review` is the primary public workflow.

It turns a local repository, an optional scope note, and an optional protocol-family lens into one review pack: Markdown for humans and JSON for tools.

```bash
arkheionx review . --scope-file scope.md --out .arkheionx/review
arkheionx review . --scope-file scope.md --lens fixed-credit-market --out .arkheionx/review
```

## Pipeline

```text
scope -> value flow -> interaction map -> assumptions -> review lanes -> evidence tasks -> evidence rubric -> report filter -> human review
```

ArkheionX does not make a vulnerability claim at any step in this pipeline. It builds context for a human reviewer.

## What the pack contains

Core artifacts:

| artifact | purpose |
|---|---|
| `00-run-context.md` | Version, repo, scope, lens, counts, read order, and boundary notes. |
| `01-scope-map.md` | Scope rules converted into structured review context. |
| `02-value-flow-map.md` | Where value appears to enter, move, and exit. |
| `03-interaction-map.md` | Cross-contract and external-call interaction surfaces. |
| `04-assumptions.md` | Trust assumptions guarding value paths. |
| `05-review-lanes.md` | Ordered review lanes. Review order is not severity. |
| `06-evidence-tasks.md` | Bounded evidence tasks with kill conditions. |
| `07-evidence-rubric.md` | How to judge whether local evidence supports the task. |
| `08-report-filter.md` | Pre-report classification for weak, out-of-scope, duplicate-prone, or under-proven candidates. |
| `09-agent-input.md` | Model-agnostic context for AI-assisted review. |
| `review.json` | Consolidated machine-readable review pack. |
| `manifest.json` | Pack manifest, counts, safety flags, and artifact metadata. |

With a lens, the pack adds protocol-family context such as behavior promises, economic invariants, temporal windows, lens review lanes, and lens evidence tasks.

## Kill conditions

Evidence tasks include kill conditions so weak hypotheses can be dropped quickly.

Examples:

- the path is out of scope;
- a trusted-role assumption fully explains the behavior;
- the invariant holds under realistic local tests;
- impact is not material;
- the candidate duplicates known/accepted behavior;
- required evidence cannot be produced.

Killing weak hypotheses is a feature. It prevents noisy report writing.

## Human workflow

1. Read `00-run-context.md`.
2. Review scope and assumptions.
3. Follow the highest-value review lanes.
4. Write or run local tests for the evidence tasks.
5. Record whether the evidence supports, rejects, or fails to prove the hypothesis.
6. Use the report filter before writing a report candidate.
7. Let a human reviewer decide severity and reportability.

## Boundary

The review pack is a planning artifact. It is not a finding, audit result, proof of safety, severity assignment, or endorsement.

See [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md), [`OUTPUT_ARTIFACTS.md`](OUTPUT_ARTIFACTS.md), and [`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md).
