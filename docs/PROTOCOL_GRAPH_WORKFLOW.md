# Protocol Graph Workflow (v3.8, in progress)

> Status: active v3.8.0 branch work, not a finalized or published release. This
> describes the **current internal** workflow of the Protocol Intelligence Core.
> It is local/static review tooling: not an audit, no confirmed vulnerabilities,
> no final severity, no audit-passed claim, and no bounty-eligibility claim.
> Manual review is always required.

This document describes how the v3.8 Protocol Intelligence Core composes a
protocol graph and connects it to the evidence, report, and review-package
layers. It is written to the **current state** of the code.

## Public CLI vs internal engine

Be precise about what is a public command today and what is internal library
behavior:

- **Public CLI today:** `arkheionx review-map` (and the focused commands
  `value-paths`, `assumptions`, `test-gap-map`, `proof-plan`, `evidence-links`),
  `arkheionx local-validate`, `arkheionx evidence`, `arkheionx report`, and
  `arkheionx review-package`.
- **Internal engine (no public CLI command in v3.8):** the function-role
  taxonomy, the value-path graph model, the assumption engine, the test-gap
  engine, the protocol graph builder, and the local-validation coverage
  correlator, all under `arkheionx/intelligence/`.

There is **no** `arkheionx graph` (or similar) command, and v3.8 ships **no**
public protocol-graph writer. The graph builder is composed in-process from
existing analysis / review-map output. The review package therefore includes
on-disk `.arkheionx/out/protocol-graph/` artifacts only when they already exist;
it never generates them. Do not assume a command exists for steps 2–7 below —
they are internal/library steps.

## Workflow

### 1. Generate baseline protocol intelligence artifacts

Run the existing review-map surface on an authorized local repository to produce
the baseline artifacts the core builds on:

```sh
arkheionx review-map .
arkheionx value-paths .
arkheionx assumptions .
arkheionx test-gap-map .
```

These write deterministic JSON/Markdown under `.arkheionx/out/review-map/`.

### 2. Classify function roles (internal)

The role engine assigns controlled review roles (for example `INFLOW`,
`ORACLE_CONSUMER`, `UPGRADE_PROXY`) to each function by boundary-aware token
matching — never substring or fuzzy matching. Roles are review surface only and
carry a stable, deterministic ID. This is internal; there is no public role CLI.

### 3. Build value paths (internal)

The value-path engine maps roles into controlled value-path kinds (for example
`VALUE_INFLOW`, `ORACLE_DEPENDENT_PATH`) with ordered segments. The mapping is
exact and non-inventive: fields stay empty unless explicit data is supplied.

### 4. Build assumptions (internal)

The assumption engine derives the protective assumptions each value path relies
on and records a support level (`ASSUMPTION_OBSERVED` through
`ASSUMPTION_TRACE_BOUND`, or `ASSUMPTION_NEEDS_HUMAN_REVIEW`). A higher support
level means more local context, never a proven-safe verdict.

### 5. Build test gaps (internal)

The test-gap engine records what is unproven and how to review it first, with a
gap status (for example `TEST_GAP_OPEN`, `TEST_GAP_LOCALLY_TESTED`) and a review
priority (`GAP_PRIORITY_*`). Priority is review order, never severity.

### 6. Build the protocol graph (internal)

The graph builder composes roles, value paths and segments, assumptions, and test
gaps into one deterministic graph of nodes and edges, then runs a deterministic
consistency-check layer. Edges link by exact ID / explicit alias only; a missing
target is an unresolved-reference warning. Duplicate IDs and dangling edges are
errors; orphan nodes, ambiguous aliases, and unresolved references are warnings.
A `ready_for_submission` true flag, a `HUMAN_REVIEWED` token, or forbidden
finality wording is a safety error.

### 7. Correlate local-validation support (internal)

When explicit local-validation result IDs and trace-receipt IDs are supplied
(from saved Foundry output ingested by `arkheionx local-validate`), the coverage
correlator connects them to graph test gaps as supporting context:
`COVERAGE_TESTED` (a result ID was linked) or `COVERAGE_TRACE_BOUND` (a trace
receipt was linked). Tested does not mean safe; trace-bound does not mean proven.

### 8. Attach graph context to evidence/report

When a graph and/or coverage summary is supplied, `arkheionx evidence` and
`arkheionx report` can carry an optional `protocol_graph_context` block (counts
and linked IDs) as additional supporting context:

```sh
arkheionx evidence . --target Contract.function
arkheionx report . --target Contract.function
```

The block is additive and optional. Evidence readiness is unchanged, the
trace-bounded `EVIDENCE_READY` rule is preserved, and the report stays a draft
needing human review.

### 9. Package graph artifacts in the review package

If `.arkheionx/out/protocol-graph/` artifacts exist, the review package includes
them automatically:

```sh
arkheionx review-package . --json
arkheionx review-package . --export zip --json
```

Graph artifacts are optional and never required for readiness. They are added to
the manifest, checksum map, and deterministic export; their JSON, checksums, and
paths are validated; their IDs are cross-referenced by exact match only; and any
overclaim is a safety failure. Unresolved cross-references are warnings.

### 10. Human review

A human reviewer reads the graph context, the validation output, and the
artifacts, and decides. Nothing in the workflow finalizes a security conclusion:
`manual_review_required` stays true and `ready_for_submission` stays false
throughout.

## Determinism

Every engine produces stable IDs from a canonical seed with no timestamp and no
randomness, so repeating the workflow over the same input yields identical IDs
and a byte-identical deterministic review-package export.

## Safety boundary

Local and static only: no RPC, no fork-url behavior, no live-chain calls, no
private keys, no seed phrases, no transaction broadcasting, no exploit
automation, and no auto-submit. No confirmed vulnerabilities, no final severity,
no audit-passed claim, and no bounty-eligibility claim. Graph consistency does
not prove safety and a graph warning does not prove a vulnerability. Manual review
is required; `ready_for_submission` stays false.

## Related docs

- [`PROTOCOL_INTELLIGENCE_CORE.md`](PROTOCOL_INTELLIGENCE_CORE.md)
- [`PROTOCOL_GRAPH_SMOKE_TEST.md`](PROTOCOL_GRAPH_SMOKE_TEST.md)
- [`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md)
- [`LOCAL_VALIDATION.md`](LOCAL_VALIDATION.md)
