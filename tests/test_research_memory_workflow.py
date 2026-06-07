"""End-to-end research-memory workflow tests (v4.1).

Exercises review-map -> agent-brief -> hypothesis-log -> case-study through the
CLI. Static runs exit 1 (heuristic review guidance); 2 is reserved for usage
failures. Asserts safety wording, artifact writing, status incorporation via
--from, and deterministic output.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "vault-strategy-oracle-fixture"
AUTH_FIXTURE = REPO_ROOT / "examples" / "periphery-auth-fixture"
ANSI = re.compile(r"\x1b\[")


def run_cli(*args: str, color: str = "never") -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = color
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


def copy_fixture(tmp: str, src: Path = FIXTURE) -> Path:
    repo = Path(tmp) / "repo"
    shutil.copytree(src, repo, ignore=shutil.ignore_patterns(".arkheionx", "out", "cache"))
    return repo


class ResearchHelpTests(unittest.TestCase):
    def test_help_lists_research_commands(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for cmd in ("agent-brief", "hypothesis-log", "case-study"):
            self.assertIn(cmd, result.stdout)

    def test_each_command_help_lists_flags(self) -> None:
        for cmd in ("agent-brief", "hypothesis-log", "case-study"):
            result = run_cli(cmd, "--help")
            self.assertEqual(result.returncode, 0, result.stderr)
            for opt in ("--out", "--json", "--no-write"):
                self.assertIn(opt, result.stdout, f"{cmd} {opt}")
        self.assertIn("--from", run_cli("case-study", "--help").stdout)


class AgentBriefWorkflowTests(unittest.TestCase):
    def test_human_output_is_safe_and_complete(self) -> None:
        result = run_cli("agent-brief", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        out = result.stdout
        self.assertIn("AGENT BRIEF", out)
        self.assertIn("Local/static review guidance only", out)
        self.assertIn("Hypotheses are review prompts, not confirmed bugs", out)
        self.assertIn("Human review required", out)
        self.assertIn("Inspect first", out)
        self.assertIn("Do not claim", out)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("Confirmed vulnerability", out)
        self.assertNotIn("guaranteed", out.lower())

    def test_json_is_pure_and_has_expected_shape(self) -> None:
        result = run_cli("agent-brief", str(FIXTURE), "--json", "--no-write", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotRegex(result.stdout, ANSI)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["kind"], "agent-brief")
        for key in ("repository", "review_priority", "value_movement", "authorization_surfaces",
                    "periphery_surfaces", "behavior_mismatch_surfaces", "coverage_ranking",
                    "hypotheses", "do_not_claim", "safety"):
            self.assertIn(key, payload)
        self.assertTrue(payload["hypotheses"])
        self.assertTrue(all(h["status"] == "open" for h in payload["hypotheses"]))

    def test_auth_fixture_surfaces_signature_and_merkle(self) -> None:
        result = run_cli("agent-brief", str(AUTH_FIXTURE), "--json", "--no-write")
        payload = json.loads(result.stdout)
        signals = {row["signal"] for row in payload["authorization_surfaces"]}
        self.assertTrue({"ecrecover", "MerkleProof"} & signals, signals)
        interactions = {tuple(r["interaction_type"]) for r in payload["periphery_surfaces"]}
        self.assertTrue(any("try-catch" in i for i in interactions), interactions)

    def test_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            result = run_cli("agent-brief", str(repo))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            research = repo / ".arkheionx" / "research"
            self.assertTrue((research / "agent-brief.md").is_file())
            self.assertTrue((research / "agent-brief.json").is_file())
            payload = json.loads((research / "agent-brief.json").read_text())
            self.assertEqual(payload["kind"], "agent-brief")

    def test_deterministic_ignoring_timestamp(self) -> None:
        first = json.loads(run_cli("agent-brief", str(FIXTURE), "--json", "--no-write").stdout)
        second = json.loads(run_cli("agent-brief", str(FIXTURE), "--json", "--no-write").stdout)
        first.pop("generated_at")
        second.pop("generated_at")
        self.assertEqual(first, second)


class HypothesisLogWorkflowTests(unittest.TestCase):
    def test_contains_hyp_ids_statuses_and_rejection_fields(self) -> None:
        result = run_cli("hypothesis-log", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("HYP-001", result.stdout)
        self.assertIn("Rejected hypotheses are useful evidence", result.stdout)
        self.assertIn("open", result.stdout)

    def test_json_template_has_empty_tracking_fields(self) -> None:
        payload = json.loads(run_cli("hypothesis-log", str(FIXTURE), "--json", "--no-write").stdout)
        self.assertEqual(payload["kind"], "hypothesis-log")
        self.assertIn("rejected_findings_are_evidence", payload["notes"])
        first = payload["hypotheses"][0]
        self.assertEqual(first["id"], "HYP-001")
        for field in ("test_command", "result", "rejection_reason", "confirmation_notes", "human_decision"):
            self.assertEqual(first[field], "")


class CaseStudyWorkflowTests(unittest.TestCase):
    def test_human_output_has_required_sections(self) -> None:
        result = run_cli("case-study", str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        out = result.stdout
        self.assertIn("CASE STUDY", out)
        self.assertIn("Not an audit", out)
        self.assertIn("Safety note", out)
        self.assertNotIn("Confirmed vulnerability", out)

    def test_markdown_artifact_has_rejected_and_safety_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            run_cli("case-study", str(repo))
            md = (repo / ".arkheionx" / "research" / "case-study.md").read_text()
            self.assertIn("## 10. Rejected hypotheses", md)
            self.assertIn("## 16. Safety note", md)
            self.assertIn("not an audit report", md)

    def test_from_incorporates_rejected_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            run_cli("hypothesis-log", str(repo))
            log_path = repo / ".arkheionx" / "research" / "hypotheses.json"
            data = json.loads(log_path.read_text())
            data["hypotheses"][0]["status"] = "rejected"
            data["hypotheses"][0]["rejection_reason"] = "invariant held under fuzzing"
            log_path.write_text(json.dumps(data, indent=2))
            result = run_cli("case-study", str(repo), "--from", str(repo / ".arkheionx" / "research"),
                             "--json", "--no-write")
            payload = json.loads(result.stdout)
            self.assertEqual([h["id"] for h in payload["rejected_hypotheses"]], ["HYP-001"])
            self.assertTrue(payload["what_held"])


class FullWorkflowTests(unittest.TestCase):
    def test_end_to_end_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_fixture(tmp)
            for cmd in ("review-map", "agent-brief", "hypothesis-log", "case-study"):
                result = run_cli(cmd, str(repo))
                self.assertIn(result.returncode, (0, 1), f"{cmd}: {result.stderr}")
                self.assertNotIn("Traceback", result.stderr, cmd)
            research = repo / ".arkheionx" / "research"
            for artifact in ("agent-brief.md", "agent-brief.json", "hypotheses.md",
                             "hypotheses.json", "case-study.md", "case-study.json"):
                self.assertTrue((research / artifact).is_file(), artifact)


if __name__ == "__main__":
    unittest.main()
