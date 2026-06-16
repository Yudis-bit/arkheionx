"""Evidence snippet extraction: turn a corpus match into a located excerpt.

Given a corpus document and a character offset (or substring), produce an
``EvidenceSnippet`` carrying the source path, the 1-based line range, and a short
excerpt. Local/static only; this just reads text already collected.
"""
from __future__ import annotations

from . import models as M


def _excerpt(text: str, line_start: int, line_end: int, max_chars: int = 240) -> str:
    lines = text.splitlines()
    chunk = lines[max(0, line_start - 1): line_end]
    excerpt = " ".join(s.strip() for s in chunk if s.strip())
    excerpt = excerpt.replace("`", "")
    if len(excerpt) > max_chars:
        excerpt = excerpt[: max_chars - 3] + "..."
    return excerpt


def snippet_at_offset(doc, offset: int, *, reason: str = "", context_lines: int = 1) -> M.EvidenceSnippet:
    line = doc.line_of(offset)
    line_start = max(1, line - context_lines)
    line_end = line + context_lines
    return M.EvidenceSnippet(
        source_path=doc.rel_path,
        line_start=line_start,
        line_end=line_end,
        excerpt=_excerpt(doc.text, line_start, line_end),
        kind=doc.kind,
        reason=reason,
    )


def snippet_for_term(doc, term: str, *, reason: str = "", context_lines: int = 1) -> M.EvidenceSnippet | None:
    if not term:
        return None
    idx = doc.lower.find(term.lower())
    if idx == -1:
        return None
    return snippet_at_offset(doc, idx, reason=reason, context_lines=context_lines)


def first_snippet(doc, terms, *, reason: str = "") -> M.EvidenceSnippet | None:
    """Return a snippet for the first matching term in ``terms``."""
    for term in terms:
        snippet = snippet_for_term(doc, term, reason=reason)
        if snippet is not None:
            return snippet
    return None
