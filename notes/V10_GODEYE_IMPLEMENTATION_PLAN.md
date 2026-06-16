# V10 GodEye War Engine — Implementation Plan (private)

Internal codename: Arkheionx V10 GodEye War Engine.
Public-safe name: Arkheionx V10 Semantic DeFi Review Engine.

This note is an engineering plan, not marketing. It records the baseline, the
target module map, the integration contract with V9.1, and the safety rules that
the implementation must not violate.

## Baseline (recorded at Phase 0)

- Repo: `DeFi-Exploit-PoCs` (package `arkheionx`).
- Branch before: `private/v9.1-reachability-truth-engine`.
- Work branch: `private/v10-godeye-war-engine` (created from the V9.1 HEAD).
- Base commit: `b74d9c751eb7f96a443c00d210d14222f855665d`.
- Package version: `9.1.0.dev0` (stable release remains `v8.0.1`).
- Test runner: `python3 -m unittest discover -s tests -p "test_*.py"` (the repo
  does **not** use pytest; CI runs unittest). New tests must be `unittest.TestCase`.
- Baseline check: representative modules
  (`test_package_imports`, `test_hunter_command`, `test_cli_commands`,
  `test_hunter_reachability_end_to_end`) = 26 tests, OK.

## V9.1 surface that must keep working

- `arkheionx/hunter/*` — reachability truth engine, value-flow, leads, scoring,
  report-filter, submission-risk, PoC planning, `triage.json`, render.
- `arkheionx/cli/main.py` — `build_parser()` registers subcommands via
  `subparsers.add_parser(...).set_defaults(func=...)`; `main()` dispatches
  `args.func(args)`. Experimental modes are imported lazily inside a thin wrapper.
- Exit codes (`arkheionx/cli/exit_codes.py`): SUCCESS=0, RUNTIME_ERROR=1,
  INVALID_ARGUMENTS=2, SAFETY_REJECTION=3.
- Reusable helpers: `arkheionx/hunter/source_scan.py`
  (`find_functions`, `strip_comments`, `line_of`, brace matcher).
- Model convention: `@dataclass` + `to_dict()` delegating to `dataclasses.asdict`.
- Artifact convention: numbered Markdown + `*.json` written under
  `.arkheionx/<mode>/`, plus a `manifest.json`.

V10 is additive. It adds a new package tree and one new CLI command. It does not
edit hunter behavior, does not change existing artifacts, does not retag/release.

## V10 module map (target)

```
arkheionx/semantic/   # Layer 1 — semantic core (fallback primary, AST interface)
arkheionx/defi/       # Layer 2 — DeFi entity model
arkheionx/state/      # Layer 3 — state transition engine
arkheionx/invariants/ # Layer 4 — invariant engine + templates
arkheionx/attack/     # Layer 5 — attack graph + ranking
arkheionx/pocgen/     # Layer 6 — Foundry PoC skeleton engine
arkheionx/severity/   # Layer 7 — economic severity gate (decision tree)
arkheionx/forklab/    # Layer 8 — fork requirement + secret redaction
arkheionx/memory/     # Layer 9 — root-cause memory / dedup brain
arkheionx/warrun/     # Layer 10 — war-run orchestrator + CLI handler
```

CLI: `arkheionx war-run <target> --scope <scope.yaml> --out <dir>` plus
`--no-fork/--allow-fork-plan/--memory/--max-candidates/--poc-skeletons/--json/--markdown`.

## Golden artifacts (one war-run)

`01-scope-map.md`, `02-semantic-map.json`, `03-call-graph.json`,
`04-storage-access-map.json`, `05-defi-entities.json` (+`.md`),
`06-state-transitions.json` (+`.md`), `07-invariants.md`, `08-invariants.json`,
`09-attack-graph.json` (+`.md`), `10-candidate-ranking.md`,
`11-poc-skeletons/`, `12-fork-plan.md` (+`fork-requirements.json`),
`13-economic-severity.md` (+`economic-severity.json`),
`14-dedup-scope-risk.md`, `triage.json`, `manifest.json`.

## Engineering decisions

- **Fallback parser is primary.** AST mode is an interface that detects solc/Foundry
  artifacts and, when absent, returns nothing so the fallback runs. Full AST ingestion
  is deferred; this is documented honestly, not hidden.
- **No new runtime dependencies.** Pure standard library (`re`, `dataclasses`,
  `json`, `hashlib`, `pathlib`). `scope.yaml` is parsed by a tiny built-in YAML-subset
  reader (no PyYAML dependency) since the project ships `dependencies = []`.
- **No target-specific logic.** No protocol/company/token names as branches.
  Benchmarks (#567 repayment rounding, route-buffer consent) are reproduced with
  generic synthetic fixtures under `tests/fixtures/godeye/`.
- **Severity never overclaims.** The gate caps dust/role-gated/buffer-capped to
  VALID_BUT_LOW/KILL/NEEDS_FORK. No report is emitted; output stops at
  invariant + candidate + skeleton + verdict.
- **Module consolidation:** where the spec lists several tiny files (e.g.
  `solidity_lexer.py`, `inheritance.py`, `modifier_resolver.py`), cohesive logic is
  folded into `fallback_parser.py`/`call_graph.py` rather than created as empty
  stubs. Deviations are listed in the final report.

## Safety rules (hard)

No live network, no transactions, no private keys, no broadcast. Fork support is a
*plan only*; RPC URLs are redacted to env-var names; `.env` is never written into
artifacts. The artifact guard rejects forbidden outcome terms (no "VALID_BUG",
"CONFIRMED_VULNERABILITY", "SUBMIT_NOW", "GUARANTEED_*", "EXPLOIT_READY",
"AUTO_SUBMITTED"). Human review is always required.

## Phase order

0 baseline/branch/plan → 1 semantic → 2 entities → 3 state → 4 invariants →
5 attack → 6 pocgen → 7 severity → 8 forklab → 9 memory → 10 war-run/CLI →
11 fixtures → 12 tests → 13 benchmark → 14 docs → 15 honest report.

Each layer ships with `unittest` tests and machine-readable artifacts before the
next layer starts.
