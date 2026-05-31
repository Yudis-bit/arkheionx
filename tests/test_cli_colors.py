"""Tests for the v2.9.0 professional CLI color output.

Color must be disabled in non-TTY/captured output (so the rest of the suite is
unaffected), respect NO_COLOR/CI, be forceable via ARKHEIONX_COLOR, and never
appear in JSON output or in artifact files written to disk.
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from arkheionx.cli import colors

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = "examples/oracle-staking-fixture"
ESC = "\033["


class _FakeTTY:
    def isatty(self):
        return True


class _FakePipe:
    def isatty(self):
        return False


def run_cli(*args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    # Start from a clean color env so host CI/NO_COLOR do not skew assertions.
    for key in ("ARKHEIONX_COLOR", "NO_COLOR", "CI"):
        env.pop(key, None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


class ColorUtilityTests(unittest.TestCase):
    def _enabled(self, env: dict, stream) -> bool:
        saved = {k: os.environ.get(k) for k in ("ARKHEIONX_COLOR", "NO_COLOR", "CI", "TERM")}
        try:
            for k in ("ARKHEIONX_COLOR", "NO_COLOR", "CI", "TERM"):
                os.environ.pop(k, None)
            os.environ.update(env)
            return colors.enabled(stream)
        finally:
            for k, v in saved.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v

    def test_auto_on_tty_off_pipe(self) -> None:
        self.assertTrue(self._enabled({}, _FakeTTY()))
        self.assertFalse(self._enabled({}, _FakePipe()))

    def test_never_and_always(self) -> None:
        self.assertFalse(self._enabled({"ARKHEIONX_COLOR": "never"}, _FakeTTY()))
        self.assertTrue(self._enabled({"ARKHEIONX_COLOR": "always"}, _FakePipe()))

    def test_no_color_and_ci_disable(self) -> None:
        self.assertFalse(self._enabled({"NO_COLOR": "1"}, _FakeTTY()))
        self.assertFalse(self._enabled({"CI": "true"}, _FakeTTY()))

    def test_always_overrides_no_color_and_ci(self) -> None:
        self.assertTrue(self._enabled({"ARKHEIONX_COLOR": "always", "NO_COLOR": "1", "CI": "1"}, _FakePipe()))

    def test_invalid_value_falls_back_to_auto(self) -> None:
        self.assertFalse(self._enabled({"ARKHEIONX_COLOR": "purple"}, _FakePipe()))
        self.assertTrue(self._enabled({"ARKHEIONX_COLOR": "purple"}, _FakeTTY()))

    def test_strip_removes_ansi(self) -> None:
        self.assertEqual(colors.strip("\033[1mARKHEIONX\033[0m"), "ARKHEIONX")

    def test_colorize_report_noop_when_disabled(self) -> None:
        os.environ["ARKHEIONX_COLOR"] = "never"
        try:
            text = "ARKHEIONX DEMO\nStatus: ok"
            self.assertEqual(colors.colorize_report(text), text)
        finally:
            os.environ.pop("ARKHEIONX_COLOR", None)

    def test_colorize_report_adds_ansi_when_forced(self) -> None:
        os.environ["ARKHEIONX_COLOR"] = "always"
        try:
            out = colors.colorize_report("ARKHEIONX DEMO\nStatus: ok\nEvidence level: EXECUTION_CONFIRMED")
            self.assertIn(ESC, out)
            self.assertEqual(colors.strip(out), "ARKHEIONX DEMO\nStatus: ok\nEvidence level: EXECUTION_CONFIRMED")
        finally:
            os.environ.pop("ARKHEIONX_COLOR", None)


class CliColorBehaviorTests(unittest.TestCase):
    def test_default_capture_is_plain(self) -> None:
        result = run_cli("version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(ESC, result.stdout)
        self.assertIn("Arkheionx package version:", result.stdout)

    def test_never_is_plain(self) -> None:
        result = run_cli("doctor", env_extra={"ARKHEIONX_COLOR": "never"})
        self.assertNotIn(ESC, result.stdout)
        self.assertIn("ARKHEIONX DOCTOR", colors.strip(result.stdout))

    def test_always_emits_ansi(self) -> None:
        for args in (("version",), ("demo", "--list"), ("demo", "--show", "amm-swap")):
            result = run_cli(*args, env_extra={"ARKHEIONX_COLOR": "always"})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(ESC, result.stdout, f"expected ANSI for {args}")
            # Content remains intact once stripped.
            self.assertIn("Arkheionx" if args == ("version",) else "ARKHEIONX", colors.strip(result.stdout))

    def test_no_color_env_disables_even_on_request(self) -> None:
        result = run_cli("version", env_extra={"NO_COLOR": "1"})
        self.assertNotIn(ESC, result.stdout)

    def test_json_has_no_ansi_even_when_forced(self) -> None:
        result = run_cli("demo", "--list", "--json", env_extra={"ARKHEIONX_COLOR": "always"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(ESC, result.stdout)
        payload = json.loads(result.stdout)  # must be valid JSON, not ANSI-polluted
        self.assertTrue(any(d["id"] == "amm-swap" for d in payload))

    def test_artifact_files_have_no_ansi_when_forced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", "-m", "arkheionx.cli.main", "hunt", FIXTURE, "--artifacts-dir", tmp],
                cwd=REPO_ROOT, text=True, capture_output=True,
                env={**os.environ, "ARKHEIONX_COLOR": "always"},
            )
            self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
            hunt_json = Path(tmp) / ".arkheionx" / "out" / "hunt.json"
            self.assertTrue(hunt_json.exists())
            self.assertNotIn(ESC, hunt_json.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
