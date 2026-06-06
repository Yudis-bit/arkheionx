# Package Data & Distribution

Arkheionx bundles its demo fixtures as **package data** so the guided demo works
from an installed package, not only from a source checkout.

## Why

In v2.7.0 the demo fixture resolved from the repository checkout. That works for
development but not for a package installed elsewhere (for example via a future
`pipx install git+...@tag`). v2.8.0 ships the fixtures inside the package.

## What is bundled

Bundled under `arkheionx/demo/fixtures/<demo-id>/` (one directory per demo):

- `oracle-staking/` — `OracleRewardFixture`
- `amm-swap/` — `AMMSwapFixture`
- `lending-vault/` — `LendingVaultFixture`

Each fixture directory contains only `README.md`, `foundry.toml`,
`src/*.sol`, and `test/*.sol`.

Only source files (`*.md`, `*.toml`, `*.sol`) are included via
`[tool.setuptools.package-data]` (`"arkheionx.demo.fixtures" = ["**/*.md",
"**/*.toml", "**/*.sol"]`). Generated directories (`out/`, `cache/`,
`.arkheionx/`), build output, secrets, RPC URLs, and private keys are **not**
bundled. The fixtures are toys — not real protocols or vulnerability reports.

## How resolution works

`arkheionx demo` resolves a fixture in this order:

1. **Bundled package fixture** — `importlib.resources.files("arkheionx.demo.fixtures")`.
2. **Source checkout fallback** — `examples/oracle-staking-fixture` (development).
3. Otherwise a clear error: *"demo fixture resource not found; reinstall
   Arkheionx or use a source checkout."*

`arkheionx demo --show oracle-staking` reports which source is in use
(`Source: bundled package fixture` or `Source: source checkout fixture`).

## Copy behavior

`arkheionx demo --copy oracle-staking <dest>`:

- copies from the resolved fixture (package resource is used even when zipped,
  via `importlib.resources.as_file`);
- copies only the source allowlist (`README.md`, `foundry.toml`, `src/`,
  `test/`);
- refuses a non-empty destination unless `--force`;
- never writes outside `<dest>` and does not depend on the current directory.

## Install confidence

A non-editable install into a fresh virtual environment can run
`arkheionx demo --copy` with no repository checkout present:

```sh
python3 -m venv /tmp/ark-venv
/tmp/ark-venv/bin/pip install .
/tmp/ark-venv/bin/arkheionx demo --copy oracle-staking /tmp/demo
```

## Known limitations

- Bundled demos: `oracle-staking`, `amm-swap`, `lending-vault` (toy fixtures).
- Not published to PyPI; no Homebrew, standalone binary, or domain installer.
- Foundry remains optional; without it the demos run in `HEURISTIC` mode.
