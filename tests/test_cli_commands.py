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
        self.assertIn("package version: 7.5.0", version.stdout)
        self.assertIn("Latest stable release: v7.5.0", version.stdout)
        self.assertIn("Current milestone: v7.5.0", version.stdout)
        self.assertIn("Next milestone: v7.6.0", version.stdout)
        doctor = self.run_cli("doctor")
        self.assertIn("LOCAL / STATIC", doctor.stdout)
        self.assertIn("Safety", doctor.stdout)

    def test_help_reads_as_guided_first_run_entrypoint(self) -> None:
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = result.stdout
        for name in ("version", "doctor", "open", "review-map"):
            self.assertIn(name, out)
        # A guided first-run section + honest safety boundary, not only an option dump.
        self.assertIn("First run", out)
        self.assertIn("arkheionx doctor", out)
        self.assertIn("local/static", out)

    def test_version_includes_package_version_and_next_step(self) -> None:
        result = self.run_cli("version")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("package version: 7.5.0", result.stdout)
        self.assertIn("Next", result.stdout)
        self.assertIn("arkheionx doctor", result.stdout)

    def test_doctor_shows_status_sections_and_safety_boundary(self) -> None:
        result = self.run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = result.stdout
        self.assertIn("ArkheionX Doctor", out)
        for section in ("Environment", "Project", "Safety", "Next"):
            self.assertIn(section, out)
        # Safety is structured rows, not a paragraph, and stays local-only.
        self.assertIn("LOCAL / STATIC", out)
        for row in ("RPC calls", "Live-chain actions", "Private keys"):
            self.assertIn(row, out)

    def test_doctor_install_view_is_useful_and_exits_zero(self) -> None:
        result = self.run_cli("doctor", "--install")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = result.stdout
        for marker in ("Install", "Package version", "PATH", "LOCAL / STATIC"):
            self.assertIn(marker, out)

    def _assert_clean_user_error(self, result: subprocess.CompletedProcess[str]) -> str:
        combined = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, combined)  # nonzero preserved
        self.assertNotIn("Traceback", combined)  # no raw Python traceback
        self.assertIn("ArkheionX error:", combined)
        self.assertIn("Next", combined)  # actionable guidance
        return combined

    def test_review_map_missing_path_is_clean_error(self) -> None:
        result = self.run_cli("review-map", "/path/that/does/not/exist")
        self._assert_clean_user_error(result)

    def test_scan_missing_path_is_clean_error(self) -> None:
        result = self.run_cli("scan", "/path/that/does/not/exist")
        self._assert_clean_user_error(result)

    def test_test_plan_missing_report_is_clean_error(self) -> None:
        result = self.run_cli("test-plan", "--report", "/path/that/does/not/exist")
        combined = self._assert_clean_user_error(result)
        self.assertIn("report JSON not found", combined)

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
