# Public Command Surface

The public surface Arkheionx intends to keep stable into v3.0. Stability labels:

- **stable** — name and core behavior kept stable into v3.0; output may be polished.
- **stable-additive** — stable, with backward-compatible additive changes expected.
- **internal/legacy** — supported for specialized workflows; may change with notice.

All commands are local-first: no RPC by default, no secrets, no transaction
broadcasting, no exploit automation, no auto-submit. JSON output (`--json`) and
files written under `.arkheionx/out/` are always plain (no color). See
[`STABILITY_CONTRACT.md`](STABILITY_CONTRACT.md).

## Workbench commands

| Command | Purpose | Human / JSON | Artifacts | Stability |
| --- | --- | --- | --- | --- |
| `arkheionx open` | One-command project orientation | human + `--json` | none by default | stable |
| `arkheionx map` | Protocol roles, journeys, money flow | human + `--json` | `map.json` | stable |
| `arkheionx flow` | Money-flow graph (+ Mermaid) | human + `--json`/`--mermaid` | `flow.json`, `money-flow.mmd` | stable |
| `arkheionx hunt` | Rank bug-hunting surfaces | human + `--json` | `hunt.json` | stable |
| `arkheionx prove` | Generate/run a targeted local Foundry proof | human + `--json` | `proof/<slug>/*` | stable |
| `arkheionx trace` | Summarize proof/trace output | human + `--json` | `proof/<slug>/trace.json` | stable |
| `arkheionx evidence` | Package proof + trace artifacts | human + `--json` | `evidence/<slug>/*` | stable |
| `arkheionx report` | Responsible local report draft | human + `--json` | `report/<slug>/*` | stable |
| `arkheionx evidence-status` | Artifact state per target | human + `--json` | reads index | stable |
| `arkheionx validate-artifacts` | Validate generated artifacts | human + `--json` | reads artifacts | stable |

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

`0` ok, `1` recoverable/heuristic-only warning, `2` invalid usage/failure,
`3` safety rejection (config). See [`CLI_REFERENCE.md`](CLI_REFERENCE.md).
