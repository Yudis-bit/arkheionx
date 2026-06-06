# Arkheionx Package Architecture

The `arkheionx/` package is the local/static CLI package for v2.0.1. It remains
stdlib-only at runtime and keeps existing scripts supported while Arkheionx
repositions toward a DeFi value-flow workbench.

```text
arkheionx/
  version.py
  core/
  config/
  rules/
  reports/
  knowledge/
  generators/
  cli/
```

## Current Modules

| Module | Purpose |
|---|---|
| `arkheionx.version` | Version, stable release, current milestone, and next milestone metadata. |
| `arkheionx.core.models` | Lightweight dataclasses for future engine migration. |
| `arkheionx.core.paths` | Project-root, package-root, runtime data, input, output, and display-path helpers. |
| `arkheionx.core.files` | JSON/text IO helpers and simple file classification helpers. |
| `arkheionx.core.constants` | Generated-artifact ignore patterns and markers. |
| `arkheionx.core.safety` | Shared safety wording and banned phrase lists. |
| `arkheionx.config.schema` | Stable config defaults, normalization, validation, and dangerous-key rejection. |
| `arkheionx.config.loader` | Config file loading and validation wrapper. |
| `arkheionx.rules.registry` | Canonical rule-family metadata. |
| `arkheionx.reports.profiles` | Report output profile settings. |
| `arkheionx.reports.ux` | Fix First, grouping, and suppression summary helpers. |
| `arkheionx.reports.summary` | Backward-compatible report UX summary metadata. |
| `arkheionx.generators.*` | Extracted generator logic behind existing scripts. |
| `arkheionx.cli.main` | Console/module CLI command surface. |
| `arkheionx.cli.commands` | Thin wrappers around existing script/module entrypoints. |
| `arkheionx.cli.exit_codes` | Candidate exit-code conventions. |

## Compatibility Strategy

v1.6.0 avoids a big-bang scanner rewrite. Scripts import package helpers where
the boundary is low-risk. Future releases can gradually migrate config,
suppression, rule selection, report rendering, and CLI command dispatch once
tests prove identical behavior.

v1.7.0 stabilizes the package-side config and rule-pack registry surfaces while
keeping `scripts/pre_audit_scan.py` as the supported scanner entrypoint.

v1.8.0 adds report UX helpers for output profiles, Fix First ranking, finding
grouping, and suppression summaries without replacing the stable scanner script.

v1.9.0 adds the pre-v2 module CLI candidate:

```sh
python3 -m arkheionx.cli.main scan .
python3 -m arkheionx.cli.main validate-config --config .arkheionx.json
python3 -m arkheionx.cli.main test-plan --report reports/arkheionx-report.json
python3 -m arkheionx.cli.main search "oracle stale price"
```

The candidate delegates to existing scripts/modules so compatibility remains
easy to test before package publishing.

v2.0.0 adds `pyproject.toml` and the `arkheionx` console entrypoint:

```sh
python3 -m pip install -e .
arkheionx scan .
```

Package-data resolution remains source-tree compatible for editable installs.
See [`PACKAGE_DATA.md`](PACKAGE_DATA.md).

v2.0.1 keeps that package surface stable and updates public direction toward
value-flow mapping and missing-test workflows. The current available commands
remain `scan`, `test-plan`, `search`, `validate-config`, `doctor`, and
`version`.

Planned future commands such as `arkheionx flow`,
`arkheionx flow --test-gaps`, `arkheionx flow explain`,
`arkheionx flow test-template`, `arkheionx flow review-map`, and
`arkheionx flow verify` are roadmap items, not implemented package commands in
v2.0.1.

## Not Yet Included

- No PyPI publishing.
- No package upload workflow.
- No database, web app, remote clone workflow, RPC workflow, or external API
  dependency.
