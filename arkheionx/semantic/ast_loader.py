"""Compatibility interface for artifact-backed semantic enrichment."""
from __future__ import annotations

from pathlib import Path

from arkheionx.ingest.artifact_discovery import discover_artifacts
from .artifact_loader import load_artifacts


class AstAvailability:
    __slots__ = ("available", "artifact_dirs", "ast_files", "notes")

    def __init__(self):
        self.available = False
        self.artifact_dirs = []
        self.ast_files = 0
        self.notes = []

    def to_dict(self) -> dict:
        return {
            "available": self.available,
            "artifact_dirs": list(self.artifact_dirs),
            "ast_files": self.ast_files,
            "notes": list(self.notes),
        }


def detect_artifacts(root: Path | str) -> AstAvailability:
    """Detect compiler artifacts that carry AST or build-info facts."""
    av = AstAvailability()
    discovery = discover_artifacts(root)
    ast_records = [record for record in discovery.records if record.style in ("ast", "build_info")]
    if ast_records:
        av.available = True
        av.ast_files = len(ast_records)
        av.artifact_dirs = sorted({str(Path(record.path).parent) for record in ast_records})
        av.notes.append("Compiler artifact facts are merged with fallback source analysis.")
    av.notes.extend(discovery.warnings)
    return av


def load_ast_map(root: Path | str):
    """Return extracted artifact facts for callers using the compatibility API."""
    return load_artifacts(root)
