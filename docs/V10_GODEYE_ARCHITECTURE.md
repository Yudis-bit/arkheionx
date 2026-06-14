# V10 GodEye War Engine — Architecture (private, internal)

Internal codename: GodEye War Engine. Public-safe name: Semantic DeFi Review Engine.
This is an internal technical document. No hype, no guarantees, no public claims.
Arkheionx does not find all bugs; it reconstructs the economic machine, derives
candidate invariants, ranks attack candidates, and tells the researcher which are
worth proving. A human always makes the security call.

## Where it lives

V10 is additive and experimental. It does not change V9.1 behavior. It adds ten
packages under `arkheionx/` and one experimental CLI command, `arkheionx war-run`.
The stable surface and the V9.1 hunter engine are untouched.

## Layered pipeline

```
scope.yaml
   |
   v
[1] semantic core        arkheionx/semantic/   -> SemanticMap
[2] DeFi entity model    arkheionx/defi/        -> DefiEntityMap
[3] state transitions    arkheionx/state/       -> TransitionMap
[4] invariant engine     arkheionx/invariants/  -> InvariantSet (suspicious-here)
[5] attack graph         arkheionx/attack/      -> AttackGraph (candidates)
[9] root-cause memory    arkheionx/memory/      -> duplicate/scope annotation
[7] economic severity    arkheionx/severity/    -> SeverityVerdict per candidate
[5] ranking              arkheionx/attack/       -> ordered candidates
[6] PoC skeletons        arkheionx/pocgen/      -> Foundry .t.sol skeletons
[8] fork lab             arkheionx/forklab/     -> ForkRequirement (plan only)
[10] war-run             arkheionx/warrun/      -> artifacts + console verdict
```

The orchestrator order is: scope -> semantic -> entities -> transitions ->
invariants -> candidates -> memory/dedup -> severity gate -> ranking -> PoC
skeletons -> fork plan -> artifacts. Memory runs before the gate so a duplicate
can be killed; the gate runs before ranking so economic severity informs order.

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
`ext_before_write`, `balance_based_assets`), and hints at relevant invariant
families.

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
plus severity-cap comments. `compile_ready_level` is `requires_manual_fill` — the
skeletons are honest and do not claim to compile unmodified. No broadcast, no
signing keys; a fork skeleton reads its RPC endpoint from an env var name only.

## Layer 7 — Economic severity gate

`classify(candidate, scope, context)` applies the decision tree: reachability /
scope / dedup hard gates, then impact, cap, repeatability, gas, realism. It is
conservative: dust and 18-decimal-immune reconciliation is capped or killed,
trusted-role paths are `KILL_TRUSTED_ROLE`, buffer-capped consent is
`NEEDS_FORK_PROOF`. It never promotes an unproven candidate to a guaranteed
severity.

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
RELATED_BUT_DISTINCT / DISTINCT / UNKNOWN and marks out-of-scope contracts.

## Layer 10 — War-run

`run_war_run(...)` runs the pipeline and emits the artifact set (see
[`V10_GODEYE_ARTIFACTS.md`](V10_GODEYE_ARTIFACTS.md)) plus a concise console verdict.
No report is generated. Default operation is local/static with no RPC; fork support
is a plan only.

## Safety boundaries

Local/static; no RPC by default; no live-chain mutation; no broadcast; no signing
keys; no auto-submit; secrets redacted; fork is a plan only; no report until an
invariant is proven; human review required. An artifact guard rejects overclaiming
outcome strings.

## Deferred (not implemented now)

Full solc AST ingestion (interface only today), Slither/symbolic/SMT integration,
real fork execution inside Arkheionx, automatic proof execution, UI, and any remote
or network behavior. See the implementation plan note under `notes/`.
