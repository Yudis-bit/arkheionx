# Packaging

Arkheionx v2.0.1 keeps package metadata for local editable installation:

```sh
python3 -m pip install -e .
```

The package name is `arkheionx`, and the console entrypoint is:

```toml
[project.scripts]
arkheionx = "arkheionx.cli.main:main"
```

## Scope

v2.0.1 is a packaging and product repositioning hotfix. It does not publish to
PyPI, upload artifacts, add publishing workflows, or require tokens. The
package surface remains the current foundation for local/static value-flow
review through `scan`, `test-plan`, `search`, `validate-config`, `doctor`, and
`version`.

## Versioning

The CLI prints `2.0.1-dev` during release preparation. `pyproject.toml` uses
the PEP 440 package metadata form `2.0.1.dev0`.

Planned future `arkheionx flow` commands are roadmap items and are not part of
the v2.0.1 package surface.

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

