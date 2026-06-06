"""Unit tests for the honest terminal UI (arkheionx/cli_ui.py).

Cover the developer-experience safety contract: animation is gated, machine
mode is a no-op, color is delegated to the color utility (so disabling it stays
plain), the spinner thread is always cleaned up, and errors propagate unchanged.
"""
import contextlib
import io
import os
import threading
import unittest

from arkheionx.cli_ui import TerminalUI

ESC = "\x1b["


class FakeTTY:
    """A writable text stream that can claim to be a TTY with an encoding."""

    def __init__(self, tty: bool = True, encoding: str = "utf-8") -> None:
        self._buf = io.StringIO()
        self._tty = tty
        self.encoding = encoding

    def write(self, text: str) -> int:
        return self._buf.write(text)

    def flush(self) -> None:
        self._buf.flush()

    def isatty(self) -> bool:
        return self._tty

    def getvalue(self) -> str:
        return self._buf.getvalue()


@contextlib.contextmanager
def env(**overrides):
    """Reset the UX-relevant env vars, then apply overrides (None = unset)."""
    saved = dict(os.environ)
    try:
        for key in ("CI", "ARKHEIONX_NO_ANIMATION", "ARKHEIONX_COLOR", "ARKHEIONX_ASCII", "NO_COLOR"):
            os.environ.pop(key, None)
        for key, value in overrides.items():
            if value is not None:
                os.environ[key] = value
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)


class AnimationGatingTests(unittest.TestCase):
    def test_tty_allows_animation(self) -> None:
        with env():
            self.assertTrue(TerminalUI(stream=FakeTTY()).animate)

    def test_non_tty_disables_animation(self) -> None:
        with env():
            self.assertFalse(TerminalUI(stream=io.StringIO()).animate)

    def test_ci_disables_animation(self) -> None:
        with env(CI="true"):
            self.assertFalse(TerminalUI(stream=FakeTTY()).animate)

    def test_no_animation_env_disables_animation(self) -> None:
        with env(ARKHEIONX_NO_ANIMATION="1"):
            self.assertFalse(TerminalUI(stream=FakeTTY()).animate)

    def test_machine_readable_disables_everything(self) -> None:
        with env():
            ui = TerminalUI(stream=FakeTTY(), machine_readable=True)
            self.assertFalse(ui.animate)
            self.assertFalse(ui.enabled)

    def test_quiet_disables_animation_and_output(self) -> None:
        with env():
            ui = TerminalUI(stream=FakeTTY(), quiet=True)
            self.assertFalse(ui.enabled)


class MachineReadableTests(unittest.TestCase):
    def test_machine_readable_is_silent(self) -> None:
        stream = io.StringIO()
        with env():
            ui = TerminalUI(stream=stream, machine_readable=True)
            ui.banner("T", "sub")
            ui.info("x")
            ui.section("S")
            ui.result("k", 1)
            ui.summary("Sum", [("a", 1)])
            with ui.phase("work", 1, 2) as p:
                p.detail = "done"
        self.assertEqual(stream.getvalue(), "")


class ColorTests(unittest.TestCase):
    def test_no_ansi_when_color_never(self) -> None:
        stream = io.StringIO()
        with env(ARKHEIONX_COLOR="never"):
            ui = TerminalUI(stream=stream)
            ui.banner("ARKHEIONX REVIEW MAP", "subtitle")
            ui.section("Summary")
            ui.success("ok message")
        self.assertNotIn(ESC, stream.getvalue())

    def test_ansi_when_color_always(self) -> None:
        stream = io.StringIO()
        with env(ARKHEIONX_COLOR="always"):
            ui = TerminalUI(stream=stream)
            ui.banner("ARKHEIONX REVIEW MAP", "subtitle")
        self.assertIn(ESC, stream.getvalue())

    def test_color_flag_false_forces_plain(self) -> None:
        stream = io.StringIO()
        with env(ARKHEIONX_COLOR="always"):
            ui = TerminalUI(stream=stream, color=False)
            ui.banner("ARKHEIONX REVIEW MAP")
        self.assertNotIn(ESC, stream.getvalue())


class MarkFallbackTests(unittest.TestCase):
    def test_ascii_marks_without_unicode_stream(self) -> None:
        stream = io.StringIO()  # no encoding attribute -> ASCII marks
        with env(ARKHEIONX_COLOR="never"):
            TerminalUI(stream=stream).success("done")
        self.assertIn("[ok]", stream.getvalue())

    def test_ascii_env_forces_ascii_on_unicode_stream(self) -> None:
        stream = FakeTTY(tty=False, encoding="utf-8")
        with env(ARKHEIONX_COLOR="never", ARKHEIONX_ASCII="1"):
            TerminalUI(stream=stream).warning("careful")
        self.assertIn("[warn]", stream.getvalue())


class PhaseTests(unittest.TestCase):
    def test_phase_prints_completion_with_detail_no_cr_when_not_animated(self) -> None:
        stream = io.StringIO()
        with env(ARKHEIONX_COLOR="never"):
            ui = TerminalUI(stream=stream)  # non-tty -> no animation
            with ui.phase("Mapping", 2, 3) as p:
                p.detail = "7 contracts"
        out = stream.getvalue()
        self.assertIn("[2/3] Mapping: 7 contracts", out)
        self.assertIn("s)", out)  # elapsed shown
        self.assertNotIn("\r", out)

    def test_animated_phase_cleans_up_thread_and_writes_line(self) -> None:
        stream = FakeTTY()
        base = threading.active_count()
        with env(ARKHEIONX_COLOR="never"):
            ui = TerminalUI(stream=stream)
            self.assertTrue(ui.animate)
            with ui.phase("Working", 1, 1) as p:
                # Let the spinner emit at least one frame, then finish honestly.
                threading.Event().wait(0.15)
                p.detail = "ok"
        self.assertEqual(threading.active_count(), base, "spinner thread was not joined")
        out = stream.getvalue()
        self.assertIn("\r", out)  # spinner animated in place
        self.assertIn("Working: ok", out)
        self.assertTrue(out.endswith("\n"))

    def test_phase_propagates_exception_and_joins_thread(self) -> None:
        stream = FakeTTY()
        base = threading.active_count()
        with env(ARKHEIONX_COLOR="never"):
            ui = TerminalUI(stream=stream)
            with self.assertRaises(ValueError):
                with ui.phase("Boom", 1, 1):
                    raise ValueError("kaboom")
        self.assertEqual(threading.active_count(), base, "spinner thread leaked on error")

    def test_step_done_reports_premeasured_elapsed(self) -> None:
        stream = io.StringIO()
        with env(ARKHEIONX_COLOR="never"):
            TerminalUI(stream=stream).step_done("Inspecting", "3 files", elapsed=0.12, index=1, total=3)
        out = stream.getvalue()
        self.assertIn("[1/3] Inspecting: 3 files (0.12s)", out)
        self.assertNotIn("\r", out)


class SummaryTests(unittest.TestCase):
    def test_summary_aligns_and_lists_rows(self) -> None:
        stream = io.StringIO()
        with env(ARKHEIONX_COLOR="never"):
            TerminalUI(stream=stream).summary("Summary", [("Contracts", 7), ("Value paths", 9)])
        out = stream.getvalue()
        self.assertIn("Summary", out)
        self.assertIn("Contracts", out)
        self.assertIn("7", out)
        self.assertIn("Value paths", out)
        self.assertNotIn(ESC, out)


if __name__ == "__main__":
    unittest.main()
