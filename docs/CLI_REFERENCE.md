# ArkheionX CLI Reference

This page reflects the command surface shown by:

```bash
python3 -m arkheionx.cli.main --help
```

Use [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md) for stability labels and longer public-surface notes.

## First commands

```bash
arkheionx version
arkheionx doctor
arkheionx review . --scope-file scope.md --out .arkheionx/review
```

`arkheionx review` is the primary review-pack command. `arkheionx review-map` remains useful for a compact focused map.

## Command surface

| command | status | purpose |
|---|---|---|
| `arkheionx version` | stable | Print package version, latest stable release, current milestone, and next milestone. |
| `arkheionx doctor` | stable | Diagnose install health, Python, git checkout, project layout, Foundry detection, artifacts directory, and safety boundary. |
| `arkheionx review` | stable/current primary | Build a local review pack: run context, scope map, value-flow map, interaction map, assumptions, review lanes, evidence tasks, evidence rubric, report filter, agent input, `review.json`, and `manifest.json`. |
| `arkheionx triage` | experimental | Run local senior research triage before review. Planning artifact, not a finding. |
| `arkheionx hunter` | experimental | V9 local-first hunter mode for prioritizing bounty surfaces. Read-only RPC only when provided, no mutation, no auto-submit. |
| `arkheionx war-run` | experimental | V10 local-first semantic review engine. Produces review artifacts and PoC skeletons; no report, no RPC by default, no broadcast. |
| `arkheionx memory` | experimental | Local root-cause memory brain for classifying candidates against prior local notes. |
| `arkheionx scan` | legacy/advanced | Run the legacy local value-flow/readiness scanner. |
| `arkheionx validate-config` | stable | Validate a local ArkheionX JSON config. |
| `arkheionx test-plan` | legacy/advanced | Generate defensive test plans from ArkheionX report JSON. |
| `arkheionx search` | legacy/advanced | Search local ArkheionX security memory metadata. |
| `arkheionx demo` | stable | List, show, and copy safe local demo workflows. |
| `arkheionx open` | advanced | One-command project understanding: scan and orient inside an authorized local repository. |
| `arkheionx map` | advanced | Draw protocol roles, journeys, money flow, and hunter targets. |
| `arkheionx flow` | advanced | Build a compact money-flow graph and Mermaid summary. |
| `arkheionx hunt` | advanced | Rank bug-hunting surfaces for a solo researcher. |
| `arkheionx prove` | advanced | Generate a local Foundry proof scaffold for a target. |
| `arkheionx trace` | advanced | Summarize the latest Foundry proof/trace for a target. |
| `arkheionx evidence` | advanced | Build a compact evidence package from proof and trace artifacts. |
| `arkheionx report` | advanced | Create a responsible local report draft from evidence. |
| `arkheionx evidence-status` | advanced | Inspect proof/evidence/report artifact state for a repository. |
| `arkheionx validate-artifacts` | advanced | Validate generated proof/evidence/report artifacts. |
| `arkheionx review-map` | stable | Build a local protocol review map: contracts, value paths, assumptions, test gaps, proof suggestions, and evidence links. |
| `arkheionx test-gap-map` | stable | Show focused test gaps from review-map artifacts or derive them locally. |
| `arkheionx value-paths` | stable | Show focused value paths from review-map artifacts or derive them locally. |
| `arkheionx assumptions` | stable | Show focused assumptions from review-map artifacts or derive them locally. |
| `arkheionx proof-plan` | stable | Show focused proof suggestions from review-map artifacts or derive them locally. |
| `arkheionx evidence-links` | stable | Show focused evidence links from review-map artifacts or derive them locally. |
| `arkheionx review-package` | advanced | Build a reviewer-ready local package with manifest, validation, README, and copied artifacts. |
| `arkheionx local-validate` | advanced | Ingest saved Foundry test output into local validation artifacts. It does not run `forge`. |
| `arkheionx agent-brief` | advanced | Build an AI-agent-ready review brief from the review map. This is context, not an AI auditor claim. |
| `arkheionx hypothesis-log` | advanced | Generate a structured hypothesis log and rejected-finding memory from review-map surfaces. |
| `arkheionx case-study` | advanced | Generate a sanitized research-session report template from artifacts. |
| `arkheionx blind-spots` | advanced | Rank likely blind-spot candidates: high-impact surfaces with weak review evidence. |
| `arkheionx criticality-map` | advanced | Map criticality potential. Criticality potential is not severity. |
| `arkheionx counterfactuals` | advanced | Generate counterfactual research prompts by negating guarding assumptions. |
| `arkheionx research-pack` | advanced | Generate a local human/agent-ready research pack. |
| `arkheionx evidence-graph` | advanced | Classify important surfaces into evidence states. Evidence state is not vulnerability validity. |
| `arkheionx interaction-matrix` | advanced | Detect meaningful combinations of surfaces that may hide bugs when tested together. Priority is not severity. |
| `arkheionx unresolved-map` | advanced | Show important surfaces and interactions not yet closed by local evidence. |
| `arkheionx complete-review` | advanced | Generate a complete local review package combining review map, blind spots, evidence graph, interaction matrix, unresolved map, agent input, checklist, and manifest. |
| `arkheionx scope-map` | advanced | Parse an audit/contest/program scope note into structured review rules. |
| `arkheionx scope-lanes` | advanced | Generate scope-aware review lanes. Lanes are planning artifacts, not findings. |
| `arkheionx scope-tasks` | advanced | Turn lanes into bounded evidence-oriented tasks. Tasks are not exploit instructions. |
| `arkheionx scope-pack` | advanced | Generate a complete local scope-aware research pack. |
| `arkheionx evidence-judge` | advanced | Judge whether local tests/evidence prove the intended task. Does not confirm vulnerabilities. |
| `arkheionx report-filter` | advanced | Classify report candidates against scope before submission. Not final triage. |
| `arkheionx lens-list` | advanced | List implemented and planned protocol lenses. |
| `arkheionx lens-map` | advanced | Build a protocol-aware lens map. Planning artifact, not a finding. |
| `arkheionx lens-lanes` | advanced | Generate protocol-aware review lanes. Lane priority is review order, not severity. |
| `arkheionx lens-tasks` | advanced | Turn lens review lanes into bounded evidence-oriented tasks. |
| `arkheionx lens-pack` | advanced | Generate a complete local protocol lens pack. |
| `arkheionx lens-evidence` | advanced | Classify local-test evidence for lens economic invariants. |
| `arkheionx lens-report-filter` | advanced | Classify lens report candidates against scope. Not final triage. |
| `arkheionx help` | stable | Print CLI help. |

## Review command

```bash
arkheionx review . --scope-file scope.md --out .arkheionx/review
arkheionx review . --scope-file scope.md --lens fixed-credit-market --out .arkheionx/review
```

Common flags:

- `--scope-file <path>`
- `--lens <id>`
- `--out <dir>`
- `--json`
- `--no-write`

See [`CORE_WORKFLOW.md`](CORE_WORKFLOW.md).

## Exit codes

- `0`: completed successfully and no warning-style review signal requires attention.
- `1`: completed, but review guidance or heuristic output requires human attention. This is not automatically a crash.
- `2`: usage or runtime error, such as a missing path or invalid flag.

CI should inspect JSON decision fields where available instead of treating every non-zero analysis result as a failure.

## Safety boundary

ArkheionX uses authorized local/static repository analysis by default. It does not perform live-chain mutation, request private keys, confirm vulnerabilities, assign final severity, or replace human review.
