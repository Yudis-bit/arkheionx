"""Shared Arkheionx version metadata."""
from __future__ import annotations

# Private V9.1 development milestone. The latest stable release remains v8.0.1;
# this development version is not tagged, released, pushed, or deployed.
__version__ = "9.1.0.dev0"
PACKAGE_VERSION = "9.1.0.dev0"
STABLE_RELEASE = "v8.0.1"
CURRENT_MILESTONE = "v9.1.0-dev"
NEXT_MILESTONE = "v9.1.0"

# The legacy pre-audit scanner emits a frozen output version so committed
# example reports remain stable across package milestones. It is intentionally
# decoupled from CURRENT_MILESTONE.
SCANNER_VERSION = "2.0.1"
SCHEMA_VERSION = "1.0.0"
