#!/usr/bin/env python3
"""Report unsafe Arkheionx product wording without adding dependencies."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BANNED_PHRASES = [
    "guaranteed secure",
    "audit replacement",
    "cheap audit",
    "fully verified database",
    "bounty guaranteed",
    "live exploit",
    "profit calculator",
    "attack live protocol",
    "autonomous exploit runner",
    "weaponize",
    "drain helper",
    "guaranteed bounty",
    "guaranteed findings",
    "auto exploit",
    "paid customer",
    "fake adoption",
    "customer claim",
    "trusted by",
    "adopted by",
    "proven in production",
    "official audit",
    "certification",
    "security guarantee",
    "bounty guarantee",
    "exploit discovery guarantee",
    "official ecosystem partner",
    "ecosystem certified",
    "audit certified",
    "trusted by ecosystems",
    "customer-proven",
    "adopted by ecosystems",
    "guaranteed security",
    "official audit partner",
]
CLEAR_PROHIBITION_CONTEXT = [
    "do not",
    "does not",
    "without",
    "not ",
    "no ",
    "must not",
    "never",
    "prohibited",
    "disallowed",
    "unsafe phrase",
    "banned",
    "avoid",
    "not included",
    "not allowed",
    "claim boundaries",
    "exclusions",
    "does not buy",
    "does not provide",
    "what this is not",
    "what paid work does not include",
    "what this work does not include",
    "disallowed language",
    "words to avoid",
    "not_included",
    "not recommended",
]


def files_to_scan() -> list[Path]:
    roots = [
        ROOT / "README.md",
        ROOT / "SERVICES.md",
        ROOT / "docs",
        ROOT / ".github",
        ROOT / "scripts",
        ROOT / "templates",
        ROOT / "examples",
        ROOT / "reports",
        ROOT / "metadata",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.exists():
            files.extend(path for path in root.rglob("*") if path.is_file())
    return [
        path
        for path in files
        if path.suffix.lower() in {".md", ".yml", ".yaml", ".json", ".py", ".sol", ".toml"}
        and path.name != "check_safety_wording.py"
    ]


def phrase_allowed(context: str) -> bool:
    lower = context.lower()
    return any(marker in lower for marker in CLEAR_PROHIBITION_CONTEXT)


def scan() -> list[str]:
    warnings: list[str] = []
    for path in files_to_scan():
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, 1):
            lower = line.lower()
            context = "\n".join(lines[max(0, number - 12) : number])
            for phrase in BANNED_PHRASES:
                if phrase in lower and not phrase_allowed(context):
                    warnings.append(f"{path.relative_to(ROOT)}:{number}: {phrase}")
    return warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Arkheionx safety wording.")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero if warnings are found.")
    args = parser.parse_args(argv)
    warnings = scan()
    if warnings:
        print("Safety wording warnings:")
        for warning in warnings:
            print(f"- {warning}")
        return 1 if args.strict else 0
    print("ok: safety wording valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
