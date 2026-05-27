"""Small local search helpers for future knowledge-engine extraction."""
from __future__ import annotations

from typing import Iterable


def normalize_query(query: str) -> str:
    return " ".join(query.lower().split())


def score_text(query_terms: Iterable[str], text: str) -> int:
    lower = text.lower()
    return sum(1 for term in query_terms if term and term in lower)
