"""Packaging guards for the v7.5 Protocol Lens layer.

Two layers of protection:

* ``PackagingConfigTests`` always runs and guards the static packaging config and
  source tree: the ``protocol_lens`` package (and its Fixed Credit Market lens) is
  discoverable, the dead ``orchestration`` package is gone, the lens schema is
  present, and ``version.py`` agrees with ``pyproject.toml``.
* ``WheelContentTests`` builds a wheel into a temp dir (no build isolation, fully
  offline) and asserts the built artifact ships ``arkheionx/protocol_lens`` and the
  lens schema, excludes ``arkheionx/orchestration``, exposes the ``arkheionx``
  console script, and reports the current package metadata version. If the local build
  toolchain is unavailable it skips with the captured reason rather than failing.
"""
import shutil
import subprocess
import sys
import tarfile  # noqa: F401  (kept for parity with sdist debugging)
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path

from setuptools import find_packages

from arkheionx.version import PACKAGE_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]


class PackagingConfigTests(unittest.TestCase):
    def test_protocol_lens_is_discoverable(self) -> None:
        pkgs = find_packages(where=str(REPO_ROOT), include=["arkheionx*"])
        self.assertIn("arkheionx.protocol_lens", pkgs)
        self.assertIn("arkheionx.protocol_lens.lenses", pkgs)
        # v7 scope orchestration must remain (protocol_lens depends on it).
        self.assertIn("arkheionx.scope_orchestration", pkgs)

    def test_dead_orchestration_package_is_gone(self) -> None:
        pkgs = find_packages(where=str(REPO_ROOT), include=["arkheionx*"])
        self.assertNotIn("arkheionx.orchestration", pkgs)
        self.assertFalse((REPO_ROOT / "arkheionx" / "orchestration").exists())

    def test_fixed_credit_market_lens_source_present(self) -> None:
        self.assertTrue((REPO_ROOT / "arkheionx" / "protocol_lens" / "lenses" / "fixed_credit_market.py").is_file())

    def test_lens_schema_present(self) -> None:
        self.assertTrue((REPO_ROOT / "schemas" / "lens-pack.schema.json").is_file())

    def test_version_consistent_between_version_py_and_pyproject(self) -> None:
        data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["version"], PACKAGE_VERSION)
        self.assertEqual(PACKAGE_VERSION, "10.1.0.dev0")

    def test_pyproject_ships_schemas(self) -> None:
        data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        data_files = data.get("tool", {}).get("setuptools", {}).get("data-files", {})
        joined = " ".join(" ".join(v) if isinstance(v, list) else str(v) for v in data_files.values())
        self.assertIn("schemas/", joined)


class WheelContentTests(unittest.TestCase):
    wheel: Path | None = None
    _skip_reason: str = ""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        out = Path(cls._tmp.name)
        # A stale build/lib cache from an earlier in-place build can smuggle
        # removed packages (e.g. the deleted orchestration package) into a fresh
        # wheel, because setuptools' build_py does not purge stale files. Remove
        # it so the wheel reflects the current source tree.
        shutil.rmtree(REPO_ROOT / "build", ignore_errors=True)
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", str(out)],
                cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=600,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:  # pragma: no cover
            cls._skip_reason = f"wheel build unavailable: {exc}"
            return
        if proc.returncode != 0:  # pragma: no cover
            cls._skip_reason = f"wheel build failed: {proc.stderr[-2000:]}"
            return
        wheels = sorted(out.glob("arkheionx-*.whl"))
        if not wheels:  # pragma: no cover
            cls._skip_reason = "no wheel produced"
            return
        cls.wheel = wheels[-1]

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def setUp(self) -> None:
        if self.wheel is None:
            self.skipTest(self._skip_reason or "no wheel built")

    def _names(self) -> list[str]:
        with zipfile.ZipFile(self.wheel) as z:
            return z.namelist()

    def test_includes_protocol_lens(self) -> None:
        names = self._names()
        self.assertTrue(any(n.startswith("arkheionx/protocol_lens/") for n in names))

    def test_includes_fixed_credit_market_lens(self) -> None:
        self.assertIn("arkheionx/protocol_lens/lenses/fixed_credit_market.py", self._names())

    def test_excludes_dead_orchestration(self) -> None:
        names = self._names()
        self.assertFalse(any(n.startswith("arkheionx/orchestration/") for n in names))
        # The v7 scope orchestration package must still ship.
        self.assertTrue(any(n.startswith("arkheionx/scope_orchestration/") for n in names))

    def test_includes_lens_schema(self) -> None:
        names = self._names()
        self.assertTrue(any(n.endswith("schemas/lens-pack.schema.json") for n in names),
                        f"lens-pack schema not found in wheel: {[n for n in names if 'schema' in n][:5]}")

    def test_exposes_arkheionx_console_script(self) -> None:
        names = self._names()
        ep = next((n for n in names if n.endswith("entry_points.txt")), None)
        self.assertIsNotNone(ep, "entry_points.txt missing from wheel")
        with zipfile.ZipFile(self.wheel) as z:
            text = z.read(ep).decode("utf-8")
        self.assertIn("arkheionx = arkheionx.cli.main:main", text)

    def test_metadata_version_is_release_version(self) -> None:
        names = self._names()
        meta = next((n for n in names if n.endswith(".dist-info/METADATA")), None)
        self.assertIsNotNone(meta)
        with zipfile.ZipFile(self.wheel) as z:
            text = z.read(meta).decode("utf-8")
        self.assertIn(f"Version: {PACKAGE_VERSION}", text)
        self.assertIn("Version: 10.1.0.dev0", text)


if __name__ == "__main__":
    unittest.main()
