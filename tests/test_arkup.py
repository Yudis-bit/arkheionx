"""Tests for the v2.6.0 `arkup` lifecycle helper and install receipt.

No real network installs and no mutation of the real home directory: tests use
temp dirs, env vars, hand-written receipts, and `--dry-run`.
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARKUP = REPO_ROOT / "arkup"
SCHEMA = REPO_ROOT / "schemas" / "install-receipt.schema.json"


def run_arkup(*args: str, env_overrides: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(["sh", str(ARKUP), *args], text=True, capture_output=True, env=env)


def write_receipt(install_dir: Path, **fields) -> Path:
    install_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": 1,
        "tool": "arkheionx",
        "installed_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "install_method": "venv",
        "source_kind": "stable",
        "repo_url": "https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git",
        "ref": "v2.5.0",
        "local_path": "",
        "install_dir": str(install_dir),
        "bin_dir": str(install_dir / "bin"),
        "command_path": str(install_dir / "bin" / "arkheionx"),
        "detected_python": "/usr/bin/python3",
        "installed_version": "2.6.0-dev",
        "installer_version": "2.6.0",
        "notes": "",
    }
    data.update(fields)
    receipt = install_dir / "install.json"
    receipt.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


class ArkupScriptTests(unittest.TestCase):
    def test_exists_and_executable(self) -> None:
        self.assertTrue(ARKUP.exists())
        self.assertTrue(os.access(ARKUP, os.X_OK))

    def test_shell_syntax_valid(self) -> None:
        result = subprocess.run(["sh", "-n", str(ARKUP)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_sudo_and_no_profile_edits(self) -> None:
        text = ARKUP.read_text(encoding="utf-8")
        self.assertNotIn("sudo", text)
        for profile in (".bashrc", ".zshrc", ".profile", ".bash_profile"):
            self.assertNotIn(profile, text)

    def test_help(self) -> None:
        result = run_arkup("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Usage", result.stdout)
        self.assertIn("--update", result.stdout)
        self.assertIn("not a full version manager", result.stdout.lower())

    def test_version(self) -> None:
        result = run_arkup("--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("arkup", result.stdout)
        self.assertIn("Stable target:", result.stdout)

    def test_check_without_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            result = run_arkup("--check", "--install-dir", str(install_dir))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("install state unknown", result.stdout)

    def test_check_with_valid_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            write_receipt(install_dir, source_kind="ref", ref="v2.5.0")
            result = run_arkup("--check", "--install-dir", str(install_dir))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("install receipt:", result.stdout)
            self.assertIn("source_kind: ref", result.stdout)

    def test_check_with_malformed_receipt_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            install_dir.mkdir(parents=True)
            (install_dir / "install.json").write_text("{not json", encoding="utf-8")
            result = run_arkup("--check", "--install-dir", str(install_dir))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("malformed", result.stdout + result.stderr)

    def test_install_dry_run_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            result = run_arkup(
                "--install", "--local", str(REPO_ROOT),
                "--install-dir", str(install_dir), "--dry-run", "--yes",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DRY-RUN", result.stdout)
            self.assertIn("kind: local", result.stdout)
            self.assertFalse(install_dir.exists(), "dry-run must not create the install dir")

    def test_update_keeps_pinned_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            write_receipt(install_dir, source_kind="ref", ref="v2.5.0")
            result = run_arkup(
                "--update", "--install-dir", str(install_dir), "--dry-run", "--yes",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("source kind: ref", result.stdout)
            self.assertIn("@v2.5.0", result.stdout)

    def test_update_keeps_local_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            write_receipt(install_dir, source_kind="local", local_path=str(REPO_ROOT), ref="")
            result = run_arkup(
                "--update", "--install-dir", str(install_dir), "--dry-run", "--yes",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("kind: local", result.stdout)

    def test_update_without_receipt_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            result = run_arkup("--update", "--install-dir", str(install_dir), "--dry-run")
            self.assertEqual(result.returncode, 1)
            self.assertIn("No install receipt", result.stderr)

    def test_uninstall_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            install_dir = Path(tmp) / ".arkheionx"
            (install_dir / "venv").mkdir(parents=True)
            write_receipt(install_dir)
            result = run_arkup("--uninstall", "--install-dir", str(install_dir), "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DRY-RUN", result.stdout)
            self.assertTrue((install_dir / "venv").exists(), "dry-run must not delete anything")


class InstallReceiptSchemaTests(unittest.TestCase):
    def test_schema_exists_and_parses(self) -> None:
        self.assertTrue(SCHEMA.exists())
        data = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(data["title"], "Arkheionx Install Receipt")
        for field in ("schema_version", "source_kind", "install_method"):
            self.assertIn(field, data["properties"])


if __name__ == "__main__":
    unittest.main()
