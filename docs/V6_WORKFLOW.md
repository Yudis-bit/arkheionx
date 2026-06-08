# Arkheionx V6 Workflow — Evidence Graph + Interaction Matrix

> Local/static and heuristic. An evidence state is not a vulnerability claim.
> Interaction priority is not severity. Unresolved does not mean vulnerable.
> Human review is required for every conclusion.

V4 maps value flow. V5 maps likely blind spots. **V6 classifies evidence and maps
unresolved interactions.**

> V5 shows where to look. V6 shows what is proven, what is unresolved, and which
> interactions still lack evidence.

The final thesis of V6 is simple: **no high-impact surface should remain
unclassified.** That does not mean no bug will be missed, that all bugs are
found, or that the protocol is safe — it means every high-impact surface is
assigned an evidence state, so the unknowns are visible.

## The progression

| Layer | Question it answers |
| --- | --- |
| V4 review-map | Where does value enter, move, and exit, and what guards it? |
| V5 blind-spots | Where is review attention weakest? |
| **V6 evidence-graph** | **What evidence exists for each surface?** |
| **V6 interaction-matrix** | **Which dangerous interactions still lack tests?** |
| **V6 unresolved-map** | **What is left before review can end?** |
| **V6 complete-review** | **The whole package, for a human or an AI agent.** |

## The commands

```bash
arkheionx evidence-graph .       # classify every important surface
arkheionx interaction-matrix .   # find combinations that may hide bugs
arkheionx unresolved-map .       # everything still unresolved
arkheionx complete-review . --out .arkheionx/complete-review  # the full package
```

See [`EVIDENCE_GRAPH.md`](EVIDENCE_GRAPH.md),
[`INTERACTION_MATRIX.md`](INTERACTION_MATRIX.md),
[`UNRESOLVED_MAP.md`](UNRESOLVED_MAP.md), and
[`COMPLETE_REVIEW.md`](COMPLETE_REVIEW.md) for each command in depth.

## How a researcher uses V6

1. Run `review-map` to understand how value moves.
2. Run `blind-spots` to rank likely blind spots.
3. Run `evidence-graph` to classify each surface's evidence state.
4. Run `interaction-matrix` to find combinations that lack tests.
5. Check `unresolved-map` to see what is still open.
6. Generate `complete-review` to assemble the package.
7. Give `08-agent-input.md` to an AI agent or reviewer.
8. Write local tests for the unresolved surfaces and interactions.
9. Record rejected and confirmed-candidate results as local research memory
   (`hypothesis-log`).
10. A human makes the final call — always.

## Evidence states at a glance

`tested`, `rejected-with-evidence`, `confirmed-candidate`, `unresolved`,
`insufficient-evidence`, `needs-human-review`, `unclassified`, `out-of-scope`.
None of them is a vulnerability claim. The two strongest states are only ever
assigned from explicit local research memory, never inferred from scoring.

## Boundaries

- Local/static only. No RPC, no live-chain calls, no private keys, no exploit
  automation, no auto-submit.
- No bug prediction, no severity, no confirmed-vulnerability claim, no audit
  replacement.
- Evidence quality still depends on the tests that exist and on human review.

## Related

- [`BLIND_SPOT_INTELLIGENCE.md`](BLIND_SPOT_INTELLIGENCE.md) and
  [`V5_WORKFLOW.md`](V5_WORKFLOW.md) — the V5 layer V6 builds on.
- [`BUG_BOUNTY_WORKFLOW.md`](BUG_BOUNTY_WORKFLOW.md) — using V6 in triage.
- [`RESEARCH_MEMORY_MODEL.md`](RESEARCH_MEMORY_MODEL.md) — how rejected/confirmed
  candidates become research memory.
