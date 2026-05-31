"""Shared Arkheionx version metadata."""
from __future__ import annotations

__version__ = "2.7.0-dev"
PACKAGE_VERSION = "2.7.0.dev0"
STABLE_RELEASE = "v2.6.0"
CURRENT_MILESTONE = "v2.7.0"
NEXT_MILESTONE = "v2.8.0"

# The legacy pre-audit scanner emits a frozen output version so committed
# example reports remain stable across package milestones. It is intentionally
# decoupled from CURRENT_MILESTONE.
SCANNER_VERSION = "2.0.1"
SCHEMA_VERSION = "1.0.0"
