"""CLI tests for `arkheionx interaction-matrix` (v6)."""
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "blind-spot-fixture"
ANSI = re.compile(r"\x1b\[")


def run_cli(*args: str, color: str = "never"):
    import subprocess
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = color
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


def copy_fixture(tmp: str) -> Path:
    repo = Path(tmp) / "repo"
    shutil.copytree(FIXTURE, repo, ignore=shutil.ignore_patterns(".arkheionx", "out", "cache"))
    return repo


class InteractionMatrixHelpTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("interaction-matrix", result.stdout)

    def test_command_help_lists_flags(self) -> None:
        result = run_cli("interaction-matrix", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--json", "--no-write", "--only-unresolved"):
            self.assertIn(opt, result.stdout)


class InteractionMatrixRunTests(unittest.TestCase):
    def test_runs_on_fixture(self) -> None:
        result = run_cli("interaction-matrix", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("INTERACTION MATRIX", result.stdout)
        self.assertIn("Interaction priority is not severity", result.stdout)
        self.assertIn("Human review required", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_json_is_pure_and_valid(self) -> None:
        result = run_cli("interaction-matrix", str(FIXTURE), "--json", "--no-write", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotRegex(result.stdout, ANSI)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["kind"], "interaction-matrix")
        for key in ("matrix_summary", "interactions", "unresolved_interactions", "safety",
                    "human_review_required"):
            self.assertIn(key, payload)
        self.assertTrue(payload["interactions"])

    def test_detects_high_impact_interaction(self) -> None:
        payload = json.loads(run_cli("interaction-matrix", str(FIXTURE), "--json", "--no-write").stdout)
        self.assertGreaterEqual(payload["matrix_summary"]["high_impact_interactions"], 1)
        high = [ix for ix in payload["interactions"]
                if ix["interaction_priority"] in ("very-high", "high")]
        self.assertTrue(high)
        for ix in payload["interactions"]:
            self.assertTrue(ix["interaction_id"].startswith("IX-"))
            self.assertIn(ix["interaction_priority"], ("very-high", "high", "medium", "monitor"))

    def test_priority_not_severity(self) -> None:
        payload = run_cli("interaction-matrix", str(FIXTURE), "--json", "--no-write").stdout
        blob = payload.lower()
        self.assertNotIn('"severity"', blob)
        self.assertNotIn("severity:", blob)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            out = repo / ".arkheionx" / "interaction-matrix"
            result = run_cli("interaction-matrix", str(repo), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertTrue((out / "interaction-matrix.md").is_file())
            self.assertTrue((out / "interaction-matrix.json").is_file())
            md = (out / "interaction-matrix.md").read_text()
            self.assertIn("# Arkheionx Interaction Matrix", md)
            self.assertIn("## Matrix Summary", md)
            self.assertIn("Interaction priority is not", md)


if __name__ == "__main__":
    unittest.main()
