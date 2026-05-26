import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"
NEGATIVE_FIXTURE = REPO_ROOT / "examples" / "negative-evidence-fixture"


def load_scanner_module():
    spec = importlib.util.spec_from_file_location("pre_audit_scan", SCANNER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["pre_audit_scan"] = module
    spec.loader.exec_module(module)
    return module


def run_scan(root: Path, output_dir: Path) -> dict:
    json_path = output_dir / "report.json"
    subprocess.run(
        [
            "python3",
            str(SCANNER),
            "--root",
            str(root),
            "--protocol-type",
            "auto",
            "--output",
            str(output_dir / "report.md"),
            "--json-output",
            str(json_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(json_path.read_text(encoding="utf-8"))


class NegativeEvidenceTests(unittest.TestCase):
    def test_negative_context_helper_does_not_count_missing_coverage_as_positive(self) -> None:
        scanner = load_scanner_module()
        text = "Intentionally missing invariant tests and no stale oracle tests."
        self.assertTrue(scanner.is_negative_context(text, "invariant tests"))
        self.assertTrue(scanner.is_negative_context(text, "stale oracle tests"))
        self.assertFalse(scanner.has_positive_term(text, "invariant tests"))
        self.assertFalse(scanner.has_positive_term("without access-control negative tests", "access-control"))
        self.assertTrue(scanner.has_positive_term("function invariant_totalAssetsConserved() public {}", "invariant"))

    def test_negative_evidence_fixture_reports_missing_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_scan(NEGATIVE_FIXTURE, Path(tmp))

        terms = {item["term"].lower() for item in report["negative_evidence"]}
        self.assertIn("invariant tests", terms)
        self.assertIn("stale oracle tests", terms)
        self.assertIn("access-control negative tests", terms)
        self.assertIn("reward conservation tests", terms)
        self.assertIn("reentrancy/callback tests", terms)
        self.assertFalse(report["analysis_quality"]["invariant_tests"])
        self.assertGreater(report["analysis_quality"]["negative_evidence_count"], 0)
        self.assertTrue(
            any(finding.get("negative_evidence_count", 0) > 0 for finding in report["findings"])
        )

    def test_missing_test_comments_do_not_increase_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with_comments = tmp_path / "with-negative-comments"
            without_comments = tmp_path / "without-negative-comments"
            shutil.copytree(NEGATIVE_FIXTURE, with_comments)
            shutil.copytree(NEGATIVE_FIXTURE, without_comments)
            test_file = without_comments / "test" / "FakeGlobalVault.t.sol"
            text = test_file.read_text(encoding="utf-8")
            cleaned = "\n".join(
                line
                for line in text.splitlines()
                if "Intentionally missing" not in line
                and "invariant tests" not in line
                and "stale oracle tests" not in line
                and "access-control negative tests" not in line
                and "reward conservation tests" not in line
                and "reentrancy/callback tests" not in line
            )
            test_file.write_text(cleaned + "\n", encoding="utf-8")

            report_with = run_scan(with_comments, tmp_path / "with-report")
            report_without = run_scan(without_comments, tmp_path / "without-report")

        self.assertLessEqual(report_with["score"], report_without["score"])
        self.assertGreater(len(report_with["negative_evidence"]), 0)
        self.assertEqual(report_without["negative_evidence"], [])


if __name__ == "__main__":
    unittest.main()
