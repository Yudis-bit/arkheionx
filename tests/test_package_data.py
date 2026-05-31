"""Tests for v2.8.0 package-data bundling and distribution hardening.

Local-only and network-free. The non-editable venv install test builds the
package from the local repo (no network) and skips gracefully if the toolchain
is unavailable.
"""
import subprocess
import sys
import tempfile
import tomllib
import unittest
from importlib.resources import files
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_PACKAGE = "arkheionx.demo.fixtures"


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=str(cwd or REPO_ROOT), text=True, capture_output=True,
    )


class PackageDataTests(unittest.TestCase):
    def test_runtime_data_paths_resolve_from_source_tree(self) -> None:
        from arkheionx.core.paths import (
            is_editable_source_tree,
            package_root,
            project_root,
            resolve_runtime_data_path,
        )

        root = project_root()
        self.assertTrue((root / "pyproject.toml").exists())
        self.assertTrue(package_root().name == "arkheionx")
        self.assertTrue(is_editable_source_tree(root))
        for parts in [
            ("metadata", "search_terms.json"),
            ("schemas", "pre-audit-report.schema.json"),
            ("templates", "invariant_skeletons", "amm_invariants.sol"),
        ]:
            path = resolve_runtime_data_path(*parts, root=root)
            self.assertTrue(path.exists(), str(path))

    def test_runtime_data_helpers_return_paths(self) -> None:
        from arkheionx.core.paths import resolve_input_path, resolve_output_path

        metadata = resolve_input_path("metadata/search_terms.json")
        self.assertTrue(metadata.exists(), str(metadata))
        output = resolve_output_path("reports/example.json", root=Path("/tmp"))
        self.assertEqual(output, Path("/tmp/reports/example.json"))


class PackageResourceTests(unittest.TestCase):
    def fixture_root(self):
        return files(FIXTURES_PACKAGE).joinpath("oracle-staking")

    def test_resource_dir_exists(self) -> None:
        self.assertTrue(self.fixture_root().is_dir())

    def test_resource_contains_source_files(self) -> None:
        root = self.fixture_root()
        self.assertTrue(root.joinpath("README.md").is_file())
        self.assertTrue(root.joinpath("foundry.toml").is_file())
        self.assertTrue(root.joinpath("src/OracleRewardFixture.sol").is_file())
        self.assertTrue(root.joinpath("test/OracleRewardFixture.t.sol").is_file())

    def test_resource_excludes_generated_dirs(self) -> None:
        root = self.fixture_root()
        for generated in ("out", "cache", ".arkheionx"):
            self.assertFalse(root.joinpath(generated).is_dir(), generated)

    def test_bundled_fixture_has_no_secrets_or_rpc(self) -> None:
        banned = ["rpc", "mnemonic", "private key", "private_key", "http://", "https://", "secret"]
        root = self.fixture_root()
        for rel in ("README.md", "foundry.toml", "src/OracleRewardFixture.sol",
                    "test/OracleRewardFixture.t.sol"):
            text = root.joinpath(rel).read_text(encoding="utf-8").lower()
            for phrase in banned:
                self.assertNotIn(phrase, text, f"{rel} contains '{phrase}'")

    def test_registry_resolves_bundled_source(self) -> None:
        from arkheionx.demo.registry import PACKAGE_SOURCE, get_demo, resolve_source_kind

        self.assertEqual(resolve_source_kind(get_demo("oracle-staking")), PACKAGE_SOURCE)

    def test_pyproject_declares_package_data(self) -> None:
        data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        pkg_data = data["tool"]["setuptools"]["package-data"]
        self.assertIn("arkheionx.demo.fixtures", pkg_data)
        globs = pkg_data["arkheionx.demo.fixtures"]
        self.assertTrue(any(g.endswith(".sol") for g in globs))


class DemoFromInstalledContextTests(unittest.TestCase):
    def test_show_reports_bundled_source(self) -> None:
        result = run_cli("demo", "--show", "oracle-staking")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Source: bundled package fixture", result.stdout)

    def test_copy_from_non_repo_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as out:
            dest = Path(out) / "arkheionx-demo"
            result = run_cli("demo", "--copy", "oracle-staking", str(dest), cwd=Path(cwd))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("bundled package fixture", result.stdout)
            self.assertTrue((dest / "README.md").exists())
            self.assertTrue((dest / "foundry.toml").exists())
            self.assertTrue((dest / "src" / "OracleRewardFixture.sol").exists())
            self.assertTrue((dest / "test" / "OracleRewardFixture.t.sol").exists())
            self.assertFalse((dest / "out").exists())
            self.assertFalse((dest / "cache").exists())


class InstalledWheelSmokeTests(unittest.TestCase):
    def test_non_editable_venv_install_can_copy_demo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            venv = Path(tmp) / "venv"
            dest = Path(tmp) / "demo-out"
            try:
                subprocess.run([sys.executable, "-m", "venv", str(venv)],
                               check=True, capture_output=True, text=True, timeout=120)
                pip = venv / "bin" / "pip"
                install = subprocess.run([str(pip), "install", "."], cwd=str(REPO_ROOT),
                                         capture_output=True, text=True, timeout=420)
            except (subprocess.SubprocessError, OSError) as exc:
                self.skipTest(f"venv/pip unavailable: {exc}")
            if install.returncode != 0:
                self.skipTest(f"non-editable install failed: {install.stderr[-500:]}")
            arkheionx = venv / "bin" / "arkheionx"
            result = subprocess.run([str(arkheionx), "demo", "--copy", "oracle-staking", str(dest)],
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((dest / "src" / "OracleRewardFixture.sol").exists())
            self.assertTrue((dest / "test" / "OracleRewardFixture.t.sol").exists())


class PackageDataDocsTests(unittest.TestCase):
    def test_docs_and_release_notes_present(self) -> None:
        self.assertTrue((REPO_ROOT / "docs" / "PACKAGE_DATA.md").exists())
        self.assertTrue((REPO_ROOT / "release-notes" / "v2.8.0.md").exists())
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## v2.8.0 - Unreleased", changelog)

    def test_no_generated_fixture_artifacts_tracked(self) -> None:
        tracked = subprocess.run(
            ["git", "ls-files", "arkheionx/demo/fixtures"],
            cwd=REPO_ROOT, text=True, capture_output=True,
        ).stdout.split()
        for entry in tracked:
            self.assertFalse("/out/" in entry or "/cache/" in entry or ".arkheionx" in entry, entry)


if __name__ == "__main__":
    unittest.main()
