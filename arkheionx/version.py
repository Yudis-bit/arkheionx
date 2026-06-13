"""Shared Arkheionx version metadata."""
from __future__ import annotations

# Package version is 8.0.0 (the v8.0.0 "Final Engine" release). v8 consolidates the
# product into one clean, local-first review workflow: it adds the primary
# `arkheionx review` command, presents Protocol Lens Packs as generic protocol-family
# models (the first shipped lens is the generic Fixed Credit Market family),
# strengthens schema-backed review artifacts, and cleans the public surface so it is
# not target-specific. This is the latest stable release the source installers and
# the GitHub Action pin to. The v8.0.0 git tag, GitHub Release, and site deploy are
# founder actions performed at release time.
__version__ = "8.0.0"
PACKAGE_VERSION = "8.0.0"
STABLE_RELEASE = "v8.0.0"
CURRENT_MILESTONE = "v8.0.0"
NEXT_MILESTONE = "v8.1.0"

# The legacy pre-audit scanner emits a frozen output version so committed
# example reports remain stable across package milestones. It is intentionally
# decoupled from CURRENT_MILESTONE.
SCANNER_VERSION = "2.0.1"
SCHEMA_VERSION = "1.0.0"
