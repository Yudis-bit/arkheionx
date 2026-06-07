"""Finding-explanation quality tests: every finding should read like reviewer
guidance (why it matters + what was seen + what to inspect next), and the report
must stay conservative and deterministic.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"


def run_scanner(root: str, protocol_type: str) -> tuple[str, dict]:
    with tempfile.TemporaryDirectory() as tmp:
        md_path = Path(tmp) / "report.md"
        json_path = Path(tmp) / "report.json"
        subprocess.run(
            [
                "python3", str(SCANNER), "--root", str(REPO_ROOT / root),
                "--protocol-type", protocol_type,
                "--output", str(md_path), "--json-output", str(json_path),
            ],
            cwd=REPO_ROOT, check=True, text=True, capture_output=True,
        )
        return md_path.read_text(encoding="utf-8"), json.loads(json_path.read_text(encoding="utf-8"))


FIXTURES = [
    ("examples/amm-fixture", "amm"),
    ("examples/lending-fixture", "lending"),
    ("examples/amm-lending-hybrid-fixture", "auto"),
]


class FindingExplanationTests(unittest.TestCase):
    def test_every_finding_explains_why_it_matters(self) -> None:
        # The review implication is the core of useful guidance; no finding,
        # including low-confidence keyword gaps, may omit it.
        for root, ptype in FIXTURES:
            _md, report = run_scanner(root, ptype)
            for finding in report["findings"]:
                why = str(finding.get("why_it_matters", "")).strip()
                self.assertTrue(why, f"{root}:{finding['id']} has no 'why_it_matters'")

    def test_every_finding_has_evidence_and_actionable_next_step(self) -> None:
        for root, ptype in FIXTURES:
            _md, report = run_scanner(root, ptype)
            for finding in report["findings"]:
                self.assertTrue(
                    str(finding.get("evidence_summary", "")).strip(),
                    f"{root}:{finding['id']} has no evidence_summary",
                )
                actionable = (
                    list(finding.get("suggested_tests", []) or [])
                    or list(finding.get("recommended_defensive_checks", []) or [])
                    or str(finding.get("recommendation", "")).strip()
                )
                self.assertTrue(actionable, f"{root}:{finding['id']} has no actionable next step")

    def test_top_finding_detail_reads_as_guidance(self) -> None:
        md, report = run_scanner("examples/amm-lending-hybrid-fixture", "auto")
        top_id = report["findings"][0]["id"]
        block = md.split(f"### {top_id}", 1)[1].split("\n### ", 1)[0]
        for section in ("What was detected:", "Why it matters:", "Suggested tests:"):
            self.assertIn(section, block, f"top finding {top_id} missing '{section}'")

    def test_report_keeps_conservative_boundary(self) -> None:
        md, _report = run_scanner("examples/amm-lending-hybrid-fixture", "auto")
        self.assertIn("not a formal audit", md.lower())
        self.assertIn("does not", md.lower())  # disclaimer / "What This Report Does Not Prove"

    def test_report_has_no_overclaiming_language(self) -> None:
        for root, ptype in FIXTURES:
            md, report = run_scanner(root, ptype)
            blob = (md + "\n" + json.dumps(report)).lower()
            for forbidden in (
                "confirmed vulnerability",
                "vulnerability confirmed",
                "audit passed",
                "guaranteed",
                "ai auditor",
            ):
                self.assertNotIn(forbidden, blob, f"{root} contains overclaiming phrase: {forbidden!r}")

    def test_explanations_are_deterministic(self) -> None:
        _m1, r1 = run_scanner("examples/amm-fixture", "amm")
        _m2, r2 = run_scanner("examples/amm-fixture", "amm")
        whys1 = {f["id"]: f.get("why_it_matters") for f in r1["findings"]}
        whys2 = {f["id"]: f.get("why_it_matters") for f in r2["findings"]}
        self.assertEqual(whys1, whys2)


if __name__ == "__main__":
    unittest.main()
