# Senior Triage Mode

Private experimental mode. Local-only. Not part of the stable product surface, not a
release, not a site feature. This note lives under `docs/internal/` and is intended
for local use only.

```text
This mode does not confirm vulnerabilities.
This mode does not replace human review.
This mode does not submit reports.
This mode does not make RPC calls by default.
```

## Why it exists

`arkheionx review` answers "how should I review this repo?". Senior triage answers a
different question first:

```text
Is this repo / surface worth reviewing at all?
```

A senior researcher does not win by reading the most files; they win by choosing the
right battlefield. The guiding principle is:

```text
Do not prove what should not be pursued.
```

So senior triage runs *before* review and decides what is worth touching, what to
kill early, and what the top few leads are — instead of returning
`NO_CLEAN_CANDIDATE` after long work.

## Command

```bash
arkheionx triage . --scope-file scope.md --out .arkheionx/triage
```

With optional known material, prior audits, deployed addresses, and an explicit
freshness baseline:

```bash
arkheionx triage . \
  --scope-file scope.md \
  --known ./known \
  --audits ./audits \
  --addresses addresses.json \
  --baseline-ref v1.2.0 \
  --out .arkheionx/triage
```

`--json` prints the triage JSON to stdout. `--no-write` builds the pack in memory
only. Exit code is `0` when the target decision is `TOUCH`, otherwise `1`
(a heuristic warning, not a crash).

## Inputs

- `--scope-file` — local scope / program-rules note (read-only).
- `--known` — folder of known issues / prior findings / public reports.
- `--audits` — folder of prior audit reports (the freshness baseline).
- `--addresses` — addresses JSON for a static deployment-reality plan.
- `--baseline-ref` / `--since-date` — optional git freshness baseline.
- `--rpc-url` — optional read-only endpoint (advanced). Disabled by default; the
  endpoint is masked in output and never called live in this pass; the chain is
  never mutated.

If an input is missing, the relevant section is marked `NOT_PROVIDED`, `NOT_RUN`, or
`INSUFFICIENT_CONTEXT` rather than failing.

## Output pack

```text
.arkheionx/triage/
  00-target-decision.md
  01-bounty-eligibility.md
  02-known-issue-map.md
  03-freshness-diff.md
  04-deployment-reality.md
  05-lead-scoreboard.md
  06-top-3-leads.md
  07-do-not-touch.md
  08-next-commands.md
  09-agent-brief.md
  triage.json
  manifest.json
```

`triage.json` and `manifest.json` validate against `schemas/senior-triage.schema.json`
and `schemas/senior-triage-manifest.schema.json`.

## Decision vocabulary

- Target: `TOUCH`, `SKIP`, `NEEDS_MORE_CONTEXT`.
- Lead: `PURSUE`, `PARK`, `KILL`.
- Known issue: `UNKNOWN`, `NO_MATCH_FOUND`, `SIMILAR_KNOWN`, `LIKELY_DUPLICATE`,
  `DOCUMENTED_BEHAVIOR`, `ACKNOWLEDGED_RISK`, `OUT_OF_SCOPE`, `TRUSTED_ROLE_ONLY`,
  `PUBLIC_TEST_COVERED`.
- Freshness: `FRESH`, `STALE`, `UNKNOWN_FRESHNESS`, `POST_AUDIT_CHANGE`,
  `LIVE_MISMATCH`, `NEW_ADAPTER`, `NEW_REGISTRY_ENTRY`, `NEW_IMPLEMENTATION`,
  `NEW_MIGRATION_PATH`.
- Submit readiness: `NOT_READY`, `NEEDS_LOCAL_PROOF`, `NEEDS_DEDUP`,
  `NEEDS_SCOPE_CONFIRMATION`, `READY_FOR_REVIEW`, `DO_NOT_SUBMIT`.

Senior triage never emits a confirmed-vulnerability status, a "submit now" verdict,
or any guaranteed-severity wording.

## Scoring model

Each lead gets a 0-100 Research Priority Score. It is a time-allocation ranking, not a
severity and not a validity claim. Weights:

```text
scope_confidence        15
freshness               20
attacker_reachability   15
materiality             15
duplicate_risk (inverse)15
trusted_role_risk (inv) 10
proof_difficulty (inv)   5
time_cost (inverse)      5
```

Decision rules: `PURSUE` at score >= 75 and not blocked; `PARK` at 45-74 or when
context is missing; `KILL` below 45 or when blocked. Out-of-scope and
public-test-covered leads are forced to `KILL`. High duplicate risk caps the score
out of the `PURSUE` band. Trusted-role-only leads can never be `PURSUE`. Without a
scope file, nothing is `PURSUE`. Every score is explained with reasons and any caps
applied.

## Dedup before PoC

Known-issue mapping runs before any proof. It scans `--known`, `--audits`, and local
`test/`, `src/`, `docs/`, and changelog material, anchored on the contract name so an
acknowledgment or duplicate note has to sit near the actual surface. If a behavior is
already covered by a public test or an audit note, the lead is killed unless there is
a strong freshness angle. When uncertain, it uses `SIMILAR_KNOWN` rather than
overclaiming an exact duplicate. Without `--known` material, dedup confidence is
reported as LOW.

## Freshness before review

Freshness asks what changed since the last known review point. A stale,
heavily-audited surface is downranked; a fresh adapter, a new implementation, or a
value-bearing surface absent from the audit baseline is upranked. Git is used only
when a baseline is explicitly provided; otherwise freshness is inferred from local
filename and behavior signals and marked `UNKNOWN_FRESHNESS` when inference is weak.

## Deployment reality is optional

Deployment reality is local-first. Without `--addresses` it is `NOT_RUN`. With
addresses but no endpoint it produces a static verification plan (implementation
slot, proxy admin, registry, oracle, role holders, paused state, balances) plus
read-only command suggestions. If an endpoint is supplied, live read-only
verification is not implemented in this pass: the mode reports
`DEPLOYMENT_REALITY_NOT_IMPLEMENTED` and suggests safe read-only commands instead of
faking a live check. No live-chain call is made and the chain is never mutated.

## Safety boundaries

```text
No RPC by default.
No live-chain scanning by default.
No auto-submit.
No exploit automation.
No vulnerability confirmation.
Human review required.
```

The endpoint passed to `--rpc-url` is masked in every artifact and is never printed
verbatim. No private keys, seed phrases, or secrets are read.

## Real-world power v2

v2 makes the engine harder to fool when deployment, audit history, and known-issue
evidence disagree with source-only reading. New principle:

```text
Do not trust source-only analysis when deployment, audit history, and known-issue evidence disagree.
```

### Known corpus engine

`corpus_v2.py` builds line-indexed `CorpusDocument` records from `--known`,
`--audits`, repo docs/tests/source comments, README, CHANGELOG, and release notes.
Each document carries detected entities (contracts, functions, roles, assets,
oracles, adapters, registries, proxies), behavior tags, and known-status tags, plus
character-to-line mapping so evidence can cite `path:Lstart-Lend`. PDF text is
extracted only if a lightweight library is already importable; otherwise the file is
marked `UNPARSED_PDF_TEXT_EXTRACTION_UNAVAILABLE` (no OCR, never fails).

### Semantic dedup v2

`dedup_v2.py` combines token-shingle Jaccard similarity, contract-anchored behavior
overlap, and audit-status / public-test proximity into an explainable verdict with a
`similarity_score`, a `LOW/MEDIUM/HIGH` confidence ladder, located evidence, and
reasons. It is conservative: a duplicate verdict needs an explicit duplicate or
acknowledged signal near the surface, a neutral mention ("reviewed", "added after
audit") is not a duplicate, and broad-only behavior overlap is `SIMILAR_KNOWN`, never
`LIKELY_DUPLICATE`. `PUBLIC_TEST_COVERED`, high-confidence `LIKELY_DUPLICATE`,
`DOCUMENTED_BEHAVIOR`, and `OUT_OF_SCOPE` are hard kills.

### Audit baseline freshness

`freshness_v2.py` reads an audit-corpus baseline (and an audit date when parseable),
or an explicit `--baseline-ref` / `--since-date` git baseline. It adds
`NEW_ORACLE_PATH` and `NEW_VALUE_OUT_PATH`, attaches evidence (changed paths, audited
snippets), and downranks stale audited surfaces.

### Read-only deployment reality

`deployment_rpc.py` is a strictly read-only JSON-RPC client. It only issues an
allowlisted set of methods (`eth_chainId`, `eth_getCode`, `eth_getStorageAt`,
`eth_call`); any other method raises before a request is built. It never sends a
transaction, never signs, never needs a key, and makes no call unless `--rpc-url` is
explicitly provided. A transport can be injected so tests never touch the network.

### Proxy implementation checks

With `--addresses`, deployment reality reads the EIP-1967 implementation slot for
proxy entries and compares the live implementation to `expected_implementation`. A
difference is reported as `IMPLEMENTATION_CHANGED` / `LIVE_SOURCE_MISMATCH` and lifts
the lead's priority; an address with no code is `ADDRESS_NO_CODE` and kills a lead
that depends on it. A mismatch is a priority signal, not a confirmed bug.

### Fail-closed scoring

`scoring.py` v2 adds a `deployment_reality` dimension and a
`known_issue_confidence` dimension, hard boosts (verified mismatch on a value-bearing
contract, new value-out surface after baseline), and fail-closed caps: no scope means
no PURSUE; no known/audit material caps weak-dedup leads to PARK; addresses without
read-only RPC parks live-wiring-dependent leads; unknown freshness without a baseline
caps to PARK. `--strict-context` applies these caps more aggressively. A verified live
deployment mismatch is a clear-enough signal to bypass the soft caps.

### Mock RPC tests

`tests/test_senior_triage_deployment_rpc.py` and
`tests/test_senior_triage_realworld_power.py` use an injected mock transport. No test
touches the network. They assert the allowlist blocks state-changing methods, the
endpoint/API key is masked, EIP-1967 decoding works, a mismatch is detected, a no-code
address is flagged, an RPC failure does not crash triage, and no mutation method ever
appears in output.

## Limitations

- Dedup, freshness, and eligibility are heuristic, not exhaustive.
- Semantic duplicate detection is intentionally simple (shingles + anchored overlap,
  no LLM); confirm the root behavior by hand.
- Read-only deployment reality covers code existence, EIP-1967 implementation, and
  user-specified `eth_call` reads; it does not enumerate storage layouts or roles
  beyond what is asked, and `code_hash` is a local sha256 digest, not the on-chain
  keccak code hash.
- Freshness uses git only when a baseline is explicitly provided; otherwise it infers
  from the audit corpus and local signals and marks `UNKNOWN_FRESHNESS` when weak.
- A high score is a research-priority hint, not proof of a bug and not a payout. A
  deployment mismatch is a priority signal, not a vulnerability.
- A real bug can still be bounty-dead; senior triage tries to surface that early, but
  the human always makes the final call.
