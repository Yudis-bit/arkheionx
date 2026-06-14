# ARKHEIONX_V10_GODEYE_WAR_ENGINE_REPORT

Status: PARTIAL — core vertical slice complete, working, and tested. Three
invariant families (adapter/oracle/cross-chain) are template+unit-tested only.

Branch: private/v10-godeye-war-engine
Base commit: b74d9c751eb7f96a443c00d210d14222f855665d
Final commit: none — changes are on the branch but uncommitted (no commit was
  requested; per git policy I did not commit). Say the word and I will commit.
Pushed: No
Tagged: No
Released: No
Website/VPS touched: No

Version metadata: package version unchanged at 9.1.0.dev0 (stable remains v8.0.1).
  The V10 milestone `v10.0.0-dev` is surfaced ONLY inside war-run artifacts
  (triage.json / manifest.json), not in global package metadata — changing the
  global version risks the version-consistency / readiness gates and the V9.1
  surface, so it was intentionally left alone.

## Modules added (10 packages, 65 modules, ~4,800 LOC)

- arkheionx/semantic/  — Layer 1 semantic core (fallback primary, AST interface):
  models, source_index, fallback_parser, ast_loader, call_graph, storage_map,
  external_calls, dataflow, core, renderer.
- arkheionx/defi/      — Layer 2 entity model: entities, entity_detector, renderer.
- arkheionx/state/     — Layer 3 transitions: transitions, transition_detector, renderer.
- arkheionx/invariants/— Layer 4 invariant engine: models, templates (9), generator,
  classifier, renderer.
- arkheionx/attack/    — Layer 5 attack graph: models, candidate_builder, ranking,
  graph, renderer.
- arkheionx/pocgen/    — Layer 6 PoC skeletons: models, actors, setup_builder,
  assertions, foundry, renderer.
- arkheionx/severity/  — Layer 7 economic gate: models, impact_model, caps,
  exploitability, realism, gas_profit, classifier, renderer.
- arkheionx/forklab/   — Layer 8 fork lab: models, env_detect, fork_requirement,
  test_plan, secret_redaction, renderer.
- arkheionx/memory/    — Layer 9 dedup brain: models, store, root_cause_hash,
  duplicate_classifier, renderer.
- arkheionx/warrun/    — Layer 10 orchestrator: scope, orchestrator, command, renderer.

## Modules modified (2)

- arkheionx/cli/main.py — added `_war_run_command` lazy wrapper + `war-run` subparser.
- docs/PUBLIC_SURFACE.md — documented `arkheionx war-run` as experimental/local-only
  (required by the public-surface contract test and the release-readiness gate).

## Commands added (1)

- `arkheionx war-run <target> --scope scope.yaml --out <dir>` with
  --max-candidates / --no-poc-skeletons / --no-fork / --allow-fork-plan / --memory /
  --asset-decimals / --json / --markdown / --no-write.

## Artifacts added (per war-run, written under <target>/.arkheionx/war-run/)

01-scope-map.md, 02-semantic-map.json (+.md), 03-call-graph.json,
04-storage-access-map.json, 05-defi-entities.json (+.md),
06-state-transitions.json (+.md), 07-invariants.md, 08-invariants.json,
09-attack-graph.json (+.md), 10-candidate-ranking.md, 11-poc-skeletons/ (+README),
12-fork-plan.md, fork-requirements.json, 13-economic-severity.md,
economic-severity.json, 14-dedup-scope-risk.md, triage.json, manifest.json.

## Docs added (private/internal, no marketing)

docs/V10_GODEYE_ARCHITECTURE.md, docs/V10_GODEYE_ARTIFACTS.md,
docs/V10_GODEYE_BENCHMARK.md, notes/V10_GODEYE_IMPLEMENTATION_PLAN.md,
notes/V10_GODEYE_BENCHMARK.md.

## Tests added / run / passed / failed

- Added: 104 V10 tests across 29 files (tests/test_v10_*.py).
- Fixtures: 5 generic synthetic targets under tests/fixtures/godeye/ (+1 scope.yaml).
- Full suite run: `python3 -m unittest discover -s tests` -> 2794 tests.
- Passed: 2794. Failed: 0. Skipped: 1 (pre-existing, not introduced by V10).
- Gate checks: safety-wording, docs-links, version-consistency, release-readiness
  all pass.

## What is truly working

1. Source indexing (local, read-only, capped). 2. Fallback semantic extraction
(contracts, functions, inheritance, state vars, structs+fields, call graph,
alias-aware storage map, external-call ordering / reentrancy relevance,
calldata->swap-route data flow). 3. DeFi entity extraction. 4. State transitions for
borrow/repay/deposit/withdraw/redeem/consume with internal-call closure. 5. Invariant
generation with suspicious-here reasons for: debt/lender reconciliation, lender
consent on value-affecting calldata, borrow conservation, deposit consumption, vault
share/asset, collateral release. 6. Attack-candidate construction + ranking
(dust/fork/role penalties). 7. Economic severity gate (decision tree): #567-like ->
VALID_BUT_LOW / KILL_DUST(18-dec); route-buffer -> NEEDS_FORK_PROOF; double-use ->
SUBMIT_HIGH_CANDIDATE; trusted role -> KILL_TRUSTED_ROLE. 8. Foundry PoC skeleton
generation (honest, requires_manual_fill; fork uses an RPC env var name only).
9. Fork requirement generation with chain inference + secret redaction (no URL/keys,
no broadcast). 10. Root-cause memory file store + semantic dedup
(SAME/RELATED/DISTINCT/UNKNOWN). 11. war-run command writing all artifacts + console
verdict. 12. Tests proving the vertical slice (104).

## What is scaffolded / partial

- AST mode: interface only. `ast_loader.detect_artifacts` finds solc/Foundry AST
  artifacts and records provenance, but `load_ast_map` returns None — the fallback
  parser is primary. Full AST ingestion is deferred.
- Invariant families SWAP_ACTUAL_RECEIVED_VS_CREDITED, ORACLE_DECIMAL_NORMALIZATION,
  and CROSS_CHAIN_SUPPLY_CONSERVATION have templates, suspicion logic, severity
  mapping, and unit coverage (incl. a synthetic fork-required severity test), but no
  dedicated end-to-end fixture in this slice.
- `arkheionx memory add` CLI subcommand was NOT added; the memory file store, model,
  and dedup classifier are implemented and tested (the spec permitted file-store-only
  if the CLI was too much for now).
- A few spec-listed micro-files were consolidated into cohesive modules rather than
  created as empty stubs: solidity_lexer/inheritance/modifier_resolver -> folded into
  fallback_parser; ledgers/lifecycle/accounting_terms -> folded into defi;
  lifecycle_graph/before_after -> folded into state; deployment_reader is minimal.

## What is deferred (not implemented now, by design)

Full solc AST ingestion, Slither integration, symbolic execution / SMT, automatic
exploit execution, real fork execution inside Arkheionx, UI, website, cloud service,
remote telemetry, multi-agent orchestration.

## Benchmark result

6 of 9 cases PASS (including both headline real-inspired cases — #567 repayment
reconciliation and the route-buffer consent/refund — replayed exactly: invariant
found, candidate produced, severity capped not High, PoC skeleton generated, fork
required only where real external state matters). 3 cases PARTIAL (adapter / oracle /
cross-chain: template + suspicion + unit coverage, no dedicated fixture). All 8
failure conditions held (no dust-as-High, no trusted-role-as-unprivileged, no report
before PoC, attacker/victim/asset always present, broken invariant always explained,
useful skeletons generated, no RPC/secret leak, duplicates handled).

## Known limitations

- Fallback parsing is regex + brace/paren matching (medium confidence): it can miss
  assembly-heavy, deeply-nested, or unusual Solidity, and confidence is never "high".
- Data flow is intraprocedural with a bounded internal-call closure; cross-contract
  flows are not fully tracked.
- Entity/invariant detection is heuristic and can over- or under-flag; suspicious !=
  confirmed. Every fact carries a confidence and human review is required.
- Severity sharpening for reconciliation uses an --asset-decimals hint; without it
  the conservative default is VALID_BUT_LOW.
- Dedup is UNKNOWN without a provided memory corpus (it does not pretend otherwise).

## Next action

1. (Optional) Commit this slice on the private branch — not done yet, awaiting the go-ahead.
2. Add dedicated end-to-end fixtures for adapter / oracle / cross-chain to lift those
   three benchmark cases from PARTIAL to PASS.
3. Implement real solc AST ingestion behind the existing ast_loader interface to
   raise semantic confidence from medium to high.
4. Run war-run against a real authorized in-scope target and compare its verdicts to
   the V9.1 hunter triage before considering any merge toward stable.
