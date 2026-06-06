"""Tests for the `arkheionx local-validate` CLI command (v3.7, saved-output only)."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "local_validation" / "foundry"
ANSI = re.compile(r"\x1b\[")


def run_cli(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=cwd, text=True, capture_output=True, env=env,
    )


class _RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        for name in ("forge-test-json-basic.json", "forge-test-text-basic.txt",
                     "forge-test-json-mixed.json", "forge-test-text-mixed.txt"):
            shutil.copyfile(_FIXTURES / name, self.repo / name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _input(self, name: str) -> str:
        return str(self.repo / name)

    def _json(self, *args: str) -> tuple[dict, subprocess.CompletedProcess[str]]:
        result = run_cli("local-validate", str(self.repo), *args)
        return json.loads(result.stdout), result


class HelpAndArgTests(unittest.TestCase):
    def test_command_in_help(self) -> None:
        self.assertEqual(run_cli("help").returncode, 0)
        self.assertIn("local-validate", run_cli("help").stdout)

    def test_missing_input_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertNotEqual(run_cli("local-validate", tmp).returncode, 0)

    def test_missing_repo_is_error(self) -> None:
        self.assertNotEqual(run_cli("local-validate", "--input", "x.json").returncode, 0)


class InvalidInputTests(_RepoCase):
    def test_invalid_repo_exit_2(self) -> None:
        result = run_cli("local-validate", str(self.repo / "nope"), "--input", self._input("forge-test-json-basic.json"))
        self.assertEqual(result.returncode, 2)

    def test_invalid_input_exit_2(self) -> None:
        result = run_cli("local-validate", str(self.repo), "--input", self._input("missing.json"))
        self.assertEqual(result.returncode, 2)

    def test_foundry_json_on_text_exit_2(self) -> None:
        result = run_cli("local-validate", str(self.repo), "--input", self._input("forge-test-text-mixed.txt"),
                         "--format", "foundry-json")
        self.assertEqual(result.returncode, 2)

    def test_output_outside_repo_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            result = run_cli("local-validate", str(self.repo),
                             "--input", self._input("forge-test-json-basic.json"), "--output", outside)
            self.assertEqual(result.returncode, 2)


class NoWriteTests(_RepoCase):
    def setUp(self) -> None:
        super().setUp()
        self.data, self.result = self._json("--input", self._input("forge-test-json-basic.json"),
                                            "--no-write", "--json")

    def test_exit_zero(self) -> None:
        self.assertEqual(self.result.returncode, 0)

    def test_command_and_flags(self) -> None:
        self.assertEqual(self.data["command"], "local-validate")
        self.assertIs(self.data["no_write"], True)
        self.assertIs(self.data["written"], False)

    def test_counts(self) -> None:
        self.assertEqual(self.data["total_tests"], 2)
        self.assertEqual(self.data["passed_tests"], 2)
        self.assertEqual(self.data["validation_status"], "LOCAL_VALIDATION_PASSED")

    def test_no_output_directory_created(self) -> None:
        self.assertFalse((self.repo / ".arkheionx").exists())


class WriteTests(_RepoCase):
    def setUp(self) -> None:
        super().setUp()
        self.data, self.result = self._json("--input", self._input("forge-test-json-basic.json"), "--json")
        self.out = self.repo / ".arkheionx" / "out" / "local-validation"

    def test_exit_zero_and_written(self) -> None:
        self.assertEqual(self.result.returncode, 0)
        self.assertIs(self.data["written"], True)

    def test_layout(self) -> None:
        for rel in ("summary.json", "run.json", "artifacts-index.json", "checksums/SHA256SUMS"):
            self.assertTrue((self.out / rel).is_file(), rel)

    def test_output_root_repo_relative(self) -> None:
        self.assertEqual(self.data["output_root"], ".arkheionx/out/local-validation")
        self.assertGreater(self.data["written_file_count"], 0)

    def test_custom_output_inside_repo(self) -> None:
        data, result = self._json("--input", self._input("forge-test-json-basic.json"),
                                  "--output", "sub/lv", "--json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(data["output_root"], "sub/lv")
        self.assertTrue((self.repo / "sub" / "lv" / "summary.json").is_file())

    def test_repeated_write_deterministic(self) -> None:
        sums = (self.out / "checksums" / "SHA256SUMS").read_bytes()
        run_cli("local-validate", str(self.repo), "--input", self._input("forge-test-json-basic.json"), "--json")
        self.assertEqual((self.out / "checksums" / "SHA256SUMS").read_bytes(), sums)


class FormatTests(_RepoCase):
    def test_text_format(self) -> None:
        data, result = self._json("--input", self._input("forge-test-text-basic.txt"),
                                  "--format", "foundry-text", "--no-write", "--json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(data["input_format"], "foundry_text")
        self.assertEqual(data["total_tests"], 2)

    def test_mixed_json_counts(self) -> None:
        data, _ = self._json("--input", self._input("forge-test-json-mixed.json"), "--no-write", "--json")
        self.assertEqual((data["total_tests"], data["passed_tests"], data["failed_tests"],
                          data["skipped_tests"], data["errored_tests"]), (5, 2, 1, 1, 1))

    def test_mixed_text_counts_and_warnings(self) -> None:
        data, _ = self._json("--input", self._input("forge-test-text-mixed.txt"),
                             "--format", "foundry-text", "--no-write", "--json")
        self.assertEqual(data["total_tests"], 4)
        self.assertTrue(data["warnings"])


class JsonPurityAndSafetyTests(_RepoCase):
    def setUp(self) -> None:
        super().setUp()
        self.result = run_cli("local-validate", str(self.repo),
                              "--input", self._input("forge-test-json-mixed.json"), "--no-write", "--json")
        self.data = json.loads(self.result.stdout)

    def test_exactly_one_json_object_no_banner_no_ansi(self) -> None:
        self.assertEqual(self.result.stdout.strip()[0], "{")
        self.assertEqual(json.loads(self.result.stdout)["command"], "local-validate")
        self.assertNotRegex(self.result.stdout, ANSI)
        self.assertNotIn("ARKHEIONX", self.result.stdout)
        self.assertNotIn("Traceback", self.result.stdout + self.result.stderr)

    def test_safety_fields(self) -> None:
        self.assertIs(self.data["manual_review_required"], True)
        self.assertIs(self.data["ready_for_submission"], False)

    def test_no_overclaim_tokens(self) -> None:
        blob = self.result.stdout
        self.assertNotIn("HUMAN_REVIEWED", blob)
        self.assertNotIn('"ready_for_submission": true', blob)
        lower = blob.lower()
        for token in ("audit passed", "confirmed vulnerability", "final severity", "bounty eligibility"):
            self.assertNotIn(token, lower)

    def test_failed_test_not_confirmed_vuln(self) -> None:
        # mixed has a failing test; status is not a confirmed-vuln claim.
        self.assertGreaterEqual(self.data["failed_tests"], 1)
        self.assertIn(self.data["validation_status"], ("LOCAL_VALIDATION_ERROR", "LOCAL_VALIDATION_PARTIAL",
                                                        "LOCAL_VALIDATION_FAILED"))


class HumanOutputTests(_RepoCase):
    def test_human_output_safe(self) -> None:
        result = run_cli("local-validate", str(self.repo),
                         "--input", self._input("forge-test-json-basic.json"), "--no-write")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Manual review required: True", result.stdout)
        self.assertIn("Ready for submission: False", result.stdout)
        lower = result.stdout.lower()
        for token in ("audit passed", "confirmed vulnerability", "final severity", "bounty"):
            self.assertNotIn(token, lower)


if __name__ == "__main__":
    unittest.main()
