"""Universal local Solidity repository ingestion."""
from __future__ import annotations

from .artifact_discovery import ArtifactDiscovery, ArtifactRecord, discover_artifacts
from .framework_detector import (
    BROWNIE_STYLE,
    FOUNDRY_STYLE,
    GENERIC_SOLIDITY,
    HARDHAT_STYLE,
    TRUFFLE_STYLE,
    UNKNOWN,
    detect_framework,
)
from .repo_detector import IngestSummary, inspect_repository
from .solidity_discovery import SolidityDiscovery, SourceFile, discover_solidity

__all__ = [
    "ArtifactDiscovery",
    "ArtifactRecord",
    "IngestSummary",
    "SolidityDiscovery",
    "SourceFile",
    "discover_artifacts",
    "discover_solidity",
    "detect_framework",
    "inspect_repository",
    "FOUNDRY_STYLE",
    "HARDHAT_STYLE",
    "TRUFFLE_STYLE",
    "BROWNIE_STYLE",
    "GENERIC_SOLIDITY",
    "UNKNOWN",
]
