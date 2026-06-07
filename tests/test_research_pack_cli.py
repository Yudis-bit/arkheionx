"""CLI tests for `arkheionx research-pack` (v5, headline)."""
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

EXPECTED_FILES = (
    "00-README.md", "01-review-map-summary.md", "02-blind-spots.md", "03-criticality-map.md",
    "04-counterfactuals.md", "05-agent-brief.md", "06-hypotheses.md", "07-evidence-log.md",
    "08-do-not-claim.md", "09-case-study-template.md", "manifest.json",
)
# These vendor names must never appear in a generated pack.
VENDORS = ("claude", "codex", "gemini", "kiro", "openai", "anthropic", "google", "copilot")


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


class ResearchPackHelpTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("research-pack", result.stdout)

    def test_command_help_lists_flags(self) -> None:
        result = run_cli("research-pack", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--json", "--no-write"):
            self.assertIn(opt, result.stdout)


class ResearchPackWriteTests(unittest.TestCase):
    def test_writes_all_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            out = repo / ".arkheionx" / "research-pack"
            result = run_cli("research-pack", str(repo), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            for name in EXPECTED_FILES:
                self.assertTrue((out / name).is_file(), f"missing {name}")

    def test_writes_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            result = run_cli("research-pack", str(repo))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            default_out = repo / ".arkheionx" / "research-pack"
            self.assertTrue((default_out / "manifest.json").is_file())
            self.assertTrue((default_out / "02-blind-spots.md").is_file())

    def test_manifest_parses_and_is_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            out = repo / ".arkheionx" / "research-pack"
            run_cli("research-pack", str(repo), "--out", str(out))
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["kind"], "research-pack-manifest")
            self.assertIn("package_version", manifest)
            self.assertIn("commands_represented", manifest)
            for cmd in ("review-map", "blind-spots", "criticality-map", "counterfactuals"):
                self.assertIn(cmd, manifest["commands_represented"])
            for name in EXPECTED_FILES:
                self.assertIn(name, manifest["artifacts"])
            self.assertTrue(manifest["safety"]["human_review_required"])
            self.assertTrue(manifest["safety"]["vendor_agnostic"])

    def test_no_vendor_names_in_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            out = repo / ".arkheionx" / "research-pack"
            run_cli("research-pack", str(repo), "--out", str(out))
            for path in out.iterdir():
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
                for vendor in VENDORS:
                    self.assertNotIn(vendor, text, f"{path.name} mentions vendor {vendor!r}")

    def test_no_unsafe_claims_in_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            out = repo / ".arkheionx" / "research-pack"
            run_cli("research-pack", str(repo), "--out", str(out))
            for path in out.iterdir():
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
                for phrase in ("critical found", "high found", "vulnerability confirmed",
                               "exploit generated", "guaranteed", "audit replacement"):
                    self.assertNotIn(phrase, text, f"{path.name}: {phrase}")

    def test_do_not_claim_and_evidence_log_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            out = repo / ".arkheionx" / "research-pack"
            run_cli("research-pack", str(repo), "--out", str(out))
            dnc = (out / "08-do-not-claim.md").read_text()
            self.assertIn("Do not submit blind spot output as a finding", dnc)
            self.assertIn("Do not submit criticality potential as severity", dnc)
            log = (out / "07-evidence-log.md").read_text()
            for field in ("Hypothesis ID", "Test file", "Command run", "Result",
                          "Evidence summary", "Rejection reason", "Confirmation notes", "Human decision"):
                self.assertIn(field, log)
            readme = (out / "00-README.md").read_text()
            self.assertIn("Safety boundaries", readme)
            self.assertIn("Human review is required", readme)

    def test_no_write_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp, AUTH)
            out = repo / ".arkheionx" / "research-pack"
            result = run_cli("research-pack", str(repo), "--out", str(out), "--no-write")
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertFalse(out.exists(), "no-write must not create the pack directory")

    def test_json_manifest_to_stdout(self) -> None:
        result = run_cli("research-pack", str(AUTH), "--json", "--no-write", color="always")
        self.assertNotRegex(result.stdout, ANSI)
        manifest = json.loads(result.stdout)
        self.assertEqual(manifest["kind"], "research-pack-manifest")


if __name__ == "__main__":
    unittest.main()
