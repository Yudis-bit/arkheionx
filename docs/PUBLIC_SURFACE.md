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
