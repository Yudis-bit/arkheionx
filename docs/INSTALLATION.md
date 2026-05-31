# Installation

Arkheionx is local-first and installs from a source checkout. It is **not
published to PyPI**. There are two supported paths.

## Option A — installer script (recommended)

```sh
ARKHEIONX_LOCAL_PATH="$PWD" sh install.sh
export PATH="$HOME/.arkheionx/bin:$PATH"   # venv method only
arkheionx doctor --install
```

The installer prefers `pipx` and falls back to an isolated virtual environment
under `~/.arkheionx`. It uses no root, edits no shell profile, asks for no
secrets, and makes no RPC or live-chain calls. See [`INSTALLER.md`](INSTALLER.md)
for options, environment variables, and a dry-run preview.

For a managed lifecycle (`install → check → update → uninstall`), use
[`arkup`](ARKUP.md):

```sh
sh arkup --install --local "$PWD"
sh arkup --check
sh arkup --update --dry-run
```

## Option B — editable pip install

```sh
python3 -m pip install -e .
arkheionx doctor
```

If your system Python blocks editable installs because it is externally
managed, create a virtual environment first:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
```

## Requirements

- Python 3.11 or newer.
- No runtime Python dependencies.
- Foundry (`forge`) is optional but recommended for compiler- and
  execution-confirmed evidence.
- No RPC endpoint, no private keys, no secrets, no GitHub token, no hosted
  service.

## Verify

```sh
arkheionx version
arkheionx doctor
arkheionx doctor --install
```

## First run

```sh
arkheionx open examples/oracle-staking-fixture
arkheionx hunt examples/oracle-staking-fixture --top 5
```

See [`ONBOARDING.md`](ONBOARDING.md) and [`TRY_IN_5_MINUTES.md`](TRY_IN_5_MINUTES.md).

## Uninstall

```sh
sh uninstall.sh --dry-run
sh uninstall.sh
```

See [`UNINSTALL.md`](UNINSTALL.md).

## Safety

The installed CLI is local/static only. It does not perform live-chain calls,
transaction execution, deployed-contract scanning, remote cloning, or exploit
automation. Trouble? See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).
