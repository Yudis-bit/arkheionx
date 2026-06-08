"""CLI tests for `arkheionx evidence-graph` (v6)."""
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


class EvidenceGraphHelpTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("evidence-graph", result.stdout)

    def test_command_help_lists_flags(self) -> None:
        result = run_cli("evidence-graph", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--json", "--no-write", "--only-unresolved"):
            self.assertIn(opt, result.stdout)


class EvidenceGraphRunTests(unittest.TestCase):
    def test_runs_on_fixture(self) -> None:
        result = run_cli("evidence-graph", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("EVIDENCE GRAPH", result.stdout)
        self.assertIn("Evidence state is not a vulnerability claim", result.stdout)
        self.assertIn("Human review required", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_json_is_pure_and_valid(self) -> None:
        result = run_cli("evidence-graph", str(FIXTURE), "--json", "--no-write", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotRegex(result.stdout, ANSI)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["kind"], "evidence-graph")
        for key in ("schema_version", "package_version", "command", "repo_summary",
                    "evidence_state_summary", "nodes", "unresolved_surfaces", "safety",
                    "human_review_required"):
            self.assertIn(key, payload)
        self.assertTrue(payload["nodes"])
        self.assertTrue(payload["safety"]["human_review_required"])

    def test_only_unresolved_filters_nodes(self) -> None:
        payload = json.loads(run_cli("evidence-graph", str(FIXTURE), "--json", "--no-write",
                                     "--only-unresolved").stdout)
        open_states = ("unresolved", "insufficient-evidence", "unclassified", "needs-human-review")
        for n in payload["nodes"]:
            self.assertIn(n["evidence_state"], open_states)

    def test_no_unsafe_claims_and_no_severity(self) -> None:
        payload = run_cli("evidence-graph", str(FIXTURE), "--json", "--no-write").stdout
        blob = payload.lower()
        for phrase in ("critical found", "high found", "vulnerability confirmed",
                       "exploit generated", "guaranteed", "audit replacement"):
            self.assertNotIn(phrase, blob)
        self.assertNotIn('"severity"', blob)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            out = repo / ".arkheionx" / "evidence-graph"
            result = run_cli("evidence-graph", str(repo), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertTrue((out / "evidence-graph.md").is_file())
            self.assertTrue((out / "evidence-graph.json").is_file())
            md = (out / "evidence-graph.md").read_text()
            self.assertIn("# Arkheionx Evidence Graph", md)
            self.assertIn("## Evidence State Summary", md)
            self.assertIn("## Evidence Nodes", md)


if __name__ == "__main__":
    unittest.main()
