# Packaging

Arkheionx v2.0.0 adds package metadata for local editable installation:

```sh
python3 -m pip install -e .
```

The package name is `arkheionx`, and the console entrypoint is:

```toml
[project.scripts]
arkheionx = "arkheionx.cli.main:main"
```

## Scope

v2.0.0 is a local package milestone. It does not publish to PyPI, upload
artifacts, add publishing workflows, or require tokens.

## Versioning

The CLI prints `2.0.0-dev` during release preparation. `pyproject.toml` uses
the PEP 440 package metadata form `2.0.0.dev0`.

## Build Artifacts

Generated packaging directories are ignored:

- `dist/`
- `build/`
- `*.egg-info/`
- `.eggs/`

Do not commit packaging artifacts from local editable installs.

