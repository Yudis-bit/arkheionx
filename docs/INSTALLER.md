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

From a local checkout (recommended while testing v2.5.0-dev):

```sh
ARKHEIONX_LOCAL_PATH="$PWD" sh install.sh
```

From the stable repository ref:

```sh
sh install.sh
```

Preview without changing anything:

```sh
sh install.sh --dry-run
```

When v2.5.0 is finalized, a one-line form will be documented here. Until then,
clone the repository and run `sh install.sh` locally.

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
| `--local PATH` | Install from a local repository checkout. |

## Environment variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `ARKHEIONX_REPO_URL` | `https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git` | Git URL to install from. |
| `ARKHEIONX_REF` | `v2.4.0` | Git ref to install (stable until v2.5.0 final). |
| `ARKHEIONX_INSTALL_DIR` | `$HOME/.arkheionx` | Base install directory. |
| `ARKHEIONX_BIN_DIR` | `$HOME/.arkheionx/bin` | Wrapper directory. |
| `ARKHEIONX_INSTALL_METHOD` | `auto` | `auto`, `pipx`, or `venv`. |
| `ARKHEIONX_LOCAL_PATH` | (unset) | Install from this local checkout. |
| `ARKHEIONX_YES` | `0` | Set `1` to skip the confirmation prompt. |
| `ARKHEIONX_DRY_RUN` | `0` | Set `1` to print actions only. |

The installer never modifies `PATH` for you; it only prints the line to add.

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
