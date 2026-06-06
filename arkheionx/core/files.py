"""Small file helpers for Arkheionx generators."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


MARKDOWN_EXTENSIONS = {".md", ".markdown"}
JSON_EXTENSIONS = {".json"}


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def is_markdown_path(path: Path) -> bool:
    return path.suffix.lower() in MARKDOWN_EXTENSIONS


def is_json_path(path: Path) -> bool:
    return path.suffix.lower() in JSON_EXTENSIONS


def discover_markdown_files(root: Path, ignored_dirs: Iterable[str] = ()) -> list[Path]:
    ignored = set(ignored_dirs)
    results: list[Path] = []
    for path in root.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file() and is_markdown_path(path):
            results.append(path)
    return sorted(results)
