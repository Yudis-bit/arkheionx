# Arkheionx Pre-Audit Readiness OS

Arkheionx Readiness is the GitHub-native layer that turns the historical
exploit memory archive into practical preparation for indie DeFi builders.

It is built for teams that are not ready to spend serious money on a formal
audit yet, but still need to know whether their repository has obvious audit
blockers: missing invariants, untested accounting assumptions, weak docs,
unclear privileged roles, and historical exploit-pattern similarity.

## What It Is

Arkheionx Readiness is:

- a local pre-audit scanner;
- a reusable GitHub Action;
- a Markdown readiness report;
- optional JSON output for automation;
- GitHub Actions job summary output;
- optional PR Readiness Comment;
- generated issue checklist;
- generated issue plan for optional GitHub issue workflows;
- stable finding IDs;
- SARIF, baseline, and diff artifacts when requested;
- semantic-lite evidence, confidence reasons, and detection sources;
- optional local Slither enrichment when explicitly enabled;
- optional local `.arkheionx.json` config;
- safe Foundry invariant skeleton generation;
- a bridge from historical DeFi failures to defensive builder checklists.

It does not inspect deployed contracts. It does not call chains. It does not
submit transactions. It does not adapt historical PoCs to live targets.

## Why Indie Builders Need It

Early DeFi teams often reach audit conversations with gaps that are expensive
to fix under time pressure:

- no invariant tests for value-bearing flows;
- oracle assumptions not documented;
- vault accounting not tested across roundtrip and rounding edges;
- admin roles and emergency controls unclear;
- reward or liquidation math lacking property tests;
- no crisp audit scope.

Arkheionx helps builders find those gaps before audit intake.

Core message:

> Find exploit-pattern risks, missing invariants, and audit blockers before
> paying for a formal smart contract audit.

Short message:

> Not an audit. A way to prepare for one.

## GitHub-Only Flow

1. A builder adds the GitHub Action or runs the CLI locally.
2. The scanner inspects source, tests, docs, configs, and workflows.
3. It classifies protocol shape: vault, AMM, lending, staking, oracle, or
   generic.
4. It detects static risk signals and test-readiness signals.
5. It maps the signals to historical pattern similarity using Arkheionx memory.
6. It writes Markdown, JSON, SARIF, baseline, summary, PR comment body,
   issue checklist, and issue plan artifacts when requested.
7. The builder uses the report, checklist, and issue plan as pre-audit planning
   material.
8. If useful, the builder opens a GitHub issue for a Launch Report or
   Pre-Audit Sprint.

No website, backend, dashboard, secrets, or RPC endpoints are required.

## Scanner Architecture

The scanner lives at [`scripts/pre_audit_scan.py`](../scripts/pre_audit_scan.py)
and uses the Python standard library only.

Main stages:

- `collect_files`: finds Solidity, tests, docs, configs, and workflow files.
- `classify_files`: separates sources, tests, docs, configs, and CI.
- `detect_protocol_type`: weights protocol-shape signals.
- `detect_signals`: identifies local risk signals from code and configs.
- `detect_test_readiness`: checks tests, assertions, invariant/fuzz signals,
  handlers, static-analysis configs, and CI.
- `extract_solidity_structure`: performs semantic-lite contract/function/test
  extraction for evidence and false-positive reduction.
- `slither_analysis`: optionally normalizes local Slither output when provided
  or explicitly requested.
- `map_historical_patterns`: maps signals to defensive historical classes.
- `compute_readiness_score`: calculates a 100-point pre-audit score.
- `finding IDs`: assigns stable IDs such as `ARK-VLT-001`.
- `suggest_invariants`: recommends Foundry invariant themes.
- `generate_report`: writes the Markdown dashboard.
- `generate_json_report`: writes machine-readable output.
- `generate_issue_checklist`: writes a copyable remediation checklist.
- `build_issue_plan`: writes structured remediation issue tasks.
- `generate_comment_output`: writes an optional PR comment body.

## Risk Signals

Arkheionx currently looks for signals in these families:

- vault rule pack: ERC4626-like interfaces, share/accounting conversion,
  totalAssets assumptions, fees, strategies, withdrawal queues, and vault
  admin operations;
- vault accounting: `totalAssets`, `convertToShares`, `withdraw`, `deposit`;
- oracle assumptions: price feeds, TWAP, staleness, reserves, decimals;
- reentrancy-sensitive value flow: external calls, transfers, callbacks;
- access control: owners, roles, setters, pause and emergency controls;
- upgradeability: initializer, proxy, UUPS, implementation, storage gap;
- reward accounting: reward indexes, accumulators, claim flows;
- AMM invariants: swaps, reserves, liquidity, invariant math;
- lending and liquidation: debt, collateral, health factor, liquidation;
- cross-chain validation: endpoints, messages, relayers, bridges;
- governance: proposals, quorum, delegates, execution.

Signals are not findings. They are review prompts.

For current rule packs, see [`RULE_PACKS.md`](RULE_PACKS.md) and
[`VAULT_RULE_PACK.md`](VAULT_RULE_PACK.md).

## Historical Pattern Similarity

The report uses language such as:

- historical pattern similarity;
- readiness gap;
- review recommended;
- missing invariant;
- audit blocker;
- defensive check.

It does not say that a vulnerability is confirmed. It does not produce an
attack path. It maps local repository structure to classes of failures that
have mattered historically.

## Report Usage

Use the report to:

- prepare a formal audit scope;
- decide which tests to add before audit;
- document assumptions for reviewers;
- prioritize role, oracle, accounting, and value-flow review;
- create internal GitHub issues;
- support grant or community updates with concrete readiness work.

Do not use the report as proof that a protocol is safe.

## Limitations

Arkheionx Readiness is static and heuristic. It can miss important issues. It
can also over-report risk signals when terms appear in harmless contexts.

Known limitations:

- semantic-lite extraction is heuristic and not a full Solidity AST;
- no call graph;
- no symbolic execution;
- no deployed-contract review;
- no fork tests;
- no private issue creation;
- no guarantee that a high score means a protocol is safe.

False positives should be reported with the `False Positive Report` issue
template so the rules improve over time.

## Formal Audit Recommendation

Arkheionx is a preparation layer. A formal smart contract audit is still
recommended before mainnet launch, material TVL, or handling real user funds.
