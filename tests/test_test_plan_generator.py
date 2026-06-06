import json
import subprocess
import unittest
from pathlib import Path

from arkheionx.generators import test_plan as tp_gen


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


class TestPlanGeneratorTests(unittest.TestCase):
    def test_finding_test_plan_map_parses_and_covers_rule_families(self) -> None:
        payload = load_json("metadata/finding_test_plan_map.json")
        self.assertEqual(payload["schema_version"], "1.5.0")
        findings = payload["findings"]
        for finding_id in [
            "ARK-VLT-001",
            "ARK-ORC-001",
            "ARK-ACC-001",
            "ARK-UPG-001",
            "ARK-REENT-001",
            "ARK-RWD-001",
            "ARK-TST-002",
            "ARK-AMM-001",
            "ARK-LEND-001",
        ]:
            self.assertIn(finding_id, findings)
            self.assertTrue(findings[finding_id]["suggested_tests"])
            self.assertTrue(findings[finding_id]["invariant_candidates"])
            self.assertTrue(findings[finding_id]["foundry_skeleton_functions"])

    def test_generate_test_plan_check_passes(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/generate_test_plan.py", "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_committed_test_plan_outputs_exist_and_parse(self) -> None:
        for path in [
            "examples/reports/amm-fixture-test-plan.md",
            "examples/reports/amm-fixture-test-plan.json",
            "examples/reports/lending-fixture-test-plan.md",
            "examples/reports/lending-fixture-test-plan.json",
            "examples/reports/amm-lending-hybrid-fixture-test-plan.md",
            "examples/reports/amm-lending-hybrid-fixture-test-plan.json",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)
        for path in [
            "examples/reports/amm-fixture-test-plan.json",
            "examples/reports/lending-fixture-test-plan.json",
            "examples/reports/amm-lending-hybrid-fixture-test-plan.json",
        ]:
            data = load_json(path)
            self.assertEqual(data["tool"], "Arkheionx Test Plan Generator")
            self.assertEqual(data["version"], "2.0.1")
            self.assertIn("source_report", data)
            self.assertTrue(data["suggested_tests"])
            self.assertTrue(data["invariant_candidates"])
            self.assertTrue(data["manual_review_required"])

    def test_markdown_test_plan_has_safety_language(self) -> None:
        text = (REPO_ROOT / "examples/reports/amm-fixture-test-plan.md").read_text(encoding="utf-8").lower()
        self.assertIn("not formal verification", text)
        self.assertIn("not proof of safety", text)
        self.assertIn("human review", text)

    def test_scanner_findings_include_test_plan_fields(self) -> None:
        report = load_json("examples/reports/amm-fixture-pre-audit-report.json")
        amm_findings = [item for item in report["findings"] if item["id"].startswith("ARK-AMM-")]
        self.assertTrue(amm_findings)
        self.assertTrue(any(item.get("invariant_candidates") for item in amm_findings))
        self.assertTrue(all("test_plan" in item for item in amm_findings))
        plan = load_json("examples/reports/amm-fixture-issue-plan.json")
        issue = next(item for item in plan["issues"] if item["finding_id"].startswith("ARK-AMM-"))
        self.assertIn("invariant_candidates", issue)
        self.assertTrue(issue["suggested_tests"])

    def test_evidence_references_are_clean_and_signal_specific(self) -> None:
        md = (REPO_ROOT / "examples/reports/amm-fixture-test-plan.md").read_text(encoding="utf-8")
        # Regression guard: no malformed location-less evidence reference.
        self.assertNotIn("Source evidence summary: :", md)
        for line in md.splitlines():
            if line.startswith("- Source evidence summary:"):
                value = line.split(":", 1)[1].strip()
                self.assertTrue(value, f"empty evidence summary: {line!r}")
                self.assertFalse(value.startswith(":"), f"malformed evidence reference: {line!r}")
        # Findings with detected signals must name them so the plan is specific.
        data = load_json("examples/reports/amm-fixture-test-plan.json")
        signal_findings = [f for f in data["findings"] if f.get("matched_signals")]
        self.assertTrue(signal_findings, "expected at least one finding with matched signals")
        for finding in signal_findings:
            self.assertTrue(all(isinstance(s, str) and s for s in finding["matched_signals"]))
        self.assertIn("Matched signals:", md)
        # The oracle coverage finding connects to the reserve-pricing signal.
        orc = next(f for f in data["findings"] if f["finding_id"] == "ARK-ORC-001")
        self.assertIn("getReserves", orc["matched_signals"])
        # Conservative wording preserved; no confirmed-vulnerability claims.
        low = md.lower()
        for forbidden in (
            "vulnerability confirmed",
            "confirmed vulnerability",
            "exploit confirmed",
            "guaranteed secure",
        ):
            self.assertNotIn(forbidden, low)


class CommittedTestPlanHygieneTests(unittest.TestCase):
    """Guard every committed test-plan against malformed evidence punctuation."""

    def test_no_malformed_evidence_summary_punctuation(self) -> None:
        plans = sorted((REPO_ROOT / "examples" / "reports").glob("*test-plan*.md"))
        self.assertTrue(plans, "expected committed test-plan markdown files")
        for path in plans:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(
                "Source evidence summary: :",
                text,
                f"{path.name} has a dangling-colon evidence summary",
            )
            for line in text.splitlines():
                if line.startswith("- Source evidence summary:"):
                    value = line.split(":", 1)[1].strip()
                    self.assertTrue(value, f"{path.name}: empty evidence summary: {line!r}")
                    self.assertFalse(
                        value.startswith(":"),
                        f"{path.name}: malformed evidence reference: {line!r}",
                    )


class InvariantCandidatePropertyTests(unittest.TestCase):
    """Invariant candidates should read as properties, not as suggested tests."""

    def test_looks_like_instruction_flags_test_verbs(self) -> None:
        self.assertTrue(tp_gen.looks_like_instruction("Assert swaps preserve the invariant."))
        self.assertTrue(tp_gen.looks_like_instruction("Test minOut enforcement."))
        self.assertFalse(
            tp_gen.looks_like_instruction("Swaps preserve documented AMM accounting.")
        )
        self.assertFalse(
            tp_gen.looks_like_instruction("Collateral value and debt remain solvent.")
        )

    def test_property_candidates_drops_instructions_keeps_properties(self) -> None:
        items = [
            "Swaps and liquidity operations preserve documented AMM accounting.",
            "Assert swaps preserve the documented constant-product invariant.",
        ]
        self.assertEqual(
            tp_gen.property_candidates(items),
            ["Swaps and liquidity operations preserve documented AMM accounting."],
        )

    def test_property_candidates_keeps_original_if_all_instructions(self) -> None:
        # Never leave a finding without any candidate, even if all read as tests.
        items = ["Assert the property holds.", "Test the boundary."]
        self.assertEqual(tp_gen.property_candidates(items), items)

    def test_committed_test_plans_have_property_style_invariants(self) -> None:
        for path in [
            "examples/reports/amm-fixture-test-plan.json",
            "examples/reports/lending-fixture-test-plan.json",
            "examples/reports/amm-lending-hybrid-fixture-test-plan.json",
        ]:
            data = load_json(path)
            candidates = list(data.get("invariant_candidates", []))
            for finding in data.get("findings", []):
                candidates.extend(finding.get("invariant_candidates", []))
            for family in data.get("rule_families", []):
                candidates.extend(family.get("invariant_candidates", []))
            self.assertTrue(candidates, f"{path} has no invariant candidates")
            for candidate in candidates:
                self.assertFalse(
                    tp_gen.looks_like_instruction(candidate),
                    f"{path}: invariant candidate reads as a test instruction: {candidate!r}",
                )


if __name__ == "__main__":
    unittest.main()
