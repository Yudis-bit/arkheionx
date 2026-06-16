# Unresolved Map (v6)

> Unresolved does not mean vulnerable. Unresolved means local evidence is
> insufficient to close the question. Human review is required.

The Unresolved Map composes the [Evidence Graph](EVIDENCE_GRAPH.md) and the
[Interaction Matrix](INTERACTION_MATRIX.md) into a single view of **everything
important that local evidence does not yet close**. It is the answer to "what is
left before I can stop reviewing?"

```bash
arkheionx unresolved-map examples/blind-spot-fixture
arkheionx unresolved-map . --json
arkheionx unresolved-map . --out .arkheionx/unresolved-map
```

## What it shows

- **High-Impact Unresolved Surfaces** — surfaces with high/very-high criticality
  potential and an open evidence state (unresolved, insufficient-evidence,
  needs-human-review, unclassified), each with why it matters, the missing
  evidence, a suggested local test, and a priority.
- **High-Impact Unresolved Interactions** — high/very-high priority interactions
  with weak or no evidence.
- **Unclassified Surfaces** — important surfaces detected but not classifiable
  from local signals (not a verdict, a prompt to look closer).
- **Final Review Checklist** — which items must be checked, which to hand to an
  AI agent, which need manual code reading, which need Foundry or fuzz/invariant
  tests, and which must never be claimed.

The V6 thesis is *no high-impact surface should remain unclassified*. The
Unresolved Map is where you verify that: it makes the unknowns visible so a human
can close them deliberately instead of by accident.

## JSON

`--json` emits `schema_version`, `package_version`, `unresolved_surfaces`,
`unresolved_interactions`, `unclassified_surfaces`, `final_checklist`, `safety`,
and `human_review_required`.

## Flags

- `--json`, `--out <dir>`, `--no-write`, `--top <n>`.

## Safety

Local/static only. No RPC, no live-chain, no exploit automation, no severity.
Unresolved is not a finding and not a vulnerability — it is an open question for a
human. Human review is required.

## Related

- [`EVIDENCE_GRAPH.md`](EVIDENCE_GRAPH.md), [`INTERACTION_MATRIX.md`](INTERACTION_MATRIX.md),
  [`COMPLETE_REVIEW.md`](COMPLETE_REVIEW.md), [`V6_WORKFLOW.md`](archive/versions/V6_WORKFLOW.md).
