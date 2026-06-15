"""Configurable Solidity source discovery for common and generic layouts."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from .path_filters import exclusion_reason

_MAX_FILE_BYTES = 600_000
_MAX_FILES = 1200
DISCOVERY_PATTERNS = (
    "**/*.sol",
    "contracts/**/*.sol",
    "src/**/*.sol",
    "modules/**/*.sol",
    "packages/**/contracts/**/*.sol",
    "packages/**/src/**/*.sol",
)


@dataclass
class SourceFile:
    path: str
    rel: str
    text: str


@dataclass
class SolidityDiscovery:
    root: str = ""
    inspected_patterns: list = field(default_factory=lambda: list(DISCOVERY_PATTERNS))
    sources: list = field(default_factory=list)
    excluded_dependency_files: int = 0
    excluded_test_files: int = 0
    excluded_script_files: int = 0
    excluded_generated_files: int = 0
    oversized_files: int = 0
    warnings: list = field(default_factory=list)

    @property
    def files_indexed(self) -> int:
        return len(self.sources)

    def to_dict(self) -> dict:
        data = dataclasses.asdict(self)
        data["files_indexed"] = self.files_indexed
        data["sources"] = [source.rel for source in self.sources]
        return data


def _included(rel: str, include_paths: list | None) -> bool:
    if not include_paths:
        return True
    path = PurePosixPath(rel)
    for raw in include_paths:
        value = str(raw or "").strip().strip("/")
        if not value:
            continue
        if path.match(value) or path.match(value.rstrip("/") + "/**"):
            return True
        prefix = value.split("*", 1)[0].rstrip("/")
        if prefix and (rel == prefix or rel.startswith(prefix + "/")):
            return True
    return False


def discover_solidity(
    root: Path | str,
    *,
    include_paths: list | None = None,
    include_deps: bool = False,
    include_tests: bool = False,
    include_scripts: bool = False,
    solidity_root: Path | str | None = None,
) -> SolidityDiscovery:
    requested = Path(root)
    scan_root = Path(solidity_root) if solidity_root else requested
    if solidity_root and not scan_root.is_absolute():
        scan_root = requested / scan_root
    result = SolidityDiscovery(root=str(scan_root))
    if scan_root.is_file() and scan_root.suffix == ".sol":
        try:
            result.sources.append(SourceFile(
                str(scan_root),
                scan_root.name,
                scan_root.read_text(encoding="utf-8", errors="ignore"),
            ))
        except OSError as exc:
            result.warnings.append(f"source read failed: {exc}")
        return result
    if not scan_root.is_dir():
        result.warnings.append("source root is not a directory")
        return result

    try:
        found: dict[Path, Path] = {}
        for pattern in DISCOVERY_PATTERNS:
            for path in scan_root.glob(pattern):
                found[path] = path
        paths = sorted(found)
    except OSError as exc:
        result.warnings.append(f"source discovery failed: {exc}")
        return result
    for path in paths:
        try:
            rel_path = path.relative_to(scan_root)
        except ValueError:
            continue
        reason = exclusion_reason(
            rel_path.parts[:-1],
            include_deps=include_deps,
            include_tests=include_tests,
            include_scripts=include_scripts,
        )
        if reason:
            attr = {
                "dependency": "excluded_dependency_files",
                "test": "excluded_test_files",
                "script": "excluded_script_files",
                "generated_or_build": "excluded_generated_files",
            }[reason]
            setattr(result, attr, getattr(result, attr) + 1)
            continue
        rel = rel_path.as_posix()
        if not _included(rel, include_paths):
            continue
        try:
            if not path.is_file():
                continue
            if path.stat().st_size > _MAX_FILE_BYTES:
                result.oversized_files += 1
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        result.sources.append(SourceFile(str(path), rel, text))
        if len(result.sources) >= _MAX_FILES:
            result.warnings.append(f"source file cap reached: {_MAX_FILES}")
            break
    if not result.sources:
        result.warnings.append(
            "ZERO_CONTRACTS_INDEXED: this war-run did not analyze Solidity contracts. "
            "Check target path, framework detection, or ingestion settings."
        )
    return result
