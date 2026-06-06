"""TerminalUI DX tests for `arkheionx open` (subprocess; no network, no Foundry).

`open` runs static/heuristic by default, so it returns 1 (heuristic) on the demo
fixtures by design; 0 is reserved for compiler/execution-confirmed runs. `open`
writes no artifacts. These tests assert the human DX presentation and JSON purity
without parsing brittle timing values.
"""
import json
import os
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "arkheionx" / "demo" / "fixtures" / "oracle-staking"
ANSI = re.compile(r"\x1b\[")


def run_cli(*args: str, color: str = "never", env_extra: dict | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = color
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


class OpenUxTests(unittest.TestCase):
    def test_banner_and_safety_line(self) -> None:
        result = run_cli("open", str(FIXTURE), "--no-artifacts")
        self.assertEqual(result.returncode, 1, result.stderr)  # heuristic by design
        self.assertIn("ARKHEIONX OPEN", result.stdout)
        self.assertIn("local/static", result.stdout)
        self.assertIn("no RPC, no keys", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_has_core_sections(self) -> None:
        result = run_cli("open", str(FIXTURE), "--no-artifacts")
        for section in ("Summary", "Top Surfaces", "Money Flow", "Next", "Boundary"):
            self.assertIn(section, result.stdout, section)

    def test_no_ansi_when_color_never(self) -> None:
        result = run_cli("open", str(FIXTURE), "--no-artifacts", color="never")
        self.assertNotRegex(result.stdout, ANSI)

    def test_ci_disables_animation_no_cr(self) -> None:
        result = run_cli("open", str(FIXTURE), "--no-artifacts", env_extra={"CI": "true"})
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("\r", result.stdout)

    def test_no_animation_env_no_cr(self) -> None:
        result = run_cli("open", str(FIXTURE), "--no-artifacts", env_extra={"ARKHEIONX_NO_ANIMATION": "1"})
        self.assertNotIn("\r", result.stdout)

    def test_json_is_pure_and_unchanged(self) -> None:
        result = run_cli("open", str(FIXTURE), "--json", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        payload = json.loads(result.stdout)  # raises if not pure JSON
        for key in ("meta", "protocol_snapshot", "money_flow", "hunter_targets", "next_commands"):
            self.assertIn(key, payload, key)
        self.assertNotRegex(result.stdout, ANSI)

    def test_json_has_no_human_chrome(self) -> None:
        result = run_cli("open", str(FIXTURE), "--json", color="always")
        for chrome in ("ARKHEIONX OPEN", "[1/1]", "Top Surfaces", "Boundary"):
            self.assertNotIn(chrome, result.stdout)


if __name__ == "__main__":
    unittest.main()
