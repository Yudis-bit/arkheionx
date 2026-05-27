#!/usr/bin/env python3
"""Check v1.5.0 invariant/test-plan release-prep version wording."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STABLE_ACTION = "Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.4.0"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")


def check() -> list[str]:
    failures: list[str] = []
    readme = read("README.md")
    changelog = read("CHANGELOG.md")
    roadmap = read("docs/ROADMAP.md")
    action_docs = read("docs/GITHUB_ACTION_USAGE.md")
    scanner = read("scripts/pre_audit_scan.py")

    if 'VERSION = "1.5.0"' not in scanner:
        failures.append("scripts/pre_audit_scan.py does not set VERSION to 1.5.0")
    if "Latest stable release: **v1.4.0" not in readme:
        failures.append("README.md does not name v1.4.0 as latest stable release")
    if "## v1.5.0 - Unreleased" not in changelog:
        failures.append("CHANGELOG.md is missing v1.5.0 - Unreleased")
    if "## v1.4.0" not in changelog or "## v1.4.0 - Unreleased" in changelog:
        failures.append("CHANGELOG.md does not treat v1.4.0 as released")
    if "v1.5.0" not in roadmap or "Invariant/Test Plan Generator Upgrade current milestone" not in roadmap:
        failures.append("docs/ROADMAP.md does not mark v1.5.0 as current invariant/test-plan milestone")
    if "v1.6.0" not in roadmap or "Internal Engine Split" not in roadmap:
        failures.append("docs/ROADMAP.md does not keep v1.6.0 as next milestone")
    if STABLE_ACTION not in readme:
        failures.append("README.md is missing stable @v1.4.0 action example")
    if STABLE_ACTION not in action_docs:
        failures.append("docs/GITHUB_ACTION_USAGE.md is missing stable @v1.4.0 action example")
    stale = re.findall(r"Latest stable release: \*\*(?:v0\.[^*]+|v1\.0\.1[^*]*|v1\.1\.[^*]*|v1\.2\.0[^*]*|v1\.3\.0[^*]*)", readme)
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
