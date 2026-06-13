"""Tests for the lens private-scope leak guard and public-output-path warning."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from arkheionx.protocol_lens import leak_check

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "morpho_midnight_toy"
SCOPE = FIXTURE / "scope.md"


def run_cli(*args: str):
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class LensLeakGuardTests(unittest.TestCase):
    def test_public_vs_private_output_path(self) -> None:
        root = FIXTURE
        private_out = root / ".arkheionx" / "lens-pack"
        public_out = root / "public-out"
        self.assertTrue(leak_check.is_private_path(root, private_out))
        self.assertFalse(leak_check.is_public_output_path(root, private_out))
        self.assertTrue(leak_check.is_public_output_path(root, public_out))
        # No warning for an output path under .arkheionx/; a warning for a public path.
        self.assertIsNone(leak_check.output_path_warning(root, private_out))
        self.assertIsNotNone(leak_check.output_path_warning(root, public_out))

    def test_warning_is_stronger_for_private_scope(self) -> None:
        root = FIXTURE
        public_out = root / "public-out"
        private_scope = str(root / ".arkheionx" / "private" / "scope.md")
        warn = leak_check.output_path_warning(root, public_out, private_scope)
        self.assertIsNotNone(warn)
        self.assertIn("private", warn.lower())

    def test_private_term_scan_catches_leak(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp)
            priv = r / ".arkheionx" / "private"
            priv.mkdir(parents=True)
            (priv / "private-terms.txt").write_text("ZzSecretTargetName\n", encoding="utf-8")
            (r / "leaky.md").write_text("mentions ZzSecretTargetName publicly", encoding="utf-8")
            (priv / "scope.md").write_text("ZzSecretTargetName scope", encoding="utf-8")
            result = leak_check.run_private_leak_check(r)
            self.assertFalse(result["clean"])
            leaked = {leak["file"] for leak in result["leaks"]}
            self.assertIn("leaky.md", leaked)
            self.assertNotIn(".arkheionx/private/scope.md", leaked)

    def test_cli_warns_on_public_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "public-pack"
            result = run_cli("lens-pack", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertIn("outside .arkheionx", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
