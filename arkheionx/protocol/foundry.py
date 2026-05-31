"""Foundry detection and safe local execution.

Foundry is an optional precision backend. Detection never raises and never
fails the calling command; absence simply keeps results at HEURISTIC evidence.

Safety: local only, no shell=True, subprocess timeouts, no transactions, no
fork unless an explicit caller flag is added later. Raw output is meant to be
captured to artifact files, not streamed to the terminal.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# Foundry status enum values.
UNAVAILABLE = "unavailable"
AVAILABLE_NOT_BUILT = "available_not_built"
BUILD_FAILED = "build_failed"
BUILD_PASSED = "build_passed"


@dataclass
class FoundryStatus:
    status: str = UNAVAILABLE
    forge_available: bool = False
    forge_version: str = ""
    has_foundry_toml: bool = False
    src_dir: str = ""
    test_dir: str = ""
    out_dir: str = ""
    compiled_contracts: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _forge_version() -> str:
    try:
        result = subprocess.run(
            ["forge", "--version"],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""


def _discover_dir(root: Path, *candidates: str) -> str:
    for name in candidates:
        if (root / name).is_dir():
            return name
    return ""


def detect_foundry(root: Path, with_version: bool = False) -> FoundryStatus:
    """Detect a Foundry project at ``root`` without building.

    ``with_version`` runs ``forge --version`` (a subprocess); callers that only
    need availability (the common case) can skip it.
    """

    status = FoundryStatus()
    status.has_foundry_toml = (root / "foundry.toml").is_file()
    status.forge_available = shutil.which("forge") is not None
    status.src_dir = _discover_dir(root, "src", "contracts")
    status.test_dir = _discover_dir(root, "test", "tests")
    status.out_dir = _discover_dir(root, "out")
    if status.forge_available and with_version:
        status.forge_version = _forge_version()
    if not status.has_foundry_toml:
        status.status = UNAVAILABLE
        status.notes.append("No foundry.toml found; static analysis only.")
    elif not status.forge_available:
        status.status = UNAVAILABLE
        status.notes.append("foundry.toml present but `forge` is not on PATH.")
    else:
        status.status = AVAILABLE_NOT_BUILT
    return status


def run_build(root: Path, timeout: int = 240) -> tuple[bool, str]:
    """Run ``forge build`` locally. Returns ``(passed, combined_output)``."""

    try:
        result = subprocess.run(
            ["forge", "build"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"forge build timed out after {timeout}s"
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"forge build could not be launched: {exc}"
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output


def collect_compiled_contracts(root: Path, out_dir: str = "out") -> list[str]:
    """List contract names that produced a compiled artifact under ``out/``."""

    out = root / (out_dir or "out")
    if not out.is_dir():
        return []
    names: set[str] = set()
    for artifact in out.rglob("*.json"):
        # Foundry layout: out/<File>.sol/<Contract>.json
        if artifact.parent.name.endswith(".sol"):
            names.add(artifact.stem)
    return sorted(names)


def build_and_confirm(root: Path, timeout: int = 240) -> tuple[FoundryStatus, str]:
    """Detect, optionally build, and confirm compiled contracts.

    Returns the updated :class:`FoundryStatus` and the raw build output (empty
    string when no build was attempted).
    """

    status = detect_foundry(root)
    if status.status != AVAILABLE_NOT_BUILT:
        return status, ""
    passed, output = run_build(root, timeout=timeout)
    if passed:
        status.status = BUILD_PASSED
        status.compiled_contracts = collect_compiled_contracts(root, status.out_dir or "out")
    else:
        status.status = BUILD_FAILED
        status.notes.append("forge build failed; falling back to heuristic analysis.")
    return status, output
