import os
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PackageInstallableTests(unittest.TestCase):
    def test_pyproject_declares_console_entrypoint(self) -> None:
        pyproject = REPO_ROOT / "pyproject.toml"
        self.assertTrue(pyproject.exists())
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["name"], "arkheionx")
        self.assertEqual(data["project"]["scripts"]["arkheionx"], "arkheionx.cli.main:main")
        self.assertEqual(data["project"]["version"], "2.6.0")
        self.assertEqual(data["project"]["dependencies"], [])

    def test_editable_install_and_console_version(self) -> None:
        env = os.environ.copy()
        env["PIP_BREAK_SYSTEM_PACKAGES"] = "1"
        install = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".", "--no-build-isolation"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            env=env,
        )
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        result = subprocess.run(
            ["arkheionx", "version"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("package version: 2.6.0", result.stdout)
        self.assertNotIn("2.6.0-dev", result.stdout)
        self.assertIn("Latest stable release: v2.6.0", result.stdout)
        self.assertIn("Current milestone: v2.6.0", result.stdout)
        self.assertIn("Next milestone: v2.7.0", result.stdout)

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
