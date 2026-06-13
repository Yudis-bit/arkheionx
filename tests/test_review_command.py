"""CLI tests for the primary `arkheionx review` command (v8)."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "fixed_credit_market_toy"
SCOPE = FIXTURE / "scope.md"

CORE_FILES = [
    "00-run-context.md", "01-scope-map.md", "02-value-flow-map.md", "03-interaction-map.md",
    "04-assumptions.md", "05-review-lanes.md", "06-evidence-tasks.md", "07-evidence-rubric.md",
    "08-report-filter.md", "09-agent-input.md", "review.json", "manifest.json",
]
LENS_FILES = [
    "10-protocol-model.md", "11-behavior-promises.md", "12-economic-invariants.md",
    "13-temporal-windows.md", "14-lens-review-lanes.md", "15-lens-evidence-tasks.md",
]


def run_cli(*args: str):
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class ReviewCommandTests(unittest.TestCase):
    def test_listed_in_help(self) -> None:
        out = run_cli("--help").stdout
        self.assertIn("review", out)
        self.assertIn("review", run_cli("review", "--help").stdout)

    def test_generates_core_pack_without_lens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review"
            result = run_cli("review", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            for name in CORE_FILES:
                self.assertTrue((out / name).is_file(), name)
            # No lens artifacts without --lens.
            for name in LENS_FILES:
                self.assertFalse((out / name).exists(), name)

    def test_generates_lens_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review"
            result = run_cli("review", str(FIXTURE), "--scope-file", str(SCOPE),
                             "--lens", "fixed-credit-market", "--out", str(out))
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            for name in CORE_FILES + LENS_FILES:
                self.assertTrue((out / name).is_file(), name)

    def test_manifest_and_review_json_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review"
            run_cli("review", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["artifact_type"], "review-pack-manifest")
            self.assertEqual(manifest["command"], "review")
            self.assertTrue(manifest["human_review_required"])
            self.assertTrue(manifest["arkheionx_version"])
            self.assertEqual(manifest["artifact_count"], len(CORE_FILES))
            review = json.loads((out / "review.json").read_text())
            self.assertEqual(review["artifact_type"], "review-pack")
            for flag in ("no_rpc", "no_live_chain", "no_auto_submit",
                         "no_vulnerability_claims", "no_severity_claims"):
                self.assertTrue(review["safety_flags"][flag])

    def test_agent_input_has_safety_and_kill_conditions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review"
            run_cli("review", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            agent = (out / "09-agent-input.md").read_text(encoding="utf-8")
            low = agent.lower()
            self.assertIn("human review required", low)
            self.assertIn("kill condition", low)
            self.assertIn("do not submit reports", low)
            self.assertIn("do not claim a finding without", low)
            self.assertIn("review lane is not a vulnerability", low)

    def test_evidence_tasks_have_kill_conditions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review"
            run_cli("review", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out))
            tasks_md = (out / "06-evidence-tasks.md").read_text(encoding="utf-8").lower()
            self.assertIn("kill condition", tasks_md)
            review = json.loads((out / "review.json").read_text())
            for t in review["data"]["evidence_tasks"]["tasks"]:
                self.assertTrue(t.get("kill_condition"))

    def test_pack_has_no_target_specific_wording(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review"
            run_cli("review", str(FIXTURE), "--scope-file", str(SCOPE),
                    "--lens", "fixed-credit-market", "--out", str(out))
            blob = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                             for p in out.iterdir() if p.is_file()).lower()
            for term in ("morpho", "midnight"):
                self.assertNotIn(term, blob, f"target-specific term in review pack: {term}")

    def test_no_write_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review"
            run_cli("review", str(FIXTURE), "--scope-file", str(SCOPE), "--out", str(out), "--no-write")
            self.assertFalse(out.exists())

    def test_json_flag_prints_manifest(self) -> None:
        result = run_cli("review", str(FIXTURE), "--scope-file", str(SCOPE), "--no-write", "--json")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["artifact_type"], "review-pack-manifest")


if __name__ == "__main__":
    unittest.main()
