import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.reporting.builder import build_report, report_markdown

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = "examples/oracle-staking-fixture"
SCHEMA = json.loads((REPO_ROOT / "schemas" / "report-draft.schema.json").read_text(encoding="utf-8"))

_EVIDENCE = {
    "target": "src/Vault.sol:Vault.withdraw(uint256)",
    "target_id": "src/Vault.sol:Vault.withdraw(uint256)#L10-L20",
    "evidence_level": "EVIDENCE_READY",
    "status": "evidence_ready",
    "source_artifacts": {"proof_json": "p.json", "trace_json": "t.json", "raw_foundry_output": "", "generated_test": ""},
    "proof_summary": {"status": "tested_failed", "tests_run": 1, "passed": 0, "failed": 1, "skipped": 0, "foundry_command": "forge test --match-test x"},
    "trace_summary": {"summary_available": True, "reverts": ["revert: bad"], "assertion_failures": [], "call_sequence": ["Vault::withdraw()"], "logs": []},
    "impact_notes": {
        "candidate_impact": "incorrect accounting on exit (candidate)",
        "affected_components": ["src/Vault.sol:Vault.withdraw#L10-L20"],
        "assumptions": ["Local results reflect committed test code only."],
        "limitations": ["Not a formal audit. Not a severity guarantee."],
    },
}

_BANNED = ["critical confirmed", "guaranteed exploit", "drain funds", "submit immediately",
           "bounty guaranteed", "attack live protocol"]


class ReportTests(unittest.TestCase):
    def test_build_report_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = build_report(_EVIDENCE, Path("."), ArtifactWriter(Path(tmp)))
            self.assertTrue(Path(draft.md_path).exists())
            self.assertTrue(Path(draft.json_path).exists())
            self.assertEqual(draft.evidence_level, "EVIDENCE_READY")

    def test_report_schema_shape(self) -> None:
        draft = build_report(_EVIDENCE, Path("."), ArtifactWriter(Path(tempfile.mkdtemp())), write=False)
        for key in SCHEMA["required"]:
            self.assertIn(key, draft.payload)

    def test_report_does_not_overclaim_or_unsafe(self) -> None:
        md = report_markdown(build_report(_EVIDENCE, Path("."), ArtifactWriter(Path(tempfile.mkdtemp())), write=False).payload).lower()
        for phrase in _BANNED:
            self.assertNotIn(phrase, md)
        # Failing test must be framed as requiring human review, not proven exploit.
        self.assertIn("human review is required", md)
        self.assertIn("safety notice", md)
        self.assertIn("local", md)
        # Reproduction must be explicitly local-only (prohibitions stated, not instructions).
        self.assertIn("no live-chain, no broadcast, no private keys", md)
        # No affirmative live-chain instructions.
        for unsafe in ["--fork-url", "rpc_url", "deploy to mainnet", "broadcast the transaction"]:
            self.assertNotIn(unsafe, md)

    def test_passing_test_language(self) -> None:
        ev = dict(_EVIDENCE)
        ev["proof_summary"] = {**_EVIDENCE["proof_summary"], "passed": 1, "failed": 0, "status": "tested_passed"}
        md = report_markdown(build_report(ev, Path("."), ArtifactWriter(Path(tempfile.mkdtemp())), write=False).payload).lower()
        self.assertIn("does not prove absence of bugs", md)

    def test_cli_report_no_evidence_gives_next(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", "-m", "arkheionx.cli.main", "report", FIXTURE, "--target", "OracleRewardFixture.claimReward", "--artifacts-dir", tmp],
                cwd=REPO_ROOT, text=True, capture_output=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("No evidence package found", result.stdout)
        self.assertIn("--run", result.stdout)

    def test_cli_help_includes_evidence_and_report(self) -> None:
        result = subprocess.run(
            ["python3", "-m", "arkheionx.cli.main", "--help"],
            cwd=REPO_ROOT, text=True, capture_output=True,
        )
        self.assertIn("evidence", result.stdout)
        self.assertIn("report", result.stdout)


    def test_report_markdown_hardening(self) -> None:
        md = report_markdown(build_report(_EVIDENCE, Path("."), ArtifactWriter(Path(tempfile.mkdtemp())), write=False).payload)
        for section in ["## Review Status", "## What Is Proven", "## What Is Not Proven",
                        "## Required Human Checks", "## Safety Notice"]:
            self.assertIn(section, md)
        self.assertIn("NEEDS_HUMAN_REVIEW", md)
        lowered = md.lower()
        for banned in ["ready to submit", "guaranteed", "final severity:"]:
            self.assertNotIn(banned, lowered)

    def test_report_review_status_field(self) -> None:
        draft = build_report(_EVIDENCE, Path("."), ArtifactWriter(Path(tempfile.mkdtemp())), write=False)
        self.assertEqual(draft.payload["review_status"], "NEEDS_HUMAN_REVIEW")
        self.assertIn("exploitability", draft.payload["what_is_not_proven"])


if __name__ == "__main__":
    unittest.main()
