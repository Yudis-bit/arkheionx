# Arkheionx CLI Reference

## Start here: the command ladder

The canonical first run is `arkheionx review-map .`. Work down the ladder:

```sh
arkheionx version          # confirm the install
arkheionx doctor           # check environment + project layout
arkheionx review-map .     # build the local review map (start here)
arkheionx value-paths .    # where value enters, moves, exits
arkheionx assumptions .    # the trust each path depends on
arkheionx test-gap-map .   # value-sensitive functions with missing tests
arkheionx proof-plan .     # a local proof direction to try by hand
```

Try the bundled demo: `arkheionx review-map examples/vault-strategy-oracle-fixture`.

## Stable V4 commands

V4 stabilizes the local review-map workflow. These run on any install (editable
or non-editable), are local/static, and need no RPC, private keys, or secrets:
`version`, `doctor`, `review-map`, `value-paths`, `assumptions`, `test-gap-map`,
`proof-plan`.

## Research memory commands (v4.1)

Three additive, local/static commands extend the workflow for AI-assisted
review. They build on the review map, emit human Markdown and `--json`, and
write artifacts under `.arkheionx/research/` (unless `--no-write`). Hypotheses
are review prompts, not findings; `manual_review_required` stays true.

- `arkheionx agent-brief <path>` — an AI-agent-ready brief: repository summary,
  coverage weakness ranking, value movement, test gaps, authorization surfaces,
  periphery/core surfaces, behavior-mismatch surfaces, open hypotheses, and a
  do-not-claim boundary. `--out <dir>`, `--json`, `--no-write`, `--top`.
- `arkheionx hypothesis-log <path>` — a structured hypothesis log and
  rejected-finding memory. Every hypothesis starts at `open` with empty fields
  for test command, result, rejection reason, confirmation notes, and human
  decision. `--out <dir>`, `--json`, `--no-write`.
- `arkheionx case-study <path>` — a sanitized case-study / research-session
  report. `--from <dir>` incorporates a hypothesis log's statuses; `--out` may
  be a directory or a `.md` file path. Makes no vulnerability claim unless a
  finding is independently confirmed.

See [`V4_1_RESEARCH_WORKFLOW.md`](V4_1_RESEARCH_WORKFLOW.md) and
[`RESEARCH_MEMORY_MODEL.md`](RESEARCH_MEMORY_MODEL.md).

## Blind spot intelligence commands (v5)

Four additive, local/static commands add the Blind Spot Intelligence layer. They
build on the review map and the v4.1 research surfaces, emit human Markdown and
`--json`, and write artifacts under `.arkheionx/` (unless `--no-write`). Blind
spot candidates are not vulnerabilities, criticality potential is not severity,
and counterfactuals are research prompts, not findings; `manual_review_required`
stays true.

- `arkheionx blind-spots <path>` — rank likely blind-spot candidates (high-impact
  surfaces with weak review evidence) with a transparent additive score
  (impact + review-gap + complexity + assumption), per-candidate reasons, a
  suggested counterfactual, a local test direction, the evidence needed, unknown
  surfaces, and notable non-blind-spots. `--out <dir>`, `--json`, `--no-write`,
  `--limit <n>`, `--top`.
- `arkheionx criticality-map <path>` — map criticality potential (heuristic blast
  radius, never severity) across surfaces by dimension, with highest-blast-radius
  and criticality-vs-review-density views. `--out <dir>`, `--json`, `--no-write`.
- `arkheionx counterfactuals <path>` — negate guarding assumptions into testable
  "what if this assumption is false?" research prompts, each with a local test
  direction, the evidence required, and a stop condition, plus a counterfactual
  matrix. `--out <dir>`, `--json`, `--no-write`.
- `arkheionx research-pack <path>` — generate a complete local, vendor-agnostic
  research pack (README, review-map summary, blind spots, criticality map,
  counterfactuals, agent brief, hypotheses, evidence log, do-not-claim,
  case-study template, and a JSON manifest). Writes by default. `--out <dir>`,
  `--json` (manifest), `--no-write`.

See [`BLIND_SPOT_INTELLIGENCE.md`](BLIND_SPOT_INTELLIGENCE.md) and
[`V5_WORKFLOW.md`](V5_WORKFLOW.md).

## Evidence graph commands (v6)

Four additive, local/static commands add the Evidence Graph + Interaction Matrix
layer. They build on the review map, the v4.1 research surfaces, and the v5
blind-spot layer, emit human Markdown and `--json`, and write artifacts under
`.arkheionx/` (unless `--no-write`). An evidence state is not a vulnerability
claim, confirmed-candidate is not a confirmed vulnerability, interaction priority
is not severity, and unresolved does not mean vulnerable; `human_review_required`
stays true.

- `arkheionx evidence-graph <path>` — classify every important review surface
  into an evidence state (tested, rejected-with-evidence, confirmed-candidate,
  unresolved, insufficient-evidence, needs-human-review, unclassified,
  out-of-scope) with an evidence strength, criticality potential, the
  missing-evidence gaps, and a next local test direction. `--out <dir>`,
  `--json`, `--no-write`, `--top`, `--only-unresolved`.
- `arkheionx interaction-matrix <path>` — detect meaningful combinations of
  surfaces that may hide bugs when tested together, scored by a transparent
  additive interaction priority (impact + review-gap + complexity), with an
  interaction test plan. `--out <dir>`, `--json`, `--no-write`, `--top`,
  `--only-unresolved`.
- `arkheionx unresolved-map <path>` — compose the evidence graph and interaction
  matrix into the high-impact unresolved surfaces, high-impact unresolved
  interactions, unclassified surfaces, and a final review checklist. `--out
  <dir>`, `--json`, `--no-write`, `--top`.
- `arkheionx complete-review <path>` — generate a complete local, vendor-agnostic
  V6 review package (review-map summary, blind spots, criticality,
  counterfactuals, evidence graph, interaction matrix, unresolved surfaces, a
  model-agnostic agent input, a human review checklist, a case-study template,
  and a JSON manifest). Writes by default. `--out <dir>`, `--json` (manifest),
  `--no-write`, `--top`.

See [`EVIDENCE_GRAPH.md`](EVIDENCE_GRAPH.md),
[`INTERACTION_MATRIX.md`](INTERACTION_MATRIX.md),
[`UNRESOLVED_MAP.md`](UNRESOLVED_MAP.md),
[`COMPLETE_REVIEW.md`](COMPLETE_REVIEW.md), and
[`V6_WORKFLOW.md`](V6_WORKFLOW.md). The supported surface is tracked in
[`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md).

## Scope-aware orchestration commands (v7)

Six additive, local/static commands turn an audit/contest/program scope note into
review lanes, scope tasks, evidence requirements, and report filters. They accept
an optional `--scope-file <markdown>`, emit human Markdown and `--json`, and write
artifacts under `.arkheionx/` (unless `--no-write`). A scope map, review lane, or
scope task is a planning artifact, not a finding; evidence quality is not
vulnerability validity; candidate-with-evidence is not a confirmed vulnerability;
and a report candidate is not final triage. `human_review_required` stays true.

- `arkheionx scope-map <path> --scope-file <md>` — parse a scope note into
  structured review rules (in/out of scope, severity conditions, trusted and
  dependency assumptions, known/accepted issues, prior-audit notes, design
  choices, invariants, focus areas, do-not-waste-time filters, report-candidate
  requirements). `--out <dir>`, `--json`, `--no-write`, `--top`.
- `arkheionx scope-lanes <path> --scope-file <md>` — generate scope-aware review
  lanes (priority, targets, hypotheses, required evidence, known/accepted filters,
  stop condition). `--out <dir>`, `--json`, `--no-write`, `--top`.
- `arkheionx scope-tasks <path> --scope-file <md>` — turn lanes into precise,
  bounded, evidence-oriented tasks. `--out <dir>`, `--json`, `--no-write`, `--top`.
- `arkheionx scope-pack <path> --scope-file <md>` — bundle a complete local
  scope-aware research pack (scope map, lanes, tasks, do-not-waste-time, evidence
  template/rubric, report-filter checklist, human review checklist, agent input,
  case-study template, JSON manifest + sidecars). Writes by default. `--out <dir>`,
  `--json` (manifest), `--no-write`, `--top`.
- `arkheionx evidence-judge <path>` — grade whether local tests/evidence prove the
  intended task on a transparent rubric. `--scope-file <md>`, `--tasks-file <json>`,
  `--evidence-dir <dir>`, `--out <dir>`, `--json`, `--no-write`, `--top`.
- `arkheionx report-filter <path> --scope-file <md>` — classify report candidates
  against the scope before submission, with a human pre-submission checklist.
  `--out <dir>`, `--json`, `--no-write`, `--top`.

See [`SCOPE_ORCHESTRATION.md`](SCOPE_ORCHESTRATION.md), [`SCOPE_MAP.md`](SCOPE_MAP.md),
[`SCOPE_TASKS.md`](SCOPE_TASKS.md), [`EVIDENCE_JUDGE.md`](EVIDENCE_JUDGE.md),
[`REPORT_FILTER.md`](REPORT_FILTER.md), and [`V7_WORKFLOW.md`](V7_WORKFLOW.md).

## Exit codes

- `0` — success; for review commands, no review guidance was surfaced.
- `1` — review guidance is present. For `review-map` and the focused views this
  is **intentional** (there is something to inspect), not a crash.
- `2` — usage or input error (bad path, bad flags, or a source-tree-only helper
  that is not available in the installed wheel).

## Output formats

- **Human** — default terminal output (ranked "inspect first" list + next steps).
- **`--json`** — structured payload for tooling.
- **Artifacts** — written under `.arkheionx/out/review-map/` (gitignored): a
  Markdown review map, a Test Gap Map, and JSON views. Each test gap carries a
  `Source: <file>:<line>` reference from the parsed source.

## Advanced / source-tree commands

The legacy scanner surface remains available but is **not** the canonical first
run. Run it from a repository checkout:

```sh
arkheionx scan .
python3 -m arkheionx.cli.main scan .
python3 scripts/pre_audit_scan.py --root .
```

The scanner and workbench commands are local/static by default. They do not
require RPC, private keys, seed phrases, or live-chain access. Current commands
help produce review maps, Test Gap Map artifacts, proof/evidence artifacts,
report drafts, readiness reports, issue plans, SARIF, and security-memory
lookups.

For the full public command + script inventory with stability labels, see
[`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md). For what stays stable into v3.0, see
[`STABILITY_CONTRACT.md`](STABILITY_CONTRACT.md).

The release-prep v3.5.0 Protocol Intelligence Model is internal infrastructure
(`arkheionx/intelligence/`) and adds no new CLI command. The command surface
below is unchanged.

The v3.8.0 Protocol Intelligence Core (function-role taxonomy, value-path graph
model, assumption engine, test-gap engine, protocol graph builder, and
local-validation coverage correlation) is also internal infrastructure under
`arkheionx/intelligence/`. It adds **no new CLI command** and **no new flags**,
and changes no existing CLI output. There is no public protocol-graph generator
command. `arkheionx local-validate` is unchanged. `arkheionx review-package` is
unchanged except that, when optional protocol-graph artifacts already exist under
`.arkheionx/out/protocol-graph/`, they are included automatically — its
`artifact_count` may rise, with no new flag and no changed output key, and
`manual_review_required` stays true and `ready_for_submission` stays false. See
[`PROTOCOL_INTELLIGENCE_CORE.md`](PROTOCOL_INTELLIGENCE_CORE.md) and
[`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md). v3.8.0 is active branch
work, not a finalized or published release.

## Current Commands

- `arkheionx scan`
- `arkheionx test-plan`
- `arkheionx search`
- `arkheionx validate-config`
- `arkheionx demo`
- `arkheionx doctor`
- `arkheionx version`
- `arkheionx open`
- `arkheionx map`
- `arkheionx flow`
- `arkheionx hunt`
- `arkheionx prove`
- `arkheionx trace`
- `arkheionx evidence`
- `arkheionx report`
- `arkheionx evidence-status`
- `arkheionx validate-artifacts`
- `arkheionx agent-brief`
- `arkheionx hypothesis-log`
- `arkheionx case-study`
- `arkheionx blind-spots`
- `arkheionx criticality-map`
- `arkheionx counterfactuals`
- `arkheionx research-pack`
- `arkheionx evidence-graph`
- `arkheionx interaction-matrix`
- `arkheionx unresolved-map`
- `arkheionx complete-review`
- `arkheionx scope-map`
- `arkheionx scope-lanes`
- `arkheionx scope-tasks`
- `arkheionx scope-pack`
- `arkheionx evidence-judge`
- `arkheionx report-filter`
- `arkheionx review-map`
- `arkheionx test-gap-map`
- `arkheionx value-paths`
- `arkheionx assumptions`
- `arkheionx proof-plan`
- `arkheionx evidence-links`

## Terminal color

Human-facing output uses restrained color when stdout is a TTY: bold headings,
green/yellow/red statuses, and evidence levels colored by level. Color is
disabled automatically for pipes, captured output, and CI, and is never applied
to `--json` output or to files written under `.arkheionx/out/`.

- `ARKHEIONX_COLOR=auto` (default) — color only on a TTY.
- `ARKHEIONX_COLOR=always` — force color on.
- `ARKHEIONX_COLOR=never` or `NO_COLOR` — force color off.

## Demo

Guided, local-only demo workflows (no RPC, no secrets, no mainnet):

- `arkheionx demo --list` — list available demos.
- `arkheionx demo --show <id>` — demo details, target, and safety notice (`--json`).
- `arkheionx demo --commands <id>` — print the heuristic and Foundry-backed command sequences.
- `arkheionx demo --copy <id> <dest>` — copy the fixture (source entries only) to `<dest>`; refuses a non-empty destination unless `--force`.

Available demos: `oracle-staking` (staking), `amm-swap` (amm),
`lending-vault` (lending). Example:

```sh
arkheionx demo --copy amm-swap ./demo-amm
arkheionx hunt ./demo-amm --top 5
```

Demo fixtures are bundled as package data and work from an installed package
(see [`PACKAGE_DATA.md`](PACKAGE_DATA.md)).

See [`DEMO_WORKFLOW.md`](DEMO_WORKFLOW.md).

## Workbench Commands

The Foundry-style workbench commands are available now:

- `arkheionx open <repo>` — one-command project understanding.
- `arkheionx map <repo>` — protocol map (roles, journeys, money flow).
- `arkheionx flow <repo>` — money-flow graph (Mermaid + JSON).
- `arkheionx hunt <repo>` — ranked bug-hunting surfaces.
- `arkheionx prove <repo> --target Contract.function [--run]` — Foundry proof scaffold / execution.
- `arkheionx trace <repo> --target Contract.function [--run]` — proof/trace summary.
- `arkheionx evidence <repo> --target Contract.function` — evidence package (also `--from-proof`; trace-bounded for `EVIDENCE_READY`).
- `arkheionx report <repo> --target Contract.function` — responsible report draft with evidence/receipt context (also `--from-evidence`).
- `arkheionx evidence-status <repo>` — which proof/evidence/report artifacts exist per target (`--target`, `--json`).
- `arkheionx validate-artifacts <repo>` — validate generated artifacts (`--json`; exit 0 valid / 1 issues or review attention / 2 command-input failure).
- `arkheionx review-map <repo>` — build a local protocol review map: contracts, value paths, assumptions, test gaps, proof suggestions, and evidence links (`--out`, `--top`, `--json`, `--no-write`, `--include-low-confidence`, `--target`). See [`REVIEW_MAP.md`](REVIEW_MAP.md).
- `arkheionx test-gap-map <repo>` — focused Test Gap Map view. Reads an existing `review-map/test-gap-map.json` when present, or derives it from the existing review-map builder (`--out`, `--top`, `--json`, `--no-write`, `--include-low-confidence`, `--target`). See [`REVIEW_MAP.md`](REVIEW_MAP.md).
- `arkheionx value-paths <repo>` — focused value-path view. Reads an existing `review-map/value-paths.json` when present, or derives it from the existing review-map builder (`--out`, `--top`, `--json`, `--no-write`, `--include-low-confidence`, `--target`). See [`REVIEW_MAP.md`](REVIEW_MAP.md).
- `arkheionx assumptions <repo>` — focused assumption prompt view. Reads an existing `review-map/assumptions.json` when present, or derives it from the existing review-map builder (`--out`, `--top`, `--json`, `--no-write`, `--include-low-confidence`, `--target`). See [`REVIEW_MAP.md`](REVIEW_MAP.md).
- `arkheionx proof-plan <repo>` — focused local proof-planning view. Reads an existing `review-map/proof-plan.json` when present, or derives it from the existing review-map builder (`--out`, `--top`, `--json`, `--no-write`, `--include-low-confidence`, `--target`). It does not execute proofs; use `arkheionx prove <repo> --target Contract.function --run` for execution. See [`REVIEW_MAP.md`](REVIEW_MAP.md).
- `arkheionx evidence-links <repo>` — focused evidence-link view. Reads an existing `review-map/evidence-links.json` when present, or derives it from the existing review-map builder (`--out`, `--top`, `--json`, `--no-write`, `--include-low-confidence`, `--target`). It can surface local proof/trace receipt IDs, evidence package IDs, readiness, and report draft paths when those artifacts already exist. It does not create evidence, execute proofs, or replace `arkheionx evidence <repo> --target Contract.function`. See [`REVIEW_MAP.md`](REVIEW_MAP.md).
- `arkheionx review-package <repo>` — assemble a local, reviewer-ready review package from existing `.arkheionx/out/` artifacts. Writes `.arkheionx/out/review-package/` containing `manifest.json`, `validation.json`, `README.md`, `limitations.md`, copied artifacts under `artifacts/`, and `checksums/SHA256SUMS`. Flags: `--json` (pure JSON only), `--no-write` (build/validate in memory; write nothing), `--output PATH`, `--strict` (exit `1` when validation is invalid or reports errors), `--exclude-unknown`, `--no-copy-artifacts`, `--export zip` (also write a deterministic local archive under `review-package/exports/arkheionx-review-package-<id>.zip`), `--export-output PATH`, `--include-protocol-model` (default on), `--no-protocol-model`. JSON includes `command`, `package_root`, `manifest_path`, `validation_path`, `readme_path`, `limitations_path`, `checksums_path`, `artifact_count`, `validation_status`, `manual_review_required`, `ready_for_submission`, `written`, `no_write`, `warnings`, `errors`, and (with `--export`) `export_requested`, `export_format`, `export_path`, `export_id`, `export_status`, `export_file_count`, `export_size_bytes`, `export_checksum_sha256`, `export_written`. The export is a deterministic ZIP (fixed 1980 timestamps, sorted relative `arkheionx-review-package/...` entries) that includes `manifest.json`, `validation.json`, `README.md`, `limitations.md`, `artifacts/`, and `checksums/SHA256SUMS`, and excludes the archive itself, the `exports/` directory, caches, and VCS metadata. `--no-write` writes no archive; `--strict` blocks the archive when validation is invalid. When buildable, a `protocol-model.json` sidecar is written under `artifacts/intelligence/` (built additively from existing review-map output, with the absolute `repo_path` scrubbed and no added timestamp) and package-level cross-reference checks resolve packaged IDs against it by exact match or explicit alias only — unresolved references are warnings, never invented or fuzzy-matched links; a missing model is a warning, not a failure. JSON adds `protocol_model_requested`, `protocol_model_included`, `protocol_model_path`, `protocol_model_id`, `crossref_check_count`, `crossref_warning_count`, and `crossref_error_count`. It builds no archive by default, records only repo-relative paths, never includes secret values, is local-only and not published, keeps `manual_review_required` true and `ready_for_submission` false, and makes no confirmed-vulnerability, final-severity, audit-passed, or bounty-eligibility claim. Review guidance only.

- `arkheionx local-validate <repo> --input PATH` — ingest a saved Foundry test output file into local validation artifacts. It reads the saved output only; it does not run `forge`, requires no Foundry install, spawns no subprocess, and uses no RPC, fork-url, private keys, or live-chain behavior. It parses the file, builds deterministic run/test-result/summary records (linking to a protocol model by exact match only when one is provided), and unless `--no-write` writes `.arkheionx/out/local-validation/` containing `summary.json`, `run.json`, `results/<id>.json`, optional `traces/<id>.json`, `artifacts-index.json`, and `checksums/SHA256SUMS`. Flags: `--json` (pure JSON only), `--no-write` (parse/build in memory; write nothing), `--output PATH` (must be inside the repo), `--format auto|foundry-json|foundry-text` (default `auto`), `--tool foundry`, `--command TEXT` (recorded for provenance only; never executed). JSON includes `command`, `repo_path`, `input_path`, `input_format`, `tool`, `no_write`, `written`, `output_root`, `summary_path`, `run_path`, `artifacts_index_path`, `checksums_path`, `total_tests`, `passed_tests`, `failed_tests`, `skipped_tests`, `errored_tests`, `unknown_tests`, `validation_status`, `run_id`, `summary_id`, `test_result_count`, `trace_receipt_count`, `artifact_count`, `written_file_count`, `manual_review_required`, `ready_for_submission`, `warnings`, and `errors`. Exit codes: `0` success, `2` invalid repo/input/format, `1` an unexpected build/write error. A passing local test supports only a tested signal and is never a confirmed vulnerability; a failing local test needs manual review and is not a confirmed vulnerability. It records only repo-relative paths, includes no secret values, keeps `manual_review_required` true and `ready_for_submission` false, and makes no confirmed-vulnerability, final-severity, audit-passed, or bounty-eligibility claim. Review guidance only. See [`LOCAL_VALIDATION.md`](LOCAL_VALIDATION.md) and [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md).

Shared flags: `--full`, `--show-all`, `--json`, `--build`, `--no-artifacts`,
`--top N` (`--mermaid` for `flow`). Evidence levels: `HEURISTIC`,
`COMPILER_CONFIRMED`, `EXECUTION_CONFIRMED`, `EVIDENCE_READY`. See
[`PROTOCOL_MAP.md`](PROTOCOL_MAP.md), [`EXECUTION_PROOF.md`](EXECUTION_PROOF.md),
[`TRACE_ENGINE.md`](TRACE_ENGINE.md), [`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md),
and [`REPORT_DRAFTS.md`](REPORT_DRAFTS.md).

`review-map` emits Test Gap Map artifacts (`test-gap-map.json` and
`test-gap-map.md`) under `.arkheionx/out/review-map/`. v3.3.0 added
`arkheionx test-gap-map` as a focused read/build command for that same derived
payload.

`review-map` also emits `value-paths.json` under the same directory. The
v3.3.0 surface adds `arkheionx value-paths` as a focused read/build command for
that artifact-compatible payload. It does not wrap the JSON or alter
`review-map --json`.

`review-map` also emits `assumptions.json`. The v3.3.0 surface adds
`arkheionx assumptions` as a focused read/build command for that
artifact-compatible payload. It emits the same JSON shape as the artifact and
does not alter `review-map --json`.

`review-map` also emits `proof-plan.json`. The v3.3.0 surface adds
`arkheionx proof-plan` as a focused read/build command for that
artifact-compatible payload. It shows suggested local proof outlines only; it
does not run Foundry or create proof/evidence/report execution artifacts.

`review-map` also emits `evidence-links.json`. The v3.3.0 surface adds
`arkheionx evidence-links` as a focused read/build command for that
artifact-compatible payload. It shows references to existing local
proof/trace/evidence/report artifacts only. In v3.4.0 it can also
show copied proof/trace receipt IDs, evidence package IDs, readiness buckets,
and report draft links when local artifacts already contain them. It does not
create evidence, execute proofs, promote evidence levels, or alter
`review-map --json` beyond additive evidence-link contents.

In v3.4.0, evidence packages include deterministic
`evidence_package_id` values and additive manifests with proof/trace source
records and readiness checks. Report drafts include `evidence_context`,
`receipt_references`, `report_readiness`, and bounded `claim_references`; they
remain draft/manual-review only and never emit `HUMAN_REVIEWED` automatically.

For strict CI around artifact validation in v3.2.0, use
`arkheionx validate-artifacts <repo> --json` and fail on `status != "ok"` until
a dedicated strict mode or artifact-validation failure code exists.

## Install & Onboarding

- `arkheionx doctor` — install, Foundry, and project-layout diagnosis.
- `arkheionx doctor --install` — focused install-health view: resolved command
  path, Python executable, package import/version, optional Foundry status, and
  a PATH hint. Exit `0`.

Local install/uninstall helpers live at the repository root:

```sh
sh install.sh --help
sh uninstall.sh --help
sh arkup --help
```

`arkup` is the MVP install/update lifecycle helper: `sh arkup --check`,
`sh arkup --install`, `sh arkup --update`, `sh arkup --uninstall`. It reads the
local install receipt (`~/.arkheionx/install.json`) and keeps your recorded
source kind (stable/main/ref/local) on update.

They use no root, edit no shell profile, ask for no secrets, and make no RPC or
live-chain calls. Arkheionx is not published to PyPI. See
[`INSTALLER.md`](INSTALLER.md), [`UNINSTALL.md`](UNINSTALL.md),
[`ARKUP.md`](ARKUP.md), [`UPDATE_FLOW.md`](UPDATE_FLOW.md),
[`ONBOARDING.md`](ONBOARDING.md), and [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

## Planned Future Commands

These commands and workspace surfaces are roadmap items, not current v3.2.0
runtime features:

- additional focused review-map commands beyond the current artifact views;
- first-class workspace baselines, diffs, sessions, reviewer notes, policy
  profiles, and review packages.

## Core

| Flag | Default | Purpose |
|---|---|---|
| `--root PATH` | `.` | Repository root to scan. |
| `--protocol-type TYPE` | `auto` | Protocol hint: `auto`, `generic`, `vault`, `oracle`, `access-control`, `rewards`, `staking`, `amm`, `lending`, or `hybrid`. |
| `--output PATH` | `ARKHEIONX_PRE_AUDIT_REPORT.md` | Markdown pre-audit readiness report. |
| `--json-output PATH` | empty | Machine-readable JSON report. |

`auto` can detect hybrid repositories through rule-pack signals. For example,
an AMM price dependency inside a lending-shaped market can emit both `ARK-AMM-*`
and `ARK-LEND-*` readiness findings even when the primary protocol label is a
single best-fit type.

## Reports

| Flag | Purpose |
|---|---|
| `--summary-output PATH` | GitHub Actions summary Markdown. |
| `--comment-output PATH` | Pull request comment body. |
| `--issue-checklist-output PATH` | Markdown remediation checklist. |
| `--issue-plan-output PATH` | JSON remediation issue plan. |
| `--launch-report-output PATH` | Launch Readiness Report Markdown. |
| `--sprint-plan-output PATH` | Pre-Audit Sprint Plan Markdown. |
| `--sprint-days N` | Sprint length: `3`, `5`, `7`, or `10`. |
| `--contest-readiness-output PATH` | Contest Readiness Report Markdown. |
| `--executive-summary-output PATH` | Short executive summary Markdown. |
| `--remediation-roadmap-output PATH` | Remediation roadmap Markdown. |

Report verbosity is controlled through config `output_profile`: `concise`,
`standard`, `full`, or `ci`.

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --config examples/configs/ci.config.json \
  --output reports/ARKHEIONX_PRE_AUDIT_REPORT.md
```

See [`OUTPUT_PROFILES.md`](OUTPUT_PROFILES.md).

## Security Output

| Flag | Purpose |
|---|---|
| `--sarif-output PATH` | SARIF 2.1.0 readiness output for GitHub Code Scanning upload. |
| `--baseline-output PATH` | Compact baseline snapshot. |
| `--compare-baseline PATH` | Previous baseline for diff mode. |
| `--diff-output PATH` | Markdown diff report. |
| `--diff-json-output PATH` | JSON diff output. |

## Behavior

| Flag | Purpose |
|---|---|
| `--config PATH` | Optional `.arkheionx.json` configuration. |
| `--generate-invariant-skeletons` | Generate safe local Foundry invariant skeletons. |
| `--fail-score-below N` | Exit with readiness failure if score is below threshold. |
| `--fail-on-new-high` | Exit with readiness failure when diff mode finds new high/critical gaps. |
| `--fail-on-unsuppressed-high` | Exit with readiness failure when unsuppressed high/critical gaps exist. |
| `--fail-on-critical-readiness-gap` | Exit with readiness failure when critical readiness gaps exist. |

## Advanced

| Flag | Purpose |
|---|---|
| `--semantic-lite` | Enable semantic-lite Solidity extraction. Enabled by default. |
| `--no-semantic-lite` | Disable semantic-lite extraction. |
| `--slither` | Enable optional local Slither enrichment if available. |
| `--slither-json PATH` | Use an existing local Slither JSON output. |
| `--slither-output PATH` | Write normalized Arkheionx Slither summary. |
| `--slither-timeout SECONDS` | Timeout for optional Slither execution. |
| `--slither-strict` | Fail if requested Slither evidence is unavailable or warns. |
| `--min-confidence-for-issue-plan LEVEL` | Include issue-plan findings at `low`, `medium`, or `high` confidence. |
| `--create-issues` | Reserved local compatibility flag. It does not create remote issues. |
| `--verbose` | Print additional scanner details. |

## Stability Policy

Patch releases may add optional fields or flags, but v1.0.0 flags should remain
backward compatible unless a future changelog explicitly marks a breaking
change. Findings remain readiness signals, not formal audit findings or
vulnerability confirmations.

## Config Validator

v1.7.0 adds a stable config validator:

```sh
python3 scripts/validate_config.py --config examples/arkheionx.config.example.json
python3 scripts/validate_config.py --config examples/configs/minimal.config.json --json
```

The validator normalizes legacy config fields, validates protocol types,
rule-pack keys, confidence levels, suppressions, and rejects dangerous keys
such as RPC URLs, private keys, live targets, remote clone targets, or attack
modes.

## Test Plan Generator

v1.5.0 adds a companion CLI:

```sh
python3 scripts/generate_test_plan.py \
  --report examples/reports/amm-fixture-pre-audit-report.json \
  --output examples/reports/amm-fixture-test-plan.md \
  --json-output examples/reports/amm-fixture-test-plan.json \
  --foundry-output examples/reports/ArkheionxAMMInvariants.t.sol
```

| Flag | Purpose |
|---|---|
| `--report PATH` | Arkheionx JSON report input. |
| `--output PATH` | Markdown defensive test plan output. |
| `--json-output PATH` | Optional machine-readable test-plan JSON. |
| `--foundry-output PATH` | Optional Foundry invariant skeleton output. |
| `--check` | Verify committed fixture test plans are current. |

Generated skeletons are local starter scaffolds with TODO placeholders. They
are not formal verification and require human review.

## Pre-v2 Module CLI Candidate

v1.9.0 added a module CLI candidate. Existing scripts remain supported and
first-class in v2.0.1.

```sh
python3 -m arkheionx.cli.main version
python3 -m arkheionx.cli.main doctor
python3 -m arkheionx.cli.main scan examples/amm-fixture --protocol-type amm
python3 -m arkheionx.cli.main validate-config --config examples/arkheionx.config.example.json
python3 -m arkheionx.cli.main test-plan --report examples/reports/amm-fixture-pre-audit-report.json
python3 -m arkheionx.cli.main search "oracle stale price"
```

Read [`CLI_COMMANDS.md`](CLI_COMMANDS.md) and
[`CLI_MIGRATION_TO_V2.md`](CLI_MIGRATION_TO_V2.md). The module CLI does not add
RPC, live-chain, transaction, remote-cloning, deployed-contract, or
exploit-automation behavior.

## Installable Console CLI

v2.0.0 added:

```sh
python3 -m pip install -e .
arkheionx version
arkheionx doctor
arkheionx scan examples/amm-fixture --protocol-type amm
arkheionx validate-config --config examples/arkheionx.config.example.json
arkheionx test-plan --report examples/reports/amm-fixture-pre-audit-report.json
arkheionx search "oracle stale price"
```

The console entrypoint is source-tree compatible and not published to PyPI in
v2.0.1.
