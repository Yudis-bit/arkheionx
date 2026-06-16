# Evidence Graph (v6)

> Local/static review artifact. Evidence state is not a vulnerability claim.
> Confirmed-candidate is not a confirmed vulnerability. Unresolved does not mean
> vulnerable. Human review is required.

V5 shows where to look. **V6 shows what is proven, what is unresolved, and which
interactions still lack evidence.** The Evidence Graph is the first of the two V6
capabilities: it classifies every important review surface into an **evidence
state** so no high-impact surface is left silently unclassified.

```bash
arkheionx evidence-graph examples/blind-spot-fixture
arkheionx evidence-graph . --json
arkheionx evidence-graph . --out .arkheionx/evidence-graph
arkheionx evidence-graph . --only-unresolved
```

## What it answers

V4 maps value flow. V5 ranks likely blind spots. The Evidence Graph answers a
different question for each surface a reviewer cares about:

- Which important surfaces actually have meaningful local test evidence?
- Which surfaces only *look* tested but lack the right evidence?
- Which high-impact surfaces are unresolved?
- What evidence is missing, and what local test would close the gap?

It does not predict bugs, assign severity, or confirm vulnerabilities.

## Evidence node

Each reviewable surface becomes one evidence node (`EV-001`, `EV-002`, ...). A
node records, all heuristically and locally:

- `surface_id`, `contract`, `function`, `source_file`, `source_line`
- `surface_type` (value-entry, value-exit, accounting, authorization, oracle,
  liquidation, periphery, callback-external, admin-emergency, lifecycle,
  share-math, blocklist, fee, connector, review-surface)
- `criticality_potential` (heuristic blast radius, **not** severity)
- `review_density`, `blind_spot_priority`
- `assumptions`, `counterfactuals`, `proof_plan_links`, `hypothesis_links`
- `tests_detected`, `invariants_detected`, `fuzz_detected`
- `evidence_state`, `evidence_strength`, `confidence`
- `why_state`, `unresolved_reason`, `missing_evidence`, `next_test_direction`
- `human_review_required` (always true)

## Evidence state

Every node is classified into exactly one evidence state. None of them is a
vulnerability claim:

| State | Meaning |
| --- | --- |
| `tested` | A direct local test exists on a structurally simple surface. |
| `rejected-with-evidence` | A local hypothesis log records this as tested and rejected with evidence. |
| `confirmed-candidate` | Local evidence marks a candidate. **This is not a confirmed vulnerability** — human review required. |
| `unresolved` | A high-impact surface has weak, missing, or unclear evidence. |
| `insufficient-evidence` | Tests exist but do not prove the relevant assumption or counterfactual. |
| `needs-human-review` | Ambiguous or shallow evidence on a high-impact surface (the "looks tested" trap). |
| `unclassified` | A surface was detected but cannot be assigned a stronger state. |
| `out-of-scope` | Only when explicitly configured or marked. |

`rejected-with-evidence` and `confirmed-candidate` are **never inferred from
scoring**. They are only assigned when an explicit local hypothesis log (with a
recorded local test) says so. In a default static run they are simply absent —
the honest result.

## Evidence strength

| Strength | Meaning |
| --- | --- |
| `strong` | Direct evidence addresses the relevant counterfactual or assumption. |
| `medium` | Evidence touches the surface but may not cover all important edges. |
| `weak` | Evidence exists but is indirect, shallow, or not focused. |
| `none` | No meaningful local evidence was found. |
| `unknown` | Could not classify evidence quality. |

A single file-level test reference on a high-impact surface is `medium` strength
at best — which is why such surfaces land in `needs-human-review`, not `tested`.
This is the core V6 improvement over "the file is referenced, so it's covered".

## Output sections

The Markdown report (and `--json`) include:

- **Boundary** — the safety boundary, restated.
- **Repository Summary** — contracts, functions, value paths, assumptions, test
  gaps, evidence node count, high-impact surface count, unresolved count.
- **Evidence State Summary** — counts per state.
- **Evidence Nodes** — every classified surface.
- **High-Impact Unresolved Surfaces** — criticality high/very-high with an open
  evidence state.
- **Evidence Gaps** — categories of missing evidence (no-direct-test,
  no-invariant, no-fuzz, no-pre-post-balance-check, no-negative-path-test, ...).
- **Human Review Checklist** — what a human must confirm.

## Flags

- `--json` — print machine-readable JSON to stdout only.
- `--out <dir>` — write `evidence-graph.md` and `evidence-graph.json`.
- `--no-write` — build in memory only.
- `--top <n>` — number of top review targets to consider.
- `--only-unresolved` — show only surfaces in an open evidence state.

## Safety

Local/static only. No RPC, no live-chain calls, no private keys, no exploit
automation, no severity. An evidence state is not a vulnerability claim. Human
review is required for every conclusion. See
[`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md).

## Related

- [`INTERACTION_MATRIX.md`](INTERACTION_MATRIX.md) — the second V6 capability.
- [`UNRESOLVED_MAP.md`](UNRESOLVED_MAP.md) — everything still unresolved.
- [`COMPLETE_REVIEW.md`](COMPLETE_REVIEW.md) — the headline V6 package.
- [`V6_WORKFLOW.md`](archive/versions/V6_WORKFLOW.md) — the end-to-end V6 workflow.
- [`BLIND_SPOT_INTELLIGENCE.md`](BLIND_SPOT_INTELLIGENCE.md) — the V5 layer V6 builds on.
