# Installation

ArkheionX is currently installed from source. It is not published to PyPI and does not ship prebuilt binaries.

## Requirements

- Python 3.11 or newer.
- Git for source checkout workflows.
- Foundry is optional, but useful when a reviewer wants compiler-confirmed or execution-confirmed local evidence.

The default workflow does not require private keys, seed phrases, RPC URLs, production credentials, hosted services, or external AI APIs.

## Editable source install

From this repository:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e .
arkheionx version
arkheionx doctor
```

## Installer script

The source installer can install from a local checkout:

```bash
ARKHEIONX_LOCAL_PATH="$PWD" sh install.sh
arkheionx version
arkheionx doctor --install
```

The installer is intended to create an isolated local install. It should not ask for secrets, modify production configuration, call RPC endpoints, or run live-chain operations.

For installer options, dry-run behavior, update flow, and uninstall details, see [`INSTALLER.md`](INSTALLER.md), [`ARKUP.md`](ARKUP.md), and [`UNINSTALL.md`](UNINSTALL.md).

## First review run

Create or collect a scope note, then run:

```bash
arkheionx review . --scope-file scope.md --out .arkheionx/review
```

If you only want a compact first map:

```bash
arkheionx review-map .
```

## Demo path

```bash
arkheionx demo --list
arkheionx review-map examples/vault-strategy-oracle-fixture
```

See [`DEMO_WORKFLOW.md`](DEMO_WORKFLOW.md) for bundled demos.

## Repository identity note

The public repository has been renamed to `Yudis-bit/arkheionx`. New users should use <https://github.com/Yudis-bit/arkheionx>. The old `DeFi-Exploit-PoCs` slug may remain in historical documents, archived material, generated artifacts, or compatibility notes. Do not rename local folders automatically during installation.

See [`REPO_IDENTITY_MIGRATION.md`](REPO_IDENTITY_MIGRATION.md).

## Troubleshooting

```bash
arkheionx doctor
arkheionx doctor --install
arkheionx --help
```

Common issues:

- The command is not on `PATH`.
- Python is older than 3.11.
- The current directory is not a Solidity or Foundry repository.
- Foundry is not installed when compiler/test evidence is expected.

See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).
