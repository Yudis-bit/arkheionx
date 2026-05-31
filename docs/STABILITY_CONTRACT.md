# Stability Contract

What Arkheionx intends to keep stable, what may change, and what will never be
weakened. This contract takes effect at the v3.0 public stable release; the v2.x
line is the run-up to it.

## CLI command names

- Public command names (see [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md)) are not
  removed or renamed after v3.0 without a deprecation period and a compatibility
  bridge.
- New commands and new optional flags are additive and allowed at any time.

## Human-readable output

- Terminal output (headings, summaries, wording, color) **may be polished** over
  time. Do not parse human output programmatically.
- Color is cosmetic, TTY-gated, and controlled by `ARKHEIONX_COLOR` / `NO_COLOR`.
  It never changes exit codes or content.

## JSON and schemas

- `--json` output and the JSON schemas under `schemas/` are treated more
  carefully than human text. Changes aim to be additive (new fields) rather than
  breaking (renamed/removed fields).
- JSON output is always plain (no ANSI), on every command and in CI.

## Artifacts

- Generated artifacts live under `.arkheionx/out/` and are gitignored.
- Artifact file contents are never colored.
- Evidence levels (`HEURISTIC`, `COMPILER_CONFIRMED`, `EXECUTION_CONFIRMED`,
  `EVIDENCE_READY`) keep their meaning; new levels would be additive.

## Install / update lifecycle

- `install.sh`, `uninstall.sh`, and `arkup` stay no-sudo, no-profile-edit,
  no-secret, no-RPC. The install receipt schema is versioned
  (`schemas/install-receipt.schema.json`).
- The stable/main/ref/local source model is stable.

## Internal modules

- Python modules under `arkheionx/` are **not** a stable import API. Use the CLI.

## Safety boundaries (never weakened)

- Local repository analysis only; no RPC by default; no live-chain mutation; no
  private keys or secrets; no transaction broadcasting; no automated
  exploitation; no auto-submit; no guaranteed vulnerability discovery; not an
  audit; no severity guarantee. Human review is required.

## Known limitations before v3.0

- Heuristic findings are ranking signals, not confirmed bugs.
- Foundry is optional; without it the workbench stays in `HEURISTIC` mode.
- Not published to PyPI; no Homebrew, standalone binary, or domain installer.

See [`V3_READINESS.md`](V3_READINESS.md) for the readiness checklist.
