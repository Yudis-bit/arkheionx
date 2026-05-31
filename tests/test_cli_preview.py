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
        self.assertIn("package version: 2.8.0", result.stdout)
        self.assertNotIn("2.8.0-dev", result.stdout)
        self.assertIn("Latest stable release: v2.7.0", result.stdout)
        self.assertIn("Current milestone: v2.8.0", result.stdout)
        self.assertIn("Next milestone: v2.9.0", result.stdout)

    def test_doctor_command(self) -> None:
        result = self.run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ARKHEIONX DOCTOR", result.stdout)
        self.assertIn("Foundry", result.stdout)
        self.assertIn("Rule packs:", result.stdout)
        self.assertIn("local/static", result.stdout)


if __name__ == "__main__":
    unittest.main()
