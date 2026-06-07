"""CLI tests for `arkheionx counterfactuals` (v5)."""
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


class CounterfactualsHelpTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("counterfactuals", result.stdout)

    def test_command_help_lists_flags(self) -> None:
        result = run_cli("counterfactuals", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--json", "--no-write"):
            self.assertIn(opt, result.stdout)


class CounterfactualsRunTests(unittest.TestCase):
    def test_runs_and_states_not_findings(self) -> None:
        result = run_cli("counterfactuals", str(AUTH), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("COUNTERFACTUAL RESEARCH PLAN", result.stdout)
        self.assertIn("not findings", result.stdout.lower())
        self.assertIn("Human review required", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_json_valid_and_has_assumption_negation(self) -> None:
        result = run_cli("counterfactuals", str(AUTH), "--json", "--no-write", color="always")
        self.assertNotRegex(result.stdout, ANSI)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["kind"], "counterfactuals")
        for key in ("repository", "counterfactuals", "counterfactual_matrix", "assumptions", "safety"):
            self.assertIn(key, payload)
        self.assertTrue(payload["counterfactuals"])
        ids = [cf["id"] for cf in payload["counterfactuals"]]
        self.assertEqual(ids, sorted(ids))
        for cf in payload["counterfactuals"]:
            self.assertTrue(cf["id"].startswith("CF-"))
            for field in ("assumption", "what_if_false", "local_test_direction",
                          "evidence_needed", "stop_condition", "do_not_claim"):
                self.assertTrue(cf[field])
            self.assertEqual(cf["status"], "open")
        topics = {cf["topic"] for cf in payload["counterfactuals"]}
        self.assertTrue({"merkle-binds", "signature-binds"} & topics, topics)

    def test_oracle_counterfactual_on_vault(self) -> None:
        payload = json.loads(run_cli("counterfactuals", str(VAULT), "--json", "--no-write").stdout)
        topics = {cf["topic"] for cf in payload["counterfactuals"]}
        self.assertIn("oracle-fresh", topics, topics)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            out = repo / ".arkheionx" / "counterfactuals"
            result = run_cli("counterfactuals", str(repo), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertTrue((out / "counterfactuals.md").is_file())
            self.assertTrue((out / "counterfactuals.json").is_file())
            md = (out / "counterfactuals.md").read_text()
            self.assertIn("# Arkheionx Counterfactual Research Plan", md)
            self.assertIn("## Counterfactual Matrix", md)
            self.assertIn("What if this is false?", md)


if __name__ == "__main__":
    unittest.main()
