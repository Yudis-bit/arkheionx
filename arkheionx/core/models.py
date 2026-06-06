"""Lightweight shared data models for future Arkheionx engine migration."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class EvidenceItem:
    """A local evidence pointer collected during static readiness analysis."""

    path: str
    line: int | None = None
    symbol: str = ""
    snippet: str = ""


@dataclass(frozen=True)
class Finding:
    """Small package-level finding shape for generators and future adapters."""

    finding_id: str
    title: str
    category: str
    priority: str = ""
    confidence: str = ""
    evidence: tuple[EvidenceItem, ...] = ()
    suggested_tests: tuple[str, ...] = ()
    invariant_candidates: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScanSourceSummary:
    """Summary of a scanned local repository tree."""

    root: Path
    protocol_type: str = "auto"
    source_files: int = 0
    test_files: int = 0


@dataclass(frozen=True)
class OutputArtifact:
    """A generated local output artifact."""

    name: str
    path: Path
    description: str = ""


@dataclass(frozen=True)
class RulePackInfo:
    """Metadata for a defensive readiness rule family."""

    key: str
    display_name: str
    prefix: str
    docs: str
    description: str = ""
    default_enabled: bool = True
    related_protocol_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class GeneratedArtifactInfo:
    """Metadata for generated content ignored by source-evidence scans."""

    pattern: str
    reason: str
    markers: tuple[str, ...] = field(default_factory=tuple)
