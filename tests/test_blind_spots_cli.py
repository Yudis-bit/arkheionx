"""CLI tests for `arkheionx blind-spots` (v5)."""
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


class BlindSpotsHelpTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blind-spots", result.stdout)

    def test_command_help_lists_flags(self) -> None:
        result = run_cli("blind-spots", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--json", "--no-write", "--limit"):
            self.assertIn(opt, result.stdout)


class BlindSpotsRunTests(unittest.TestCase):
    def test_runs_on_vault_fixture(self) -> None:
        result = run_cli("blind-spots", str(VAULT), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("BLIND SPOT MAP", result.stdout)
        self.assertIn("Criticality potential is not severity", result.stdout)
        self.assertIn("Human review required", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_runs_on_periphery_auth_fixture(self) -> None:
        result = run_cli("blind-spots", str(AUTH), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("blind spot candidates", result.stdout.lower())

    def test_json_is_pure_and_valid(self) -> None:
        result = run_cli("blind-spots", str(AUTH), "--json", "--no-write", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotRegex(result.stdout, ANSI)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["kind"], "blind-spots")
        for key in ("repository", "candidates", "scoring", "unknown_surfaces",
                    "notable_non_blind_spots", "counterfactuals", "safety"):
            self.assertIn(key, payload)
        self.assertTrue(payload["candidates"])
        for c in payload["candidates"]:
            self.assertTrue(c["id"].startswith("BSP-"))
            self.assertIn(c["criticality_potential"],
                          ("very-high", "high", "medium", "low", "unknown"))
        self.assertTrue(payload["safety"]["human_review_required"])

    def test_score_not_called_severity(self) -> None:
        payload = json.loads(run_cli("blind-spots", str(AUTH), "--json", "--no-write").stdout)
        blob = json.dumps(payload).lower()
        self.assertNotIn('"severity"', blob)
        self.assertNotIn("severity:", blob)

    def test_no_unsafe_claims(self) -> None:
        out = run_cli("blind-spots", str(AUTH), "--no-write").stdout.lower()
        for phrase in ("critical found", "high found", "vulnerability confirmed",
                       "exploit generated", "guaranteed", "audit replacement"):
            self.assertNotIn(phrase, out)

    def test_out_writes_md_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            out = repo / ".arkheionx" / "blind-spots"
            result = run_cli("blind-spots", str(repo), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertTrue((out / "blind-spots.md").is_file())
            self.assertTrue((out / "blind-spots.json").is_file())
            payload = json.loads((out / "blind-spots.json").read_text())
            self.assertEqual(payload["kind"], "blind-spots")
            md = (out / "blind-spots.md").read_text()
            self.assertIn("# Arkheionx Blind Spot Map", md)
            self.assertIn("## Boundary", md)
            self.assertIn("## Top Blind Spot Candidates", md)


if __name__ == "__main__":
    unittest.main()
