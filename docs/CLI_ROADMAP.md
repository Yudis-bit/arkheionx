# Arkheionx CLI Roadmap

The supported v1 CLI remains the script surface documented in
[`docs/CLI_REFERENCE.md`](CLI_REFERENCE.md).

v1.6.0 adds a preview internal package CLI for health checks only:

```sh
python3 -m arkheionx.cli.main version
python3 -m arkheionx.cli.main doctor
```

## Preview Commands

`version` prints:

- Arkheionx package version;
- latest stable release;
- current milestone.

`doctor` checks:

- Python version;
- package imports;
- available rule packs;
- local/static safety boundary reminder.

## Future Path

- v1.7.0: stabilize config and rule-pack metadata inside package modules.
- v1.8.0: report UX and noise reduction after config behavior is stable.
- v1.9.0: continue extracting scanner/report internals behind stable
  tests.
- v2.0.0: consider an installable package and official CLI only after script
  compatibility, schemas, docs, and GitHub-native workflows remain stable.

## Boundary

The preview CLI does not run scans. It does not add network access, RPC calls,
live-chain checks, transaction execution, exploit automation, target
enumeration, or secret handling.
