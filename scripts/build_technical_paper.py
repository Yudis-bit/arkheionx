#!/usr/bin/env python3
"""Build the Arkheionx v4 technical paper as a self-contained PDF (and HTML).

This script has no third-party dependencies. It parses a constrained Markdown
subset (front matter, headings, paragraphs, lists, fenced code/diagram blocks,
pipe tables, blockquotes, and inline bold/italic/code) and typesets it directly
into a vector PDF using the 14 standard PDF fonts (Times family + Courier +
Helvetica-Bold). No network access, no external font files, and no CDN are used.

Usage:
    python3 scripts/build_technical_paper.py [--no-copy]

Outputs:
    docs/papers/arkheionx-v4-technical-paper.pdf
    docs/papers/arkheionx-v4-technical-paper.html
    site/public/arkheionx-v4-technical-paper.pdf   (unless --no-copy)
"""
from __future__ import annotations

import argparse
import html as _html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_MD = ROOT / "docs" / "papers" / "arkheionx-v4-technical-paper.md"
OUT_PDF = ROOT / "docs" / "papers" / "arkheionx-v4-technical-paper.pdf"
OUT_HTML = ROOT / "docs" / "papers" / "arkheionx-v4-technical-paper.html"
SITE_PDF = ROOT / "site" / "public" / "arkheionx-v4-technical-paper.pdf"

# --- Standard-14 font metrics (ASCII 32..126), metrically compatible widths ---
# Proportional fonts use exact Adobe core metrics; Courier is fixed at 600.
_TIMES_ROMAN = {32: 250, 33: 333, 34: 408, 35: 500, 36: 500, 37: 833, 38: 778, 39: 333, 40: 333, 41: 333, 42: 500, 43: 564, 44: 250, 45: 333, 46: 250, 47: 278, 48: 500, 49: 500, 50: 500, 51: 500, 52: 500, 53: 500, 54: 500, 55: 500, 56: 500, 57: 500, 58: 278, 59: 278, 60: 564, 61: 564, 62: 564, 63: 444, 64: 921, 65: 722, 66: 667, 67: 667, 68: 722, 69: 611, 70: 556, 71: 722, 72: 722, 73: 333, 74: 389, 75: 722, 76: 611, 77: 889, 78: 722, 79: 722, 80: 556, 81: 722, 82: 667, 83: 556, 84: 611, 85: 722, 86: 722, 87: 944, 88: 722, 89: 722, 90: 611, 91: 333, 92: 278, 93: 333, 94: 469, 95: 500, 96: 333, 97: 444, 98: 500, 99: 444, 100: 500, 101: 444, 102: 333, 103: 500, 104: 500, 105: 278, 106: 278, 107: 500, 108: 278, 109: 778, 110: 500, 111: 500, 112: 500, 113: 500, 114: 333, 115: 389, 116: 278, 117: 500, 118: 500, 119: 722, 120: 500, 121: 500, 122: 444, 123: 480, 124: 200, 125: 480, 126: 541}
_TIMES_BOLD = {32: 250, 33: 333, 34: 555, 35: 500, 36: 500, 37: 1000, 38: 833, 39: 333, 40: 333, 41: 333, 42: 500, 43: 570, 44: 250, 45: 333, 46: 250, 47: 278, 48: 500, 49: 500, 50: 500, 51: 500, 52: 500, 53: 500, 54: 500, 55: 500, 56: 500, 57: 500, 58: 333, 59: 333, 60: 570, 61: 570, 62: 570, 63: 500, 64: 930, 65: 722, 66: 667, 67: 722, 68: 722, 69: 667, 70: 611, 71: 778, 72: 778, 73: 389, 74: 500, 75: 778, 76: 667, 77: 944, 78: 722, 79: 778, 80: 611, 81: 778, 82: 722, 83: 556, 84: 667, 85: 722, 86: 722, 87: 1000, 88: 722, 89: 722, 90: 667, 91: 333, 92: 278, 93: 333, 94: 581, 95: 500, 96: 333, 97: 500, 98: 556, 99: 444, 100: 556, 101: 444, 102: 333, 103: 500, 104: 556, 105: 278, 106: 333, 107: 556, 108: 278, 109: 833, 110: 556, 111: 500, 112: 556, 113: 556, 114: 444, 115: 389, 116: 333, 117: 556, 118: 500, 119: 722, 120: 500, 121: 500, 122: 444, 123: 394, 124: 220, 125: 394, 126: 520}
_TIMES_ITALIC = {32: 250, 33: 333, 34: 420, 35: 500, 36: 500, 37: 833, 38: 778, 39: 333, 40: 333, 41: 333, 42: 500, 43: 675, 44: 250, 45: 333, 46: 250, 47: 278, 48: 500, 49: 500, 50: 500, 51: 500, 52: 500, 53: 500, 54: 500, 55: 500, 56: 500, 57: 500, 58: 333, 59: 333, 60: 675, 61: 675, 62: 675, 63: 500, 64: 920, 65: 611, 66: 611, 67: 667, 68: 722, 69: 611, 70: 611, 71: 722, 72: 722, 73: 333, 74: 444, 75: 667, 76: 556, 77: 833, 78: 667, 79: 722, 80: 611, 81: 722, 82: 611, 83: 500, 84: 556, 85: 722, 86: 611, 87: 833, 88: 611, 89: 556, 90: 556, 91: 389, 92: 278, 93: 389, 94: 422, 95: 500, 96: 333, 97: 500, 98: 500, 99: 444, 100: 500, 101: 444, 102: 278, 103: 500, 104: 500, 105: 278, 106: 278, 107: 444, 108: 278, 109: 722, 110: 500, 111: 500, 112: 500, 113: 500, 114: 389, 115: 389, 116: 278, 117: 500, 118: 444, 119: 667, 120: 444, 121: 444, 122: 389, 123: 400, 124: 275, 125: 400, 126: 541}
_HELV_BOLD = {32: 278, 33: 333, 34: 474, 35: 556, 36: 556, 37: 889, 38: 722, 39: 278, 40: 333, 41: 333, 42: 389, 43: 584, 44: 278, 45: 333, 46: 278, 47: 278, 48: 556, 49: 556, 50: 556, 51: 556, 52: 556, 53: 556, 54: 556, 55: 556, 56: 556, 57: 556, 58: 333, 59: 333, 60: 584, 61: 584, 62: 584, 63: 611, 64: 975, 65: 722, 66: 722, 67: 722, 68: 722, 69: 667, 70: 611, 71: 778, 72: 722, 73: 278, 74: 556, 75: 722, 76: 611, 77: 833, 78: 722, 79: 778, 80: 667, 81: 778, 82: 722, 83: 667, 84: 611, 85: 722, 86: 667, 87: 944, 88: 667, 89: 667, 90: 611, 91: 333, 92: 278, 93: 333, 94: 584, 95: 556, 96: 278, 97: 556, 98: 611, 99: 556, 100: 611, 101: 556, 102: 333, 103: 611, 104: 611, 105: 278, 106: 278, 107: 556, 108: 278, 109: 889, 110: 611, 111: 611, 112: 611, 113: 611, 114: 389, 115: 556, 116: 333, 117: 611, 118: 556, 119: 778, 120: 556, 121: 556, 122: 500, 123: 389, 124: 280, 125: 389, 126: 584}
_HELV = {32: 278, 33: 278, 34: 355, 35: 556, 36: 556, 37: 889, 38: 667, 39: 222, 40: 333, 41: 333, 42: 389, 43: 584, 44: 278, 45: 333, 46: 278, 47: 278, 48: 556, 49: 556, 50: 556, 51: 556, 52: 556, 53: 556, 54: 556, 55: 556, 56: 556, 57: 556, 58: 278, 59: 278, 60: 584, 61: 584, 62: 584, 63: 556, 64: 1015, 65: 667, 66: 667, 67: 722, 68: 722, 69: 667, 70: 611, 71: 778, 72: 722, 73: 278, 74: 500, 75: 667, 76: 556, 77: 833, 78: 722, 79: 778, 80: 667, 81: 778, 82: 722, 83: 667, 84: 611, 85: 722, 86: 667, 87: 944, 88: 667, 89: 667, 90: 611, 91: 278, 92: 278, 93: 278, 94: 469, 95: 556, 96: 222, 97: 556, 98: 556, 99: 500, 100: 556, 101: 556, 102: 278, 103: 556, 104: 556, 105: 222, 106: 222, 107: 500, 108: 222, 109: 833, 110: 556, 111: 556, 112: 556, 113: 556, 114: 333, 115: 500, 116: 278, 117: 556, 118: 500, 119: 722, 120: 500, 121: 500, 122: 500, 123: 334, 124: 260, 125: 334, 126: 584}

# font key -> (PDF base font name, width table or None for fixed-600 Courier)
FONTS = {
    "body": ("Times-Roman", _TIMES_ROMAN),
    "bold": ("Times-Bold", _TIMES_BOLD),
    "italic": ("Times-Italic", _TIMES_ITALIC),
    "code": ("Courier", None),
    "codebold": ("Courier-Bold", None),
    "sans": ("Helvetica-Bold", _HELV_BOLD),
    "sansreg": ("Helvetica", _HELV),
}

_FOLD = {
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "--", "\u2026": "...", "\u2192": "->",
    "\u2190": "<-", "\u2022": "-", "\u00a0": " ", "\u00b7": "-",
    "\u25b6": ">", "\u2502": "|", "\u2500": "-", "\u251c": "+",
    "\u2524": "+", "\u252c": "+", "\u2534": "+", "\u253c": "+",
    "\u250c": "+", "\u2510": "+", "\u2514": "+", "\u2518": "+",
}


def ascii_fold(s: str) -> str:
    for k, v in _FOLD.items():
        s = s.replace(k, v)
    return "".join(c if 32 <= ord(c) <= 126 else ("\n" if c == "\n" else "") for c in s)


def char_width(font_key: str, ch: str, size: float) -> float:
    table = FONTS[font_key][1]
    if table is None:  # Courier family is monospaced
        return 600 * size / 1000.0
    return table.get(ord(ch), 500) * size / 1000.0


def text_width(font_key: str, s: str, size: float) -> float:
    return sum(char_width(font_key, c, size) for c in s)


# ---------------------------------------------------------------------------
# Markdown parsing (constrained subset)
# ---------------------------------------------------------------------------
def parse_front_matter(text: str) -> tuple[dict, str]:
    meta: dict[str, str] = {}
    if not text.startswith("---"):
        return meta, text
    end = text.find("\n---", 3)
    if end == -1:
        return meta, text
    block = text[3:end].strip("\n")
    body = text[end + 4:]
    for line in block.splitlines():
        m = re.match(r'^([A-Za-z0-9_]+):\s*(.*)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        meta[key] = val
    return meta, body


def parse_blocks(body: str) -> list[dict]:
    """Return a list of block dicts: heading/para/ul/ol/code/table/quote."""
    lines = body.split("\n")
    blocks: list[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        # fenced code / diagram block
        if stripped.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            blocks.append({"type": "code", "lines": buf})
            continue
        # heading
        if stripped.startswith("#"):
            m = re.match(r'^(#+)\s+(.*)$', stripped)
            if m:
                blocks.append({"type": "heading", "level": len(m.group(1)), "text": m.group(2).strip()})
                i += 1
                continue
        # table (header line with | and a separator row of ---)
        if "|" in line and i + 1 < n and re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]+$', lines[i + 1]):
            header = _split_row(line)
            i += 2  # skip header + separator
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            blocks.append({"type": "table", "header": header, "rows": rows})
            continue
        # blockquote
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            blocks.append({"type": "quote", "text": " ".join(x.strip() for x in buf if x.strip())})
            continue
        # unordered list
        if re.match(r'^\s*[-*]\s+', line):
            items = []
            while i < n and re.match(r'^\s*[-*]\s+', lines[i]):
                item = re.sub(r'^\s*[-*]\s+', '', lines[i])
                i += 1
                # continuation lines (indented)
                while i < n and lines[i].strip() and not re.match(r'^\s*[-*]\s+', lines[i]) \
                        and not re.match(r'^\s*\d+\.\s+', lines[i]) and lines[i].startswith("  "):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(item.strip())
            blocks.append({"type": "ul", "items": items})
            continue
        # ordered list
        if re.match(r'^\s*\d+\.\s+', line):
            items = []
            while i < n and re.match(r'^\s*\d+\.\s+', lines[i]):
                item = re.sub(r'^\s*\d+\.\s+', '', lines[i])
                i += 1
                while i < n and lines[i].strip() and not re.match(r'^\s*\d+\.\s+', lines[i]) \
                        and not re.match(r'^\s*[-*]\s+', lines[i]) and lines[i].startswith("   "):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(item.strip())
            blocks.append({"type": "ol", "items": items})
            continue
        # paragraph
        buf = []
        while i < n and lines[i].strip() and not lines[i].strip().startswith("#") \
                and not lines[i].strip().startswith("```") \
                and not lines[i].strip().startswith(">") \
                and not re.match(r'^\s*[-*]\s+', lines[i]) \
                and not re.match(r'^\s*\d+\.\s+', lines[i]):
            if "|" in lines[i] and i + 1 < n and re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]+$', lines[i + 1]):
                break
            buf.append(lines[i].strip())
            i += 1
        blocks.append({"type": "para", "text": " ".join(buf)})
    return blocks


def _split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def parse_inline(s: str) -> list[tuple[str, str]]:
    """Return list of (text, style) where style in normal/bold/italic/code."""
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)  # links -> visible text
    runs: list[tuple[str, str]] = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == '`':
            j = s.find('`', i + 1)
            if j != -1:
                runs.append((s[i + 1:j], "code"))
                i = j + 1
                continue
        if s.startswith("**", i):
            j = s.find("**", i + 2)
            if j != -1:
                runs.append((s[i + 2:j], "bold"))
                i = j + 2
                continue
        if s[i] == '*':
            j = s.find('*', i + 1)
            if j != -1:
                runs.append((s[i + 1:j], "italic"))
                i = j + 1
                continue
        # plain run until next marker
        j = i
        while j < n and s[j] != '`' and s[j] != '*':
            j += 1
        if j > i:
            runs.append((s[i:j], "normal"))
        i = j if j > i else i + 1
    return [(ascii_fold(t), st) for (t, st) in runs if t]


# ---------------------------------------------------------------------------
# Page geometry and styling
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = 595.28, 841.89  # A4
ML, MR, MT, MB = 64.0, 64.0, 70.0, 62.0
CONTENT_W = PAGE_W - ML - MR
CONTENT_R = PAGE_W - MR
TOP_Y = PAGE_H - MT
BOTTOM_Y = MB
HEADER_BAND = 26.0  # reserved at the top of body pages

INK = (0.10, 0.10, 0.12)
MUTED = (0.42, 0.46, 0.52)
ACCENT = (0.12, 0.32, 0.58)       # restrained blue
RULE = (0.78, 0.80, 0.84)
CODE_BG = (0.957, 0.965, 0.975)
CODE_INK = (0.14, 0.16, 0.20)
TABLE_HEAD_BG = (0.92, 0.94, 0.965)

BODY_SIZE = 10.3
BODY_LEAD = 14.6
STYLE_FONT = {"normal": "body", "bold": "bold", "italic": "italic", "code": "code"}


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class PDF:
    """Minimal PDF writer: pages as content streams + standard-14 fonts."""

    def __init__(self) -> None:
        self.pages: list[str] = []      # content stream per page
        self.ops: list[str] = []        # current page ops

    def new_page(self) -> None:
        if self.pages:
            self.pages[-1] = "\n".join(self.ops)
        self.pages.append("")
        self.ops = []

    def _commit(self) -> None:
        self.pages[-1] = "\n".join(self.ops)

    # drawing primitives (PDF origin is bottom-left) -----------------------
    def text(self, font_key: str, size: float, color, x: float, baseline: float, s: str) -> None:
        r, g, b = color
        self.ops.append(f"BT /{font_key} {size:.2f} Tf {r:.3f} {g:.3f} {b:.3f} rg "
                        f"1 0 0 1 {x:.2f} {baseline:.2f} Tm ({esc(s)}) Tj ET")

    def rect_fill(self, x: float, y: float, w: float, h: float, color) -> None:
        r, g, b = color
        self.ops.append(f"{r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")

    def line(self, x1: float, y1: float, x2: float, y2: float, color, width: float = 0.6) -> None:
        r, g, b = color
        self.ops.append(f"{r:.3f} {g:.3f} {b:.3f} RG {width:.2f} w "
                        f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def rect_stroke(self, x: float, y: float, w: float, h: float, color, width: float = 0.6) -> None:
        r, g, b = color
        self.ops.append(f"{r:.3f} {g:.3f} {b:.3f} RG {width:.2f} w {x:.2f} {y:.2f} {w:.2f} {h:.2f} re S")

    # serialization --------------------------------------------------------
    def build(self, title: str, author: str) -> bytes:
        self._commit()
        objs: list[bytes] = []

        def add(data: bytes) -> int:
            objs.append(data)
            return len(objs)

        font_objs = {}
        for key, (base, _tbl) in FONTS.items():
            num = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /%s /Encoding /WinAnsiEncoding >>"
                      % base.encode("latin-1"))
            font_objs[key] = num

        font_res = " ".join(f"/{k} {num} 0 R" for k, num in font_objs.items())
        page_obj_nums: list[int] = []
        content_nums: list[int] = []
        # reserve pages object number after we know kids; build content first
        for stream in self.pages:
            data = stream.encode("latin-1", "replace")
            content_nums.append(add(b"<< /Length %d >>\nstream\n%s\nendstream" % (len(data), data)))

        pages_obj_num = len(objs) + len(self.pages) + 1  # placeholder; fixed below
        # create page objects referencing the (future) Pages object
        for idx, cnum in enumerate(content_nums):
            page = (b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %.2f %.2f] "
                    b"/Resources << /Font << %s >> >> /Contents %d 0 R >>"
                    % (pages_obj_num, PAGE_W, PAGE_H, font_res.encode("latin-1"), cnum))
            page_obj_nums.append(add(page))

        kids = " ".join(f"{num} 0 R" for num in page_obj_nums)
        pages_num = add(b"<< /Type /Pages /Count %d /Kids [%s] >>"
                        % (len(page_obj_nums), kids.encode("latin-1")))
        assert pages_num == pages_obj_num, (pages_num, pages_obj_num)
        info_num = add(b"<< /Title (%s) /Author (%s) /Creator (Arkheionx paper builder) >>"
                       % (esc(ascii_fold(title)).encode("latin-1"), esc(ascii_fold(author)).encode("latin-1")))
        catalog_num = add(b"<< /Type /Catalog /Pages %d 0 R >>" % pages_num)

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for i, data in enumerate(objs, start=1):
            offsets.append(len(out))
            out += b"%d 0 obj\n" % i
            out += data
            out += b"\nendobj\n"
        xref_pos = len(out)
        out += b"xref\n0 %d\n" % (len(objs) + 1)
        out += b"0000000000 65535 f \n"
        for off in offsets[1:]:
            out += b"%010d 00000 n \n" % off
        out += (b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                % (len(objs) + 1, catalog_num, info_num, xref_pos))
        return bytes(out)


# ---------------------------------------------------------------------------
# Word wrapping for mixed inline runs
# ---------------------------------------------------------------------------
def runs_to_words(runs: list[tuple[str, str]], size: float):
    """Split styled runs into words. Each word = list of (text, font_key, size)."""
    words: list[list[tuple[str, str, float]]] = []
    current: list[tuple[str, str, float]] = []
    for text, style in runs:
        fk = STYLE_FONT.get(style, "body")
        sz = size * 0.93 if style == "code" else size
        parts = text.split(" ")
        for k, seg in enumerate(parts):
            if k > 0:
                if current:
                    words.append(current)
                    current = []
            if seg:
                current.append((seg, fk, sz))
    if current:
        words.append(current)
    return words


def word_width(word) -> float:
    return sum(text_width(fk, t, sz) for (t, fk, sz) in word)


def wrap_words(words, max_w: float, space_w: float):
    """Greedy wrap. Returns list of lines; each line = list of words."""
    lines = []
    cur = []
    cur_w = 0.0
    for w in words:
        ww = word_width(w)
        add = ww if not cur else space_w + ww
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur = [w]
            cur_w = ww
        else:
            cur.append(w)
            cur_w += add
    if cur:
        lines.append(cur)
    return lines or [[]]


# ---------------------------------------------------------------------------
# Layout / rendering
# ---------------------------------------------------------------------------
class Renderer:
    def __init__(self, pdf: PDF, meta: dict):
        self.pdf = pdf
        self.meta = meta
        self.y = TOP_Y
        self.page_no = 0
        self.space_w = text_width("body", " ", BODY_SIZE)

    # page scaffolding -----------------------------------------------------
    def start_body_page(self):
        self.pdf.new_page()
        self.page_no += 1
        hdr = "Arkheionx v4.0.0  -  Technical Paper"
        self.pdf.text("sansreg", 7.6, MUTED, ML, PAGE_H - 44, hdr)
        right = self.meta.get("author", "")
        rw = text_width("sansreg", right, 7.6)
        self.pdf.text("sansreg", 7.6, MUTED, CONTENT_R - rw, PAGE_H - 44, right)
        self.pdf.line(ML, PAGE_H - 50, CONTENT_R, PAGE_H - 50, RULE, 0.5)
        num = str(self.page_no)
        nw = text_width("body", num, 9.0)
        self.pdf.text("body", 9.0, MUTED, (PAGE_W - nw) / 2.0, 40, num)
        self.y = TOP_Y

    def ensure(self, h: float):
        if self.y - h < BOTTOM_Y:
            self.start_body_page()

    def vspace(self, h: float):
        self.y -= h
        if self.y < BOTTOM_Y:
            self.start_body_page()

    def draw_line(self, words, size, leading, color, x0=ML):
        self.ensure(leading)
        baseline = self.y - size * 0.82
        x = x0
        for k, w in enumerate(words):
            if k > 0:
                x += self.space_w if size == BODY_SIZE else text_width("body", " ", size)
            for (t, fk, sz) in w:
                self.pdf.text(fk, sz, color, x, baseline, t)
                x += text_width(fk, t, sz)
        self.y -= leading

    def paragraph(self, runs, size=BODY_SIZE, leading=BODY_LEAD, color=INK, x0=ML, max_w=CONTENT_W, gap=6.0):
        words = runs_to_words(runs, size)
        sw = text_width("body", " ", size)
        for line in wrap_words(words, max_w - (x0 - ML), sw):
            self.draw_line(line, size, leading, color, x0)
        self.vspace(gap)

    # blocks ---------------------------------------------------------------
    def heading(self, level, text):
        if level <= 2:
            self.vspace(10.0)
            self.ensure(BODY_LEAD * 3 + 8)
            runs = parse_inline(text)
            words = runs_to_words(runs, 13.2)
            sw = text_width("bold", " ", 13.2)
            for w in words:
                for k in range(len(w)):
                    w[k] = (w[k][0], "bold", 13.2)
            for line in wrap_words(words, CONTENT_W, sw):
                self.draw_line(line, 13.2, 17.0, INK)
            self.pdf.line(ML, self.y + 3, CONTENT_R, self.y + 3, ACCENT, 0.8)
            self.vspace(7.0)
        else:
            self.vspace(6.0)
            self.ensure(BODY_LEAD * 2)
            runs = parse_inline(text)
            words = runs_to_words(runs, 11.2)
            for w in words:
                for k in range(len(w)):
                    w[k] = (w[k][0], "bold", 11.2)
            sw = text_width("bold", " ", 11.2)
            for line in wrap_words(words, CONTENT_W, sw):
                self.draw_line(line, 11.2, 14.5, INK)
            self.vspace(3.0)

    def listing(self, items, ordered):
        indent = 16.0
        for idx, item in enumerate(items, 1):
            marker = f"{idx}." if ordered else "-"
            runs = parse_inline(item)
            words = runs_to_words(runs, BODY_SIZE)
            sw = text_width("body", " ", BODY_SIZE)
            lines = wrap_words(words, CONTENT_W - indent, sw)
            self.ensure(BODY_LEAD)
            baseline = self.y - BODY_SIZE * 0.82
            self.pdf.text("bold" if ordered else "body", BODY_SIZE, ACCENT, ML, baseline, marker)
            first = True
            for line in lines:
                if not first:
                    self.ensure(BODY_LEAD)
                    baseline = self.y - BODY_SIZE * 0.82
                x = ML + indent
                for k, w in enumerate(line):
                    if k > 0:
                        x += sw
                    for (t, fk, sz) in w:
                        self.pdf.text(fk, sz, INK, x, baseline, t)
                        x += text_width(fk, t, sz)
                self.y -= BODY_LEAD
                first = False
        self.vspace(5.0)

    def code_block(self, lines):
        lines = [ascii_fold(l).replace("\t", "    ") for l in lines]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if not lines:
            return
        maxlen = max(len(l) for l in lines) or 1
        pad = 7.0
        size = min(8.7, (CONTENT_W - 2 * pad - 2) / (maxlen * 0.6))
        size = max(6.9, size)
        lead = size * 1.32
        i = 0
        n = len(lines)
        self.vspace(2.0)
        # Keep a block together if it fits within a single page.
        block_h = n * lead + 2 * pad
        full_page_h = TOP_Y - BOTTOM_Y
        if block_h <= full_page_h and self.y - block_h < BOTTOM_Y:
            self.start_body_page()
        while i < n:
            avail = self.y - BOTTOM_Y
            fit = int((avail - 2 * pad) // lead)
            if fit < 1:
                self.start_body_page()
                avail = self.y - BOTTOM_Y
                fit = int((avail - 2 * pad) // lead)
            seg = lines[i:i + fit]
            seg_h = len(seg) * lead + 2 * pad
            top = self.y
            self.pdf.rect_fill(ML, top - seg_h, CONTENT_W, seg_h, CODE_BG)
            self.pdf.line(ML, top - seg_h, ML, top, ACCENT, 1.2)
            baseline = top - pad - size * 0.9
            for l in seg:
                self.pdf.text("code", size, CODE_INK, ML + pad + 3, baseline, l)
                baseline -= lead
            self.y = top - seg_h
            i += len(seg)
            if i < n:
                self.start_body_page()
        self.vspace(7.0)

    def table(self, header, rows):
        cols = len(header)
        tsize = 9.2
        lead = tsize * 1.28
        cpad = 4.5
        all_rows = [header] + rows
        nat = [0.0] * cols
        for r, row in enumerate(all_rows):
            for c in range(cols):
                cell = row[c] if c < len(row) else ""
                fk = "bold" if r == 0 else "body"
                w = text_width(fk, ascii_fold(re.sub(r'[*`]', '', cell)), tsize) + 2 * cpad
                nat[c] = max(nat[c], w)
        total = sum(nat) or 1.0
        scale = CONTENT_W / total
        colw = [w * scale for w in nat]

        def cell_lines(cell, header_cell):
            runs = parse_inline(cell)
            if header_cell:
                runs = [(t, "bold") for (t, _s) in runs]
            words = runs_to_words(runs, tsize)
            sw = text_width("body", " ", tsize)
            cidx = 0  # placeholder
            return words, sw

        def draw_row(row, is_header):
            cell_wrapped = []
            maxlines = 1
            for c in range(cols):
                cell = row[c] if c < len(row) else ""
                words, sw = cell_lines(cell, is_header)
                wl = wrap_words(words, colw[c] - 2 * cpad, sw)
                cell_wrapped.append((wl, sw))
                maxlines = max(maxlines, len(wl))
            row_h = maxlines * lead + 2 * cpad
            self.ensure(row_h)
            top = self.y
            if is_header:
                self.pdf.rect_fill(ML, top - row_h, CONTENT_W, row_h, TABLE_HEAD_BG)
            x = ML
            for c in range(cols):
                self.pdf.rect_stroke(x, top - row_h, colw[c], row_h, RULE, 0.5)
                wl, sw = cell_wrapped[c]
                baseline = top - cpad - tsize * 0.84
                for line in wl:
                    xx = x + cpad
                    for k, w in enumerate(line):
                        if k > 0:
                            xx += sw
                        for (t, fk, sz) in w:
                            self.pdf.text(fk, sz, INK, xx, baseline, t)
                            xx += text_width(fk, t, sz)
                    baseline -= lead
                x += colw[c]
            self.y = top - row_h

        self.vspace(3.0)
        draw_row(header, True)
        for row in rows:
            if self.y - (lead + 2 * cpad) < BOTTOM_Y:
                self.start_body_page()
                draw_row(header, True)
            draw_row(row, False)
        self.vspace(8.0)

    def quote(self, text):
        runs = parse_inline(text)
        for k in range(len(runs)):
            t, s = runs[k]
            runs[k] = (t, "italic" if s == "normal" else s)
        indent = 18.0
        words = runs_to_words(runs, BODY_SIZE)
        sw = text_width("italic", " ", BODY_SIZE)
        lines = wrap_words(words, CONTENT_W - indent - 6, sw)
        self.vspace(3.0)
        top = self.y
        self.ensure(len(lines) * BODY_LEAD + 4)
        top = self.y
        for line in lines:
            self.ensure(BODY_LEAD)
            baseline = self.y - BODY_SIZE * 0.82
            x = ML + indent
            for k, w in enumerate(line):
                if k > 0:
                    x += sw
                for (t, fk, sz) in w:
                    self.pdf.text(fk, sz, (0.30, 0.34, 0.40), x, baseline, t)
                    x += text_width(fk, t, sz)
            self.y -= BODY_LEAD
        self.pdf.line(ML + 4, self.y + 2, ML + 4, top - 2, ACCENT, 1.6)
        self.vspace(8.0)

    # title page -----------------------------------------------------------
    def title_page(self):
        self.pdf.new_page()
        self.page_no += 1
        y = PAGE_H - 150
        label = "T E C H N I C A L   P A P E R"
        self.pdf.text("sans", 10.0, ACCENT, ML, y, label)
        y -= 12
        self.pdf.line(ML, y, CONTENT_R, y, ACCENT, 1.2)
        y -= 44

        title = ascii_fold(self.meta.get("title", "Arkheionx"))
        words = [[(w, "bold", 23.0)] for w in title.split(" ")]
        sw = text_width("bold", " ", 23.0)
        for line in wrap_words(words, CONTENT_W, sw):
            x = ML
            for k, wd in enumerate(line):
                if k > 0:
                    x += sw
                for (t, fk, sz) in wd:
                    self.pdf.text(fk, sz, INK, x, y, t)
                    x += text_width(fk, t, sz)
            y -= 30
        y -= 6

        sub = ascii_fold(self.meta.get("subtitle", ""))
        if sub:
            words = [[(w, "italic", 13.0)] for w in sub.split(" ")]
            sw = text_width("italic", " ", 13.0)
            for line in wrap_words(words, CONTENT_W, sw):
                x = ML
                for k, wd in enumerate(line):
                    if k > 0:
                        x += sw
                    for (t, fk, sz) in wd:
                        self.pdf.text(fk, sz, (0.32, 0.36, 0.42), x, y, t)
                        x += text_width(fk, t, sz)
                y -= 19
        y -= 26

        self.pdf.text("body", 12.5, INK, ML, y, ascii_fold(self.meta.get("author", "")))
        y -= 26

        meta_rows = [
            ("PROJECT", self.meta.get("project", "")),
            ("VERSION", self.meta.get("version", "")),
            ("DATE", self.meta.get("date", "")),
            ("WEBSITE", self.meta.get("website", "")),
            ("REPOSITORY", self.meta.get("repository", "")),
        ]
        for lab, val in meta_rows:
            if not val:
                continue
            self.pdf.text("sans", 8.2, MUTED, ML, y, lab)
            self.pdf.text("body", 10.3, INK, ML + 92, y, ascii_fold(val))
            y -= 16
        y -= 16

        self.pdf.line(ML, y, CONTENT_R, y, RULE, 0.6)
        y -= 22
        self.pdf.text("sans", 9.0, ACCENT, ML, y, "ABSTRACT")
        y -= 16
        abstract = ascii_fold(self.meta.get("abstract", ""))
        if abstract:
            words = runs_to_words([(abstract, "normal")], 10.0)
            sw = text_width("body", " ", 10.0)
            for line in wrap_words(words, CONTENT_W, sw):
                x = ML
                for k, wd in enumerate(line):
                    if k > 0:
                        x += sw
                    for (t, fk, sz) in wd:
                        self.pdf.text(fk, sz, (0.20, 0.22, 0.26), x, y, t)
                        x += text_width(fk, t, sz)
                y -= 14.2
        y -= 18
        self.pdf.text("italic", 9.6, MUTED, ML, y,
                      "Local and static only. No RPC, no live-chain calls, no exploit "
                      "automation. Human review required.")


# ---------------------------------------------------------------------------
# HTML emitter (standalone, embedded CSS, no external fonts/CDN)
# ---------------------------------------------------------------------------
def inline_html(s: str) -> str:
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', s)
    out = []
    i, n = 0, len(s)
    while i < n:
        if s[i] == '`':
            j = s.find('`', i + 1)
            if j != -1:
                out.append("<code>" + _html.escape(s[i + 1:j]) + "</code>")
                i = j + 1
                continue
        if s.startswith("**", i):
            j = s.find("**", i + 2)
            if j != -1:
                out.append("<strong>" + _html.escape(s[i + 2:j]) + "</strong>")
                i = j + 2
                continue
        if s[i] == '*':
            j = s.find('*', i + 1)
            if j != -1:
                out.append("<em>" + _html.escape(s[i + 1:j]) + "</em>")
                i = j + 1
                continue
        j = i
        while j < n and s[j] not in '`*':
            j += 1
        out.append(_html.escape(s[i:j]))
        i = j if j > i else i + 1
    return "".join(out)


HTML_CSS = """
:root{--ink:#15171c;--muted:#5b626b;--accent:#1f5296;--rule:#d6dae0;--bg:#f6f7f9;--code:#eef1f5;}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:#15171c;
 font-family:Georgia,'Times New Roman',serif;line-height:1.55;}
.sheet{max-width:760px;margin:0 auto;background:#fff;padding:64px 72px;
 box-shadow:0 1px 4px rgba(0,0,0,.08);}
.cover{border-bottom:2px solid var(--accent);padding-bottom:26px;margin-bottom:30px;}
.kicker{letter-spacing:.32em;font-family:Helvetica,Arial,sans-serif;font-size:12px;
 color:var(--accent);font-weight:700;margin:0 0 14px;}
h1.title{font-size:30px;line-height:1.18;margin:0 0 10px;color:#15171c;}
.subtitle{font-style:italic;color:#3a3f47;font-size:17px;margin:0 0 20px;}
.author{font-size:16px;margin:0 0 14px;}
.meta{font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#3a3f47;margin:0;}
.meta div{margin:3px 0;}
.meta span{display:inline-block;width:110px;color:#6a7079;letter-spacing:.08em;
 font-size:11px;text-transform:uppercase;}
.abstract{background:#f7f9fb;border-left:3px solid var(--accent);padding:14px 18px;
 font-size:15px;margin:22px 0;}
h2{font-size:19px;border-bottom:1px solid var(--accent);padding-bottom:5px;
 margin:34px 0 12px;}
h3{font-size:16px;margin:22px 0 8px;}
p{margin:0 0 12px;}
ul,ol{margin:0 0 14px;padding-left:24px;}
li{margin:5px 0;}
blockquote{margin:16px 0;padding:6px 0 6px 18px;border-left:3px solid var(--accent);
 font-style:italic;color:#3a3f47;}
pre{background:var(--code);border-left:3px solid var(--accent);padding:12px 14px;
 overflow-x:auto;font-family:'Courier New',monospace;font-size:12.5px;line-height:1.4;}
code{font-family:'Courier New',monospace;font-size:.92em;background:#eef1f5;
 padding:0 3px;border-radius:2px;}
pre code{background:none;padding:0;}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:13.5px;}
th,td{border:1px solid var(--rule);padding:6px 9px;text-align:left;vertical-align:top;}
th{background:#eef2f8;}
.foot{margin-top:40px;border-top:1px solid var(--rule);padding-top:12px;
 font-size:12px;color:#6a7079;font-family:Helvetica,Arial,sans-serif;}
"""


def render_html(meta: dict, blocks: list[dict]) -> str:
    parts = [
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        f"<title>{_html.escape(meta.get('title',''))}</title>",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        "<meta name=\"robots\" content=\"index,follow\">",
        f"<style>{HTML_CSS}</style></head><body><main class=\"sheet\">",
        "<div class=\"cover\">",
        "<p class=\"kicker\">TECHNICAL PAPER</p>",
        f"<h1 class=\"title\">{_html.escape(meta.get('title',''))}</h1>",
        f"<p class=\"subtitle\">{_html.escape(meta.get('subtitle',''))}</p>",
        f"<p class=\"author\">{_html.escape(meta.get('author',''))}</p>",
        "<div class=\"meta\">",
    ]
    for lab, key in [("Project", "project"), ("Version", "version"), ("Date", "date"),
                     ("Website", "website"), ("Repository", "repository")]:
        if meta.get(key):
            parts.append(f"<div><span>{lab}</span>{_html.escape(meta[key])}</div>")
    parts.append("</div>")
    if meta.get("abstract"):
        parts.append(f"<div class=\"abstract\">{_html.escape(meta['abstract'])}</div>")
    parts.append("</div>")

    for b in blocks:
        t = b["type"]
        if t == "heading":
            tag = "h2" if b["level"] <= 2 else "h3"
            parts.append(f"<{tag}>{inline_html(b['text'])}</{tag}>")
        elif t == "para":
            parts.append(f"<p>{inline_html(b['text'])}</p>")
        elif t == "ul":
            parts.append("<ul>" + "".join(f"<li>{inline_html(x)}</li>" for x in b["items"]) + "</ul>")
        elif t == "ol":
            parts.append("<ol>" + "".join(f"<li>{inline_html(x)}</li>" for x in b["items"]) + "</ol>")
        elif t == "code":
            parts.append("<pre><code>" + _html.escape("\n".join(b["lines"])) + "</code></pre>")
        elif t == "quote":
            parts.append(f"<blockquote>{inline_html(b['text'])}</blockquote>")
        elif t == "table":
            rowhtml = ["<tr>" + "".join(f"<th>{inline_html(c)}</th>" for c in b["header"]) + "</tr>"]
            for row in b["rows"]:
                rowhtml.append("<tr>" + "".join(f"<td>{inline_html(c)}</td>" for c in row) + "</tr>")
            parts.append("<table>" + "".join(rowhtml) + "</table>")
    parts.append(f"<div class=\"foot\">{_html.escape(meta.get('author',''))} - "
                 f"{_html.escape(meta.get('version',''))} - {_html.escape(meta.get('date',''))} - "
                 f"{_html.escape(meta.get('website',''))}</div>")
    parts.append("</main></body></html>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
def render_pdf(meta: dict, blocks: list[dict]) -> bytes:
    pdf = PDF()
    r = Renderer(pdf, meta)
    r.title_page()
    r.start_body_page()
    for b in blocks:
        t = b["type"]
        if t == "heading":
            r.heading(b["level"], b["text"])
        elif t == "para":
            r.paragraph(parse_inline(b["text"]))
        elif t == "ul":
            r.listing(b["items"], ordered=False)
        elif t == "ol":
            r.listing(b["items"], ordered=True)
        elif t == "code":
            r.code_block(b["lines"])
        elif t == "table":
            r.table(b["header"], b["rows"])
        elif t == "quote":
            r.quote(b["text"])
    return pdf.build(meta.get("title", "Arkheionx"), meta.get("author", ""))


def validate_pdf(path: Path) -> list[str]:
    notes = []
    try:
        info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, timeout=30)
        pages = re.search(r'Pages:\s+(\d+)', info.stdout)
        if pages:
            notes.append(f"pages={pages.group(1)}")
        txt = subprocess.run(["pdftotext", "-f", "1", "-l", "1", str(path), "-"],
                             capture_output=True, text=True, timeout=30)
        first = txt.stdout
        for needed in ("Yudistira Putra", "Arkheionx", "TECHNICAL PAPER"):
            notes.append(f"{'OK' if needed in first else 'MISSING'}:{needed}")
    except Exception as exc:  # noqa: BLE001
        notes.append(f"validate-error:{exc}")
    return notes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build the Arkheionx v4 technical paper PDF/HTML.")
    ap.add_argument("--no-copy", action="store_true", help="Do not copy the PDF into site/public.")
    args = ap.parse_args(argv)

    text = SRC_MD.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)
    blocks = parse_blocks(body)

    pdf_bytes = render_pdf(meta, blocks)
    OUT_PDF.write_bytes(pdf_bytes)
    OUT_HTML.write_text(render_html(meta, blocks), encoding="utf-8")

    notes = validate_pdf(OUT_PDF)
    print(f"PDF  : {OUT_PDF.relative_to(ROOT)}  ({len(pdf_bytes)} bytes)  [{'; '.join(notes)}]")
    print(f"HTML : {OUT_HTML.relative_to(ROOT)}")

    if not args.no_copy:
        SITE_PDF.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(OUT_PDF, SITE_PDF)
        print(f"COPY : {SITE_PDF.relative_to(ROOT)}")

    if any(s.startswith("MISSING") or s.startswith("validate-error") for s in notes):
        print("WARNING: PDF validation reported issues.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
