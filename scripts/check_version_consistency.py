#!/usr/bin/env python3
"""Check v1.0.0 release-candidate version wording."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STABLE_ACTION = "Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.0.0"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")


def check() -> list[str]:
    failures: list[str] = []
    readme = read("README.md")
    changelog = read("CHANGELOG.md")
    roadmap = read("docs/ROADMAP.md")
    action_docs = read("docs/GITHUB_ACTION_USAGE.md")
    scanner = read("scripts/pre_audit_scan.py")

    if 'VERSION = "1.0.0"' not in scanner:
        failures.append("scripts/pre_audit_scan.py does not set VERSION to 1.0.0")
    if "Latest stable release: **v1.0.0" not in readme:
        failures.append("README.md does not name v1.0.0 as latest stable release")
    if "## v1.0.0 - Unreleased" not in changelog:
        failures.append("CHANGELOG.md is missing v1.0.0 - Unreleased")
    if "v1.0.0" not in roadmap or "Stable public release" not in roadmap:
        failures.append("docs/ROADMAP.md does not mention v1.0.0 stable public release")
    if STABLE_ACTION not in readme:
        failures.append("README.md is missing stable @v1.0.0 action example")
    if STABLE_ACTION not in action_docs:
        failures.append("docs/GITHUB_ACTION_USAGE.md is missing stable @v1.0.0 action example")
    stale = re.findall(r"Latest stable release: \*\*v0\.[^*]+", readme)
    if stale:
        failures.append("README.md still has stale v0.x latest stable wording")
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
