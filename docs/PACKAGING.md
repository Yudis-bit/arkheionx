# Packaging

Arkheionx ships package metadata for local installation:

```sh
python3 -m pip install -e .   # source / development
python3 -m pip install .      # non-editable
```

The package name is `arkheionx`, and the console entrypoint is:

```toml
[project.scripts]
arkheionx = "arkheionx.cli.main:main"
```

## Scope

This is local/static review tooling. It does not publish to PyPI, upload
artifacts, add publishing workflows, or require tokens. The canonical local
review workflow is `arkheionx review-map .`; `doctor` and `version` are the
first orientation commands.

## Versioning

The installed package version is `3.9.0` (the current local/public-safe
technical state); `pyproject.toml` declares `version = "3.9.0"`. The latest
tagged stable release is `v3.1.0`, and `v4.0.0` is the next milestone (planned
direction, not tagged here). `arkheionx version` prints all of these.

These package milestones are deliberately separate from the legacy pre-audit
scanner's frozen output version (`SCANNER_VERSION`), which stays pinned so the
committed example reports under `examples/reports/` remain byte-stable across
package milestones. A scanner report showing an older output version is
expected, not stale package metadata.

Planned future `arkheionx flow` sub-commands are roadmap items and are not part
of the current package surface.

## Build Artifacts

Generated packaging directories are ignored:

- `dist/`
- `build/`
- `*.egg-info/`
- `.eggs/`

Do not commit packaging artifacts from local editable installs.

## Installed vs source-tree commands

Two command families ship with ArkheionX, and they have different install
requirements:

- **Packaged workbench (works after any install, editable or not):** `version`,
  `doctor`, `review-map`, `test-gap-map`, `value-paths`, `assumptions`,
  `proof-plan`, `evidence-links`, `open`, `map`, `flow`, `hunt`, `prove`,
  `trace`, `evidence`, `report`, `review-package`, `local-validate`,
  `validate-config`. These live entirely inside the `arkheionx` package. The
  canonical first run, `arkheionx review-map .`, is verified to work from a
  non-editable `pip install .`.

- **Source-tree readiness scanner (requires a repository checkout):** the legacy
  `scan`, `test-plan`, and `search` commands delegate to helpers under
  `scripts/`, which are not bundled in the installed wheel. Run them from a clone
  of the repository (or via `make demo`). In a non-editable install they exit
  with a clear message pointing at `arkheionx review-map` rather than a
  traceback.

Bundling the legacy scanner into the wheel is a tracked follow-up; it is not
required for the canonical local review workflow.

