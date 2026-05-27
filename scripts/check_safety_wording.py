#!/usr/bin/env python3
"""Report unsafe Arkheionx product wording without adding dependencies."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from arkheionx.core.safety import BANNED_PHRASES, CLEAR_PROHIBITION_CONTEXT  # noqa: E402


def files_to_scan() -> list[Path]:
    roots = [
        ROOT / "README.md",
        ROOT / "SERVICES.md",
        ROOT / "docs",
        ROOT / ".github",
        ROOT / "scripts",
        ROOT / "templates",
        ROOT / "arkheionx",
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
        and path.name != "safety.py"
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
