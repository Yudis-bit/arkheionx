"""Path helpers shared by Arkheionx scripts and package modules."""
from __future__ import annotations

from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[1]
SOURCE_ROOT = Path(__file__).resolve().parents[2]

# Backward-compatible name used by existing generator modules. In editable
# source-tree installs this is the project root that contains metadata/.
PACKAGE_ROOT = SOURCE_ROOT


def repo_root() -> Path:
    """Return the repository root for the current source checkout."""

    return project_root()


def project_root(start: Path | None = None) -> Path:
    """Return the nearest Arkheionx source tree root.

    Editable installs place the source checkout on sys.path, so runtime metadata
    can still be resolved from the repository root. If no marker is found, fall
    back to the source root inferred from this file.
    """

    candidates = []
    if start is not None:
        candidates.append(start.resolve())
    candidates.extend([Path.cwd().resolve(), SOURCE_ROOT])
    markers = ("pyproject.toml", "metadata", "schemas", "templates")
    for candidate in candidates:
        for path in (candidate, *candidate.parents):
            if (path / "arkheionx").is_dir() and any((path / marker).exists() for marker in markers):
                return path
    return SOURCE_ROOT


def package_root() -> Path:
    """Return the installed/imported `arkheionx` package directory."""

    return PACKAGE_DIR


def is_editable_source_tree(root: Path | None = None) -> bool:
    """Return true when runtime data is available in a source checkout."""

    base = root or project_root()
    return (base / "pyproject.toml").exists() and (base / "metadata").is_dir()


def resolve_runtime_data_path(*parts: str, root: Path | None = None) -> Path:
    """Resolve metadata, schema, template, report, or doc data paths.

    v2.0.0 keeps package data source-tree compatible for editable installs. A
    future wheel can populate `arkheionx/data/` without changing callers.
    """

    relative = Path(*parts)
    source_candidate = (root or project_root()) / relative
    if source_candidate.exists():
        return source_candidate
    package_data_candidate = package_root() / "data" / relative
    if package_data_candidate.exists():
        return package_data_candidate
    return source_candidate


def repo_relative(path: Path, root: Path | None = None) -> str:
    """Return a POSIX path relative to the repository when possible."""

    base = (root or project_root()).resolve()
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
    return (root or project_root()) / candidate


def resolve_input_path(path: str | Path, root: Path | None = None) -> Path:
    """Resolve an input path from cwd, an optional root, or runtime data."""

    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate
    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate
    if root is not None:
        root_candidate = root / candidate
        if root_candidate.exists():
            return root_candidate
    runtime_candidate = resolve_runtime_data_path(*candidate.parts, root=root)
    if runtime_candidate.exists():
        return runtime_candidate
    return cwd_candidate


def resolve_output_path(path: str | Path, root: Path | None = None) -> Path:
    """Resolve an output path without requiring that it already exists."""

    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate
    return (root or Path.cwd()) / candidate
