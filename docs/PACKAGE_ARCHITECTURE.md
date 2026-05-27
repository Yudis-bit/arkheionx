# Arkheionx Package Architecture

The `arkheionx/` package is a preview internal engine boundary. It is stdlib
only and intentionally small in v1.6.0.

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
| `arkheionx.core.paths` | Repo-root and display-path helpers. |
| `arkheionx.core.files` | JSON/text IO helpers and simple file classification helpers. |
| `arkheionx.core.constants` | Generated-artifact ignore patterns and markers. |
| `arkheionx.core.safety` | Shared safety wording and banned phrase lists. |
| `arkheionx.config.schema` | Stable config defaults, normalization, validation, and dangerous-key rejection. |
| `arkheionx.config.loader` | Config file loading and validation wrapper. |
| `arkheionx.rules.registry` | Canonical rule-family metadata. |
| `arkheionx.generators.*` | Extracted generator logic behind existing scripts. |
| `arkheionx.cli.main` | Preview `version` and `doctor` commands. |

## Compatibility Strategy

v1.6.0 avoids a big-bang scanner rewrite. Scripts import package helpers where
the boundary is low-risk. Future releases can gradually migrate config,
suppression, rule selection, report rendering, and CLI command dispatch once
tests prove identical behavior.

v1.7.0 stabilizes the package-side config and rule-pack registry surfaces while
keeping `scripts/pre_audit_scan.py` as the supported scanner entrypoint.

## Not Yet Included

- No package publishing.
- No `pyproject.toml`.
- No official scan command under `python3 -m arkheionx`.
- No database, web app, remote clone workflow, RPC workflow, or external API
  dependency.
