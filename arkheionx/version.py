"""Shared Arkheionx version metadata."""
from __future__ import annotations

# Package version is 7.5.0 (the v7.5.0 Protocol Lens Packs release). v7.5 adds the
# protocol-lens layer on top of the v7.0 Scope-Aware Orchestration + Evidence Judge
# layer; the first shipped lens is Morpho Midnight. This is the latest stable
# release the source installers and the GitHub Action pin to. The v7.5.0 git tag,
# GitHub Release, and site deploy are founder actions performed at release time.
__version__ = "7.5.0"
PACKAGE_VERSION = "7.5.0"
STABLE_RELEASE = "v7.5.0"
CURRENT_MILESTONE = "v7.5.0"
NEXT_MILESTONE = "v7.6.0"

# The legacy pre-audit scanner emits a frozen output version so committed
# example reports remain stable across package milestones. It is intentionally
# decoupled from CURRENT_MILESTONE.
SCANNER_VERSION = "2.0.1"
SCHEMA_VERSION = "1.0.0"
