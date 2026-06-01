"""Protocol Review Map CLI tests (subprocess; no network, no Foundry)."""
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "arkheionx" / "demo" / "fixtures" / "oracle-staking"
ANSI = re.compile(r"\x1b\[")


def run_cli(*args: str, color: str = "never") -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = color
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


class ReviewMapCliTests(unittest.TestCase):
    def test_help_lists_review_map(self) -> None:
        result = run_cli("--help")
        self.assertIn("review-map", result.stdout)

    def test_review_map_help(self) -> None:
        result = run_cli("review-map", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--top", "--json", "--no-write", "--include-low-confidence", "--target"):
            self.assertIn(opt, result.stdout)

    def test_nonexistent_path_clean_error(self) -> None:
        result = run_cli("review-map", "no/such/dir")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a directory", result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_no_solidity_files_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("review-map", tmp)
        self.assertEqual(result.returncode, 2)
        self.assertIn("no Solidity files", result.stdout)
        self.assertIn("demo --copy", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_top_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("review-map", str(FIXTURE), "--top", "0", "--out", tmp)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--top", result.stdout)

    def test_writes_artifacts_to_out(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("review-map", str(FIXTURE), "--out", tmp)
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertIn("ARKHEIONX REVIEW MAP", result.stdout)
            self.assertTrue((Path(tmp) / "review-map.json").is_file())
            self.assertTrue((Path(tmp) / "review-map.md").is_file())

    def test_json_is_valid_and_only_json(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--json", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        payload = json.loads(result.stdout)  # raises if not pure JSON
        self.assertIn("schema_version", payload)
        self.assertIn("generated_at", payload)
        self.assertNotRegex(result.stdout, ANSI)

    def test_no_write_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            copy = run_cli("demo", "--copy", "lending-vault", str(repo))
            self.assertEqual(copy.returncode, 0, copy.stderr)
            result = run_cli("review-map", str(repo), "--no-write")
            self.assertIn(result.returncode, (0, 1))
            self.assertFalse((repo / ".arkheionx" / "out" / "review-map").exists())

    def test_human_output_color_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plain = run_cli("review-map", str(FIXTURE), "--no-write", color="never")
            self.assertNotRegex(plain.stdout, ANSI)
            forced = run_cli("review-map", str(FIXTURE), "--no-write", color="always")
            self.assertRegex(forced.stdout, ANSI)  # color utility forces ANSI

    def test_target_filter_and_bad_target(self) -> None:
        ok = run_cli("review-map", str(FIXTURE), "--target", "OracleRewardFixture.claimReward", "--no-write")
        self.assertIn(ok.returncode, (0, 1))
        bad = run_cli("review-map", str(FIXTURE), "--target", "Nope.nope", "--no-write")
        self.assertEqual(bad.returncode, 2)
        self.assertIn("could not resolve target", bad.stdout)
        self.assertNotIn("Traceback", bad.stderr)


class ReviewMapDemoIntegrationTests(unittest.TestCase):
    def test_review_map_on_each_demo(self) -> None:
        for demo in ("oracle-staking", "amm-swap", "lending-vault"):
            with self.subTest(demo=demo), tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp) / "demo"
                out = Path(tmp) / "out"
                self.assertEqual(run_cli("demo", "--copy", demo, str(repo)).returncode, 0)
                result = run_cli("review-map", str(repo), "--out", str(out))
                self.assertIn(result.returncode, (0, 1), result.stderr)
                data = json.loads((out / "review-map.json").read_text(encoding="utf-8"))
                self.assertGreater(data["summary"]["functions_mapped"], 0)
                self.assertGreater(data["summary"]["value_paths"], 0)


if __name__ == "__main__":
    unittest.main()
