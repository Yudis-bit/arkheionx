"""Restrained, professional terminal color for Arkheionx human output.

Color is opt-in by environment and TTY. It is disabled automatically when
stdout is not a TTY (so captured output, pipes, CI logs, and the test suite get
plain text), and it is never applied to JSON or to content written to artifact
files. Standard library only.

Control:
- ARKHEIONX_COLOR=always  force color on
- ARKHEIONX_COLOR=never   force color off
- ARKHEIONX_COLOR=auto    (default) color only when stdout is a TTY
- NO_COLOR (any value)    disables color (unless ARKHEIONX_COLOR=always)
- CI (any value)          disables color (unless ARKHEIONX_COLOR=always)
- TERM=dumb               disables color (unless ARKHEIONX_COLOR=always)
"""
from __future__ import annotations

import os
import re
import sys

_RESET = "\033[0m"
_CODES = {
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
}
_ANSI_RE = re.compile(r"\033\[[0-9;]*m")

# Evidence/review level -> style.
_EVIDENCE_STYLE = {
    "HEURISTIC": ("yellow",),
    "COMPILER_CONFIRMED": ("cyan",),
    "EXECUTION_CONFIRMED": ("green",),
    "EVIDENCE_READY": ("green", "bold"),
    "NEEDS_HUMAN_REVIEW": ("yellow", "bold"),
    "HUMAN_REVIEW_REQUIRED": ("yellow", "bold"),
}
_EVIDENCE_RE = re.compile(r"\b(" + "|".join(_EVIDENCE_STYLE) + r")\b")

# Bare section labels that should render bold in report-style output.
_SECTIONS = {
    "Core", "Foundry", "Foundry (optional)", "Project", "Install", "PATH",
    "Install receipt", "Generated", "Proof", "Summary", "Money", "Top Surfaces",
    "Top Contracts", "Money Flow Summary", "Roles", "Journeys", "Next", "Safety",
    "Available demos", "Artifacts", "Evidence", "Report", "Status legend",
}


def enabled(stream=None) -> bool:
    """Whether color should be emitted for the given stream (default stdout)."""
    mode = os.environ.get("ARKHEIONX_COLOR", "auto").strip().lower()
    if mode == "always":
        return True
    if mode == "never":
        return False
    # Any other value (including invalid) falls back to auto.
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("CI") is not None:
        return False
    if os.environ.get("TERM", "") == "dumb":
        return False
    stream = stream or sys.stdout
    try:
        return bool(stream.isatty())
    except Exception:
        return False


def strip(text: str) -> str:
    """Remove ANSI escape sequences."""
    return _ANSI_RE.sub("", text)


def paint(text: str, *styles: str, stream=None) -> str:
    if not styles or not enabled(stream):
        return text
    prefix = "".join(_CODES[s] for s in styles if s in _CODES)
    return f"{prefix}{text}{_RESET}" if prefix else text


def _status_styles(value: str) -> tuple[str, ...]:
    v = value.strip().lower()
    if v in {"error", "failed", "fail", "build_failed", "tested_failed"}:
        return ("red",)
    if v in {"warning", "warn", "scaffolded", "no_proof", "no-artifacts", "heuristic"}:
        return ("yellow",)
    if v in {"ok", "passed", "pass", "tested_passed", "ready", "valid"}:
        return ("green",)
    return ("cyan",)


def _colorize_line(line: str) -> str:
    stripped = line.strip()
    if line.startswith("ARKHEIONX ") or line.startswith("Arkheionx package version:"):
        return paint(line, "bold")
    if stripped.startswith("Status:"):
        label, _, value = line.partition(":")
        return f"{label}:{paint(value, *_status_styles(value))}" if value else line
    if stripped in _SECTIONS and line == stripped:
        return paint(line, "bold")
    # Color evidence/review level tokens wherever they appear.
    return _EVIDENCE_RE.sub(lambda m: paint(m.group(0), *_EVIDENCE_STYLE[m.group(0)]), line)


def colorize_report(text: str, stream=None) -> str:
    """Apply restrained color to a full report-style string.

    No-op (returns text unchanged) when color is disabled, so non-TTY output,
    JSON, and tests are unaffected.
    """
    if not enabled(stream):
        return text
    return "\n".join(_colorize_line(line) for line in text.split("\n"))
