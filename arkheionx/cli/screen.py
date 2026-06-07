"""Structured terminal presentation for ArkheionX command-center views.

Pure string builders (testable) plus a TTY-only live step reporter. Color is
delegated to :mod:`arkheionx.cli.colors`, so NO_COLOR / ARKHEIONX_NO_COLOR / CI /
non-TTY stay plain and JSON / artifacts are never styled. Animation is gated
separately and is never required for correctness. Standard library only.

The builders return lists of lines so callers can assemble a view and tests can
assert on stripped output. Coloring is purely additive: ``colors.strip`` of any
rendered line equals the plain text, so plain mode stays deterministic.
"""
from __future__ import annotations

import contextlib
import os
import sys
import threading

from arkheionx.cli import colors

# Status chips. Red is reserved for hard failures; review/missing use amber;
# local-only guarantees use cyan; priority chips mirror the review palette.
_CHIP_STYLE: dict[str, tuple[str, ...]] = {
    "OK": ("green",),
    "WARN": ("yellow", "bold"),
    "REVIEW": ("yellow",),
    "MISSING": ("yellow",),
    "LOCAL": ("cyan",),
    "WRITE": ("cyan",),
    "FAIL": ("red", "bold"),
    "CRITICAL": ("red", "bold"),
    "HIGH": ("yellow", "bold"),
    "MEDIUM": ("yellow",),
    "LOW": ("dim",),
}

_SPIN_UNICODE = "\u25d0\u25d3\u25d1\u25d2"  # ◐◓◑◒
_SPIN_ASCII = "|/-\\"


def chip(kind: str, width: int = 0, stream=None) -> str:
    """A status chip padded to ``width`` (in plain characters) before coloring,
    so columns stay aligned whether or not ANSI is emitted."""
    label = str(kind).strip().upper()
    text = label.ljust(width) if width else label
    style = _CHIP_STYLE.get(label)
    return colors.paint(text, *style, stream=stream) if style else text


def header(title: str, tagline: str, stream=None) -> list[str]:
    """Brand banner: cyan/bold product title above a dim local/static tagline."""
    return [
        colors.paint(title, "cyan", "bold", stream=stream),
        colors.paint(tagline, "dim", stream=stream),
        "",
    ]


def section(title: str, stream=None) -> list[str]:
    """A bold section heading preceded by a blank divider line."""
    return ["", colors.paint(title, "bold", stream=stream)]


def kv_rows(rows, stream=None) -> list[str]:
    """Aligned ``label   value`` rows. The value is the last column and may be a
    pre-styled string, so only labels drive alignment."""
    pairs = [(str(label), "" if value is None else str(value)) for label, value in rows]
    width = max((len(label) for label, _ in pairs), default=0)
    return [f"{label.ljust(width)}  {value}".rstrip() for label, value in pairs]


def chip_rows(rows, stream=None) -> list[str]:
    """Aligned ``CHIP  label   value`` rows from ``(chip_kind, label, value)``."""
    triples = [
        (str(kind), str(label), "" if value is None else str(value))
        for kind, label, value in rows
    ]
    chip_width = max((len(str(kind)) for kind, _, _ in triples), default=0)
    label_width = max((len(label) for _, label, _ in triples), default=0)
    out: list[str] = []
    for kind, label, value in triples:
        token = chip(kind, chip_width, stream=stream)
        out.append(f"{token}  {label.ljust(label_width)}  {value}".rstrip())
    return out


def dim(text: str, stream=None) -> str:
    """Dim metadata such as artifact paths."""
    return colors.paint(str(text), "dim", stream=stream)


def animation_enabled(stream=None) -> bool:
    """Whether the live spinner may animate for ``stream`` (default stdout).

    ARKHEIONX_ANIMATION force/off wins; otherwise animation needs a real TTY and
    is suppressed under CI, ARKHEIONX_NO_ANIMATION, or when color is disabled.
    """
    stream = stream or sys.stdout
    value = os.environ.get("ARKHEIONX_ANIMATION", "").strip().lower()
    if value in {"0", "never", "off", "false", "no"}:
        return False
    if value in {"1", "always", "force", "yes", "true", "on"}:
        return True
    if os.environ.get("ARKHEIONX_NO_ANIMATION"):
        return False
    if os.environ.get("CI") is not None:
        return False
    if not colors.enabled(stream):
        return False
    try:
        return bool(stream.isatty())
    except Exception:
        return False


def _supports_unicode(stream) -> bool:
    if os.environ.get("ARKHEIONX_ASCII"):
        return False
    return "utf" in (getattr(stream, "encoding", None) or "").lower()


class _StepDetail:
    """Mutable handle a caller fills in with the real result detail."""

    __slots__ = ("detail",)

    def __init__(self) -> None:
        self.detail = ""


class StepReporter:
    """Render multi-step progress as aligned ``OK  label  detail`` rows.

    In a real TTY (and when animation is allowed) each step shows a brief spinner
    while its real work runs, then settles into a static row. In CI / non-TTY /
    forced-off mode it prints deterministic static rows only - no control
    characters, no timing - so snapshots and tests stay stable.
    """

    def __init__(self, labels, *, stream=None, animate=None, color: bool | None = None) -> None:
        self.stream = stream or sys.stdout
        self.labels = [str(label) for label in labels]
        self._label_width = max((len(label) for label in self.labels), default=0)
        self.animate = animation_enabled(self.stream) if animate is None else bool(animate)
        self._color = colors.enabled(self.stream) if color is None else bool(color)
        self._unicode = _supports_unicode(self.stream)
        self._pending = 0

    def _frames(self) -> str:
        return _SPIN_UNICODE if self._unicode else _SPIN_ASCII

    def _row(self, kind: str, label: str, detail: str) -> str:
        token = chip(kind, 4, stream=self.stream) if self._color else kind.ljust(4)
        return f"{token}  {label.ljust(self._label_width)}  {detail}".rstrip()

    @contextlib.contextmanager
    def step(self, label: str):
        detail = _StepDetail()
        stop = self._spin(label) if self.animate else None
        try:
            yield detail
        except BaseException:
            if stop:
                stop()
            self._clear()
            raise
        else:
            if stop:
                stop()
            self._clear()
            self.stream.write(self._row("OK", label, detail.detail) + "\n")
            self.stream.flush()

    def _spin(self, label: str):
        event = threading.Event()
        frames = self._frames()

        def run() -> None:
            i = 0
            while not event.is_set():
                glyph = colors.paint(frames[i % len(frames)], "cyan", stream=self.stream)
                text = f"{glyph}  {label}"
                pad = max(0, self._pending - len(colors.strip(text)))
                self.stream.write("\r" + text + " " * pad)
                self.stream.flush()
                self._pending = len(colors.strip(text))
                i += 1
                event.wait(0.08)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        def stop() -> None:
            event.set()
            thread.join(timeout=1.0)

        return stop

    def _clear(self) -> None:
        if self._pending:
            self.stream.write("\r" + " " * self._pending + "\r")
            self.stream.flush()
            self._pending = 0
