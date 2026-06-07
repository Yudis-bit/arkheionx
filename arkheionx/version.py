"""Shared Arkheionx version metadata."""
from __future__ import annotations

# Package version is finalized at 4.1.0 (the v4.1.0 research-memory release). The
# v4.1.0 git tag, GitHub Release, and site deploy are founder actions; until that
# tag is cut, the last published tag remains v4.0.0, and the last actually-tagged
# stable release the source installers and the GitHub Action pin to remains
# v3.1.0.
__version__ = "4.1.0"
PACKAGE_VERSION = "4.1.0"
STABLE_RELEASE = "v3.1.0"
CURRENT_MILESTONE = "v4.1.0"
NEXT_MILESTONE = "v4.2.0"

# The legacy pre-audit scanner emits a frozen output version so committed
# example reports remain stable across package milestones. It is intentionally
# decoupled from CURRENT_MILESTONE.
SCANNER_VERSION = "2.0.1"
SCHEMA_VERSION = "1.0.0"
