# V10 GodEye War Engine — Architecture (private, internal)

Internal codename: GodEye War Engine. Public-safe name: Semantic DeFi Review Engine.
This is an internal technical document. No hype, no guarantees, no public claims.
Arkheionx does not find all bugs; it reconstructs the economic machine, derives
candidate invariants, ranks attack candidates, and tells the researcher which are
worth proving. A human always makes the security call.

## Where it lives

V10 is additive and experimental. It does not change V9.1 behavior. It adds ten
packages under `arkheionx/` and two experimental CLI commands, `arkheionx war-run`
and `arkheionx memory`. The stable surface and the V9.1 hunter engine are untouched.
The internal benchmark (`docs/V10_GODEYE_BENCHMARK.md`) is 9/9 PASS on generic
synthetic fixtures.

## Layered pipeline

```
scope.yaml
   |
   v
[1] semantic core        arkheionx/semantic/   -> SemanticMap (+ taint findings)
[2] DeFi entity model    arkheionx/defi/        -> DefiEntityMap
[3] state transitions    arkheionx/state/       -> TransitionMap (+ contradictions)
[4] invariant engine     arkheionx/invariants/  -> InvariantSet (suspicious-here)
[5] attack graph         arkheionx/attack/      -> AttackGraph (candidates)
[9] root-cause memory    arkheionx/memory/      -> duplicate/scope annotation (+ CLI)
[7] economic severity    arkheionx/severity/    -> SeverityVerdict + SeverityScore
[5] ranking              arkheionx/attack/       -> ordered candidates
[6] PoC skeletons        arkheionx/pocgen/      -> Foundry .t.sol skeletons
[8] fork lab             arkheionx/forklab/     -> ForkRequirement (plan only)
[10] war-run             arkheionx/warrun/      -> quality gates + artifacts + verdict
```

The orchestrator order is: scope -> semantic (+ taint) -> entities -> transitions
(+ contradictions) -> invariants -> candidates -> memory/dedup -> severity gate ->
ranking -> PoC skeletons -> fork plan -> secret scan -> quality gates -> artifacts.
Memory runs before the gate so a duplicate can be killed; the gate runs before
ranking so economic severity informs order; quality gates run last and downgrade any
SUBMIT candidate that slipped past a hard gate.

## Layer 1 — Semantic core (fallback primary)

`build_semantic_map(root)` discovers `.sol` files, then parses them. AST mode is a
pluggable interface (`ast_loader`): it detects solc / Foundry artifacts and, when
ingestion is unavailable, returns nothing so the fallback parser runs. The fallback
parser (`fallback_parser`) is the primary path today. It blanks comments and string
literals while preserving every newline (so line numbers stay accurate), then uses
brace/paren matching to recover contracts, inheritance, state variables,
structs/enums/events/modifiers, and functions with their effects: internal/external
calls, storage reads/writes (alias-aware for `T storage p = stateVar[...]`), events,
transfers, low-level calls, calldata field access, msg.sender/value use, and role
gates. Cross-cutting engines derive the call graph, storage-access map, external
calls with state-write ordering (reentrancy relevance), and the calldata->sink data
flow. The critical capability is detecting counterparty-controlled calldata reaching
a value path (the swap-route tag). Every fact carries a confidence; fallback mode is
medium confidence by design.

**Named taint detectors** (`semantic/detectors.py`) sit on top of the dataflow hints
and bodies and surface attacker-controlled / external-return flows into value sinks
as first-class findings: `CALLDATA_TO_SWAP_ROUTE`, `CALLDATA_TO_REFUND_AFFECTING_ROUTE`,
`CALLDATA_NOT_IN_HASH_BUT_IN_VALUE_SINK` (the consent-gap detector),
`CALLDATA_TO_HASH_INPUT`, `CALLDATA_TO_TRANSFER_AMOUNT`, `ORACLE_RETURN_TO_BORROW_LIMIT`,
`CREDIT_WRITE_FROM_NOMINAL_AMOUNT`, `ADAPTER_RETURN_TO_CREDIT`,
`MESSAGE_ID_TO_MINT_WITHOUT_CONSUME`, `MSG_SENDER_TO_COLLATERAL_OWNER`, and
`STATUS_WRITE_AFTER_EXTERNAL_CALL`. Each names a source, a sink, the likely invariant
family, the attacker role, and any missing binding.

## Layer 2 — DeFi entity model

`build_defi_entities(smap)` classifies symbols (contract names, state vars,
functions, struct names and fields) into economic entities (Asset, Share, Loan,
Debt, Collateral, Tranche, Lender, Borrower, Deposit, Refund, Fee, Vault, Adapter,
OraclePrice, ...) using ordered name/shape rules. Confidence rises with independent
evidence.

## Layer 3 — State transitions

`build_transitions(smap, emap)` builds a before/action/after transition per
value-affecting entry function. It folds the effects of directly-called internal
helpers into the entry point via a bounded closure, infers the actor, lifecycle,
assets in/out, and status changes, raises flags (`has_division`, `calldata_route`,
`ext_before_write`, `balance_based_assets`, and the shape flags
`credit_no_balance_delta`, `oracle_value_math` / `oracle_hardcoded_scale`, and
`xchain_overmint`), and hints at relevant invariant families. The shape flags attach
a family from semantics rather than the function name, so an adapter `deposit`, an
oracle-reading `borrow`, or a bridge `receiveMessage` reach the right invariant.

**State-machine contradictions** (`state/contradictions.py`) read the transitions
and name broken-lifecycle states: `REPAID_BUT_LENDER_NOT_SETTLED`,
`COLLATERAL_RELEASED_WITH_DEBT`, `CREDIT_EXCEEDS_ACTUAL_RECEIVED`,
`ORACLE_DECIMAL_MISMATCH` / `ORACLE_PRICE_ACCEPTED_STALE`,
`MESSAGE_PROCESSED_NONCE_NOT_CONSUMED`, `DESTINATION_MINT_EXCEEDS_SOURCE_LOCK`,
`DEPOSIT_CONSUMED_STILL_WITHDRAWABLE`, `ZERO_SHARES_FOR_NONZERO_ASSETS`, and more —
each pointing at the transition, the likely invariant, the PoC family, and a
severity hint.

## Layer 4 — Invariant engine

`build_invariants(smap, emap, tmap)` instantiates one of nine invariant templates
per transition hint and evaluates whether it is *suspicious here* using semantic
signals (flags, data flow, entity context, raw-body ordering). A suspicious
invariant is a breakage hypothesis with explicit reasons. This is the "no finding
until an invariant breaks" gate: only suspicious invariants become candidates.

## Layer 5 — Attack graph + ranking

`build_candidates(...)` turns each suspicious invariant into an attack candidate
(attacker, victim, asset, entry point, call sequence, broken invariant, required
conditions, proof strategy, fork need), and additionally emits a candidate for a
role-gated value-moving transition so the access-control case reaches the gate and
is killed. `ranking.rank()` orders candidates by realistic value, using the
economic-severity verdict when present and a family base plus penalties otherwise.

## Layer 6 — PoC skeletons

`build_skeletons(graph, smap)` writes a Foundry `.t.sol` skeleton per top candidate:
actors, setup, action sequence, and assertions that falsify the broken invariant,
plus severity-cap comments. Each skeleton carries an economic-severity line, an
EXPECTED-violation comment (the assertion should fail on the vulnerable target), a
MANUAL FILL marker, and — for fork skeletons — a secret-redaction note. Two honesty
fields ride along: `compile_ready_level` stays `requires_manual_fill`, and a separate
`compile_readiness` ladder is at most `near_compile` (a structured family with named
actors/actions/assertions) and never `compile_likely` / `fixture_tested_compile` —
we never claim a skeleton compiles or passes without an executed test. No broadcast,
no signing keys; a fork skeleton reads its RPC endpoint from an env var name only.

## Layer 7 — Economic severity gate

`classify(candidate, scope, context)` applies the decision tree: reachability /
scope / dedup hard gates, then impact, cap, repeatability, gas, realism. It is
conservative: dust and 18-decimal-immune reconciliation is capped or killed,
trusted-role paths are `KILL_TRUSTED_ROLE`, buffer-capped consent is
`NEEDS_FORK_PROOF`. It never promotes an unproven candidate to a guaranteed
severity.

Each verdict carries a typed breakdown — `impact_type` (e.g. `DIRECT_THEFT`,
`ORACLE_OVERBORROW`, `CROSS_CHAIN_OVERMINT`, `DUST_ONLY`), `cap_type` (e.g.
`UNCAPPED`, `ROUNDING_UNIT_CAPPED`, `DEPOSIT_BUFFER_CAPPED`), `proof_quality`
(`STATIC_ONLY` / `LOCAL_POC_SKELETON` / `FORK_PLAN_ONLY` / `MANUAL_REVIEW_REQUIRED`)
— and an explainable numeric `SeverityScore` (impact / likelihood / realism / proof /
repeatability scores; cap / scope / duplicate penalties) so a label can be read as
"high impact, but rounding-unit capped and only a local skeleton, so Low." A
`PARK_INCOMPLETE` gate downgrades any SUBMIT_* candidate missing
attacker/victim/asset/invariant.

**Severity label glossary (what to do):** `SUBMIT_{CRITICAL,HIGH,MEDIUM}_CANDIDATE`
= worth a PoC and submission consideration at that level; `SUBMIT_LOW_ONLY` /
`VALID_BUT_LOW` / `VALID_BUT_LOW_LIKELIHOOD` = technically valid but economically
capped, submit only if the program accepts low; `NEEDS_LOCAL_POC` /
`NEEDS_FORK_PROOF` / `NEEDS_REAL_ASSET_PROOF` / `NEEDS_CAPTURE_PROOF` = prove the
named thing before deciding; `PARK_{CONTEXT,THEORY,REACHABILITY,INCOMPLETE}` = hold
pending more context; `KILL_{DUST,SELF_GRIEF,TRUSTED_ROLE,ADMIN_ONLY,OUT_OF_SCOPE,
DUPLICATE_ROOT_CAUSE,NOT_REACHABLE,EXPECTED_DESIGN}` = do not pursue. A label is
review guidance, never a confirmed vulnerability or a guaranteed payout.

## Layer 8 — Fork lab

`build_fork_plan(graph, smap, scope)` decides which candidates need fork proof and
what that proof must verify, inferring the chain from scope and the matching RPC env
var name. It never writes a URL or a key into an artifact, always sets
`do_not_broadcast`, and a redaction pass scrubs any URL/key-like text.

## Layer 9 — Root-cause memory

`MemoryStore` persists prior findings/kills/parks/out-of-scope as JSON. The
root-cause hash is semantic (invariant family + function role + attacker category),
so the same root cause on a different pool hashes the same while a different bug
hashes differently. The dedup classifier annotates candidates SAME_ROOT_CAUSE /
RELATED_BUT_DISTINCT / DISTINCT / UNKNOWN and marks out-of-scope contracts. The
`arkheionx memory` command (`add` / `list` / `classify` / `export`) operates the
store from the CLI: record a prior root cause, list the corpus, classify a candidate,
or export the shareable semantic fingerprint with the private `notes` field redacted.
The same root cause on a different pool classifies the same; an empty store is UNKNOWN.

## Layer 10 — War-run

`run_war_run(...)` runs the pipeline and emits the artifact set (see
[`V10_GODEYE_ARTIFACTS.md`](V10_GODEYE_ARTIFACTS.md)) plus a concise console verdict.
No report is generated. Default operation is local/static with no RPC; fork support
is a plan only.

Before output it runs **quality gates** (`warrun/quality_gates.py`): a verification
pass — REQUIRED_FIELDS, NO_REPORT, NO_SECRET, NO_DUST_HIGH, NO_TRUSTED_ROLE_SUBMIT,
NO_DUPLICATE_SUBMIT, NO_SCOPE_SUBMIT, FORK_DEPENDENCY, PROOF_QUALITY, HUMAN_REVIEW —
each pass/warn/fail with the affected candidates. A hard-gate failure downgrades the
offending SUBMIT candidate (defense-in-depth; the economic gate enforces these
upstream). Every JSON artifact is then stamped with a standard header
(`schema_version`, `engine_version`, `generated_at`, `target_label`, `target_hash`,
`semantic_mode`, `confidence`, `warnings`, `artifact_type`) and the manifest lists
every artifact with its type, path, generated flag, and warning count.

## Safety boundaries

Local/static; no RPC by default; no live-chain mutation; no broadcast; no signing
keys; no auto-submit; secrets redacted; fork is a plan only; no report until an
invariant is proven; human review required. An artifact guard rejects overclaiming
outcome strings.

## Deferred (not implemented now)

Full solc AST ingestion (interface only today), Slither/symbolic/SMT integration,
real fork execution inside Arkheionx, automatic proof execution, UI, and any remote
or network behavior. See the implementation plan note under `notes/`.
