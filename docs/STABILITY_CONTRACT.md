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
- v3.2.0 does not migrate schema dialects or normalize existing `$schema`
  declarations. A schema policy and registry are deferred governance work.

## Artifacts

- Generated artifacts live under `.arkheionx/out/` and are gitignored.
- In v3.2.0, `.arkheionx/out/` is generated local state and is not intended to
  be committed. Future committed workspace, baseline, session, policy-profile,
  or review-package surfaces require explicit release governance.
- Artifact file contents are never colored.
- Evidence levels (`HEURISTIC`, `COMPILER_CONFIRMED`, `EXECUTION_CONFIRMED`,
  `EVIDENCE_READY`, `HUMAN_REVIEWED`) keep their meaning; new levels would be
  additive. `HUMAN_REVIEWED` requires manual reviewer attestation and is not
  emitted automatically. `REPORT_READY` is legacy protocol-era terminology for
  the `EVIDENCE_READY` support level and is not the current canonical term.
  Review-map signals start at `HEURISTIC`.

## Exit codes

- v3.2.0 keeps the current exit-code behavior. `validate-artifacts` returns `0`
  for clean validation, `1` for validation issues or review attention, and `2`
  for command/input failure.
- A dedicated artifact-validation failure code or strict mode is deferred to a
  later release and would require documentation, tests, and release notes.

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
