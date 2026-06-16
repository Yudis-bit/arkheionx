"""Deterministic normalization for root-cause descriptions."""
from __future__ import annotations

import re
import unicodedata

_SPACE = re.compile(r"\s+")
_PUNCT = re.compile(r"[^a-z0-9_./ -]+")


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").lower()
    text = text.replace("cross token", "cross-token")
    text = text.replace("chainid", "chain id")
    text = text.replace("zero-address", "zero address")
    text = _PUNCT.sub(" ", text)
    return _SPACE.sub(" ", text).strip()


def normalize_field(value: str, default: str = "unknown") -> str:
    text = normalize_text(value).replace(" ", "_")
    return text or default
