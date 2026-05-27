"""Preview internal Arkheionx CLI.

This is not the future v2 installable CLI. It exposes only package health and
version information while existing scripts remain the supported entrypoints.
"""
from __future__ import annotations

import argparse
import platform
import sys

from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER
from arkheionx.rules.registry import RULE_PACKS
from arkheionx.version import CURRENT_MILESTONE, STABLE_RELEASE, __version__


def command_version() -> int:
    print(f"Arkheionx package version: {__version__}")
    print(f"Latest stable release: {STABLE_RELEASE}")
    print(f"Current milestone: {CURRENT_MILESTONE}")
    return 0


def command_doctor() -> int:
    print("Arkheionx doctor")
    print(f"Python: {platform.python_version()}")
    print(f"Package imports: ok")
    print("Rule packs:")
    for key, info in sorted(RULE_PACKS.items()):
        print(f"- {key}: {info['display_name']} ({info['prefix']})")
    print(LOCAL_ONLY_DISCLAIMER)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview Arkheionx internal CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("version", help="Print package and release milestone metadata.")
    subparsers.add_parser("doctor", help="Check local package imports and rule-pack metadata.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "version":
        return command_version()
    if args.command == "doctor":
        return command_doctor()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
