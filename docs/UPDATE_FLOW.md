# Update Flow & Install State

Arkheionx tracks how it was installed in a local **install receipt** and uses it
to update predictably. This document explains the receipt, the source model, and
how `arkup --update` behaves.

## Install receipt

`install.sh` writes a receipt on success:

```
$ARKHEIONX_INSTALL_DIR/install.json   (default: ~/.arkheionx/install.json)
```

Fields (see [`../schemas/install-receipt.schema.json`](../schemas/install-receipt.schema.json)):

| Field | Meaning |
| --- | --- |
| `schema_version` | Receipt schema version (currently `1`). |
| `tool` | Always `arkheionx`. |
| `installed_at` / `updated_at` | First install and last update timestamps. |
| `install_method` | `pipx` or `venv`. |
| `source_kind` | `stable`, `main`, `ref`, or `local`. |
| `repo_url` / `ref` / `local_path` | Where it was installed from. |
| `install_dir` / `bin_dir` / `command_path` | Where it lives. |
| `detected_python` | Python used for the install. |
| `installed_version` | Arkheionx version recorded at install time. |
| `installer_version` | Installer/arkup lifecycle version. |

The receipt is **local runtime state**. It is never committed and is removed by
`uninstall.sh`.

## Source model

Precedence when resolving a source: **local > ref > channel**.

- **stable** — default. Installs the documented stable tag
  (`ARKHEIONX_STABLE_TAG`, currently `v2.6.0`).
- **main** — `--channel main`. Latest development `main`; opt-in and
  development-risk.
- **ref** — `--ref <tag|branch|sha>`. Pinned to an explicit ref.
- **local** — `--local <path>`. Installs from a local checkout.

## Update behavior

`arkup --update` reads `source_kind` from the receipt and preserves it:

| Recorded kind | `arkup --update` does |
| --- | --- |
| `stable` | Reinstall the current stable tag. |
| `main` | Reinstall from `main`. |
| `ref` | Reinstall the **same pinned ref** (stays pinned). |
| `local` | Reinstall from the **same local path**. |

Rules:

- Update never silently changes your channel or ref.
- To change source, pass an explicit `--channel`, `--ref`, or `--local`.
- `--dry-run` prints exactly what would happen and writes nothing.
- `installed_at` is preserved across updates; `updated_at` is refreshed.

## Inspecting state

```sh
sh arkup --check            # reads the receipt, degrades gracefully if absent
arkheionx doctor --install  # same receipt, install-health framing
```

Both report "install state unknown" if there is no receipt (for example after a
plain `pip install -e .`) and neither crashes on a missing or malformed receipt.

## Examples

```sh
# Stable install, then later update to current stable
sh arkup --install --yes
sh arkup --update --dry-run
sh arkup --update --yes

# Pinned ref stays pinned on update
sh arkup --install --ref v2.6.0 --yes
sh arkup --update --yes      # still v2.6.0

# Move from stable to main explicitly (opt-in)
sh arkup --update --channel main --yes
```

## Safety

No root, no shell-profile edits, no secrets, no RPC, no live-chain activity, no
PyPI/Homebrew/binary distribution. See [`ARKUP.md`](ARKUP.md) and
[`INSTALLER.md`](INSTALLER.md).
