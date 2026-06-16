"""Secret redaction for fork-lab artifacts (Layer 8).

Artifacts must never contain RPC URLs, API keys, or private keys. This module
redacts those patterns and reports whether any were found.
"""
from __future__ import annotations

import re

_URL_RE = re.compile(r"\b(?:https?|wss?)://[^\s\"'<>)\]]+", re.I)
_PRIVKEY_RE = re.compile(r"\b0x[0-9a-fA-F]{64}\b")
_APIKEY_RE = re.compile(r"(?i)\b(api[_-]?key|secret|access[_-]?token|password)\b\s*[=:]\s*\S+")
_INFURA_ALCHEMY = re.compile(r"(?i)\b(infura|alchemy|quiknode|ankr)\b[^\s]*")

REDACTED_URL = "[REDACTED_RPC_URL — use an env var name instead]"
REDACTED_KEY = "[REDACTED_KEY]"
REDACTED_SECRET = "[REDACTED_SECRET]"


def redact(text: str) -> str:
    if not text:
        return text
    text = _URL_RE.sub(REDACTED_URL, text)
    text = _PRIVKEY_RE.sub(REDACTED_KEY, text)
    text = _APIKEY_RE.sub(lambda m: m.group(0).split("=")[0].split(":")[0].rstrip() + "=" + REDACTED_SECRET, text)
    text = _INFURA_ALCHEMY.sub(REDACTED_SECRET, text)
    return text


def scan(text: str) -> list:
    warnings = []
    if _URL_RE.search(text or ""):
        warnings.append("An RPC/WS URL appears in an artifact; redact it (use an env var name).")
    if _PRIVKEY_RE.search(text or ""):
        warnings.append("A 32-byte hex value (possible private key) appears; redact it.")
    if _APIKEY_RE.search(text or ""):
        warnings.append("An api-key/secret/token assignment appears; redact it.")
    return warnings
