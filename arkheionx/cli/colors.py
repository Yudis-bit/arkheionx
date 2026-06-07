"""Restrained, professional terminal color for Arkheionx human output.

Color is opt-in by environment and TTY. It is disabled automatically when
stdout is not a TTY (so captured output, pipes, CI logs, and the test suite get
plain text), and it is never applied to JSON or to content written to artifact
files. Standard library only.

Control (first match wins):
- NO_COLOR (any value)         disables color (authoritative, no-color.org)
- ARKHEIONX_NO_COLOR (any)     disables color (authoritative)
- ARKHEIONX_COLOR=never|0|off  disables color (also false/no)
- ARKHEIONX_COLOR=always|force|1|on  forces color on, even for a non-TTY or CI
  (also true/yes) so redirected smoke tests and `| cat` still show color
- ARKHEIONX_COLOR=auto (default, or any unknown value) colors only a TTY
- CI (any value)               disables auto color (force still wins)
- TERM=dumb                    disables auto color (force still wins)
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

# ARKHEIONX_COLOR values that force color on (even for a non-TTY or under CI) and
# values that force it off. Anything else (including "auto") is TTY-driven.
_COLOR_FORCE = {"always", "force", "1", "true", "yes", "on"}
_COLOR_OFF = {"never", "0", "false", "no", "off"}

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
    "Boundary", "Progress",
}

# Section headers that carry trailing descriptive text, e.g.
# "Review Priorities (review order, not confirmed findings)".
_SECTION_PREFIXES = ("Review Priorities", "Inspect first")

# Review/hunt priority tags, e.g. "[high]". Red is reserved for real errors, so
# severity escalates through bold amber and dim rather than red.
_PRIORITY_STYLE = {
    "critical": ("red", "bold"),
    "high": ("yellow", "bold"),
    "medium": ("yellow",),
    "low": ("dim",),
}
_PRIORITY_RE = re.compile(r"\[(" + "|".join(_PRIORITY_STYLE) + r")\]")

# Inline status values in an indented "  label: value" health line (doctor).
# Only the leading status token of the value is colored; versions, counts, and
# free text are left untouched so the line stays readable and copyable.
_VALUE_STATUS_STYLE = {
    "ok": ("green",),
    "yes": ("green",),
    "clean": ("green",),
    "passed": ("green",),
    "ready": ("green",),
    "valid": ("green",),
    "writable": ("green",),
    "enabled": ("green",),
    "missing": ("yellow",),
    "warning": ("yellow",),
    "heuristic": ("yellow",),
    "disabled": ("yellow",),
    "scaffolded": ("yellow",),
    "partial": ("yellow",),
    "failed": ("red",),
    "error": ("red",),
}
_KV_RE = re.compile(r"^(\s+[\w .()/+-]+:\s+)([A-Za-z][\w-]*)(.*)$")


def enabled(stream=None) -> bool:
    """Whether color should be emitted for the given stream (default stdout).

    Precedence: an explicit opt-out (NO_COLOR / ARKHEIONX_NO_COLOR) always wins;
    then ARKHEIONX_COLOR off/force values; otherwise auto, which colors only a
    real TTY and stays off under CI or TERM=dumb. A force value (1/always/force/
    on/true/yes) deliberately overrides CI and non-TTY so that redirected smoke
    tests and piped output still show color.
    """
    # Authoritative opt-out: respected even over an explicit force request.
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("ARKHEIONX_NO_COLOR") is not None:
        return False
    mode = os.environ.get("ARKHEIONX_COLOR", "auto").strip().lower()
    if mode in _COLOR_OFF:
        return False
    if mode in _COLOR_FORCE:
        return True
    # auto (default, or any unrecognized value): TTY-driven, off in CI/dumb term.
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


def priority_tag(priority: str, stream=None) -> str:
    """Render a bracketed review-priority tag (e.g. ``[high]``) with restrained
    color. Returns the plain ``[priority]`` when color is disabled. Red is
    reserved for real errors, so severity escalates through bold amber and dim.
    """
    style = _PRIORITY_STYLE.get(priority.strip().lower())
    return paint(f"[{priority}]", *style, stream=stream) if style else f"[{priority}]"


def _status_styles(value: str) -> tuple[str, ...]:
    v = value.strip().lower()
    if v in {"error", "failed", "fail", "build_failed", "tested_failed"}:
        return ("red",)
    if v in {"warning", "warn", "scaffolded", "no_proof", "no-artifacts", "heuristic"}:
        return ("yellow",)
    if v in {"ok", "passed", "pass", "tested_passed", "ready", "valid"}:
        return ("green",)
    return ("cyan",)


def _color_tokens(text: str) -> str:
    """Color inline evidence-level and priority tokens wherever they appear."""
    text = _EVIDENCE_RE.sub(lambda m: paint(m.group(0), *_EVIDENCE_STYLE[m.group(0)]), text)
    text = _PRIORITY_RE.sub(lambda m: paint(m.group(0), *_PRIORITY_STYLE[m.group(1)]), text)
    return text


def _colorize_line(line: str) -> str:
    stripped = line.strip()
    # Product identity (header / version banner) carries the brand color.
    if line.startswith("ARKHEIONX ") or line.startswith("Arkheionx package version:"):
        return paint(line, "cyan", "bold")
    if stripped.startswith("Status:"):
        label, _, value = line.partition(":")
        return f"{label}:{paint(value, *_status_styles(value))}" if value else line
    if line == stripped and (
        stripped in _SECTIONS or any(stripped.startswith(p) for p in _SECTION_PREFIXES)
    ):
        return paint(line, "bold")
    # Indented "  label: value" health line: color the leading status token only.
    kv = _KV_RE.match(line)
    if kv and kv.group(2).lower() in _VALUE_STATUS_STYLE:
        prefix, value, rest = kv.group(1), kv.group(2), kv.group(3)
        return prefix + paint(value, *_VALUE_STATUS_STYLE[value.lower()]) + _color_tokens(rest)
    return _color_tokens(line)


def colorize_report(text: str, stream=None) -> str:
    """Apply restrained color to a full report-style string.

    No-op (returns text unchanged) when color is disabled, so non-TTY output,
    JSON, and tests are unaffected.
    """
    if not enabled(stream):
        return text
    return "\n".join(_colorize_line(line) for line in text.split("\n"))
