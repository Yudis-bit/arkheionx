"""AST mode interface for the semantic core (Mode A).

If solc / Foundry compiler artifacts carrying a Solidity AST are present, this is
where they would be ingested. Full AST ingestion is intentionally deferred in the
V10 vertical slice: this module only *detects* artifacts and reports availability
so the orchestrator can record provenance, then falls back to the robust parser.

This is an honest interface, not a fake implementation: ``load_ast_map`` returns
``None`` today, which is the documented "fallback primary" behavior.
"""
from __future__ import annotations

import json
from pathlib import Path

_ARTIFACT_DIRS = ("out", "artifacts", "build")


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
    """Detect compiler artifacts that *could* carry a Solidity AST."""
    root = Path(root)
    av = AstAvailability()
    if not root.is_dir():
        return av
    for d in _ARTIFACT_DIRS:
        ad = root / d
        if not ad.is_dir():
            continue
        ast_hits = 0
        try:
            for jf in list(ad.rglob("*.json"))[:400]:
                try:
                    head = jf.read_text(encoding="utf-8", errors="ignore")[:4000]
                except OSError:
                    continue
                if '"ast"' in head or '"nodeType"' in head:
                    ast_hits += 1
        except OSError:
            continue
        if ast_hits:
            av.artifact_dirs.append(d)
            av.ast_files += ast_hits
    if av.ast_files:
        av.available = True
        av.notes.append(
            "Compiler AST artifacts detected. Full AST ingestion is deferred in V10; "
            "the fallback parser is used and provenance is recorded.")
    return av


def load_ast_map(root: Path | str):
    """Return a parsed semantic map from AST artifacts, or ``None`` (deferred).

    Returning ``None`` is the contract that tells the orchestrator to use the
    fallback parser. This keeps AST mode an honest, pluggable interface.
    """
    return None
