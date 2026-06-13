"""Private-scope leak guard for the lens layer.

Reuses the v7 private-term scanner verbatim (a private contest scope under
``.arkheionx/private/`` must never leak into the public surface) and adds a
warning when a lens pack would be written to a *public* path (anywhere outside the
gitignored ``.arkheionx/`` tree), especially when the scope note is itself private.

Local/static only: it reads files; it never transmits anything anywhere.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.scope_orchestration.leak_check import (
    default_private_dir,
    default_private_terms_path,
    load_private_terms,
    run_private_leak_check,
    scan_text_for_terms,
)

__all__ = [
    "run_private_leak_check",
    "load_private_terms",
    "scan_text_for_terms",
    "default_private_dir",
    "default_private_terms_path",
    "is_public_output_path",
    "is_private_path",
    "output_path_warning",
]


def _arkheionx_dir(repo_root: Path | str) -> Path:
    return Path(repo_root).resolve() / ".arkheionx"


def is_private_path(repo_root: Path | str, path: Path | str) -> bool:
    """True if ``path`` resolves under ``<repo_root>/.arkheionx/`` (gitignored)."""
    try:
        Path(path).resolve().relative_to(_arkheionx_dir(repo_root))
        return True
    except ValueError:
        return False


def is_public_output_path(repo_root: Path | str, path: Path | str) -> bool:
    """True if ``path`` is NOT under the gitignored ``.arkheionx/`` tree."""
    return not is_private_path(repo_root, path)


def output_path_warning(repo_root: Path | str, out_dir: Path | str,
                        scope_file: str | None = None) -> str | None:
    """Return a warning string if a lens pack would land on a public path.

    The warning is stronger when the scope note is itself private (under
    ``.arkheionx/private/``): writing derived artifacts to a public path could leak
    private scope detail into a committed location.
    """
    if not is_public_output_path(repo_root, out_dir):
        return None
    base = (f"warning: output path '{out_dir}' is outside .arkheionx/ (a public/committable "
            f"location). Generated lens artifacts may contain scope-derived detail; prefer an "
            f"output path under .arkheionx/ (e.g. .arkheionx/lens-pack) and never commit private scope.")
    if scope_file and is_private_path(repo_root, scope_file):
        base += (" The scope note is private (under .arkheionx/private/); writing derived artifacts "
                 "to a public path risks leaking private scope. Redirect output under .arkheionx/.")
    return base
