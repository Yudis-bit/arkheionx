"""Path helpers shared by Arkheionx scripts and package modules."""
from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    """Return the repository root for the current source checkout."""

    return PACKAGE_ROOT


def repo_relative(path: Path, root: Path | None = None) -> str:
    """Return a POSIX path relative to the repository when possible."""

    base = (root or PACKAGE_ROOT).resolve()
    try:
        return path.resolve().relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def display_path(path: Path | None, root: Path | None = None) -> str:
    """Format optional paths for deterministic generated artifacts."""

    if not path:
        return ""
    return repo_relative(path, root)


def resolve_from_root(path: str | Path, root: Path | None = None) -> Path:
    """Resolve a path from the repository root unless it is already absolute."""

    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (root or PACKAGE_ROOT) / candidate
