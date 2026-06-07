"""Honest, dependency-free terminal UX for Arkheionx human output.

Goal: make local/static runs feel clear and developer-native without ever
faking work. Progress is honest — a spinner runs only while real work is in
flight, phase lines carry real labels and real elapsed time, and counts are
shown only after they are known. No fake percentages, no artificial sleeps.

Standard library only. Color is delegated to :mod:`arkheionx.cli.colors`, so the
existing ``ARKHEIONX_COLOR`` / ``NO_COLOR`` / ``CI`` rules apply unchanged and
JSON/artifacts are never colored. Animation is disabled automatically for
non-TTY streams, ``CI``, ``ARKHEIONX_NO_ANIMATION``, machine-readable/quiet mode.
"""
from __future__ import annotations

import contextlib
import os
import sys
import threading
import time

from arkheionx.cli import colors

_FRAMES = "|/-\\"
_MARKS = {
    "ok": ("\u2713", "[ok]", "green"),
    "warn": ("!", "[warn]", "yellow"),
    "error": ("\u2717", "[error]", "red"),
}


def _animation_allowed(stream) -> bool:
    if os.environ.get("ARKHEIONX_NO_ANIMATION"):
        return False
    if os.environ.get("CI"):
        return False
    try:
        return bool(stream.isatty())
    except Exception:
        return False


def _supports_unicode(stream) -> bool:
    if os.environ.get("ARKHEIONX_ASCII"):
        return False
    return "utf" in (getattr(stream, "encoding", None) or "").lower()


class _Phase:
    """Mutable handle a caller fills in with the real result detail."""

    __slots__ = ("detail",)

    def __init__(self) -> None:
        self.detail = ""


class TerminalUI:
    def __init__(
        self,
        *,
        enabled: bool = True,
        animate: bool = True,
        color: bool = True,
        stream=None,
        quiet: bool = False,
        machine_readable: bool = False,
    ) -> None:
        self.stream = stream or sys.stdout
        self.machine_readable = machine_readable
        self.quiet = quiet
        self.enabled = bool(enabled and not machine_readable and not quiet)
        self._color = bool(color)
        self._unicode = _supports_unicode(self.stream)
        self.animate = bool(self.enabled and animate and _animation_allowed(self.stream))
        self._last = 0

    # -- low-level ---------------------------------------------------------
    def _paint(self, text: str, *styles: str) -> str:
        if not self._color:
            return text
        return colors.paint(text, *styles, stream=self.stream)

    def _print(self, text: str = "") -> None:
        if not self.enabled:
            return
        self.stream.write(text + "\n")
        self.stream.flush()

    def _mark(self, kind: str) -> str:
        glyph, ascii_glyph, style = _MARKS[kind]
        return self._paint(glyph if self._unicode else ascii_glyph, style)

    def _overwrite(self, text: str, newline: bool) -> None:
        pad = max(0, self._last - len(colors.strip(text)))
        self.stream.write("\r" + text + (" " * pad) + ("\n" if newline else ""))
        self.stream.flush()
        self._last = 0 if newline else len(colors.strip(text))

    # -- public surface ----------------------------------------------------
    def banner(self, title: str, subtitle: str | None = None) -> None:
        if not self.enabled:
            return
        self._print(self._paint(title, "cyan", "bold"))
        if subtitle:
            self._print(self._paint(subtitle, "dim"))
        self._print()

    def info(self, message: str) -> None:
        self._print(message)

    def section(self, title: str) -> None:
        if not self.enabled:
            return
        self._print()
        self._print(self._paint(title, "bold"))

    def result(self, label: str, value: str | int) -> None:
        self._print(f"  {label}: {value}")

    def success(self, message: str) -> None:
        self._print(f"{self._mark('ok')} {message}")

    def warning(self, message: str) -> None:
        self._print(f"{self._mark('warn')} {message}")

    def error(self, message: str) -> None:
        self._print(f"{self._mark('error')} {message}")

    def summary(self, title: str, rows: list[tuple[str, str | int]]) -> None:
        if not self.enabled:
            return
        self.section(title)
        width = max((len(str(k)) for k, _ in rows), default=0)
        for key, value in rows:
            self._print(f"  {str(key).ljust(width)}  {value}")

    def _clear_line(self) -> None:
        if self._last:
            self.stream.write("\r" + (" " * self._last) + "\r")
            self.stream.flush()
            self._last = 0

    def _done_line(self, kind: str, head: str, label: str, detail: str, elapsed: float | None) -> str:
        detail_s = f": {detail}" if detail else ""
        elapsed_s = f" ({elapsed:.2f}s)" if elapsed is not None else ""
        return f"{self._mark(kind)} {head}{label}{detail_s}{elapsed_s}"

    def step_done(
        self,
        label: str,
        detail: str = "",
        *,
        elapsed: float | None = None,
        index: int | None = None,
        total: int | None = None,
        kind: str = "ok",
    ) -> None:
        """Report a phase whose work already ran (real, externally measured)."""
        if not self.enabled:
            return
        head = f"[{index}/{total}] " if index and total else ""
        self._print(self._done_line(kind, head, label, detail, elapsed))

    @contextlib.contextmanager
    def phase(self, label: str, index: int | None = None, total: int | None = None):
        """Run a real unit of work as a timed phase.

        Yields a handle; set ``handle.detail`` to the real result. A spinner
        animates only while the body runs and only when animation is allowed.
        On error the line is cleared and the exception propagates unchanged.
        """
        handle = _Phase()
        if not self.enabled:
            yield handle
            return
        head = f"[{index}/{total}] " if index and total else ""
        start = time.monotonic()
        stop = self._spin(f"{head}{label}") if self.animate else None
        try:
            yield handle
        except BaseException:
            if stop:
                stop()
            self._clear_line()
            raise
        else:
            if stop:
                stop()
            line = self._done_line("ok", head, label, handle.detail, time.monotonic() - start)
            if self.animate:
                self._overwrite(line, newline=True)
            else:
                self._print(line)

    def _spin(self, prefix: str):
        event = threading.Event()

        def run() -> None:
            i = 0
            while not event.is_set():
                frame = self._paint(_FRAMES[i % len(_FRAMES)], "dim")
                self._overwrite(f"{prefix} {frame}", newline=False)
                i += 1
                event.wait(0.1)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        def stop() -> None:
            event.set()
            thread.join(timeout=1.0)

        return stop
