#!/usr/bin/env python3
"""Check v1.6.0 internal-engine release-prep version wording."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from arkheionx.version import CURRENT_MILESTONE, NEXT_MILESTONE, SCANNER_VERSION, STABLE_RELEASE  # noqa: E402


STABLE_ACTION = f"Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@{STABLE_RELEASE}"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")


def check() -> list[str]:
    failures: list[str] = []
    readme = read("README.md")
    changelog = read("CHANGELOG.md")
    roadmap = read("docs/ROADMAP.md")
    action_docs = read("docs/GITHUB_ACTION_USAGE.md")
    scanner = read("scripts/pre_audit_scan.py")

    if "VERSION = SCANNER_VERSION" not in scanner and f'VERSION = "{SCANNER_VERSION}"' not in scanner:
        failures.append(f"scripts/pre_audit_scan.py does not use scanner version {SCANNER_VERSION}")
    if f"Latest stable release: **{STABLE_RELEASE}" not in readme:
        failures.append(f"README.md does not name {STABLE_RELEASE} as latest stable release")
    if f"## {CURRENT_MILESTONE} - Unreleased" not in changelog:
        failures.append(f"CHANGELOG.md is missing {CURRENT_MILESTONE} - Unreleased")
    if "## v1.5.0" not in changelog or "## v1.5.0 - Unreleased" in changelog:
        failures.append("CHANGELOG.md does not treat v1.5.0 as released")
    if CURRENT_MILESTONE not in roadmap or "Internal Engine Split current milestone" not in roadmap:
        failures.append(f"docs/ROADMAP.md does not mark {CURRENT_MILESTONE} as current internal-engine milestone")
    if NEXT_MILESTONE not in roadmap or "Config + Rule Pack Stabilization" not in roadmap:
        failures.append(f"docs/ROADMAP.md does not keep {NEXT_MILESTONE} as next milestone")
    if STABLE_ACTION not in readme:
        failures.append(f"README.md is missing stable {STABLE_RELEASE} action example")
    if STABLE_ACTION not in action_docs:
        failures.append(f"docs/GITHUB_ACTION_USAGE.md is missing stable {STABLE_RELEASE} action example")
    stale = re.findall(r"Latest stable release: \*\*(?:v0\.[^*]+|v1\.0\.1[^*]*|v1\.1\.[^*]*|v1\.2\.0[^*]*|v1\.3\.0[^*]*|v1\.4\.0[^*]*)", readme)
    if stale:
        failures.append("README.md still has stale latest stable wording")
    if "## v1.0.0 - Unreleased" in changelog:
        failures.append("CHANGELOG.md still treats v1.0.0 as unreleased")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Arkheionx version consistency.")
    parser.add_argument("--check", action="store_true", help="Exit nonzero on version mismatches.")
    args = parser.parse_args(argv)
    failures = check()
    if failures:
        print("Version consistency issues:")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("ok: version consistency valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
