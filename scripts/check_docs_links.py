#!/usr/bin/env python3
"""Check local Markdown links used by Arkheionx docs."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "file:", "app://", "#")
PLACEHOLDER_TARGETS = {"url", "<url>"}


def markdown_files() -> list[Path]:
    files = [ROOT / "README.md"]
    files.extend(sorted((ROOT / "docs").rglob("*.md")))
    search_index = ROOT / "reports" / "search_index.md"
    if search_index.exists():
        files.append(search_index)
    return [path for path in files if path.exists()]


def normalize_target(raw: str) -> str:
    target = raw.strip()
    if not target or target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    return unquote(target.split("#", 1)[0].strip())


def candidate_paths(source: Path, target: str) -> list[Path]:
    candidates: list[Path] = []
    if target.startswith("/"):
        candidates.append(ROOT / target.lstrip("/"))
    else:
        candidates.append((source.parent / target).resolve())
        candidates.append((ROOT / target).resolve())
        candidates.append((ROOT / "docs" / target).resolve())
        candidates.append((ROOT / "docs" / "business" / target).resolve())
        candidates.append((ROOT / "docs" / "marketing" / target).resolve())
        candidates.append((ROOT / "docs" / "launch" / target).resolve())
        if target.startswith("../"):
            candidates.append((ROOT / target[3:]).resolve())
        if target.startswith("launch/"):
            candidates.append((ROOT / "docs" / target).resolve())
    seen: set[Path] = set()
    unique: list[Path] = []
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            unique.append(candidate)
    return unique


def missing_links() -> list[str]:
    failures: list[str] = []
    for source in markdown_files():
        text = source.read_text(encoding="utf-8", errors="ignore")
        for match in LINK_RE.finditer(text):
            raw_target = match.group(1)
            target = normalize_target(raw_target)
            if not target or target.startswith(SKIP_PREFIXES):
                continue
            if target.lower() in PLACEHOLDER_TARGETS:
                continue
            candidates = []
            for candidate in candidate_paths(source, target):
                try:
                    candidate.relative_to(ROOT)
                except ValueError:
                    continue
                candidates.append(candidate)
            if not any(candidate.exists() for candidate in candidates):
                failures.append(f"{source.relative_to(ROOT)} -> {raw_target}")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check local Markdown links.")
    parser.add_argument("--check", action="store_true", help="Exit nonzero if missing links are found.")
    args = parser.parse_args(argv)
    failures = missing_links()
    if failures:
        print("Missing local Markdown links:")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("ok: docs links valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
