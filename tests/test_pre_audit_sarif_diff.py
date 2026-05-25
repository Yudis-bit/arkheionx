import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"


class PreAuditSarifDiffTests(unittest.TestCase):
    def run_vault_fixture(self, tmp_path: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
        command = [
            "python3",
            str(SCANNER),
            "--root",
            str(REPO_ROOT / "examples/vault-risk-fixture"),
            "--protocol-type",
            "vault",
            "--output",
            str(tmp_path / "report.md"),
            "--json-output",
            str(tmp_path / "report.json"),
        ]
        if extra_args:
            command.extend(extra_args)
        return subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)

    def test_sarif_generation_is_valid_and_defensive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sarif_path = tmp_path / "arkheionx.sarif.json"
            result = self.run_vault_fixture(tmp_path, ["--sarif-output", str(sarif_path)])
            self.assertEqual(result.returncode, 0, result.stderr)

            sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
            self.assertEqual(sarif["version"], "2.1.0")
            run = sarif["runs"][0]
            self.assertEqual(run["tool"]["driver"]["name"], "Arkheionx Pre-Audit Scanner")
            self.assertTrue(run["tool"]["driver"]["rules"])
            self.assertTrue(run["results"])
            levels = {result["level"] for result in run["results"]}
            self.assertTrue(levels <= {"note", "warning", "error"})
            first = run["results"][0]
            self.assertTrue(first["properties"]["not_a_vulnerability_confirmation"])
            self.assertTrue(first["properties"]["readiness_gap"])
            self.assertIn("pre-audit readiness gap", first["message"]["text"])

    def test_baseline_generation_contains_fingerprints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            baseline_path = tmp_path / "baseline.json"
            result = self.run_vault_fixture(tmp_path, ["--baseline-output", str(baseline_path)])
            self.assertEqual(result.returncode, 0, result.stderr)

            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            self.assertEqual(baseline["fingerprint_version"], "0.4.0")
            self.assertTrue(baseline["findings"])
            self.assertTrue(all(item["fingerprint"] for item in baseline["findings"]))

    def test_diff_mode_detects_unchanged_new_and_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            baseline_path = tmp_path / "baseline.json"
            initial = self.run_vault_fixture(tmp_path, ["--baseline-output", str(baseline_path)])
            self.assertEqual(initial.returncode, 0, initial.stderr)

            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            removed = baseline["findings"].pop(0)
            baseline["findings"].append(
                {
                    "id": "ARK-DOC-999",
                    "title": "Synthetic resolved documentation readiness gap",
                    "category": "documentation",
                    "priority": "Medium readiness gap",
                    "severity": "Medium readiness gap",
                    "confidence": "low",
                    "fingerprint": "synthetic-resolved-fingerprint",
                    "affected_files": ["README.md"],
                    "tags": ["test-fixture"],
                }
            )
            baseline_path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")

            diff_json = tmp_path / "diff.json"
            diff_report = tmp_path / "diff.md"
            summary = tmp_path / "summary.md"
            comment = tmp_path / "comment.md"
            checklist = tmp_path / "checklist.md"
            result = self.run_vault_fixture(
                tmp_path,
                [
                    "--compare-baseline",
                    str(baseline_path),
                    "--diff-output",
                    str(diff_report),
                    "--diff-json-output",
                    str(diff_json),
                    "--summary-output",
                    str(summary),
                    "--comment-output",
                    str(comment),
                    "--issue-checklist-output",
                    str(checklist),
                ],
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            diff = json.loads(diff_json.read_text(encoding="utf-8"))
            self.assertGreaterEqual(diff["counts"]["new"], 1)
            self.assertGreaterEqual(diff["counts"]["resolved"], 1)
            self.assertGreaterEqual(diff["counts"]["unchanged"], 1)
            self.assertIn(removed["id"], {item["id"] for item in diff["new"]})
            self.assertIn("Baseline Diff", diff_report.read_text(encoding="utf-8"))
            self.assertIn("Diff vs baseline", comment.read_text(encoding="utf-8"))
            self.assertIn("New Findings Since Baseline", checklist.read_text(encoding="utf-8"))

    def test_fail_thresholds_are_explicit_and_default_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            default = self.run_vault_fixture(tmp_path)
            self.assertEqual(default.returncode, 0, default.stderr)

            low_score = self.run_vault_fixture(tmp_path, ["--fail-score-below", "99"])
            self.assertEqual(low_score.returncode, 2)
            self.assertIn("pre-audit readiness gate", low_score.stderr)

            passing_score = self.run_vault_fixture(tmp_path, ["--fail-score-below", "10"])
            self.assertEqual(passing_score.returncode, 0, passing_score.stderr)

            high_gap = self.run_vault_fixture(tmp_path, ["--fail-on-unsuppressed-high"])
            self.assertEqual(high_gap.returncode, 2)


if __name__ == "__main__":
    unittest.main()
