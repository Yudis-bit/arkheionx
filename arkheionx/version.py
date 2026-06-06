"""Shared Arkheionx version metadata."""
from __future__ import annotations

__version__ = "3.9.0"
PACKAGE_VERSION = "3.9.0"
STABLE_RELEASE = "v3.1.0"
CURRENT_MILESTONE = "v3.9.0"
NEXT_MILESTONE = "v4.0.0"

# The legacy pre-audit scanner emits a frozen output version so committed
# example reports remain stable across package milestones. It is intentionally
# decoupled from CURRENT_MILESTONE.
SCANNER_VERSION = "2.0.1"
SCHEMA_VERSION = "1.0.0"
