"""Tests for the release-readiness gate."""
import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_gate():
    path = REPO_ROOT / "scripts" / "check_release_readiness.py"
    spec = importlib.util.spec_from_file_location("check_release_readiness", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseReadinessGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = load_gate()

    def test_gate_passes(self) -> None:
        failures = self.gate.check()
        self.assertEqual(failures, [], "\n".join(failures))

    def test_main_check_exits_zero(self) -> None:
        self.assertEqual(self.gate.main(["--check"]), 0)

    def test_gate_covers_full_command_surface(self) -> None:
        commands = self.gate.public_commands()
        for expected in ("version", "doctor", "demo", "open", "hunt", "prove", "evidence-status"):
            self.assertIn(expected, commands)

    def test_gate_detects_missing_command_in_doc(self) -> None:
        # A command absent from PUBLIC_SURFACE.md must be reported.
        original = self.gate.public_commands
        self.gate.public_commands = lambda: original() + ["totally-made-up-command"]
        try:
            failures = self.gate.check()
        finally:
            self.gate.public_commands = original
        self.assertTrue(any("totally-made-up-command" in f for f in failures))


if __name__ == "__main__":
    unittest.main()
