"""Known Corpus Engine v2 for senior triage.

Builds normalized, line-indexed records from local known-issue / audit material,
repo docs, tests, and source comments. Everything is local/static and read-only: no
network, no secrets, no OCR. PDF text is only extracted if a lightweight library is
already importable; otherwise the document is marked unavailable, never failing.

These records give later stages real evidence — source paths and line ranges — so a
dedup or freshness decision can point at exactly what it matched.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import models as M
from .corpus import (
    ACK_TERMS,
    AUDIT_FIRMS,
    DUP_TERMS,
    Doc,
    collect_known_corpus,
    collect_repo_corpus,
    is_test_doc,
)

# A broad, generic behavior vocabulary (superset of corpus.BEHAVIOR_TERMS).
BEHAVIOR_TAGS = (
    "withdrawal", "withdraw", "deposit", "redeem", "mint", "burn", "oracle", "price",
    "rounding", "inflation", "first-depositor", "first depositor", "liquidation",
    "solvency", "settlement", "settle", "fee", "reward", "vesting", "pause", "admin",
    "owner", "guardian", "registry", "adapter", "migration", "migrate", "proxy",
    "implementation", "upgrade", "access-control", "access control", "accounting",
    "collateral", "debt", "share", "claim", "sweep", "rescue", "donation", "approve",
    "allowance", "reentrancy", "slippage",
)

# Known-status phrases that mark a behavior as already-handled / out of bounds.
STATUS_TAGS = (
    "duplicate", "known issue", "knownissue", "acknowledged", "by design", "by-design",
    "won't fix", "wont fix", "wontfix", "documented limitation", "out of scope",
    "out-of-scope", "oos", "trusted role", "trusted-role", "public test",
    "regression test", "audit finding", "formal verification", "invariant covered",
    "accepted risk",
)

# Role / asset / oracle words used for entity detection.
_ROLE_WORDS = ("owner", "admin", "governance", "guardian", "operator", "keeper", "timelock")
_ASSET_WORDS = ("usdc", "usdt", "dai", "weth", "wbtc", "token", "asset", "collateral")
_ORACLE_WORDS = ("oracle", "chainlink", "twap", "pricefeed", "price feed", "aggregator")

_CAMEL_RE = re.compile(r"\b([A-Z][a-zA-Z0-9]{2,})\b")
_CALL_RE = re.compile(r"\b([a-z][a-zA-Z0-9]{2,})\s*\(")
_PDF_NOTE = "UNPARSED_PDF_TEXT_EXTRACTION_UNAVAILABLE"


@dataclass
class BehaviorFingerprint:
    behaviors: set = field(default_factory=set)
    entities: set = field(default_factory=set)
    statuses: set = field(default_factory=set)
    shingles: set = field(default_factory=set)
    tokens: set = field(default_factory=set)


@dataclass
class CorpusSection:
    heading: str
    line_start: int
    line_end: int


@dataclass
class CorpusDocument:
    rel_path: str
    kind: str
    text: str
    line_offsets: list = field(default_factory=list)  # char offset of each line start
    sections: list = field(default_factory=list)       # CorpusSection
    fingerprint: BehaviorFingerprint = field(default_factory=BehaviorFingerprint)
    note: str = ""

    @property
    def lower(self) -> str:
        return self.text.lower()

    def line_of(self, offset: int) -> int:
        """1-based line number for a character offset (binary-search the offsets)."""
        import bisect

        if not self.line_offsets:
            return 1
        idx = bisect.bisect_right(self.line_offsets, offset) - 1
        return max(1, idx + 1)

    def is_test(self) -> bool:
        return is_test_doc(Doc(rel_path=self.rel_path, text=self.text, kind=self.kind))

    def to_record(self) -> dict:
        fp = self.fingerprint
        return {
            "source_path": self.rel_path,
            "kind": self.kind,
            "line_count": len(self.line_offsets),
            "sections": [s.heading for s in self.sections][:12],
            "detected_entities": sorted(fp.entities)[:24],
            "detected_behaviors": sorted(fp.behaviors)[:24],
            "risk_tags": sorted(fp.statuses)[:24],
            "note": self.note,
        }


def _line_offsets(text: str) -> list:
    offsets = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            offsets.append(i + 1)
    return offsets


def _sections(text: str, offsets: list) -> list:
    sections: list = []
    for m in re.finditer(r"(?m)^(#{1,6}\s+.+|/\*\*?.*|///\s+.+|\s*//\s*@\w+.*)$", text):
        heading = m.group(1).strip()[:120]
        # Map char offset to 1-based line.
        import bisect

        line = max(1, bisect.bisect_right(offsets, m.start()))
        sections.append(CorpusSection(heading=heading, line_start=line, line_end=line))
    return sections[:64]


def detect_entities(text: str) -> set:
    low = text.lower()
    entities: set = set()
    for m in _CAMEL_RE.finditer(text):
        entities.add(m.group(1))
    for m in _CALL_RE.finditer(text):
        entities.add(m.group(1))
    for group in (_ROLE_WORDS, _ASSET_WORDS, _ORACLE_WORDS):
        for word in group:
            if word in low:
                entities.add(word)
    return {e for e in entities if len(e) >= 3}


def detect_behaviors(text: str) -> set:
    low = text.lower()
    return {tag for tag in BEHAVIOR_TAGS if tag in low}


def detect_statuses(text: str) -> set:
    low = text.lower()
    found = {tag for tag in STATUS_TAGS if tag in low}
    found |= {firm for firm in AUDIT_FIRMS if firm in low}
    if any(a in low for a in ACK_TERMS):
        found.add("acknowledged")
    if any(d in low for d in DUP_TERMS):
        found.add("duplicate")
    return found


def token_shingles(text: str, size: int = 2) -> set:
    words = re.findall(r"[a-z0-9]+", text.lower())
    words = [w for w in words if len(w) >= 3]
    if len(words) < size:
        return set(words)
    return {" ".join(words[i:i + size]) for i in range(len(words) - size + 1)}


def _fingerprint(text: str) -> BehaviorFingerprint:
    return BehaviorFingerprint(
        behaviors={b.lower() for b in detect_behaviors(text)},
        entities={e.lower() for e in detect_entities(text)},
        statuses=detect_statuses(text),
        shingles=token_shingles(text, 2),
        tokens=set(re.findall(r"[a-z0-9]+", text.lower())),
    )


def _to_corpus_document(doc: Doc) -> CorpusDocument:
    offsets = _line_offsets(doc.text)
    return CorpusDocument(
        rel_path=doc.rel_path,
        kind=doc.kind,
        text=doc.text,
        line_offsets=offsets,
        sections=_sections(doc.text, offsets),
        fingerprint=_fingerprint(doc.text),
    )


def _maybe_pdf_documents(known_path: str, audits_path: str) -> list:
    """Locate any .pdf inputs and mark them unparsed (no OCR, no heavy deps)."""
    docs: list = []
    try:
        import importlib.util

        have_lib = any(
            importlib.util.find_spec(name) is not None
            for name in ("pypdf", "PyPDF2", "pdfminer")
        )
    except Exception:
        have_lib = False
    for base in (known_path, audits_path):
        if not base:
            continue
        root = Path(base).expanduser()
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.pdf")):
            text = ""
            note = "" if have_lib else _PDF_NOTE
            if have_lib:
                text = _extract_pdf(path)
                if not text:
                    note = _PDF_NOTE
            cd = CorpusDocument(
                rel_path=str(path.name), kind="audit", text=text,
                line_offsets=_line_offsets(text), note=note,
            )
            cd.fingerprint = _fingerprint(text) if text else BehaviorFingerprint()
            docs.append(cd)
    return docs


def _extract_pdf(path: Path) -> str:
    try:  # best-effort, only if a lib is already present
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return ""


def build_corpus(ctx: M.TriageContext, root: Path) -> list:
    """Build the v2 corpus: explicit known/audit material + local repo material."""
    docs = collect_known_corpus(ctx.known_path, ctx.audits_path)
    docs += collect_repo_corpus(root)
    corpus = [_to_corpus_document(d) for d in docs]
    corpus += _maybe_pdf_documents(ctx.known_path, ctx.audits_path)
    return corpus
