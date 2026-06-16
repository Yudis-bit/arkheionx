# Interaction Matrix (v6)

> Interaction candidates are not vulnerabilities. Interaction priority is not
> severity. This is a local/static review artifact. Human review is required.

The Interaction Matrix is the second V6 capability. Where the
[Evidence Graph](EVIDENCE_GRAPH.md) classifies individual surfaces, the
Interaction Matrix detects **meaningful combinations of surfaces** that may hide
bugs when tested together — the bugs that live between two functions, not inside
one.

```bash
arkheionx interaction-matrix examples/blind-spot-fixture
arkheionx interaction-matrix . --json
arkheionx interaction-matrix . --out .arkheionx/interaction-matrix
arkheionx interaction-matrix . --only-unresolved
```

## Why interactions

A single function can be fully tested and still combine dangerously with another:
a value-exit path that also makes an external call (reentrancy ordering), a
liquidation path that depends on an oracle (stale price), a signed claim that
relies on a nonce (replay), a periphery route that must match the core path. The
matrix surfaces these combinations and scores how much review attention each one
deserves.

It does not generate every possible pair. It filters to meaningful combinations
where at least one side is high-impact and the combination is value-relevant.

## Interaction classes

The matrix detects or infers classes including:

- value-exit × authorization / external-call / share-accounting / fee / blocklist
- deposit × share-math, share-math × donation, preview × actual-execute
- liquidation × oracle, liquidation × bad-debt, oracle × decimals
- signature × nonce, signature × deadline, signature × Merkle, Merkle × amount
- accounting × periphery, periphery × direct-call-equivalence, callback × state-order
- external-call × accounting-update, loop × external-call, connector × vault-accounting
- admin × emergency, upgrade × init, pause × withdraw, blocklist × transfer,
  fee × share-accounting, lifecycle × authorization

## Interaction evidence

Each interaction (`IX-001`, `IX-002`, ...) records:

- `surfaces`, `contracts`, `functions`, `source_refs`
- `interaction_class`, `why_combination_matters`
- `criticality_potential`, `review_density`
- `evidence_state`, `evidence_strength`, `tests_detected`
- `interaction_priority` and its score components
- `missing_test_direction`, `suggested_invariant`, `suggested_counterfactual`,
  `stop_condition`
- `human_review_required` (always true)

The interaction's evidence state is derived from the weakest evidence among its
surfaces: even if both sides are individually tested, the *combination* is rarely
proven, so it is only `tested` when both sides have strong evidence.

## Scoring (transparent and additive)

```text
interaction_priority = impact_score + review_gap_score + interaction_complexity_score
```

- **impact_score** sums the impact dimensions the interaction *defines* (value
  exit +25, accounting +20, authorization +20, liquidation +20, oracle +18,
  external call/callback +15, periphery/core +15, admin/emergency +12,
  connector +12, share/fee +12, lifecycle/upgrade +10, cross-contract +10).
- **review_gap_score** reflects the weakest constituent evidence (no evidence
  +30, weak +20, medium +10, strong +0).
- **interaction_complexity_score** adds structural difficulty (cross-contract
  +15, external call +12, periphery +10, lifecycle +10, signature/Merkle +10,
  oracle/accounting +10, loop/batch +8).

Labels: `85+` very-high, `65-84` high, `40-64` medium, below `40` monitor. This
is **interaction priority**, a heuristic review order — never a severity.

## Output sections

- **Boundary** — the safety boundary, restated.
- **Matrix Summary** — total, high-impact, unresolved, tested, weak-evidence
  interactions, and the classes detected.
- **Top Interactions** — each interaction with its score, evidence, and guidance.
- **Untested High-Impact Interactions** — high/very-high priority with weak or no
  evidence: inspect first.
- **Interaction Test Plan** — for each high-priority unresolved interaction: a
  pre-state, action, assertion, evidence needed, and rejection condition.

## Flags

- `--json`, `--out <dir>`, `--no-write`, `--top <n>`, `--only-unresolved`.

## Safety

Local/static only. No RPC, no live-chain, no exploit automation, no severity. An
interaction candidate is a review prompt, not a vulnerability. Human review is
required.

## Related

- [`EVIDENCE_GRAPH.md`](EVIDENCE_GRAPH.md), [`UNRESOLVED_MAP.md`](UNRESOLVED_MAP.md),
  [`COMPLETE_REVIEW.md`](COMPLETE_REVIEW.md), [`V6_WORKFLOW.md`](archive/versions/V6_WORKFLOW.md).
