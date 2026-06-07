"""CLI tests for `arkheionx criticality-map` (v5)."""
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VAULT = REPO_ROOT / "examples" / "vault-strategy-oracle-fixture"
AUTH = REPO_ROOT / "examples" / "periphery-auth-fixture"
ANSI = re.compile(r"\x1b\[")


def run_cli(*args: str, color: str = "never"):
    import subprocess
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = color
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


def copy_fixture(tmp: str, src: Path) -> Path:
    repo = Path(tmp) / "repo"
    shutil.copytree(src, repo, ignore=shutil.ignore_patterns(".arkheionx", "out", "cache"))
    return repo


class CriticalityMapHelpTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("criticality-map", result.stdout)

    def test_command_help_lists_flags(self) -> None:
        result = run_cli("criticality-map", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--json", "--no-write"):
            self.assertIn(opt, result.stdout)


class CriticalityMapRunTests(unittest.TestCase):
    def test_runs_and_states_not_severity(self) -> None:
        result = run_cli("criticality-map", str(AUTH), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("CRITICALITY POTENTIAL MAP", result.stdout)
        self.assertIn("not severity", result.stdout.lower())
        self.assertIn("Human review required", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_json_valid_and_ranks_value_exit(self) -> None:
        result = run_cli("criticality-map", str(AUTH), "--json", "--no-write", color="always")
        self.assertNotRegex(result.stdout, ANSI)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["kind"], "criticality-map")
        for key in ("repository", "dimensions", "surfaces", "highest_blast_radius",
                    "criticality_vs_review_density", "safety"):
            self.assertIn(key, payload)
        by_target = {s["target"]: s for s in payload["surfaces"]}
        self.assertIn("LedgerCore.withdraw", by_target)
        self.assertEqual(by_target["LedgerCore.withdraw"]["criticality_potential"], "very-high")
        self.assertTrue(payload["highest_blast_radius"])

    def test_never_called_severity(self) -> None:
        payload = json.loads(run_cli("criticality-map", str(AUTH), "--json", "--no-write").stdout)
        blob = json.dumps(payload).lower()
        self.assertNotIn('"severity"', blob)
        self.assertNotIn("severity:", blob)
        self.assertIn("not severity", blob)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            out = repo / ".arkheionx" / "criticality-map"
            result = run_cli("criticality-map", str(repo), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertTrue((out / "criticality-map.md").is_file())
            self.assertTrue((out / "criticality-map.json").is_file())
            md = (out / "criticality-map.md").read_text()
            self.assertIn("# Arkheionx Criticality Potential Map", md)
            self.assertIn("## Criticality Dimensions", md)
            self.assertIn("## Surface Table", md)
            self.assertIn("## Safety Note", md)


if __name__ == "__main__":
    unittest.main()
