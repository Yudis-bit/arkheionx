"""Tests for the structured terminal presentation layer (arkheionx/cli/screen.py)
and the rebuilt doctor / review-map command-center layouts.

The builders must stay plain and deterministic when color is disabled, emit ANSI
only when color is allowed, and keep ``colors.strip`` lossless. The StepReporter
must be exercisable without a real TTY, and animation must never run under CI /
non-TTY / forced-off so captured output and snapshots stay stable.
"""
import io
import os
import re
import subprocess
import unittest
from pathlib import Path

from arkheionx.cli import colors, screen

REPO_ROOT = Path(__file__).resolve().parents[1]
ESC = "\x1b["
ANSI = re.compile(r"\x1b\[")
HYBRID = "examples/amm-lending-hybrid-fixture"


class FakeTTY:
    """Writable stream that claims to be a TTY and carries an encoding."""

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


def run_cli(*args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    for key in ("ARKHEIONX_COLOR", "ARKHEIONX_NO_COLOR", "NO_COLOR", "CI", "ARKHEIONX_ANIMATION"):
        env.pop(key, None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


class ScreenBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = {k: os.environ.get(k) for k in ("ARKHEIONX_COLOR", "NO_COLOR", "ARKHEIONX_NO_COLOR", "CI")}
        for k in self._saved:
            os.environ.pop(k, None)

    def tearDown(self) -> None:
        for k, v in self._saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v

    def test_chip_pads_plain_before_color(self) -> None:
        os.environ["NO_COLOR"] = "1"
        self.assertEqual(screen.chip("OK", 7), "OK".ljust(7))
        self.assertEqual(screen.chip("REVIEW"), "REVIEW")

    def test_chip_colors_when_forced_and_strips_back(self) -> None:
        os.environ["ARKHEIONX_COLOR"] = "force"
        token = screen.chip("WARN", 7)
        self.assertIn(ESC, token)
        self.assertEqual(colors.strip(token), "WARN".ljust(7))

    def test_kv_rows_align_on_label(self) -> None:
        os.environ["NO_COLOR"] = "1"
        rows = screen.kv_rows([("Status", "WARN"), ("Version", "3.9.0")])
        self.assertEqual(rows[0].index("WARN"), rows[1].index("3.9.0"))

    def test_chip_rows_align_and_strip_lossless(self) -> None:
        os.environ["ARKHEIONX_COLOR"] = "force"
        rows = screen.chip_rows([("REVIEW", "Foundry project", "not detected"), ("OK", "Solidity files", "24")])
        self.assertTrue(all(ESC in row for row in rows))
        plain = [colors.strip(row) for row in rows]
        self.assertEqual(plain[0].index("Foundry project"), plain[1].index("Solidity files"))
        self.assertTrue(plain[0].startswith("REVIEW"))

    def test_header_is_cyan_when_forced(self) -> None:
        os.environ["ARKHEIONX_COLOR"] = "force"
        lines = screen.header("ArkheionX Doctor", "LOCAL / STATIC")
        self.assertIn(ESC, lines[0])
        self.assertEqual(colors.strip(lines[0]), "ArkheionX Doctor")


class StepReporterTests(unittest.TestCase):
    def test_static_rows_when_not_animated(self) -> None:
        buf = io.StringIO()
        reporter = screen.StepReporter(
            ["Inspect repository", "Map review surface"], stream=buf, animate=False, color=False
        )
        with reporter.step("Inspect repository") as detail:
            detail.detail = "1 source files, 1 test files"
        with reporter.step("Map review surface") as detail:
            detail.detail = "2 contracts, 9 functions"
        out = buf.getvalue()
        self.assertNotIn("\r", out)  # no animation control characters
        self.assertIn("OK", out)
        self.assertIn("Inspect repository", out)
        self.assertIn("2 contracts, 9 functions", out)

    def test_spinner_path_runs_without_real_tty_and_settles(self) -> None:
        # Force animation on a fake TTY: the spinner code path must execute, not
        # crash, and still settle into the final OK row.
        buf = FakeTTY()
        reporter = screen.StepReporter(["Map review surface"], stream=buf, animate=True, color=True)
        with reporter.step("Map review surface") as detail:
            detail.detail = "done"
        settled = colors.strip(buf.getvalue())
        self.assertIn("OK", settled)
        self.assertIn("Map review surface", settled)

    def test_animation_disabled_under_ci_and_no_animation(self) -> None:
        saved = {k: os.environ.get(k) for k in ("CI", "ARKHEIONX_NO_ANIMATION", "ARKHEIONX_ANIMATION")}
        try:
            for k in saved:
                os.environ.pop(k, None)
            os.environ["CI"] = "1"
            self.assertFalse(screen.animation_enabled(FakeTTY()))
            os.environ.pop("CI")
            os.environ["ARKHEIONX_NO_ANIMATION"] = "1"
            self.assertFalse(screen.animation_enabled(FakeTTY()))
            os.environ.pop("ARKHEIONX_NO_ANIMATION")
            os.environ["ARKHEIONX_ANIMATION"] = "force"
            self.assertTrue(screen.animation_enabled(io.StringIO()))
        finally:
            for k, v in saved.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v


class DoctorStructureTests(unittest.TestCase):
    def test_doctor_is_a_structured_command_center(self) -> None:
        out = run_cli("doctor").stdout
        self.assertIn("ArkheionX Doctor", out)
        self.assertNotIn("ARKHEIONX DOCTOR", out)  # old all-caps banner is gone
        for sec in ("Environment", "Project", "Safety", "Next"):
            self.assertIn(sec, out)
        for row in ("RPC calls", "Live-chain actions", "Private keys"):
            self.assertIn(row, out)  # structured safety rows, not a paragraph

    def test_doctor_forced_color_and_plain_ci(self) -> None:
        forced = run_cli("doctor", env_extra={"ARKHEIONX_COLOR": "force"})
        self.assertIn(ESC, forced.stdout)
        self.assertEqual(colors.strip(forced.stdout).count("ARKHEIONX DOCTOR"), 0)
        ci = run_cli("doctor", env_extra={"CI": "1"})
        self.assertNotRegex(ci.stdout, ANSI)
        self.assertNotIn("\r", ci.stdout)


class ReviewMapStructureTests(unittest.TestCase):
    def _artifact_line_count(self, out: str) -> int:
        lines = out.splitlines()
        if "Artifacts" not in lines:
            return 0
        start = lines.index("Artifacts") + 1
        count = 0
        for line in lines[start:]:
            if not line.strip():
                break
            count += 1
        return count

    def test_review_map_is_a_structured_command_center(self) -> None:
        result = run_cli("review-map", HYBRID)
        out = result.stdout
        self.assertEqual(result.returncode, 1)  # heuristic, by design
        self.assertIn("ArkheionX Review Map", out)
        self.assertIn("Inspect first", out)
        self.assertNotIn("Review Priorities", out)
        self.assertNotIn("ARKHEIONX REVIEW MAP", out)
        # Terminal shows at most three artifact lines; the rest stay on disk.
        self.assertLessEqual(self._artifact_line_count(out), 3)
        # Conservative safety boundary preserved.
        self.assertIn("Not confirmed vulnerabilities", out)
        self.assertIn("Human review required", out)
        self.assertIn("exit code 1", out)

    def test_review_map_forced_color_and_ci_plain(self) -> None:
        forced = run_cli("review-map", HYBRID, env_extra={"ARKHEIONX_COLOR": "force"})
        self.assertIn(ESC, forced.stdout)
        ci = run_cli("review-map", HYBRID, env_extra={"CI": "1"})
        self.assertNotRegex(ci.stdout, ANSI)
        self.assertNotIn("\r", ci.stdout)
        # JSON path stays pure.
        js = run_cli("review-map", HYBRID, "--json", env_extra={"ARKHEIONX_COLOR": "force"})
        self.assertNotRegex(js.stdout, ANSI)


if __name__ == "__main__":
    unittest.main()
