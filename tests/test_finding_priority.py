"""Finding prioritization tests: the report must lead with strong, well-evidenced
findings and must not let low-confidence keyword-only signals dominate.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"


def load_scanner_module():
    spec = importlib.util.spec_from_file_location("pre_audit_scan", SCANNER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["pre_audit_scan"] = module
    spec.loader.exec_module(module)
    return module


def run_scanner(root: str, protocol_type: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        json_path = Path(tmp) / "report.json"
        subprocess.run(
            [
                "python3", str(SCANNER), "--root", str(REPO_ROOT / root),
                "--protocol-type", protocol_type,
                "--output", str(Path(tmp) / "report.md"), "--json-output", str(json_path),
            ],
            cwd=REPO_ROOT, check=True, text=True, capture_output=True,
        )
        return json.loads(json_path.read_text(encoding="utf-8"))


_RANK = {"high": 0, "medium": 1, "low": 2}


class GapOrderingUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_scanner_module()

    def _gap(self, priority, confidence, fid, evidence=None):
        return self.module.ReadinessGap(
            severity=priority, title=fid, detail="d", recommendation="r", tags=["t"],
            priority=priority, id=fid, confidence=confidence, evidence=evidence or [],
        )

    def test_confidence_rank_orders_high_first(self) -> None:
        self.assertLess(
            self.module.gap_confidence_rank(self._gap("Low readiness gap", "high", "A")),
            self.module.gap_confidence_rank(self._gap("Low readiness gap", "low", "B")),
        )

    def test_strong_finding_sorts_before_weak_keyword_finding(self) -> None:
        weak = self._gap("Low readiness gap", "low", "ARK-ORC-002")
        strong = self._gap("High readiness gap", "high", "ARK-AMM-002", evidence=[{"file": "x"}])
        ordered = self.module.sort_gaps_for_review([weak, strong])
        self.assertEqual([g.id for g in ordered], ["ARK-AMM-002", "ARK-ORC-002"])

    def test_ordering_is_deterministic_with_id_tiebreak(self) -> None:
        gaps = [
            self._gap("Medium readiness gap", "medium", "ARK-B"),
            self._gap("Medium readiness gap", "medium", "ARK-A"),
        ]
        self.assertEqual([g.id for g in self.module.sort_gaps_for_review(gaps)], ["ARK-A", "ARK-B"])


class RenderedPriorityTests(unittest.TestCase):
    def test_report_leads_with_strongest_findings(self) -> None:
        report = run_scanner("examples/amm-fixture", "amm")
        findings = report["findings"]
        ranks = [
            (_RANK.get(str(f.get("priority", "")).split()[0].lower().replace("critical", "high"), 9),
             _RANK.get(str(f.get("confidence", "")).lower(), 9))
            for f in findings
        ]
        # Priority/confidence ranks must be non-decreasing: strongest first.
        self.assertEqual(ranks, sorted(ranks), "findings are not ordered strongest-first")
        # The strongest AMM findings must still be present and lead the list.
        ids = [f["id"] for f in findings]
        self.assertIn("ARK-AMM-002", ids[:3])
        self.assertIn("ARK-AMM-003", ids[:3])

    def test_low_confidence_keyword_findings_do_not_lead(self) -> None:
        report = run_scanner("examples/amm-fixture", "amm")
        ids = [f["id"] for f in report["findings"]]
        # Keyword-only oracle/testing gaps are conservative signals: kept, but
        # they must not appear above the high-confidence AMM findings.
        self.assertGreater(ids.index("ARK-ORC-002"), ids.index("ARK-AMM-002"))
        self.assertGreater(ids.index("ARK-TST-002"), ids.index("ARK-AMM-002"))

    def test_fix_first_items_are_actionable_and_confident(self) -> None:
        for root, ptype in (("examples/amm-fixture", "amm"), ("examples/lending-fixture", "lending")):
            report = run_scanner(root, ptype)
            fix_first = report.get("fix_first", [])
            self.assertTrue(fix_first)
            for item in fix_first:
                self.assertIn(item["confidence"], {"high", "medium"}, f"{root}:{item['id']} weak in Fix First")
                self.assertTrue(item.get("recommended_next_action"))

    def test_important_fixture_findings_remain_present(self) -> None:
        amm = {f["id"] for f in run_scanner("examples/amm-fixture", "amm")["findings"]}
        self.assertTrue({"ARK-AMM-002", "ARK-AMM-003", "ARK-ORC-001"} <= amm)
        lending = {f["id"] for f in run_scanner("examples/lending-fixture", "lending")["findings"]}
        self.assertTrue({"ARK-LEND-004", "ARK-ORC-001", "ARK-ACC-001"} <= lending)

    def test_finding_order_is_deterministic(self) -> None:
        a = [f["id"] for f in run_scanner("examples/amm-lending-hybrid-fixture", "auto")["findings"]]
        b = [f["id"] for f in run_scanner("examples/amm-lending-hybrid-fixture", "auto")["findings"]]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
