import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _pip_env(tmp: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        PIP_CACHE_DIR=str(tmp / "pip-cache"),
        PIP_DISABLE_PIP_VERSION_CHECK="1",
        PIP_NO_INDEX="1",
    )
    return env


class PackageInstallableTests(unittest.TestCase):
    def test_pyproject_declares_console_entrypoint(self) -> None:
        pyproject = REPO_ROOT / "pyproject.toml"
        self.assertTrue(pyproject.exists())
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["name"], "arkheionx")
        self.assertEqual(data["project"]["scripts"]["arkheionx"], "arkheionx.cli.main:main")
        self.assertEqual(data["project"]["version"], "3.9.0")
        self.assertEqual(data["project"]["dependencies"], [])

    def test_editable_install_and_console_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            venv = tmp_path / "venv"
            create = subprocess.run(
                [sys.executable, "-m", "venv", "--system-site-packages", str(venv)],
                text=True,
                capture_output=True,
            )
            if create.returncode != 0:
                self.skipTest(f"venv unavailable: {create.stdout + create.stderr}")
            python = venv / "bin" / "python"
            install = subprocess.run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "-e",
                    str(REPO_ROOT),
                    "--no-build-isolation",
                ],
                cwd=tmp_path,
                text=True,
                capture_output=True,
                env=_pip_env(tmp_path),
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            result = subprocess.run(
                [str(venv / "bin" / "arkheionx"), "version"],
                cwd=tmp_path,
                text=True,
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("package version: 3.9.0", result.stdout)
        self.assertIn("Latest stable release: v3.1.0", result.stdout)
        self.assertIn("Current milestone: v3.9.0", result.stdout)
        self.assertIn("Next milestone: v4.0.0", result.stdout)

    def test_no_publish_workflow_keywords(self) -> None:
        haystack = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in [
                REPO_ROOT / "pyproject.toml",
                REPO_ROOT / "README.md",
                REPO_ROOT / "docs" / "PACKAGING.md",
            ]
        ).lower()
        for phrase in ["twine upload", "pypi_api_token", "trusted publishing"]:
            self.assertNotIn(phrase, haystack)


if __name__ == "__main__":
    unittest.main()
