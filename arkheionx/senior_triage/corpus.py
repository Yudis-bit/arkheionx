"""Local text-collection helpers for senior triage.

All readers here are local/static and read-only. They never reach the network,
never read secrets, and cap how much they read so a triage run stays cheap. No
RPC, no live-chain access, no private keys.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# File types accepted from --known / --audits folders and local scan targets.
TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv", ".sol"}

# Local scan targets (relative to the repo root) used when mapping known behavior.
LOCAL_SCAN_DIRS = ("test", "tests", "src", "contracts", "docs", "release-notes")
LOCAL_SCAN_FILES = ("README.md", "CHANGELOG.md")

# Behavior vocabulary used for heuristic dedup / freshness matching. Generic and
# protocol-agnostic on purpose.
BEHAVIOR_TERMS = (
    "inflation",
    "first-depositor",
    "first depositor",
    "withdrawal",
    "withdraw",
    "redeem",
    "deposit",
    "mint",
    "oracle",
    "price",
    "adapter",
    "registry",
    "migration",
    "migrate",
    "proxy",
    "implementation",
    "fee",
    "rounding",
    "access control",
    "liquidation",
    "solvency",
    "settlement",
    "settle",
    "reward",
    "vesting",
    "pause",
    "admin",
    "owner",
    "guardian",
    "donation",
    "share",
    "accounting",
)

# Words that signal a known / accepted / out-of-scope behavior near a match.
ACK_TERMS = (
    "known issue",
    "knownissue",
    "acknowledged",
    "won't fix",
    "wont fix",
    "wontfix",
    "by design",
    "by-design",
    "documented limitation",
    "accepted risk",
    "out of scope",
    "out-of-scope",
)

DUP_TERMS = (
    "duplicate",
    "previously reported",
    "already reported",
    "known finding",
    "prior finding",
)

# Auditor / contest firm names commonly seen in audit corpora.
AUDIT_FIRMS = (
    "certora",
    "spearbit",
    "cantina",
    "sherlock",
    "code4rena",
    "trail of bits",
    "dedaub",
    "chainsecurity",
    "openzeppelin",
    "consensys",
    "halborn",
)

# Test-intent words that indicate a behavior is exercised by a public test.
TEST_INTENT = ("test", "invariant", "revert", "regression", "fuzz", "assert")


@dataclass
class Doc:
    """A single collected local document."""

    rel_path: str
    text: str
    kind: str  # "known" | "audit" | "test" | "src" | "doc" | "scope"

    @property
    def lower(self) -> str:
        return self.text.lower()


def _safe_read(path: Path, max_bytes: int = 400_000) -> str:
    try:
        if not path.is_file() or path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def collect_dir(base: Path, kind: str, max_files: int = 200) -> list[Doc]:
    """Collect text docs from a directory tree (read-only, capped)."""
    docs: list[Doc] = []
    if not base.is_dir():
        return docs
    for path in sorted(base.rglob("*")):
        if len(docs) >= max_files:
            break
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if "__pycache__" in path.parts:
            continue
        text = _safe_read(path)
        if text:
            try:
                rel = str(path.relative_to(base.parent))
            except ValueError:
                rel = str(path)
            docs.append(Doc(rel_path=rel, text=text, kind=kind))
    return docs


def collect_known_corpus(known_path: str, audits_path: str) -> list[Doc]:
    """Collect the explicit known-issue and audit corpora (may be empty)."""
    docs: list[Doc] = []
    if known_path:
        docs += collect_dir(Path(known_path).expanduser(), "known")
    if audits_path:
        docs += collect_dir(Path(audits_path).expanduser(), "audit")
    return docs


def collect_repo_corpus(root: Path) -> list[Doc]:
    """Collect local repo text used for dedup / freshness (tests, src, docs)."""
    docs: list[Doc] = []
    for name in LOCAL_SCAN_DIRS:
        sub = root / name
        if sub.is_dir():
            kind = "test" if name in ("test", "tests") else ("doc" if name in ("docs", "release-notes") else "src")
            docs += collect_dir(sub, kind)
    for name in LOCAL_SCAN_FILES:
        text = _safe_read(root / name)
        if text:
            docs.append(Doc(rel_path=name, text=text, kind="doc"))
    return docs


def is_test_doc(doc: Doc) -> bool:
    low = doc.rel_path.lower()
    return doc.kind == "test" or low.endswith(".t.sol") or "/test" in low or low.startswith("test")


def behavior_terms_in(text: str) -> list[str]:
    low = text.lower()
    return [term for term in BEHAVIOR_TERMS if term in low]


def windows_around(text: str, needle: str, radius: int = 160) -> list[str]:
    """Return context windows around each occurrence of ``needle`` (lowercased)."""
    low = text.lower()
    out: list[str] = []
    start = 0
    while True:
        idx = low.find(needle, start)
        if idx == -1:
            break
        out.append(low[max(0, idx - radius): idx + len(needle) + radius])
        start = idx + len(needle)
    return out


_WORD_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]+")


def identifiers(text: str) -> set[str]:
    return {m.group(0).lower() for m in _WORD_RE.finditer(text)}
