"""Local, read-only Solidity source discovery for the semantic core.

Walks a target directory for ``.sol`` files, skipping dependency/build/VCS
directories, with hard caps on file size and count. Never touches the network.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.ingest.solidity_discovery import discover_solidity

# Directories we never treat as in-scope protocol source.
_SKIP_DIRS = {
    ".git", "node_modules", "out", "cache", "artifacts", "build", "dist",
    ".arkheionx", "broadcast", "coverage", "__pycache__", ".vscode", ".idea",
}
# Dependency roots commonly vendored under Foundry/Hardhat projects.
_DEP_DIRS = {"lib", "dependencies", "vendor"}

_MAX_FILE_BYTES = 600_000
_MAX_FILES = 800


class SourceFile:
    __slots__ = ("path", "rel", "text")

    def __init__(self, path: str, rel: str, text: str):
        self.path = path
        self.rel = rel
        self.text = text


def _is_skipped(parts: tuple, include_deps: bool, include_tests: bool) -> bool:
    for p in parts:
        if p in _SKIP_DIRS:
            return True
        if not include_deps and p in _DEP_DIRS:
            return True
        if not include_tests and p.lower() in ("test", "tests") :
            return True
    return False


def discover_sources(
    root: Path | str,
    *,
    include_paths: list | None = None,
    include_deps: bool = False,
    include_tests: bool = False,
    include_scripts: bool = False,
    solidity_root: Path | str | None = None,
) -> list:
    """Return a capped list of ``SourceFile`` for ``.sol`` files under ``root``.

    ``include_paths`` (relative globs/prefixes from scope) restricts discovery
    when provided; otherwise the whole tree (minus skip dirs) is scanned.
    """
    result = discover_solidity(
        root,
        include_paths=include_paths,
        include_deps=include_deps,
        include_tests=include_tests,
        include_scripts=include_scripts,
        solidity_root=solidity_root,
    )
    return result.sources
