# Troubleshooting

Common install and first-run issues. Everything below is local and static.

## `arkheionx: command not found`

The CLI is installed but not on your `PATH`. For the venv install method, add
the bin dir:

```sh
export PATH="$HOME/.arkheionx/bin:$PATH"
```

Make it permanent by adding that line to your own shell profile. The installer
never edits your profile for you. Then check:

```sh
arkheionx doctor --install
```

## `Python 3.11+ is required`

Install a newer Python and re-run the installer. Confirm with:

```sh
python3 --version
```

## Externally managed environment / pip refuses editable install

Use a virtual environment, which is exactly what the venv install method does:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
```

## `pipx requested but not installed`

Either install `pipx`, or use the venv method:

```sh
sh install.sh --method venv
```

## Native Windows shell is unsupported

The installer exits `2` on `MINGW`/`MSYS`/`CYGWIN`. Use WSL2 or another POSIX
shell. The Python package itself still installs with `pip` on supported shells.

## `not-a-foundry-project` / heuristic only

This is expected outside a Foundry project. Arkheionx runs in `HEURISTIC` mode
and `hunt`/`open` exit `1`. Run inside a Foundry project (with `forge`
available) for `COMPILER_CONFIRMED` and `EXECUTION_CONFIRMED` evidence.

## `--target Contract.function is required`

`prove`/`trace`/`evidence`/`report` need a fully-qualified target. Find one:

```sh
arkheionx hunt . --top 5
```

## Uninstaller refuses to run

`uninstall.sh` exits `2` if `ARKHEIONX_INSTALL_DIR` does not end in
`.arkheionx`. This is a safety guard. Point it at the managed install dir:

```sh
ARKHEIONX_INSTALL_DIR="$HOME/.arkheionx" sh uninstall.sh --dry-run
```

## Terminal color looks wrong, or I want plain output

Arkheionx colors human output only when stdout is a TTY. To force plain text
(for logs, pipes, or unsupported terminals), set `NO_COLOR=1` or
`ARKHEIONX_COLOR=never`. To force color in a pipe, use `ARKHEIONX_COLOR=always`.
`--json` output and artifact files are always plain.

## demo fixture resource not found

This appears only if the package is installed without its bundled demo data.
Reinstall Arkheionx (`sh install.sh` or `pip install .`) so the package data is
present, or run from a source checkout that contains
`examples/oracle-staking-fixture`. See [`PACKAGE_DATA.md`](PACKAGE_DATA.md).

## `arkup --update` says the receipt is missing or malformed

`arkup --update` needs a valid receipt at `~/.arkheionx/install.json`. If you
installed with a plain `pip install -e .` there is no receipt; reinstall via the
script to create one:

```sh
sh arkup --install --local "$PWD"
sh arkup --check
```

A malformed receipt is reported clearly (never crashes). Reinstalling repairs
it. `arkup --check` and `arkheionx doctor --install` read the same receipt and
should agree.

## Still stuck?

Run `arkheionx doctor` and `arkheionx doctor --install` and read the reported
status lines. See [`INSTALLER.md`](INSTALLER.md) and [`ONBOARDING.md`](ONBOARDING.md).
