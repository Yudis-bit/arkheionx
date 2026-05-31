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
