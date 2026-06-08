"""CLI tests for `arkheionx unresolved-map` (v6)."""
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


class UnresolvedMapHelpTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("unresolved-map", result.stdout)


class UnresolvedMapRunTests(unittest.TestCase):
    def test_runs_on_fixture(self) -> None:
        result = run_cli("unresolved-map", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("UNRESOLVED MAP", result.stdout)
        self.assertIn("Unresolved does not mean vulnerable", result.stdout)
        self.assertIn("Human review required", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_json_is_pure_and_valid(self) -> None:
        result = run_cli("unresolved-map", str(FIXTURE), "--json", "--no-write", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotRegex(result.stdout, ANSI)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["kind"], "unresolved-map")
        for key in ("schema_version", "package_version", "unresolved_surfaces",
                    "unresolved_interactions", "unclassified_surfaces", "final_checklist",
                    "safety", "human_review_required"):
            self.assertIn(key, payload)

    def test_lists_high_impact_unresolved_or_says_none(self) -> None:
        # The output must either list high-impact unresolved surfaces or say none.
        result = run_cli("unresolved-map", str(FIXTURE), "--no-write")
        payload = json.loads(run_cli("unresolved-map", str(FIXTURE), "--json", "--no-write").stdout)
        if payload["unresolved_surfaces"]:
            self.assertIn("unresolved", result.stdout.lower())
        else:
            self.assertIn("none surfaced", result.stdout.lower())

    def test_no_severity(self) -> None:
        blob = run_cli("unresolved-map", str(FIXTURE), "--json", "--no-write").stdout.lower()
        self.assertNotIn('"severity"', blob)
        self.assertNotIn("severity:", blob)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            out = repo / ".arkheionx" / "unresolved-map"
            result = run_cli("unresolved-map", str(repo), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertTrue((out / "unresolved-map.md").is_file())
            self.assertTrue((out / "unresolved-map.json").is_file())
            md = (out / "unresolved-map.md").read_text()
            self.assertIn("# Arkheionx Unresolved Map", md)
            self.assertIn("## Final Review Checklist", md)


if __name__ == "__main__":
    unittest.main()
