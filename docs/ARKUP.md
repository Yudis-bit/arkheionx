# arkup — Install/Update Lifecycle Helper (MVP)

`arkup` is a small, honest, local-first wrapper around `install.sh`,
`uninstall.sh`, and the local install receipt. It gives Arkheionx a clean
lifecycle: **install → check → update → inspect → uninstall**.

## What arkup is

- An MVP convenience layer over the `install.sh` / `uninstall.sh` scripts.
- A reader of the local install receipt (`~/.arkheionx/install.json`).
- A way to update while keeping your recorded source kind.

## What arkup is not

- Not a full version manager and **not** a clone of foundryup.
- Not a PyPI, Homebrew, or binary distributor.
- Not a background updater, daemon, or telemetry agent.
- Not a root installer and never edits your shell profile.

## Commands

```sh
sh arkup --help          # usage
sh arkup --version       # arkup version + stable target + installed version
sh arkup --check         # install state (alias: --status)
sh arkup --install       # install via install.sh
sh arkup --update        # update using the recorded source kind
sh arkup --uninstall     # remove via uninstall.sh
```

## Options

| Option | Meaning |
| --- | --- |
| `--channel stable\|main` | Source channel (install/update). |
| `--ref REF` | Pin an explicit tag/branch/sha. |
| `--local PATH` | Install from a local checkout. |
| `--dry-run` | Print actions without changing anything. |
| `--yes` | Skip confirmation prompts. |
| `--install-dir PATH` | Base install dir (default `~/.arkheionx`). |
| `--bin-dir PATH` | Wrapper dir (default `<install-dir>/bin`). |

## Source model

`arkup`/`install.sh` support four source kinds (precedence: local > ref > channel):

| Kind | How | Update behavior |
| --- | --- | --- |
| `stable` | default | Reinstalls the documented stable tag. |
| `main` | `--channel main` | Reinstalls from development `main` (opt-in). |
| `ref` | `--ref vX.Y.Z` | Stays pinned to the recorded ref. |
| `local` | `--local PATH` | Reinstalls from the same local checkout. |

`arkup --update` reads the recorded `source_kind` from the receipt and keeps it.
It never silently jumps from `stable` to `main` or from a pinned `ref` to
`stable`. Pass an explicit `--channel`/`--ref`/`--local` to override.

See [`UPDATE_FLOW.md`](UPDATE_FLOW.md) for the full update model and
[`INSTALLER.md`](INSTALLER.md) for the underlying installer.

## Inspecting install state

`arkup --check` and `arkheionx doctor --install` both read the same receipt and
agree on the reported state:

```sh
sh arkup --check
arkheionx doctor --install
```

If no receipt exists (for example, a plain `pip install -e .`), both report the
install state as unknown and still work.

## Examples

```sh
# Inspect, then update a stable install
sh arkup --check
sh arkup --update --dry-run
sh arkup --update --yes

# Install from a local checkout (contributors)
sh arkup --install --local "$PWD" --yes

# Pin a specific tag
sh arkup --install --ref v2.10.0 --yes
```

## Safety

- No root, no `sudo`.
- No shell-profile edits by default.
- No secrets, no RPC, no live-chain activity.
- Not published to PyPI; installs from the GitHub repo or a local checkout.
- The install receipt is local runtime state and is never committed.
