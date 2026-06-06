import unittest
from dataclasses import dataclass, field

from arkheionx.reports.ux import fix_first_items, group_findings_by_confidence, group_findings_by_rule_family, rank_fix_first


@dataclass
class ToyFinding:
    id: str
    title: str
    priority: str
    confidence: str
    severity: str = ""
    category: str = ""
    affected_files: list[str] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    negative_evidence: list[dict] = field(default_factory=list)
    suggested_tests: list[str] = field(default_factory=list)
    recommendation: str = ""


class FixFirstTests(unittest.TestCase):
    def test_fix_first_prefers_high_confidence_high_priority(self) -> None:
        low = ToyFinding("ARK-TST-001", "Testing gap", "Low readiness gap", "low")
        high = ToyFinding(
            "ARK-AMM-002",
            "LP share accounting",
            "High readiness gap",
            "high",
            affected_files=["src/Pool.sol", "test/Pool.t.sol"],
            evidence=[{"file": "src/Pool.sol"}],
            suggested_tests=["LP mint/burn proportionality test"],
        )
        ranked = rank_fix_first([low, high], 2)
        self.assertEqual(ranked[0].id, "ARK-AMM-002")
        items = fix_first_items([low, high], 2)
        self.assertEqual(items[0]["rule_family"], "amm")
        self.assertIn("high-confidence", items[0]["why_fix_first"])
        self.assertIn("LP mint/burn", items[0]["recommended_next_action"])

    def test_grouping_helpers(self) -> None:
        findings = [
            ToyFinding("ARK-AMM-001", "AMM", "Medium readiness gap", "medium"),
            ToyFinding("ARK-AMM-002", "AMM", "High readiness gap", "high"),
            ToyFinding("ARK-LEND-001", "Lending", "High readiness gap", "high"),
        ]
        self.assertEqual(group_findings_by_rule_family(findings), {"amm": 2, "lending": 1})
        self.assertEqual(group_findings_by_confidence(findings), {"high": 2, "medium": 1})


if __name__ == "__main__":
    unittest.main()
