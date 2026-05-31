"""Tests for the v2.5.0 installer/uninstaller scripts and onboarding surface.

These tests never perform a real remote install. They rely on `sh -n` syntax
checks, `--help`, and `ARKHEIONX_DRY_RUN=1` with temporary directories.
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL = REPO_ROOT / "install.sh"
UNINSTALL = REPO_ROOT / "uninstall.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class InstallerScriptTests(unittest.TestCase):
    def test_scripts_exist_and_executable(self) -> None:
        for script in (INSTALL, UNINSTALL):
            self.assertTrue(script.exists(), script)
            self.assertTrue(os.access(script, os.X_OK), f"not executable: {script}")

    def test_shell_syntax_valid(self) -> None:
        for script in (INSTALL, UNINSTALL):
            result = subprocess.run(["sh", "-n", str(script)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_help_exits_zero(self) -> None:
        for script in (INSTALL, UNINSTALL):
            result = subprocess.run(["sh", str(script), "--help"], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Usage", result.stdout)

    def test_no_sudo_and_no_profile_edits(self) -> None:
        for script in (INSTALL, UNINSTALL):
            text = read(script)
            self.assertNotIn("sudo", text)
            for profile in (".bashrc", ".zshrc", ".profile", ".bash_profile"):
                self.assertNotIn(profile, text)

    def test_default_repo_and_ref_documented(self) -> None:
        text = read(INSTALL)
        self.assertIn("github.com/Yudis-bit/DeFi-Exploit-PoCs", text)
        self.assertIn("v2.10.0", text)  # stable tag default (ARKHEIONX_STABLE_TAG)

    def test_no_pypi_claim(self) -> None:
        text = (read(INSTALL) + read(REPO_ROOT / "docs/INSTALLER.md")).lower()
        self.assertIn("not published to pypi", text)
        self.assertNotIn("pip install arkheionx\n", text)

    def test_install_dry_run_changes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            env = os.environ.copy()
            env.update(
                ARKHEIONX_DRY_RUN="1",
                ARKHEIONX_INSTALL_METHOD="venv",
                ARKHEIONX_INSTALL_DIR=str(install_dir),
                ARKHEIONX_LOCAL_PATH=str(REPO_ROOT),
            )
            result = subprocess.run(["sh", str(INSTALL)], text=True, capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DRY-RUN", result.stdout)
            self.assertIn('export PATH="', result.stdout)  # PATH hint printed
            self.assertFalse(install_dir.exists(), "dry-run must not create the install dir")

    def test_uninstall_refuses_non_managed_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            unsafe = Path(tmp) / "not-arkheionx"
            unsafe.mkdir()
            env = os.environ.copy()
            env["ARKHEIONX_INSTALL_DIR"] = str(unsafe)
            result = subprocess.run(
                ["sh", str(UNINSTALL), "--dry-run"], text=True, capture_output=True, env=env
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("Refusing", result.stderr)

    def test_uninstall_dry_run_removes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            (install_dir / "venv").mkdir(parents=True)
            env = os.environ.copy()
            env["ARKHEIONX_INSTALL_DIR"] = str(install_dir)
            result = subprocess.run(
                ["sh", str(UNINSTALL), "--dry-run"], text=True, capture_output=True, env=env
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DRY-RUN", result.stdout)
            self.assertTrue((install_dir / "venv").exists(), "dry-run must not delete anything")

    def test_uninstall_mentions_pipx_guidance(self) -> None:
        self.assertIn("pipx uninstall arkheionx", read(UNINSTALL))

    def test_install_writes_receipt_and_uninstall_removes_it(self) -> None:
        import json

        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            env = os.environ.copy()
            env.update(
                ARKHEIONX_YES="1",
                ARKHEIONX_INSTALL_METHOD="venv",
                ARKHEIONX_INSTALL_DIR=str(install_dir),
                ARKHEIONX_LOCAL_PATH=str(REPO_ROOT),
            )
            install = subprocess.run(["sh", str(INSTALL)], text=True, capture_output=True, env=env)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            receipt = install_dir / "install.json"
            self.assertTrue(receipt.exists(), "install.sh must write the receipt")
            data = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], 1)
            self.assertEqual(data["source_kind"], "local")
            self.assertEqual(data["install_method"], "venv")
            for field in ("installed_at", "updated_at", "install_dir", "bin_dir", "command_path"):
                self.assertIn(field, data)

            uninstall = subprocess.run(
                ["sh", str(UNINSTALL)], text=True, capture_output=True,
                env={**os.environ, "ARKHEIONX_YES": "1", "ARKHEIONX_INSTALL_DIR": str(install_dir)},
            )
            self.assertEqual(uninstall.returncode, 0, uninstall.stdout + uninstall.stderr)
            self.assertFalse(receipt.exists(), "uninstall.sh must remove the receipt")


class OnboardingSurfaceTests(unittest.TestCase):
    def test_onboarding_docs_exist(self) -> None:
        for doc in [
            "docs/INSTALLER.md",
            "docs/UNINSTALL.md",
            "docs/ONBOARDING.md",
            "docs/TROUBLESHOOTING.md",
            "docs/INSTALLATION.md",
            "docs/TRY_IN_5_MINUTES.md",
            "docs/ARKUP.md",
            "docs/UPDATE_FLOW.md",
        ]:
            self.assertTrue((REPO_ROOT / doc).exists(), doc)

    def test_readme_stays_concise_and_links_installer(self) -> None:
        readme = read(REPO_ROOT / "README.md")
        self.assertLess(len(readme.splitlines()), 650)  # v3 launch README bound (300-650)
        self.assertIn("sh install.sh", readme)
        self.assertIn("docs/INSTALLER.md", readme)

    def test_release_notes_and_changelog_present(self) -> None:
        self.assertTrue((REPO_ROOT / "release-notes/v2.6.0.md").exists())
        changelog = read(REPO_ROOT / "CHANGELOG.md")
        self.assertIn("## v2.6.0", changelog)
        self.assertNotIn("## v2.5.0 - Unreleased", changelog)

    def test_version_metadata(self) -> None:
        from arkheionx.version import CURRENT_MILESTONE, NEXT_MILESTONE, STABLE_RELEASE, __version__

        self.assertEqual(__version__, "3.0.0-dev")
        self.assertEqual(STABLE_RELEASE, "v2.10.0")
        self.assertEqual(CURRENT_MILESTONE, "v3.0.0")
        self.assertEqual(NEXT_MILESTONE, "v3.1.0")


if __name__ == "__main__":
    unittest.main()
