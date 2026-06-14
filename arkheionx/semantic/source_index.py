"""Local, read-only Solidity source discovery for the semantic core.

Walks a target directory for ``.sol`` files, skipping dependency/build/VCS
directories, with hard caps on file size and count. Never touches the network.
"""
from __future__ import annotations

from pathlib import Path

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
) -> list:
    """Return a capped list of ``SourceFile`` for ``.sol`` files under ``root``.

    ``include_paths`` (relative globs/prefixes from scope) restricts discovery
    when provided; otherwise the whole tree (minus skip dirs) is scanned.
    """
    root = Path(root)
    if root.is_file() and root.suffix == ".sol":
        try:
            return [SourceFile(str(root), root.name, root.read_text(encoding="utf-8", errors="ignore"))]
        except OSError:
            return []
    if not root.is_dir():
        return []

    prefixes = [p.strip().strip("/") for p in (include_paths or []) if p and p.strip()]
    out: list = []
    for path in sorted(root.rglob("*.sol")):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        parts = rel.parts
        if _is_skipped(parts[:-1], include_deps, include_tests):
            continue
        rel_str = str(rel)
        if prefixes and not any(rel_str == pre or rel_str.startswith(pre.rstrip("/") + "/") or pre in rel_str
                                for pre in prefixes):
            continue
        try:
            if not path.is_file() or path.stat().st_size > _MAX_FILE_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        out.append(SourceFile(str(path), rel_str, text))
        if len(out) >= _MAX_FILES:
            break
    return out
