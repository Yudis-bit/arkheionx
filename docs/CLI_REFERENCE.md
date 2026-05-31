# Arkheionx CLI Reference

Arkheionx v2.0.1 supports the installable console command, the module CLI, and
the stable script surface as the current functional foundation for local
value-flow review:

```sh
arkheionx scan .
python3 -m arkheionx.cli.main scan .
python3 scripts/pre_audit_scan.py --root .
```

The scanner is local/static. It does not require RPC, private keys, mnemonics,
or live-chain access. Current commands help produce review reports, missing
test prompts, issue plans, SARIF, and security-memory lookups. The future
`arkheionx flow` command family is planned, not available in v2.0.1.

For the full public command + script inventory with stability labels, see
[`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md). For what stays stable into v3.0, see
[`STABILITY_CONTRACT.md`](STABILITY_CONTRACT.md).

## Current Commands

- `arkheionx scan`
- `arkheionx test-plan`
- `arkheionx search`
- `arkheionx validate-config`
- `arkheionx demo`
- `arkheionx doctor`
- `arkheionx version`

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
- `arkheionx evidence <repo> --target Contract.function` — evidence package (also `--from-proof`).
- `arkheionx report <repo> --target Contract.function` — responsible report draft (also `--from-evidence`).
- `arkheionx evidence-status <repo>` — which proof/evidence/report artifacts exist per target (`--target`, `--json`).
- `arkheionx validate-artifacts <repo>` — validate generated artifacts (`--json`; exit 0 valid / 1 issues / 2 failure).

Shared flags: `--full`, `--show-all`, `--json`, `--build`, `--no-artifacts`,
`--top N` (`--mermaid` for `flow`). Evidence levels: `HEURISTIC`,
`COMPILER_CONFIRMED`, `EXECUTION_CONFIRMED`, `EVIDENCE_READY`. See
[`PROTOCOL_MAP.md`](PROTOCOL_MAP.md), [`EXECUTION_PROOF.md`](EXECUTION_PROOF.md),
[`TRACE_ENGINE.md`](TRACE_ENGINE.md), [`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md),
and [`REPORT_DRAFTS.md`](REPORT_DRAFTS.md).

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

These commands are roadmap items and are not available in v2.0.1:

- `arkheionx flow`
- `arkheionx flow --test-gaps`
- `arkheionx flow explain`
- `arkheionx flow test-template`
- `arkheionx flow review-map`
- `arkheionx flow verify`

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
