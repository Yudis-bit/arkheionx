# Protocol Intelligence Core (v3.8, in progress)

> Status: active v3.8.0 branch work, not a finalized or published release. The
> Protocol Intelligence Core is local/static review tooling. It is not an audit,
> does not replace a human reviewer, and makes no confirmed-vulnerability,
> final-severity, audit-passed, or bounty-eligibility claim. `v3.8.0` is not
> tagged, pushed, or published here.

The v3.8 **Protocol Intelligence Core** is the internal engine layer that turns
the structure Arkheionx already extracts from a local repository into one
deterministic, connected review surface: function roles, value paths,
assumptions, test gaps, a protocol graph, and local-validation coverage
correlation. Higher layers (evidence, report, and the review package) can carry
this surface as additional supporting context for a human reviewer.

It is "machine leverage" in a deliberately narrow sense: it organizes and
connects review context deterministically so a person can review faster. It does
not decide anything.

## 1. What the Protocol Intelligence Core Is

- An internal, additive set of modules under `arkheionx/intelligence/`.
- A function-role taxonomy, a value-path graph model, an assumption engine, a
  test-gap engine, a protocol graph builder, and a local-validation coverage
  correlator.
- Deterministic: every record carries a stable ID derived from a canonical seed,
  with no timestamp and no randomness, so identical input yields identical output.
- Exact-only: every link is made by exact ID or an explicit alias. There is no
  fuzzy matching and no substring matching, and no link is invented.
- Review surface only: every record keeps `manual_review_required` true and
  `ready_for_submission` false, and never emits a `HUMAN_REVIEWED` status.

## 2. What the Protocol Intelligence Core Is Not

- It is **not** an AI auditor and not an autonomous auditor.
- It is **not** a replacement for human review or for a human auditor.
- It does **not** confirm vulnerabilities.
- It does **not** assign a final severity.
- It does **not** claim an audit passed.
- It makes **no** bounty-eligibility claim.
- A graph warning does **not** prove a vulnerability.
- Graph consistency does **not** prove protocol safety.
- A passing local test does **not** prove safety.
- A missing or open test gap does **not** prove a vulnerability.
- It adds **no** new public CLI command and changes no existing CLI output.

Priority and ordering throughout the core are **review ordering**, never a
severity ranking. A classification's `confidence` reports that the engine
produced a structural classification; it is never security confidence.

## 3. Function Role Taxonomy

The role engine assigns controlled, descriptive review roles to a Solidity
function from its name and signature using boundary-aware token matching (never
substring or fuzzy matching). The controlled roles are:

`INFLOW`, `OUTFLOW`, `ACCOUNTING_MUTATION`, `EXTERNAL_CALL`, `ORACLE_CONSUMER`,
`ORACLE_SETTER`, `ADMIN_PARAM`, `ACCESS_CONTROL`, `PAUSE_EMERGENCY`,
`UPGRADE_PROXY`, `DELEGATECALL`, `BORROW_REPAY`, `LIQUIDATION`, `SWAP`,
`MINT_BURN`, `CLAIM_REWARD`, `BRIDGE`, and `VIEW_PURE`, plus `UNCLASSIFIED` when
nothing controlled matches (`UNCLASSIFIED` never implies safety).

A stable role priority orders the output for review; it is not a severity. Role
IDs are deterministic.

## 4. Value Path Graph Model

The value-path engine turns roles into structured, deterministic value paths and
their ordered segments. The controlled value-path kinds are:

`VALUE_INFLOW`, `VALUE_OUTFLOW`, `ACCOUNTING_MUTATION_PATH`, `EXTERNAL_CALL_PATH`,
`ORACLE_DEPENDENT_PATH`, `AUTHORITY_PATH`, `EMERGENCY_PATH`, `UPGRADE_PATH`,
`LIQUIDATION_PATH`, `SWAP_PATH`, `BRIDGE_PATH`, `REWARD_PATH`, `VIEW_ONLY_PATH`,
and `UNCLASSIFIED_PATH`.

Mapping from roles is exact and non-inventive: assets, oracle sources, external
targets, and state variables stay empty unless explicit data is supplied, and an
ambiguous mapping records a warning rather than guessing.

## 5. Assumption Engine

The assumption engine derives the protective assumptions a value path relies on
and tracks how well each is supported. Support levels are:

`ASSUMPTION_OBSERVED`, `ASSUMPTION_CLASSIFIED`, `ASSUMPTION_LINKED`,
`ASSUMPTION_TESTED`, `ASSUMPTION_TRACE_BOUND`, and
`ASSUMPTION_NEEDS_HUMAN_REVIEW`. A higher support level means more local context
exists, never that the assumption is proven safe.

## 6. Test Gap Engine

The test-gap engine records what is unproven today and how to review it first.
Gap statuses are `TEST_GAP_OPEN`, `TEST_GAP_PARTIALLY_COVERED`,
`TEST_GAP_LOCALLY_TESTED`, `TEST_GAP_TRACE_BOUND`, `TEST_GAP_NEEDS_HUMAN_REVIEW`,
and `TEST_GAP_UNCLASSIFIED`. Gap priority (`GAP_PRIORITY_UNKNOWN`, `_LOW`,
`_MEDIUM`, `_HIGH`, `_CRITICAL_REVIEW`) is review priority, never severity. A
`LOCALLY_TESTED` or `TRACE_BOUND` gap is supported by context only; it is not a
resolved or safe verdict.

## 7. Protocol Graph Builder

The graph builder composes roles, value paths and segments, assumptions, and test
gaps into one deterministic graph of nodes and edges, plus a deterministic
consistency-check layer. Node kinds include `GRAPH_NODE_FUNCTION_ROLE`,
`GRAPH_NODE_VALUE_PATH`, `GRAPH_NODE_VALUE_PATH_SEGMENT`, `GRAPH_NODE_ASSUMPTION`,
`GRAPH_NODE_TEST_GAP`, `GRAPH_NODE_LOCAL_VALIDATION`, `GRAPH_NODE_TRACE_RECEIPT`,
`GRAPH_NODE_EVIDENCE_REF`, `GRAPH_NODE_REPORT_REF`, and `GRAPH_NODE_UNKNOWN`.

Edges connect concepts by exact ID or explicit alias only; a missing target is an
unresolved-reference warning, never a fabricated link. The consistency checks
treat a duplicate ID or a dangling edge as an error, and an orphan node, an
ambiguous alias, or an unresolved reference as a warning. A `ready_for_submission`
true flag, a `HUMAN_REVIEWED` token, or forbidden finality wording anywhere in
the graph is a safety error. No check proves safety, and no warning proves a
vulnerability.

## 8. Local-Validation Coverage Correlation

The coverage correlator connects explicitly linked local-validation result IDs
and trace-receipt IDs to protocol-graph test gaps (and, through them, to function
roles, value paths, and assumptions) as supporting context. `COVERAGE_TESTED`
means a local-validation result ID was explicitly linked; `COVERAGE_TRACE_BOUND`
means a trace-receipt ID was explicitly linked. Neither means anything is safe,
proven, confirmed, final, or audit-passed. Correlation is exact-ID / explicit
alias only and invents no coverage, no local-validation ID, and no trace-receipt
ID.

## 9. Evidence and Report Graph Context

Evidence packages and report drafts can carry an optional
`protocol_graph_context` block summarizing the graph and coverage (counts and
linked IDs) as additional supporting context. This is additive and optional: a
missing block is not an error, evidence readiness is unchanged, and the
trace-bounded `EVIDENCE_READY` rule is preserved. The block never finalizes a
conclusion and never emits a `HUMAN_REVIEWED` status. See
[`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md) and
[`REPORT_DRAFTS.md`](REPORT_DRAFTS.md).

## 10. Review-Package Protocol Graph Inclusion

When protocol-graph artifacts already exist under
`.arkheionx/out/protocol-graph/`, the review package discovers, classifies,
validates, cross-references, and exports them as **optional** artifacts — never
required for readiness. The validation enforces JSON parseability, path safety,
checksum integrity, and the no-overclaim boundary; cross-references resolve by
exact ID / explicit alias only. See [`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md) and
[`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md).

## 11. Exact-Only Linking and Deterministic IDs

Every engine links by exact ID or an explicit alias only. There is no fuzzy
matching and no substring matching, and an unresolved reference is recorded as a
warning rather than turned into a fabricated link. IDs are deterministic SHA-256
digests over a canonical, sorted seed, with no timestamp and no randomness:

- `protocol-graph-node:<kind>:<hash>`
- `protocol-graph-edge:<kind>:<hash>`
- `protocol-graph-check:<kind>:<hash>`
- `protocol-intelligence-graph:<name>:<hash>`
- `local-validation-coverage:<hash>`
- `local-validation-coverage-summary:<name>:<hash>`

Repeating a build over the same input yields identical IDs.

## 12. Safety Boundary

- Local and static only; no RPC, no fork-url behavior, and no live-chain calls.
- No private keys and no seed phrases.
- No transaction broadcasting and no exploit automation.
- No auto-submit and no automatic `HUMAN_REVIEWED` status.
- No confirmed vulnerabilities and no final severity.
- No audit-passed claim and no bounty-eligibility claim.
- Graph consistency does not prove safety; a graph warning does not prove a
  vulnerability; a passing local test does not prove safety; a missing test does
  not prove a vulnerability.
- `manual_review_required` is true and `ready_for_submission` is false. Manual
  review is always required.

## 13. Related Docs

- [`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md) — the end-to-end
  internal workflow.
- [`PROTOCOL_GRAPH_SMOKE_TEST.md`](PROTOCOL_GRAPH_SMOKE_TEST.md) — local/offline
  verification.
- [`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md) — review-package protocol-graph
  inclusion.
- [`LOCAL_VALIDATION.md`](LOCAL_VALIDATION.md) — saved Foundry-output ingestion.
- [`REVIEW_MAP.md`](REVIEW_MAP.md) — the review-map surface the core builds on.
- [`ROADMAP.md`](ROADMAP.md) and [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md).
