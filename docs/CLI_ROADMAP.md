# Arkheionx CLI Roadmap

The supported CLI surface includes the installed console command, the module
CLI, and the legacy script surface documented in [`docs/CLI_REFERENCE.md`](CLI_REFERENCE.md).
v2.0.1 keeps those commands as the current functional foundation while the
roadmap shifts toward local DeFi value-flow mapping.

v2.0.0 added local editable installation:

```sh
python3 -m pip install -e .
arkheionx version
arkheionx doctor
arkheionx scan .
arkheionx validate-config --config .arkheionx.json
arkheionx test-plan --report reports/arkheionx-report.json
arkheionx search "oracle stale price"
```

The v1.9.0 module CLI remains available:

```sh
python3 -m arkheionx.cli.main version
python3 -m arkheionx.cli.main doctor
python3 -m arkheionx.cli.main scan .
python3 -m arkheionx.cli.main validate-config --config .arkheionx.json
python3 -m arkheionx.cli.main test-plan --report reports/arkheionx-report.json
python3 -m arkheionx.cli.main search "oracle stale price"
```

## Preview Commands

`version` prints:

- Arkheionx package version;
- latest stable release;
- current milestone;
- next milestone.

`doctor` checks:

- Python version;
- package imports;
- available rule packs;
- local/static safety boundary reminder.

`scan`, `validate-config`, `test-plan`, and `search` wrap the existing script
entrypoints so script compatibility remains testable after v2 packaging.

## Planned Flow Commands

These commands are planned future roadmap items and are not available in
v2.0.1:

- `arkheionx flow`
- `arkheionx flow --test-gaps`
- `arkheionx flow explain`
- `arkheionx flow test-template`
- `arkheionx flow review-map`
- `arkheionx flow verify`

## Future Path

- v1.7.0: stabilize config and rule-pack metadata inside package modules.
- v1.8.0: add report UX helpers, output profiles, Fix First ranking, and
  noise-reduction summaries.
- v1.9.0: Pre-v2 CLI Candidate released.
- v2.0.0: Installable Arkheionx CLI / Package released.
- v2.0.1: Packaging + Product Repositioning Hotfix current milestone.
- v2.1.0: Value Flow Map MVP next milestone.

## Boundary

The candidate CLI does not add network access, RPC calls, live-chain checks,
transaction execution, exploit automation, target enumeration, or secret
handling.
