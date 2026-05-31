# Arkheionx

<p align="center">
  <strong>Foundry-style local security workbench for DeFi protocol research.</strong>
</p>

<p align="center">
  <strong>Find the money. Map the protocol. Prove the path.</strong>
</p>

<p align="center">
  <code>Stable: v2.8.0</code> ·
  <code>Python 3.11+</code> ·
  <code>Local-first</code> ·
  <code>No RPC by default</code> ·
  <code>Foundry-aware</code>
</p>

<p align="center">
  <img src="docs/assets/arkheionx-workflow-v27.svg" alt="Arkheionx workflow: install, doctor/open, map/flow/hunt, prove/trace, evidence/report, validate/review" width="900">
</p>

Arkheionx turns a DeFi codebase into a focused local research workflow:

- a protocol map
- a money-flow graph
- a ranked hunter plan
- a local Foundry proof workflow
- trace summaries, evidence packages, and responsible report drafts

Foundry proves. Arkheionx maps, ranks, guides, summarizes, validates, and
packages the evidence — locally, with no RPC and no secrets.

## Why Arkheionx

Foundry tells you whether tests pass. Arkheionx helps you decide what to test
first, then packages the result for human review.

- Map where value enters, exits, and is controlled.
- Rank high-signal review targets instead of guessing.
- Run targeted local proof workflows.
- Turn proof/trace output into evidence and report drafts with honest evidence
  levels.

## Core Workflow

```mermaid
flowchart LR
  Install["install / arkup"] --> Open["doctor / open"]
  Open --> Hunt["map / flow / hunt"]
  Hunt --> Prove["prove --run / trace"]
  Prove --> Evidence["evidence / report"]
  Evidence --> Review["validate / human review"]
```

## 60-Second Quickstart

Install (local-first, no sudo, no PyPI):

```sh
sh install.sh
arkheionx doctor
```

Try the bundled demo (local-only, no RPC):

```sh
arkheionx demo --list
arkheionx demo --copy oracle-staking ./arkheionx-demo
arkheionx open ./arkheionx-demo
arkheionx hunt ./arkheionx-demo --top 5
```

Bundled demos cover staking (`oracle-staking`), AMM (`amm-swap`), and lending
(`lending-vault`) surfaces. Demo fixtures ship as package data, so `demo --copy`
works from an installed
Arkheionx, not only a source checkout ([`docs/PACKAGE_DATA.md`](docs/PACKAGE_DATA.md)).

Run the full loop on a repo you own or are authorized to review:

```sh
arkheionx open .
arkheionx hunt . --top 5
arkheionx prove . --target Contract.function --run
arkheionx trace . --target Contract.function
arkheionx evidence . --target Contract.function
arkheionx report . --target Contract.function
```

If proof artifacts do not exist yet, Arkheionx prints the next command instead
of crashing. See [`docs/DEMO_WORKFLOW.md`](docs/DEMO_WORKFLOW.md) for the full
guided run.

## Command Set

| Command              | Purpose                                            |
| -------------------- | -------------------------------------------------- |
| `demo`               | List and copy a safe local demo workflow           |
| `doctor`             | Check install, Foundry, and project layout         |
| `open`               | One-command project orientation                    |
| `map`                | Show protocol roles, journeys, and money flow      |
| `flow`               | Build the money-flow graph                         |
| `hunt`               | Rank bug-hunting surfaces                          |
| `prove`              | Generate or run a targeted local Foundry proof     |
| `trace`              | Summarize proof/trace output                       |
| `evidence`           | Package proof and trace artifacts                  |
| `report`             | Create a responsible local report draft            |
| `evidence-status`    | Show which artifacts exist per target              |
| `validate-artifacts` | Validate generated proof/evidence/report artifacts |

Install lifecycle: `sh install.sh`, `sh arkup --check`, `sh uninstall.sh`.
Legacy/advanced commands (`scan`, `validate-config`, `test-plan`, `search`)
remain supported for specialized workflows.

## Outputs

Every run writes deterministic local artifacts under `.arkheionx/out/`
(gitignored):

- protocol understanding and a money-flow graph (JSON + Mermaid)
- a ranked hunter plan of high-signal review targets
- Foundry proof scaffolds and execution summaries
- compact trace summaries
- structured evidence packages
- responsible report drafts labelled for human review

## Evidence Model

Arkheionx keeps evidence levels explicit so a local finding is not overstated.

- `HEURISTIC` - static analysis and pattern matching only.
- `COMPILER_CONFIRMED` - the target compiles in the local project.
- `EXECUTION_CONFIRMED` - a relevant local Foundry test executed.
- `EVIDENCE_READY` - proof and trace artifacts are packaged for review.

A passing test does not prove absence of bugs. A failing test does not
automatically prove a vulnerability. Human review is required.

## Safety Boundaries

- Local repository analysis only.
- No RPC by default.
- No live-chain mutation.
- No private keys or secrets.
- No transaction broadcasting.
- No automated exploitation.
- No auto-submit.
- No guaranteed vulnerability discovery.
- Not an audit, certification, or replacement for manual review.
- No severity guarantee.
- Use only on repositories you own or are authorized to review.

## Install / Requirements

- Python 3.11+.
- Foundry is optional but recommended for compiler and execution confirmation.
- Local install is the supported path. No PyPI package is published.

```sh
sh install.sh                # safe local installer (pipx or venv, no sudo)
sh arkup --check             # inspect/update an existing install (MVP)
python3 -m pip install -e .  # or a plain editable install
arkheionx doctor
```

See [`docs/INSTALLER.md`](docs/INSTALLER.md) and [`docs/ARKUP.md`](docs/ARKUP.md)
for options and the install/update lifecycle, and
[`docs/UNINSTALL.md`](docs/UNINSTALL.md) to remove it.

## Documentation

Start:

- [`docs/INSTALLATION.md`](docs/INSTALLATION.md)
- [`docs/DEMO_WORKFLOW.md`](docs/DEMO_WORKFLOW.md)
- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md)
- [`docs/SOLO_RESEARCH_WORKFLOW.md`](docs/SOLO_RESEARCH_WORKFLOW.md)

Core workflow:

- [`docs/PROTOCOL_MAP.md`](docs/PROTOCOL_MAP.md)
- [`docs/VALUE_FLOW_WORKBENCH.md`](docs/VALUE_FLOW_WORKBENCH.md)
- [`docs/EXECUTION_PROOF.md`](docs/EXECUTION_PROOF.md)
- [`docs/TRACE_ENGINE.md`](docs/TRACE_ENGINE.md)
- [`docs/EVIDENCE_PACKAGE.md`](docs/EVIDENCE_PACKAGE.md)
- [`docs/REPORT_DRAFTS.md`](docs/REPORT_DRAFTS.md)

Advanced:

- [`docs/ARKUP.md`](docs/ARKUP.md) · [`docs/UPDATE_FLOW.md`](docs/UPDATE_FLOW.md)
- [`docs/GITHUB_ACTION_USAGE.md`](docs/GITHUB_ACTION_USAGE.md)
- [`docs/SARIF_OUTPUT.md`](docs/SARIF_OUTPUT.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)

## Current Release

Latest stable release: **v2.8.0 — Package Data & Distribution Hardening**.

```text
doctor -> open -> map -> flow -> hunt -> prove --run -> trace -> evidence -> report -> manual review
```

Current milestone: **v2.8.0 — Package Data & Distribution Hardening** (shipped).
Active development: **v2.9.0 — Multi-Fixture Demo Expansion & Public Workflow Hardening**. See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## GitHub Action

Minimal static pre-audit workflow:

```yaml
- uses: actions/checkout@v4
- uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v2.8.0
  with:
    protocol-type: "auto"
```

See [`docs/GITHUB_ACTION_USAGE.md`](docs/GITHUB_ACTION_USAGE.md) for options.

## Research Archive

Arkheionx began as a defensive DeFi exploit-reproduction archive, still
available as background research material:

- [`docs/VULNERABILITY_REGISTRY.md`](docs/VULNERABILITY_REGISTRY.md)
- [`reports/research_dashboard.md`](reports/research_dashboard.md)

## Maintainer

Built by Yudistira Putra / [@Yudis-bit](https://github.com/Yudis-bit).
Arkheionx prioritizes local-first analysis, honest evidence levels, safe
workflows, and human review.

## License / Disclaimer

Defensive research and authorized review only. Not security, legal, or
investment advice.
