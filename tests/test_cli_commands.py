import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class CliCommandTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-m", "arkheionx.cli.main", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def test_help_version_and_doctor_exit_zero(self) -> None:
        for args in [("--help",), ("help",), ("version",), ("doctor",)]:
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        version = self.run_cli("version")
        self.assertIn("package version: 3.0.0-dev", version.stdout)
        self.assertIn("Latest stable release: v2.10.0", version.stdout)
        self.assertIn("Current milestone: v3.0.0", version.stdout)
        self.assertIn("Next milestone: v3.1.0", version.stdout)
        doctor = self.run_cli("doctor")
        self.assertIn("local/static", doctor.stdout)
        self.assertIn("Rule packs:", doctor.stdout)

    def test_validate_config_valid_and_dangerous(self) -> None:
        valid = self.run_cli("validate-config", "--config", "examples/arkheionx.config.example.json")
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump({"rpc_url": "http://localhost:8545"}, handle)
            dangerous_path = Path(handle.name)
        try:
            invalid = self.run_cli("validate-config", "--config", str(dangerous_path))
            self.assertEqual(invalid.returncode, 3)
            self.assertIn("Dangerous config key", invalid.stderr)
        finally:
            dangerous_path.unlink(missing_ok=True)

    def test_search_text_and_json(self) -> None:
        text_result = self.run_cli("search", "oracle stale price", "--limit", "2")
        self.assertEqual(text_result.returncode, 0, text_result.stdout + text_result.stderr)
        self.assertIn("oracle stale price", text_result.stdout.lower())
        json_result = self.run_cli("search", "oracle stale price", "--json", "--limit", "2")
        self.assertEqual(json_result.returncode, 0, json_result.stdout + json_result.stderr)
        payload = json.loads(json_result.stdout)
        self.assertEqual(payload["query"], "oracle stale price")
        self.assertTrue(payload["matches"])

    def test_cli_docs_exist(self) -> None:
        for path in [
            "docs/CLI_CANDIDATE.md",
            "docs/CLI_COMMANDS.md",
            "docs/CLI_MIGRATION_TO_V2.md",
        ]:
            text = (REPO_ROOT / path).read_text(encoding="utf-8")
            self.assertIn("CLI", text)
        commands = (REPO_ROOT / "docs/CLI_COMMANDS.md").read_text(encoding="utf-8")
        self.assertIn("validate-config", commands)
        self.assertIn("test-plan", commands)


if __name__ == "__main__":
    unittest.main()
