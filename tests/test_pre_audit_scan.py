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
    def run_scanner(
        self,
        root: str,
        protocol_type: str = "auto",
        extra_args: list[str] | None = None,
    ) -> tuple[str, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            md_path = Path(tmp) / "report.md"
            json_path = Path(tmp) / "report.json"
            command = [
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
            ]
            if extra_args:
                command.extend(extra_args)
            subprocess.run(
                command,
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
        self.assertIn("findings", report)

    def test_vault_risk_fixture_surfaces_vault_rule_pack_gaps(self) -> None:
        markdown, report = self.run_scanner("examples/vault-risk-fixture", "vault")
        gap_titles = {gap["title"] for gap in report["readiness_gaps"]}
        finding_ids = {gap["id"] for gap in report["findings"]}
        pattern_names = {pattern["name"] for pattern in report["historical_patterns"]}

        self.assertIn("Vault Rule Pack Coverage", markdown)
        self.assertIn("ARK-VLT-001", markdown)
        self.assertIn("Top Readiness Gaps", markdown)
        self.assertIn("Generated Issue Checklist", markdown)
        self.assertIn("Vault accounting without invariant tests", gap_titles)
        self.assertIn("ERC4626-like interface without preview function tests", gap_titles)
        self.assertIn("Shares/assets conversion without rounding tests", gap_titles)
        self.assertIn("Strategy accounting without gain/loss tests", gap_titles)
        self.assertIn("Withdrawal queue/cooldown without lifecycle tests", gap_titles)
        self.assertIn("ARK-VLT-001", finding_ids)
        self.assertIn("ARK-ORC-001", finding_ids)
        self.assertIn("Vault accounting invariant readiness gap", pattern_names)
        self.assertIn("vault_rule_pack", report)
        self.assertFalse(report["vault_rule_pack"]["coverage"]["invariant"])

    def test_evidence_summaries_are_well_formed(self) -> None:
        _markdown, report = self.run_scanner("examples/amm-fixture", "amm")
        findings = report["findings"]
        self.assertTrue(findings)
        for finding in findings:
            summary = str(finding.get("evidence_summary", ""))
            # Every active finding must carry a non-empty evidence summary.
            self.assertTrue(summary.strip(), f"{finding['id']} has an empty evidence_summary")
            # Regression guard: location-less evidence must not emit a dangling
            # ": <reason>" prefix with no subject.
            self.assertFalse(
                summary.startswith(":"),
                f"{finding['id']} evidence_summary has an empty location prefix: {summary!r}",
            )
        # The AMM fixture has reserve-based pricing without oracle test terms, so
        # oracle coverage-note findings are expected; their summaries must be
        # labelled the same way the human report labels them, not blank-prefixed.
        coverage_notes = [
            finding
            for finding in findings
            if "No semantic-lite oracle test coverage" in str(finding.get("evidence_summary", ""))
        ]
        self.assertTrue(coverage_notes, "expected oracle coverage-note findings in the AMM fixture")
        for finding in coverage_notes:
            summary = str(finding["evidence_summary"])
            self.assertTrue(
                summary.startswith("test/documentation coverage"),
                f"{finding['id']} coverage-note summary not labelled: {summary!r}",
            )
            signals = finding.get("detected_signals") or []
            if signals:
                # Location-less evidence with matched signals must name them so a
                # reviewer knows what actually triggered the finding and where to
                # look next, not only that test coverage was absent.
                self.assertIn(
                    "Matched signals:",
                    summary,
                    f"{finding['id']} omits matched signals: {summary!r}",
                )
                self.assertTrue(
                    any(signal in summary for signal in signals),
                    f"{finding['id']} names no detected signal: {summary!r}",
                )

    def test_product_outputs_do_not_include_banned_phrases(self) -> None:
        markdown, report = self.run_scanner("examples/vault-risk-fixture", "vault")
        combined = markdown.lower() + "\n" + json.dumps(report).lower()
        for phrase in BANNED_PHRASES:
            self.assertNotIn(phrase, combined)

    def test_v03_outputs_are_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            md_path = tmp_path / "report.md"
            json_path = tmp_path / "report.json"
            summary_path = tmp_path / "summary.md"
            comment_path = tmp_path / "comment.md"
            checklist_path = tmp_path / "checklist.md"
            subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/vault-risk-fixture"),
                    "--protocol-type",
                    "vault",
                    "--output",
                    str(md_path),
                    "--json-output",
                    str(json_path),
                    "--summary-output",
                    str(summary_path),
                    "--comment-output",
                    str(comment_path),
                    "--issue-checklist-output",
                    str(checklist_path),
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            report = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertIn("findings", report)
            self.assertIn("summary", report)
            self.assertTrue(report["findings"][0]["id"].startswith("ARK-"))
            self.assertIn("Score:", summary_path.read_text(encoding="utf-8"))
            self.assertIn("<!-- arkheionx-pre-audit-comment -->", comment_path.read_text(encoding="utf-8"))
            self.assertIn("- [ ]", checklist_path.read_text(encoding="utf-8"))

    def test_config_suppression_is_visible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_path = tmp_path / ".arkheionx.json"
            config_path.write_text(
                json.dumps(
                    {
                        "version": "0.3.0",
                        "suppress_findings": [
                            {
                                "id": "ARK-VLT-001",
                                "reason": "Accepted temporarily during prototype phase.",
                                "expires": "2026-12-31",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            md_path = tmp_path / "report.md"
            json_path = tmp_path / "report.json"
            subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/vault-risk-fixture"),
                    "--protocol-type",
                    "vault",
                    "--config",
                    str(config_path),
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
            report = json.loads(json_path.read_text(encoding="utf-8"))
            active_ids = {finding["id"] for finding in report["findings"]}
            suppressed_ids = {finding["id"] for finding in report["suppressed_findings"]}
            self.assertNotIn("ARK-VLT-001", active_ids)
            self.assertIn("ARK-VLT-001", suppressed_ids)
            self.assertIn("Suppressed Readiness Gaps", md_path.read_text(encoding="utf-8"))

    def test_invalid_config_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_path = tmp_path / ".arkheionx.json"
            config_path.write_text("{invalid", encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    str(SCANNER),
                    "--root",
                    str(REPO_ROOT / "examples/vault-risk-fixture"),
                    "--protocol-type",
                    "vault",
                    "--config",
                    str(config_path),
                    "--output",
                    str(tmp_path / "report.md"),
                    "--json-output",
                    str(tmp_path / "report.json"),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Could not parse config", result.stderr)

    def test_config_ignore_paths_are_respected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_path = tmp_path / ".arkheionx.json"
            config_path.write_text(
                json.dumps({"version": "0.3.0", "ignore_paths": ["src/", "test/"]}),
                encoding="utf-8",
            )
            _, report = self.run_scanner(
                "examples/vault-risk-fixture",
                "vault",
                ["--config", str(config_path)],
            )
            self.assertEqual(report["files_scanned"]["solidity_sources"], [])
            self.assertEqual(report["files_scanned"]["solidity_tests"], [])


if __name__ == "__main__":
    unittest.main()
