"""Shared Arkheionx version metadata."""
from __future__ import annotations

# Package version is finalized at 4.0.0 (the v4.0.0 release candidate). The
# v4.0.0 git tag and GitHub Release are founder actions; until that tag exists,
# STABLE_RELEASE remains the last actually-tagged stable (v3.1.0), which is what
# the source installers and the GitHub Action pin to.
__version__ = "4.0.0"
PACKAGE_VERSION = "4.0.0"
STABLE_RELEASE = "v3.1.0"
CURRENT_MILESTONE = "v4.0.0"
NEXT_MILESTONE = "v4.1.0"

# The legacy pre-audit scanner emits a frozen output version so committed
# example reports remain stable across package milestones. It is intentionally
# decoupled from CURRENT_MILESTONE.
SCANNER_VERSION = "2.0.1"
SCHEMA_VERSION = "1.0.0"
