"""Private-scope leak guard for the v7 layer.

A researcher may keep a private contest scope under ``.arkheionx/private/`` (which
is gitignored). This module scans the public, committed surface of the repository
for any private term listed in ``.arkheionx/private/private-terms.txt`` so that a
private target name, sponsor, or wording never leaks into public source, tests,
fixtures, docs, or generated example output.

Local/static only. It reads files; it never transmits anything anywhere.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

# Directories that are private/local or never part of the public surface.
_EXCLUDED_DIRS = {
    ".arkheionx", ".git", "node_modules", "dist", "build", "site", "__pycache__",
    ".venv", "venv", ".pytest_cache", ".mypy_cache", ".ruff_cache", "out", "cache",
}
_SCANNED_SUFFIXES = {
    ".py", ".md", ".sol", ".json", ".toml", ".yml", ".yaml", ".txt", ".astro",
    ".cfg", ".ini", ".sh", ".rst",
}


def default_private_dir(repo_root: Path | str) -> Path:
    return Path(repo_root) / ".arkheionx" / "private"


def default_private_terms_path(repo_root: Path | str) -> Path:
    return default_private_dir(repo_root) / "private-terms.txt"


def load_private_terms(path: Path | str | None) -> list[str]:
    """Load one private term per line. Blank lines and ``#`` comments are ignored.

    A missing or unreadable file yields an empty list — the guard is an optional
    convenience and never raises for bad input.
    """
    if not path:
        return []
    p = Path(path)
    if not p.is_file():
        return []
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    terms: list[str] = []
    for line in lines:
        term = line.strip()
        if not term or term.startswith("#"):
            continue
        terms.append(term)
    return terms


def scan_text_for_terms(text: str, terms: list[str]) -> list[str]:
    """Return the subset of ``terms`` that appear in ``text`` (case-insensitive)."""
    lower = text.lower()
    hits: list[str] = []
    for term in terms:
        t = term.strip().lower()
        if t and t in lower:
            hits.append(term)
    return hits


def _public_files(repo_root: Path) -> list[Path]:
    """List public files to scan: git-tracked files when possible, else a walk."""
    root = Path(repo_root)
    tracked: list[Path] = []
    try:
        result = subprocess.run(
            ["git", "ls-files"], cwd=str(root), text=True,
            capture_output=True, timeout=30,
        )
        if result.returncode == 0:
            for rel in result.stdout.splitlines():
                rel = rel.strip()
                if not rel:
                    continue
                parts = Path(rel).parts
                if any(part in _EXCLUDED_DIRS for part in parts):
                    continue
                tracked.append(root / rel)
    except (OSError, subprocess.SubprocessError):
        tracked = []

    if tracked:
        return [p for p in tracked if p.suffix.lower() in _SCANNED_SUFFIXES and p.is_file()]

    # Fallback: walk the tree, skipping excluded directories.
    files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in _SCANNED_SUFFIXES:
            continue
        if any(part in _EXCLUDED_DIRS for part in p.relative_to(root).parts):
            continue
        files.append(p)
    return files


def run_private_leak_check(repo_root: Path | str, terms_file: Path | str | None = None) -> dict:
    """Scan the public surface for private terms.

    Returns a deterministic record: whether a terms file was present, how many
    terms were checked, how many public files were scanned, and any leaks found
    as ``{"file": <rel>, "terms": [...]}``. A clean result has ``leaks == []``.
    """
    root = Path(repo_root)
    terms_path = Path(terms_file) if terms_file else default_private_terms_path(root)
    terms = load_private_terms(terms_path)

    leaks: list[dict] = []
    scanned = 0
    if terms:
        for path in _public_files(root):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            scanned += 1
            hits = scan_text_for_terms(text, terms)
            if hits:
                try:
                    rel = str(path.relative_to(root))
                except ValueError:
                    rel = str(path)
                leaks.append({"file": rel, "terms": sorted(set(hits))})

    return {
        "terms_file_present": bool(terms),
        "terms_checked": len(terms),
        "files_scanned": scanned,
        "leaks": leaks,
        "clean": not leaks,
        "human_review_required": True,
    }
