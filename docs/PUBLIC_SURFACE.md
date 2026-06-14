# Public Command Surface

The public surface Arkheionx intends to keep stable into v3.0. Stability labels:

- **stable** — name and core behavior kept stable into v3.0; output may be polished.
- **stable-additive** — stable, with backward-compatible additive changes expected.
- **internal/legacy** — supported for specialized workflows; may change with notice.

All commands are local-first: no RPC by default, no secrets, no transaction
broadcasting, no exploit automation, no auto-submit. JSON output (`--json`) and
files written under `.arkheionx/out/` are always plain (no color). See
[`STABILITY_CONTRACT.md`](STABILITY_CONTRACT.md).

Generated `.arkheionx/out/` artifacts are local, gitignored by default, and not
intended to be committed in v3.2.0. Future workspace features such as baselines,
diffs, sessions, reviewer notes, policy profiles, and review packages are
planned surfaces, not current public commands.

In locally finalized v3.4.0, the existing public commands gain additive artifact
context only: trace-bounded evidence packages, deterministic evidence package
IDs, manifests, report receipt references, and enriched read-only evidence-link
backfill. v3.4.0 has been finalized locally and tagged locally, but it has not
been pushed or published.

In release-prep v3.5.0, the public command surface is unchanged. The v3.5
Protocol Intelligence Model (`arkheionx/intelligence/`) is internal
infrastructure: it adds stable IDs and dataclasses built additively from
existing `analyze()` / `review-map` output, with no new public command, no
public schema-breaking migration, no mandatory `protocol-model.json`, and old
IDs preserved as aliases. v3.5.0 is release prep only — not finalized, tagged,
pushed, or published.

In active v3.8.0 branch work, the public command surface is **unchanged** and no
new public CLI surface is added. The v3.8 Protocol Intelligence Core
(`arkheionx/intelligence/`: the function-role taxonomy, value-path graph model,
assumption engine, test-gap engine, protocol graph builder, and local-validation
coverage correlation) is internal/additive infrastructure with deterministic IDs
and exact-only linking — no new public command, no new flags, and no
schema-breaking migration. `arkheionx review-package` gains optional inclusion of
protocol-graph artifacts when they already exist under
`.arkheionx/out/protocol-graph/` (its `artifact_count` may rise, with no new flag
and no changed output key); `arkheionx local-validate`, `arkheionx evidence`, and
`arkheionx report` are unchanged except for optional, additive protocol-graph
context. `manual_review_required` stays true and `ready_for_submission` stays
false. v3.8.0 is active branch work, not a finalized or published release. See
[`PROTOCOL_INTELLIGENCE_CORE.md`](PROTOCOL_INTELLIGENCE_CORE.md).

## Workbench commands

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx open` | One-command project orientation | human + `--json` | none by default | stable |
| `arkheionx map` | Protocol roles, journeys, money flow | human + `--json` | `map.json` | stable |
| `arkheionx flow` | Money-flow graph (+ Mermaid) | human + `--json`/`--mermaid` | `flow.json`, `money-flow.mmd` | stable |
| `arkheionx hunt` | Rank bug-hunting surfaces | human + `--json` | `hunt.json` | stable |
| `arkheionx prove` | Generate/run a targeted local Foundry proof | human + `--json` | `proof/<slug>/*` | stable |
| `arkheionx trace` | Summarize proof/trace output | human + `--json` | `proof/<slug>/trace.json` | stable |
| `arkheionx evidence` | Package proof + trace artifacts with trace-bounded readiness, package IDs, and manifests | human + `--json` | `evidence/<slug>/*` | stable |
| `arkheionx report` | Responsible local report draft with evidence and receipt references | human + `--json` | `reports/<slug>/*` | stable |
| `arkheionx evidence-status` | Artifact state per target | human + `--json` | reads index | stable |
| `arkheionx validate-artifacts` | Validate generated artifacts | human + `--json` | reads artifacts | stable |
| `arkheionx review-map` | Protocol review map: value paths, assumptions, test gaps, proof suggestions, evidence links, and Test Gap Map artifacts | human + `--json` | `review-map/*` | stable-additive |
| `arkheionx test-gap-map` | Focused Test Gap Map view from existing review-map artifacts or the review-map builder | human + `--json` | reads/writes `review-map/*` when building | stable-additive |
| `arkheionx value-paths` | Focused value-path view from existing review-map artifacts or the review-map builder | human + `--json` | reads/writes `review-map/*` when building | stable-additive |
| `arkheionx assumptions` | Focused assumption prompt view from existing review-map artifacts or the review-map builder | human + `--json` | reads/writes `review-map/*` when building | stable-additive |
| `arkheionx proof-plan` | Focused local proof-planning view from existing review-map artifacts or the review-map builder; does not execute proofs | human + `--json` | reads/writes `review-map/*` when building | stable-additive |
| `arkheionx evidence-links` | Focused evidence-link view from existing review-map artifacts or the review-map builder; can surface local receipt/package/report draft links; does not create evidence | human + `--json` | reads/writes `review-map/*` when building | stable-additive |
| `arkheionx review-package` | Assemble a local reviewer-ready review package (manifest, validation, README, limitations, copied artifacts, checksums, and a protocol-model.json sidecar when buildable) from existing local artifacts; runs exact-match cross-reference validation (unresolved references are warnings, never invented links); `--no-write` dry run; `--export zip` writes a deterministic local archive under `review-package/exports/` (no publication); review guidance only | human + `--json` | `review-package/*` | stable-additive |
| `arkheionx local-validate` | Ingest a saved Foundry test output file (JSON or text) into local validation artifacts; parses, builds deterministic run/test-result/summary records with exact-match protocol links, and (unless `--no-write`) writes `local-validation/*`; never runs `forge`, requires no Foundry install, no live forge runner, no review-package/evidence integration yet; review guidance only | human + `--json` | `local-validation/*` | stable-additive |

## Research memory commands (v4.1)

In active v4.1 branch work, the public surface gains three additive,
local/static research-memory commands built on top of the review map. They emit
human Markdown and `--json`, write artifacts under `.arkheionx/research/` (unless
`--no-write`), and never run RPC, live-chain, or exploit automation.
`manual_review_required` stays true: hypotheses are review prompts, not findings.
See [`V4_1_RESEARCH_WORKFLOW.md`](V4_1_RESEARCH_WORKFLOW.md) and
[`RESEARCH_MEMORY_MODEL.md`](RESEARCH_MEMORY_MODEL.md).

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx agent-brief` | AI-agent-ready review brief: repository summary, coverage weakness ranking, value movement, test gaps, authorization surfaces, periphery/core surfaces, behavior-mismatch surfaces, open hypotheses, and a do-not-claim boundary | human + `--json` | `research/agent-brief.{md,json}` | stable-additive |
| `arkheionx hypothesis-log` | Structured hypothesis log and rejected-finding memory: open hypotheses with surface, source, bug class, suggested local test, and empty fields for test command, result, rejection reason, confirmation notes, and human decision | human + `--json` | `research/hypotheses.{md,json}` | stable-additive |
| `arkheionx case-study` | Sanitized case-study / research-session report from review-map and research surfaces; optional `--from` incorporates a hypothesis log's statuses; makes no vulnerability claim unless independently confirmed | human + `--json` | `research/case-study.{md,json}` | stable-additive |

## Blind spot intelligence commands (v5)

In finalized v5.0 branch work, the public surface gains four additive,
local/static Blind Spot Intelligence commands built on top of the review map and
the v4.1 research surfaces. They emit human Markdown and `--json`, write
artifacts under `.arkheionx/` (unless `--no-write`), and never run RPC,
live-chain, or exploit automation. `manual_review_required` stays true: blind
spot candidates are not vulnerabilities, criticality potential is not severity,
and counterfactuals are research prompts, not findings. See
[`BLIND_SPOT_INTELLIGENCE.md`](BLIND_SPOT_INTELLIGENCE.md) and
[`V5_WORKFLOW.md`](V5_WORKFLOW.md).

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx blind-spots` | Rank likely blind-spot candidates (high-impact surfaces with weak review evidence) with a transparent additive score (impact + review-gap + complexity + assumption), per-candidate reasons, a suggested counterfactual, a local test direction, evidence needed, unknown surfaces, and notable non-blind-spots | human + `--json` | `blind-spots/blind-spots.{md,json}` | stable-additive |
| `arkheionx criticality-map` | Map criticality potential (heuristic blast radius, never severity) across surfaces by dimension, with highest-blast-radius and criticality-vs-review-density views | human + `--json` | `criticality-map/criticality-map.{md,json}` | stable-additive |
| `arkheionx counterfactuals` | Negate guarding assumptions into testable "what if this assumption is false?" research prompts with a local test direction, evidence required, and a stop condition, plus a counterfactual matrix | human + `--json` | `counterfactuals/counterfactuals.{md,json}` | stable-additive |
| `arkheionx research-pack` | Generate a complete local, vendor-agnostic bug bounty research pack (README, review-map summary, blind spots, criticality map, counterfactuals, agent brief, hypotheses, evidence log, do-not-claim, case-study template, JSON manifest). Writes by default | human + `--json` (manifest) | `research-pack/*` | stable-additive |

## Evidence graph commands (v6)

In finalized v6.0 branch work, the public surface gains four additive,
local/static Evidence Graph + Interaction Matrix commands built on top of the
review map, the v4.1 research surfaces, and the v5 blind-spot layer. They emit
human Markdown and `--json`, write artifacts under `.arkheionx/` (unless
`--no-write`), and never run RPC, live-chain, or exploit automation.
`human_review_required` stays true: an evidence state is not a vulnerability
claim, confirmed-candidate is not a confirmed vulnerability, interaction priority
is not severity, and unresolved does not mean vulnerable. See
[`EVIDENCE_GRAPH.md`](EVIDENCE_GRAPH.md), [`INTERACTION_MATRIX.md`](INTERACTION_MATRIX.md),
[`UNRESOLVED_MAP.md`](UNRESOLVED_MAP.md), [`COMPLETE_REVIEW.md`](COMPLETE_REVIEW.md),
and [`V6_WORKFLOW.md`](V6_WORKFLOW.md).

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx evidence-graph` | Classify every important review surface into an evidence state (tested, rejected-with-evidence, confirmed-candidate, unresolved, insufficient-evidence, needs-human-review, unclassified, out-of-scope) with an evidence strength, criticality potential, missing-evidence gaps, and a next local test direction | human + `--json` | `evidence-graph/evidence-graph.{md,json}` | stable-additive |
| `arkheionx interaction-matrix` | Detect meaningful combinations of surfaces that may hide bugs when tested together, scored by a transparent additive interaction priority (impact + review-gap + complexity), with an interaction test plan; interaction priority is not severity | human + `--json` | `interaction-matrix/interaction-matrix.{md,json}` | stable-additive |
| `arkheionx unresolved-map` | Compose the evidence graph and interaction matrix into the high-impact unresolved surfaces, high-impact unresolved interactions, unclassified surfaces, and a final review checklist; unresolved does not mean vulnerable | human + `--json` | `unresolved-map/unresolved-map.{md,json}` | stable-additive |
| `arkheionx complete-review` | Generate a complete local, vendor-agnostic V6 review package (review-map summary, blind spots, criticality, counterfactuals, evidence graph, interaction matrix, unresolved surfaces, model-agnostic agent input, human review checklist, case-study template, JSON manifest). Writes by default | human + `--json` (manifest) | `complete-review/*` | stable-additive |

## Scope-aware orchestration commands (v7)

The v7 layer turns an audit/contest/program scope note into review lanes, scope
tasks, evidence requirements, and report filters. Commands accept an optional
`--scope-file <markdown>`, emit human Markdown and `--json`, write artifacts under
`.arkheionx/` (unless `--no-write`), and never run RPC, live-chain, or exploit
automation. `human_review_required` stays true: a scope map, review lane, or scope
task is a planning artifact, not a finding; evidence quality is not vulnerability
validity; candidate-with-evidence is not a confirmed vulnerability; and a report
candidate is not final triage. Private scope notes are read only from local,
gitignored files and are never committed. See
[`SCOPE_ORCHESTRATION.md`](SCOPE_ORCHESTRATION.md), [`SCOPE_MAP.md`](SCOPE_MAP.md),
[`SCOPE_TASKS.md`](SCOPE_TASKS.md), [`EVIDENCE_JUDGE.md`](EVIDENCE_JUDGE.md),
[`REPORT_FILTER.md`](REPORT_FILTER.md), and [`V7_WORKFLOW.md`](V7_WORKFLOW.md).

## One-command review (v8)

`arkheionx review` is the primary, "start here" command. It builds one review pack
from a repo, an optional scope note, and an optional generic protocol-family lens,
orchestrating the review-map, scope-aware, and protocol-lens layers. Exit behavior:
`0` clean, `1` heuristic / human-review-required warning (not a crash), `2` only on
invalid usage or a runtime error. See [`CORE_WORKFLOW.md`](CORE_WORKFLOW.md).

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx review` | One-command local review pack: run context, scope map, value-flow map, interaction map, assumptions, review lanes, evidence tasks (with kill conditions), evidence rubric, report filter, agent input, `review.json`, and `manifest.json`; add `--lens` for protocol-aware artifacts. Writes by default | human + `--json` (manifest) | `review/*` | stable-additive |

## Private / experimental commands (local-only)

`arkheionx triage` is a **private, experimental, local-only** senior research-triage
mode. It runs *before* `arkheionx review` and decides what is worth reviewing and
what to kill early, so review time is not spent proving what should never be pursued.
It is intentionally **not** part of the stable command contract, is not wired into any
release, site, or remote surface, and makes no RPC or live-chain calls by default.
Output is a local planning pack — not a finding, not severity; human review is
required. Internal note: `docs/internal/SENIOR_TRIAGE_MODE.md` (local only).

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx triage` | Senior research triage before review: target decision, bounty-eligibility read, known-issue / dedup map, freshness diff, optional deployment-reality plan, research-priority scoreboard, top-3 leads, do-not-touch list, agent brief, `triage.json`, and `manifest.json`. No RPC by default; no auto-submit; no vulnerability claims. Writes by default | human + `--json` | `triage/*` | experimental (local-only) |

`arkheionx hunter` is a **private, experimental, local-only** V9 universal senior
exploit-hunter mode (also reachable as `arkheionx triage --hunter`). It chooses the
highest-EV bounty surface — fresh, in-scope, payable, non-duplicate, attacker-reachable
— and avoids known / out-of-scope / dead leads before any PoC. It is intentionally
**not** part of the stable command contract, is not wired into any release, site, or
remote surface, makes read-only RPC calls only when an endpoint is explicitly provided
(the endpoint is masked), performs no live-chain mutation, and never auto-submits.
Output is a local planning pack — not a finding, not severity; human review is
required. Internal notes live under `docs/private/` (local only).

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx hunter` | V9 universal senior exploit-hunter: program identity / scope map, source provenance, dedup corpus quality, freshness map, deployment reality, live-registry diff, value-flow and state-machine maps, ranked leads with a decision (PURSUE_NOW / NEEDS_POC / PARK_* / KILL_*), PoC plans, submission-risk, a report filter (default Submit: NO), engine evaluation, `triage.json`, and `manifest.json`. Read-only RPC only when provided (masked); no mutation; no auto-submit. Writes by default | human + `--json` | `hunter/*` | experimental (local-only) |

`arkheionx war-run` is a **private, experimental, local-only** V10 Semantic DeFi
Review Engine (internal codename: GodEye War Engine). It reconstructs a Solidity
codebase as an economic machine — semantic map, DeFi entities, state transitions —
derives candidate invariants, ranks attack candidates, generates Foundry PoC
skeletons, gates economic severity (capping dust / trusted-role / unproven-buffer
candidates), plans fork proof when deployed external state matters, and applies
root-cause dedup memory. It is intentionally **not** part of the stable command
contract, is not wired into any release, site, or remote surface, makes no RPC
calls by default, performs no live-chain mutation, never broadcasts, requires no
signing keys, and never auto-submits. Fork support is a plan only; RPC endpoints are
referenced by environment variable name and redacted. No report is generated until
an invariant is proven; output is local review context, not a finding or a severity,
and human review is required.

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx war-run` | V10 semantic DeFi review engine: scope map, semantic map, call graph, storage-access map, DeFi entities, state transitions, candidate invariants (with suspicious-here reasons), attack-candidate ranking, Foundry PoC skeletons, economic severity verdicts (SUBMIT_* / VALID_BUT_LOW / NEEDS_FORK_PROOF / KILL_*), fork plan, dedup/scope risk, `triage.json`, and `manifest.json`. No RPC by default; no broadcast; fork is a plan only; no report generated. Writes by default | human + `--json` | `war-run/*` | experimental (local-only) |


| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx scope-map` | Parse a scope note into structured review rules (in/out of scope, severity conditions, trusted assumptions, dependency assumptions, known/accepted issues, prior-audit notes, design choices, invariants, focus areas, do-not-waste-time filters, report-candidate requirements) | human + `--json` | `scope-map/scope-map.{md,json}` | stable-additive |
| `arkheionx scope-lanes` | Generate scope-aware review lanes from repository surfaces plus scope rules, each with priority, targets, hypotheses, required evidence, known/accepted filters, and a stop condition; lanes are planning artifacts, not findings | human + `--json` | `scope-lanes/scope-lanes.{md,json}` | stable-additive |
| `arkheionx scope-tasks` | Turn lanes into precise, bounded, evidence-oriented tasks (hypothesis, counterfactual, setup, action, required assertions, validity and known-issue filters, stop condition, report-candidate threshold); tasks are research instructions, not exploit instructions | human + `--json` | `scope-tasks/scope-tasks.{md,json}` | stable-additive |
| `arkheionx scope-pack` | Generate a complete local scope-aware research pack (scope map, review lanes, scope tasks, do-not-waste-time, evidence template/rubric, report-filter checklist, human review checklist, model-agnostic agent input, case-study template, JSON manifest + sidecars). Writes by default | human + `--json` (manifest) | `scope-pack/*` | stable-additive |
| `arkheionx evidence-judge` | Judge whether local tests/evidence prove the intended task on a transparent rubric, with an evidence quality (strong/medium/weak/invalid/insufficient/unknown) and a judgment (rejected-with-evidence / candidate-with-evidence / insufficient / invalid / scope-filtered / needs-human-review); does not confirm vulnerabilities | human + `--json` | `evidence-judge/evidence-judge.{md,json}` | stable-additive |
| `arkheionx report-filter` | Classify report candidates against scope rules before submission (potentially-reportable, needs-more-evidence, likely-known/accepted/trusted-role/out-of-scope/low-only, duplicate-prone, not-a-finding, needs-human-review) with a human pre-submission checklist; not final triage | human + `--json` | `report-filter/report-filter.{md,json}` | stable-additive |

## Protocol lens commands (v7.5)

Protocol Lens Packs model a specific protocol family so review lanes, tasks, and
evidence requirements are protocol-aware. The first lens is Fixed Credit Market
(`fixed-credit-market`). A lens is a model, not a finding; a review lane is not a
vulnerability; an evidence score is not vulnerability validity; a candidate with
evidence is not confirmed. The lens layer ships in the v7.5.0 package and
carries its own schema version. See
[`V7_5_PROTOCOL_LENS.md`](V7_5_PROTOCOL_LENS.md) and
[`FIXED_CREDIT_MARKET_LENS.md`](FIXED_CREDIT_MARKET_LENS.md).

Exit behavior: `lens-list` exits `0`; the analysis commands (`lens-map`,
`lens-lanes`, `lens-tasks`, `lens-pack`, `lens-evidence`, `lens-report-filter`) exit
`1` as a heuristic, human-review-required warning (not a crash) and `2` only on
invalid usage or a runtime error. In CI, read the `--json` decision fields rather
than gating on the analysis exit code.

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx lens-list` | List implemented (and planned) protocol lenses | human + `--json` | none | stable-additive |
| `arkheionx lens-map` | Build a protocol-aware map: extracted protocol model, scope map, behavior promises, and economic invariants for the chosen lens | human + `--json` | `lens-map/lens-map.{md,json}` | stable-additive |
| `arkheionx lens-lanes` | Generate protocol-aware review lanes from the lens plus repository surfaces and scope; lane priority is review order, not severity | human + `--json` | `lens-lanes/lens-lanes.{md,json}` | stable-additive |
| `arkheionx lens-tasks` | Turn lens review lanes into precise, bounded, evidence-oriented tasks; tasks are research instructions, not exploit instructions | human + `--json` | `lens-tasks/lens-tasks.{md,json}` | stable-additive |
| `arkheionx lens-pack` | Generate a complete local lens pack (run context, scope map, protocol model, value-flow map, behavior promises, economic invariants, temporal windows, periphery bundle map, evidence map, review lanes, scope tasks, blind-spot ranking, evidence rubric, report filter, agent input, JSON). Writes by default | human + `--json` (manifest) | `lens-pack/<lens>/*` | stable-additive |
| `arkheionx lens-evidence` | Classify each economic invariant's local-test coverage into one of nine evidence statuses; evidence quality is not vulnerability validity | human + `--json` | `lens-evidence/lens-evidence.{md,json}` | stable-additive |
| `arkheionx lens-report-filter` | Classify lens report candidates against scope before submission with a pre-submission checklist; not final triage and never says "submit now" | human + `--json` | `lens-report-filter/lens-report-filter.{md,json}` | stable-additive |

## Setup and lifecycle commands

| Command | Purpose | Stability |
| --- | --- | --- |
| `arkheionx version` | Package + milestone metadata | stable |
| `arkheionx doctor` | Install / Foundry / project diagnosis (`--install`) | stable-additive |
| `arkheionx demo` | List/show/copy safe local demos (`--list/--show/--commands/--copy`) | stable-additive |
| `arkheionx help` | Print CLI help | stable |

## Legacy / advanced commands

| Command | Purpose | Stability |
| --- | --- | --- |
| `arkheionx scan` | Local pre-audit readiness scan | internal/legacy |
| `arkheionx validate-config` | Validate a local Arkheionx config | internal/legacy |
| `arkheionx test-plan` | Generate defensive test plans | internal/legacy |
| `arkheionx search` | Search local security-memory metadata | internal/legacy |

## Shell scripts

| Script | Purpose | Stability |
| --- | --- | --- |
| `install.sh` | Safe local installer (pipx/venv, no sudo) | stable |
| `uninstall.sh` | Remove Arkheionx-managed paths | stable |
| `arkup` | Install/update lifecycle helper (MVP) | stable-additive |

## Exit codes

`0` ok or clean validation, `1` attention/review-guidance/validation issue,
`2` invalid usage/failure, `3` safety rejection (config).
`validate-artifacts` uses `1` for validation issues in v3.2.0; a dedicated
artifact-validation failure code is deferred. See
[`CLI_REFERENCE.md`](CLI_REFERENCE.md).
