# Installer (`install.sh`)

`install.sh` is a safe, local-first installer for the Arkheionx CLI. It prefers
`pipx` and falls back to an isolated virtual environment under your home
directory. It is designed to be readable and `curl`-friendly.

## Safety boundaries

The installer:

- never uses root and never asks for a password;
- never edits your shell profile (`.bashrc`/`.zshrc`);
- never asks for secrets, no API keys, no private keys;
- never performs RPC or live-chain calls;
- only runs `pip` against the Arkheionx repository or a local checkout you
  point it at;
- installs into `~/.arkheionx` (or `ARKHEIONX_INSTALL_DIR`), nothing system-wide.

Arkheionx is **not published to PyPI**. The installer pulls from the GitHub
repository (pinned to a stable ref) or from a local checkout.

## Quick start

Stable channel (default):

```sh
sh install.sh
```

From a local checkout (contributors / dev testing):

```sh
sh install.sh --local "$PWD"
```

Pin an explicit ref, or use development `main`:

```sh
sh install.sh --ref v3.0.0
sh install.sh --channel main
```

Preview without changing anything:

```sh
sh install.sh --dry-run
```

For a friendlier lifecycle (`install → check → update → uninstall`), use
[`arkup`](ARKUP.md), which wraps this script and reads the install receipt.

## Methods

| Method | When | Result |
| --- | --- | --- |
| `pipx` | `pipx` is installed | Isolated app install managed by pipx |
| `venv` | no `pipx` (default fallback) | `~/.arkheionx/venv` + wrapper at `~/.arkheionx/bin/arkheionx` |

Force a method:

```sh
sh install.sh --method venv
sh install.sh --method pipx
```

## Options

| Flag | Meaning |
| --- | --- |
| `--help` | Show usage and exit. |
| `--dry-run` | Print actions without changing anything. |
| `--method auto\|pipx\|venv` | Choose the install method (default `auto`). |
| `--channel stable\|main` | Source channel (default `stable`). |
| `--ref REF` | Install a pinned tag/branch/sha. |
| `--local PATH` | Install from a local repository checkout. |

## Source model

Precedence: **local > ref > channel**.

| Kind | How | Notes |
| --- | --- | --- |
| `stable` | default | Documented stable tag (`ARKHEIONX_STABLE_TAG`, currently `v3.0.0`). |
| `main` | `--channel main` | Development `main`; opt-in. |
| `ref` | `--ref vX.Y.Z` | Pinned explicit ref. |
| `local` | `--local PATH` | Local checkout. |

The chosen source is recorded in the install receipt so [`arkup`](ARKUP.md) can
update predictably. See [`UPDATE_FLOW.md`](UPDATE_FLOW.md).

## Environment variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `ARKHEIONX_REPO_URL` | `https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git` | Git URL to install from. |
| `ARKHEIONX_STABLE_TAG` | `v2.6.0` | Tag used by the stable channel. |
| `ARKHEIONX_CHANNEL` | `stable` | `stable` or `main`. |
| `ARKHEIONX_REF` | (unset) | Explicit git ref (sets source kind `ref`). |
| `ARKHEIONX_LOCAL_PATH` | (unset) | Local checkout (sets source kind `local`). |
| `ARKHEIONX_INSTALL_DIR` | `$HOME/.arkheionx` | Base install directory. |
| `ARKHEIONX_BIN_DIR` | `$HOME/.arkheionx/bin` | Wrapper directory. |
| `ARKHEIONX_INSTALL_METHOD` | `auto` | `auto`, `pipx`, or `venv`. |
| `ARKHEIONX_YES` | `0` | Set `1` to skip the confirmation prompt. |
| `ARKHEIONX_DRY_RUN` | `0` | Set `1` to print actions only. |

The installer never modifies `PATH` for you; it only prints the line to add.

## Install receipt

On success the installer writes a local receipt to
`$ARKHEIONX_INSTALL_DIR/install.json` (schema:
[`../schemas/install-receipt.schema.json`](../schemas/install-receipt.schema.json)).
It records the install method, source kind, ref/local path, install/bin dirs,
command path, detected Python, and installed version. The receipt is local
runtime state, is never committed, and is removed by `uninstall.sh`.
[`arkup`](ARKUP.md) and `arkheionx doctor --install` read it.

## After install

```sh
export PATH="$HOME/.arkheionx/bin:$PATH"   # only needed for the venv method
arkheionx version
arkheionx doctor --install
arkheionx open .
```

`arkheionx doctor --install` reports the resolved command path, Python
executable, package import/version, optional Foundry status, and a PATH hint.

## Uninstall

See [`UNINSTALL.md`](UNINSTALL.md). In short: `sh uninstall.sh`.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success. |
| `1` | Recoverable warning or user abort. |
| `2` | Failure (missing Python, unsupported OS, bad option). |
