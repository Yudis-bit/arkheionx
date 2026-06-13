import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class CliPreviewTests(unittest.TestCase):
    def run_cli(self, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-m", "arkheionx.cli.main", command],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def test_version_command(self) -> None:
        result = self.run_cli("version")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("package version: 7.5.0", result.stdout)
        self.assertIn("Latest stable release: v7.5.0", result.stdout)
        self.assertIn("Current milestone: v7.5.0", result.stdout)
        self.assertIn("Next milestone: v7.6.0", result.stdout)

    def test_doctor_command(self) -> None:
        result = self.run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ArkheionX Doctor", result.stdout)
        self.assertIn("Project", result.stdout)
        self.assertIn("Safety", result.stdout)
        self.assertIn("LOCAL / STATIC", result.stdout)


if __name__ == "__main__":
    unittest.main()
