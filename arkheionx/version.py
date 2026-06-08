"""Shared Arkheionx version metadata."""
from __future__ import annotations

# Package version is finalized at 7.0.0 (the v7.0.0 Scope-Aware Orchestration +
# Evidence Judge release) and is the latest stable release the source installers
# and the GitHub Action pin to. The v7.0.0 git tag, GitHub Release, and site
# deploy are founder actions; until that tag is pushed, the last published tag
# remains v4.0.0.
__version__ = "7.0.0"
PACKAGE_VERSION = "7.0.0"
STABLE_RELEASE = "v7.0.0"
CURRENT_MILESTONE = "v7.0.0"
NEXT_MILESTONE = "v7.1.0"

# The legacy pre-audit scanner emits a frozen output version so committed
# example reports remain stable across package milestones. It is intentionally
# decoupled from CURRENT_MILESTONE.
SCANNER_VERSION = "2.0.1"
SCHEMA_VERSION = "1.0.0"
