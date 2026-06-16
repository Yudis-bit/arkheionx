"""Repository-level ingestion summary."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path

from .artifact_discovery import FALLBACK_ONLY, discover_artifacts
from .framework_detector import detect_framework
from .solidity_discovery import discover_solidity


@dataclass
class IngestSummary:
    target: str = ""
    framework: str = "unknown"
    solidity_files_indexed: int = 0
    contracts_indexed: int = 0
    real_contracts_indexed: int = 0
    artifact_only_contracts_indexed: int = 0
    artifact_mode: str = FALLBACK_ONLY
    artifact_records: int = 0
    stale_artifacts_ignored: int = 0
    sample_artifacts_ignored: int = 0
    excluded_dependency_files: int = 0
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def inspect_repository(
    target: Path | str,
    *,
    framework: str = "auto",
    build_artifacts: Path | str | None = None,
    solidity_root: Path | str | None = None,
    include_paths: list | None = None,
    include_deps: bool = False,
    include_tests: bool = False,
    include_scripts: bool = False,
):
    target = Path(target)
    sources = discover_solidity(
        target,
        include_paths=include_paths,
        include_deps=include_deps,
        include_tests=include_tests,
        include_scripts=include_scripts,
        solidity_root=solidity_root,
    )
    artifacts = discover_artifacts(target, build_artifacts)
    summary = IngestSummary(
        target=str(target),
        framework=detect_framework(target, framework),
        solidity_files_indexed=sources.files_indexed,
        artifact_mode=artifacts.mode,
        artifact_records=len(artifacts.records),
        excluded_dependency_files=sources.excluded_dependency_files,
        warnings=list(sources.warnings) + list(artifacts.warnings),
    )
    return summary, sources, artifacts
