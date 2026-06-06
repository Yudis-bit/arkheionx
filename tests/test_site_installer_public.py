import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "site/public/install"


class SiteInstallerPublicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = INSTALLER.read_text(encoding="utf-8")
        cls.lower = cls.text.lower()

    def test_installer_exists_is_executable_and_bash_compatible(self) -> None:
        self.assertTrue(INSTALLER.is_file())
        self.assertTrue(os.access(INSTALLER, os.X_OK))
        self.assertTrue(self.text.startswith("#!/usr/bin/env bash\n"))
        result = subprocess.run(["bash", "-n", str(INSTALLER)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_installer_uses_public_main_source(self) -> None:
        self.assertIn("set -euo pipefail", self.text)
        self.assertIn("https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git", self.text)
        self.assertIn('BRANCH="main"', self.text)
        self.assertIn('git clone --branch "$BRANCH" --single-branch', self.text)
        self.assertIn('merge --ff-only "origin/$BRANCH"', self.text)

    def test_installer_checks_requirements_and_builds_managed_paths(self) -> None:
        for marker in [
            "Linux|Darwin",
            "command -v git",
            "command -v python3",
            "sys.version_info >= (3, 11)",
            'SRC_DIR="$ARKHEIONX_HOME/src"',
            'VENV_DIR="$ARKHEIONX_HOME/venv"',
            'python3 -m venv "$VENV_DIR"',
            "-m pip install",
            'ARKHEIONX_WRAPPER="$BIN_DIR/arkheionx"',
            'ARKUP_WRAPPER="$BIN_DIR/arkup"',
            '"$ARKHEIONX_WRAPPER" version',
        ]:
            self.assertIn(marker, self.text)

    def test_installer_has_no_private_branch_or_project_execution(self) -> None:
        for forbidden in [
            "origin/internal",
            "origin/private",
            "refs/heads/internal",
            "refs/heads/private",
            "forge ",
            "cast ",
            "anvil ",
            "v3.9.0",
        ]:
            self.assertNotIn(forbidden, self.lower)


if __name__ == "__main__":
    unittest.main()
