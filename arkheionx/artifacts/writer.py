"""Deterministic artifact writer for the Arkheionx workbench.

All generated artifacts live under ``artifacts/arkheionx/`` (relative to the
chosen base directory, default: current working directory). Overwrites are
allowed only inside this directory and are deterministic.
"""
from __future__ import annotations

from pathlib import Path

ARTIFACT_ROOT = Path(".arkheionx") / "out"


class ArtifactWriter:
    def __init__(self, base_dir: Path | None = None) -> None:
        base = Path(base_dir) if base_dir is not None else Path.cwd()
        self.root = base / ARTIFACT_ROOT
        self.written: list[str] = []

    def write_text(self, relative_path: str, content: str) -> Path:
        target = self.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not content.endswith("\n"):
            content += "\n"
        target.write_text(content, encoding="utf-8")
        self.written.append(relative_path)
        return target

    def path_for(self, relative_path: str) -> Path:
        return self.root / relative_path
