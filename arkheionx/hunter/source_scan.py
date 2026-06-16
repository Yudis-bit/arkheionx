"""Shared, local, read-only Solidity source-scanning helpers for hunter engines.

Deliberately lightweight (regex + brace matching, no compiler). Used by the
value-flow, state-machine, and call-graph engines so they all see the same parsed
functions and comment-stripped bodies. Read-only; capped; never touches the network.
"""
from __future__ import annotations

import re
from pathlib import Path

_FUNC_RE = re.compile(
    r"function\s+([A-Za-z_]\w*)\s*\(([^)]*)\)([^{;]*)(\{|;)",
    re.DOTALL,
)
_LINE_COMMENT = re.compile(r"//[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_VIS_RE = re.compile(r"\b(public|external|internal|private)\b")
_MUT_RE = re.compile(r"\b(view|pure|payable)\b")


def strip_comments(text: str) -> str:
    text = _BLOCK_COMMENT.sub(" ", text)
    text = _LINE_COMMENT.sub(" ", text)
    return text


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, max(0, index)) + 1


def _match_body(text: str, brace_start: int) -> tuple[str, int]:
    """Return (body_text, end_index) by matching braces from ``brace_start``."""
    depth = 0
    i = brace_start
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start + 1:i], i
        i += 1
    return text[brace_start + 1:], n


class ParsedFunction:
    __slots__ = ("name", "visibility", "mutability", "body", "line", "raw_signature")

    def __init__(self, name, visibility, mutability, body, line, raw_signature):
        self.name = name
        self.visibility = visibility
        self.mutability = mutability
        self.body = body
        self.line = line
        self.raw_signature = raw_signature


def find_functions(text: str) -> list:
    """Find function definitions with comment-stripped bodies and detected visibility."""
    clean = strip_comments(text)
    out: list = []
    for m in _FUNC_RE.finditer(clean):
        name = m.group(1)
        attrs = m.group(3) or ""
        vis_m = _VIS_RE.search(attrs)
        mut_m = _MUT_RE.search(attrs)
        visibility = vis_m.group(1) if vis_m else "public"
        mutability = mut_m.group(1) if mut_m else ""
        if m.group(4) == "{":
            body, _ = _match_body(clean, m.end() - 1)
        else:
            body = ""  # abstract / interface declaration, no body
        out.append(ParsedFunction(name, visibility, mutability, body,
                                  line_of(clean, m.start()), m.group(0)))
    return out


def load_contract_sources(review_map, root: Path) -> dict:
    """Map contract name -> (path, raw_text) using review-map contract paths."""
    sources: dict[str, tuple[str, str]] = {}
    for c in getattr(review_map, "contracts", []) or []:
        path = getattr(c, "path", "")
        if not path:
            continue
        p = Path(path)
        if not p.is_absolute():
            p = root / path
        try:
            if p.is_file() and p.stat().st_size <= 600_000:
                sources[c.name] = (str(p), p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return sources
