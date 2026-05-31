# Uninstall (`uninstall.sh`)

`uninstall.sh` removes only the paths created by `install.sh`. It is
intentionally conservative.

## What it removes

- `~/.arkheionx/bin/arkheionx` (the wrapper)
- `~/.arkheionx/venv` (the isolated environment)
- `~/.arkheionx/bin` and `~/.arkheionx` **only if empty afterwards**

## What it never touches

- your repository checkout;
- your reports or any per-project `.arkheionx/` artifacts in other repositories;
- your shell profile (`.bashrc`/`.zshrc`);
- anything requiring root.

If `ARKHEIONX_INSTALL_DIR` does not end in `.arkheionx`, the script refuses to
run and exits `2`. This prevents accidental deletion of unrelated directories.

## Usage

Preview first:

```sh
sh uninstall.sh --dry-run
```

Then remove:

```sh
sh uninstall.sh
```

Non-interactive:

```sh
ARKHEIONX_YES=1 sh uninstall.sh
```

## pipx installs

If you installed with `pipx`, the script prints guidance instead of guessing:

```sh
pipx uninstall arkheionx
```

To let the script run it for you:

```sh
ARKHEIONX_PIPX_UNINSTALL=1 sh uninstall.sh
```

It only ever uninstalls the `arkheionx` package; it never removes unrelated
pipx applications.

## Environment variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `ARKHEIONX_INSTALL_DIR` | `$HOME/.arkheionx` | Base install directory (must end in `.arkheionx`). |
| `ARKHEIONX_BIN_DIR` | `$HOME/.arkheionx/bin` | Wrapper directory. |
| `ARKHEIONX_YES` | `0` | Set `1` to skip the confirmation prompt. |
| `ARKHEIONX_DRY_RUN` | `0` | Set `1` to print actions only. |
| `ARKHEIONX_PIPX_UNINSTALL` | `0` | Set `1` to also run `pipx uninstall arkheionx`. |
