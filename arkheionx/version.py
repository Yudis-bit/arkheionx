"""Shared Arkheionx version metadata."""
from __future__ import annotations

# Package version is 9.0.0.dev0 (the v9.0.0.dev0 "Clean Product Surface" release). v9.0.0.dev0 is a
# product-surface patch on top of the v8.0.0 "Final Engine" release: it rewrites the
# root README and rebuilds the website so Arkheionx reads as one current product
# instead of a version-heavy archive. It adds no engine behavior, no CLI command, and
# no analysis change; the v8.0.0 review workflow, Protocol Lens Packs, schemas, and
# safety boundaries are preserved. This is the latest stable release the source
# installers and the GitHub Action pin to. The v9.0.0.dev0 git tag, GitHub Release, and
# site deploy are founder actions performed at release time.
__version__ = "9.0.0.dev0"
PACKAGE_VERSION = "9.0.0.dev0"
STABLE_RELEASE = "v8.0.1"
CURRENT_MILESTONE = "v9.0.0-dev"
NEXT_MILESTONE = "v9.0.0"

# The legacy pre-audit scanner emits a frozen output version so committed
# example reports remain stable across package milestones. It is intentionally
# decoupled from CURRENT_MILESTONE.
SCANNER_VERSION = "2.0.1"
SCHEMA_VERSION = "1.0.0"
