"""Compiler artifact and build-info discovery."""
from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path

FALLBACK_ONLY = "FALLBACK_ONLY"
ABI_PLUS_FALLBACK = "ABI_PLUS_FALLBACK"
AST_PLUS_FALLBACK = "AST_PLUS_FALLBACK"
BUILD_INFO_PLUS_FALLBACK = "BUILD_INFO_PLUS_FALLBACK"
LEGACY_ARTIFACT_PLUS_FALLBACK = "LEGACY_ARTIFACT_PLUS_FALLBACK"


@dataclass
class ArtifactRecord:
    path: str = ""
    style: str = ""
    data: dict = field(default_factory=dict)


@dataclass
class ArtifactDiscovery:
    mode: str = FALLBACK_ONLY
    records: list = field(default_factory=list)
    malformed_files: int = 0
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "record_count": len(self.records),
            "malformed_files": self.malformed_files,
            "paths": [record.path for record in self.records],
            "warnings": list(self.warnings),
        }


def _style(data: dict) -> str:
    if isinstance(data.get("input"), dict) and isinstance(data.get("output"), dict):
        return "build_info"
    if "source" in data and ("sourcePath" in data or "compiler" in data):
        return "legacy"
    if "ast" in data or "storageLayout" in data or \
            isinstance(data.get("output", {}).get("sources"), dict):
        return "ast"
    if "abi" in data and (
        "contractName" in data or "bytecode" in data or "deployedBytecode" in data
    ):
        return "abi"
    return ""


def discover_artifacts(root: Path | str, build_artifacts: Path | str | None = None) -> ArtifactDiscovery:
    root = Path(root)
    bases: list[Path] = []
    if build_artifacts:
        base = Path(build_artifacts)
        bases.append(base if base.is_absolute() else root / base)
    else:
        bases.extend(root / name for name in ("out", "artifacts", "build", "build-info"))
    result = ArtifactDiscovery()
    seen: set[Path] = set()
    for base in bases:
        if base.is_file() and base.suffix == ".json":
            paths = [base]
        elif base.is_dir():
            try:
                paths = sorted(base.rglob("*.json"))[:1000]
            except OSError:
                continue
        else:
            continue
        for path in paths:
            if path in seen:
                continue
            seen.add(path)
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError, TypeError):
                result.malformed_files += 1
                continue
            if not isinstance(data, dict):
                continue
            style = _style(data)
            if style:
                result.records.append(ArtifactRecord(str(path), style, data))
    styles = {record.style for record in result.records}
    if "build_info" in styles:
        result.mode = BUILD_INFO_PLUS_FALLBACK
    elif "ast" in styles:
        result.mode = AST_PLUS_FALLBACK
    elif "legacy" in styles:
        result.mode = LEGACY_ARTIFACT_PLUS_FALLBACK
    elif "abi" in styles:
        result.mode = ABI_PLUS_FALLBACK
    if result.malformed_files:
        result.warnings.append(
            f"ignored {result.malformed_files} malformed compiler artifact file(s)"
        )
    return result
