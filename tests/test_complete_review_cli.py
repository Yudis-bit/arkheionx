"""CLI tests for `arkheionx complete-review` (v6, headline)."""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "blind-spot-fixture"

REQUIRED_FILES = [
    "00-README.md", "01-review-map-summary.md", "02-blind-spots-summary.md",
    "03-criticality-summary.md", "04-counterfactuals-summary.md", "05-evidence-graph.md",
    "06-interaction-matrix.md", "07-unresolved-surfaces.md", "08-agent-input.md",
    "09-human-review-checklist.md", "10-case-study-template.md", "manifest.json",
]


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


class CompleteReviewHelpTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("complete-review", result.stdout)


class CompleteReviewRunTests(unittest.TestCase):
    def test_writes_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            out = repo / ".arkheionx" / "complete-review"
            result = run_cli("complete-review", str(repo), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            for name in REQUIRED_FILES:
                self.assertTrue((out / name).is_file(), name)

    def test_manifest_parses_and_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            out = repo / ".arkheionx" / "complete-review"
            run_cli("complete-review", str(repo), "--out", str(out))
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["kind"], "complete-review-manifest")
            self.assertEqual(manifest["command"], "complete-review")
            self.assertTrue(manifest["human_review_required"])
            self.assertIn("artifact_list", manifest)
            self.assertGreater(manifest["evidence_node_count"], 0)
            self.assertGreater(manifest["interaction_count"], 0)
            self.assertTrue(manifest["safety_flags"]["no_vulnerability_claims"])

    def test_json_manifest_to_stdout(self) -> None:
        manifest = json.loads(run_cli("complete-review", str(FIXTURE), "--json", "--no-write").stdout)
        self.assertEqual(manifest["kind"], "complete-review-manifest")

    def test_no_write_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            out = repo / ".arkheionx" / "complete-review"
            run_cli("complete-review", str(repo), "--out", str(out), "--no-write")
            self.assertFalse(out.exists())

    def test_no_unsafe_claims_in_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            out = repo / ".arkheionx" / "complete-review"
            run_cli("complete-review", str(repo), "--out", str(out))
            blob = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                             for p in out.iterdir() if p.is_file()).lower()
        for phrase in ("vulnerability confirmed", "exploit generated", "guaranteed bug",
                       "audit replacement", "proof of safety"):
            self.assertNotIn(phrase, blob)
        self.assertNotIn('"severity"', blob)


if __name__ == "__main__":
    unittest.main()
