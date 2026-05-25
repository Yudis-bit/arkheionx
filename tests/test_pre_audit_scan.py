import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"
BANNED_PHRASES = [
    "guaranteed " + "secure",
    "audit " + "replacement",
    "cheap " + "audit",
    "exploit " + "live",
    "d" + "rain helper",
    "profit " + "calculator",
    "bounty " + "guaranteed",
    "fully " + "verified database",
    "autonomous " + "exploit runner",
    "attack " + "live protocol",
    "weapon" + "ize",
    "exploit " + "any protocol",
]


class PreAuditScannerTests(unittest.TestCase):
    def run_scanner(self, root: str, protocol_type: str = "auto") -> tuple[str, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            md_path = Path(tmp) / "report.md"
            json_path = Path(tmp) / "report.json"
            subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / root),
                    "--protocol-type",
                    protocol_type,
                    "--output",
                    str(md_path),
                    "--json-output",
                    str(json_path),
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            self.assertTrue(md_path.exists())
            self.assertTrue(json_path.exists())
            return md_path.read_text(encoding="utf-8"), json.loads(json_path.read_text(encoding="utf-8"))

    def test_mini_vault_scan_generates_markdown_and_json(self) -> None:
        markdown, report = self.run_scanner("examples/mini-vault")

        self.assertIn("Arkheionx Pre-Audit Readiness Report", markdown)
        self.assertIn("not a formal audit", markdown)
        self.assertEqual(report["protocol_type"], "vault")
        self.assertIsInstance(report["score"], int)
        self.assertIn("historical_patterns", report)
        self.assertIn("vault_rule_pack", report)

    def test_vault_risk_fixture_surfaces_vault_rule_pack_gaps(self) -> None:
        markdown, report = self.run_scanner("examples/vault-risk-fixture", "vault")
        gap_titles = {gap["title"] for gap in report["readiness_gaps"]}
        pattern_names = {pattern["name"] for pattern in report["historical_patterns"]}

        self.assertIn("Vault Rule Pack Coverage", markdown)
        self.assertIn("Vault accounting without invariant tests", gap_titles)
        self.assertIn("ERC4626-like interface without preview function tests", gap_titles)
        self.assertIn("Shares/assets conversion without rounding tests", gap_titles)
        self.assertIn("Strategy accounting without gain/loss tests", gap_titles)
        self.assertIn("Withdrawal queue/cooldown without lifecycle tests", gap_titles)
        self.assertIn("Vault accounting invariant readiness gap", pattern_names)
        self.assertIn("vault_rule_pack", report)
        self.assertFalse(report["vault_rule_pack"]["coverage"]["invariant"])

    def test_product_outputs_do_not_include_banned_phrases(self) -> None:
        markdown, report = self.run_scanner("examples/vault-risk-fixture", "vault")
        combined = markdown.lower() + "\n" + json.dumps(report).lower()
        for phrase in BANNED_PHRASES:
            self.assertNotIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()
