"""Safe copy of demo fixtures to a user-chosen destination.

Resolves the fixture from bundled package resources (with a source-checkout
fallback), copies only source entries (never generated build/artifact dirs),
refuses to overwrite a non-empty destination unless forced, and never writes
outside the requested destination.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from arkheionx.demo.model import Demo
from arkheionx.demo.registry import fixture_source

# Allowlist of fixture source entries to copy (excludes out/, cache/, .arkheionx/).
SOURCE_ENTRIES = ("README.md", "foundry.toml", "src", "test")


class DemoCopyError(Exception):
    """Raised when a demo cannot be copied safely."""


def copy_demo(demo: Demo, dest: str, force: bool = False) -> tuple[Path, list[str], str]:
    target = Path(dest).expanduser()
    if target.exists():
        if not target.is_dir():
            raise DemoCopyError(f"destination exists and is not a directory: {target}")
        if any(target.iterdir()) and not force:
            raise DemoCopyError(
                f"destination is not empty: {target} (use --force to overwrite)"
            )

    try:
        with fixture_source(demo) as (src, source_kind):
            target.mkdir(parents=True, exist_ok=True)
            copied: list[str] = []
            for entry in SOURCE_ENTRIES:
                source = src / entry
                if not source.exists():
                    continue
                destination = target / entry
                if source.is_dir():
                    shutil.copytree(source, destination, dirs_exist_ok=True)
                else:
                    shutil.copy2(source, destination)
                copied.append(entry)
    except FileNotFoundError as exc:
        raise DemoCopyError(str(exc)) from exc

    if not copied:
        raise DemoCopyError(f"no source entries found to copy for demo '{demo.id}'")
    return target, copied, source_kind
