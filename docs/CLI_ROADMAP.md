# Arkheionx CLI Roadmap

The supported v1 CLI remains the script surface documented in
[`docs/CLI_REFERENCE.md`](CLI_REFERENCE.md).

v1.9.0 adds a pre-v2 module CLI candidate:

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
entrypoints so the migration path can be tested before v2 package publishing.

## Future Path

- v1.7.0: stabilize config and rule-pack metadata inside package modules.
- v1.8.0: add report UX helpers, output profiles, Fix First ranking, and
  noise-reduction summaries.
- v1.9.0: Pre-v2 CLI Candidate current milestone.
- v2.0.0: Installable Arkheionx CLI / Package.
- v2.0.1: Packaging/Release Hotfix follow-up.

## Boundary

The candidate CLI does not add network access, RPC calls, live-chain checks,
transaction execution, exploit automation, target enumeration, or secret
handling.
