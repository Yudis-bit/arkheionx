"""Regression tests for matched-signal naming on readiness findings.

Some readiness gaps are constructed without an explicit signal list (for example
the protocol-shape and rule-family coverage gaps raised during scoring). Before
this guard those findings rendered a generic ``scanner signal`` placeholder and
carried an empty ``detected_signals`` list, which weakened evidence snippets,
evidence summaries, and downstream test-plan matched signals.

``backfill_detected_signals`` names the local/static terms that triggered such a
finding without altering its confidence, priority, severity, or the readiness
score. These tests lock both the unit behaviour and the rendered output.
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


def make_gap(module, category: str, detected=None):
    return module.ReadinessGap(
        severity="Medium readiness gap",
        title="Example readiness gap",
        detail="detail",
        recommendation="rec",
        tags=["example"],
        category=category,
        detected=list(detected or []),
    )


class SignalCategoryMappingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_scanner_module()

    def test_rule_family_category_maps_to_signal_bucket(self) -> None:
        gap = make_gap(self.module, "oracle-pricing")
        self.assertEqual(self.module.signal_categories_for_gap(gap), ("oracle",))
        gap = make_gap(self.module, "reentrancy-value-flow")
        self.assertEqual(
            self.module.signal_categories_for_gap(gap),
            ("reentrancy_value_flow",),
        )

    def test_testing_category_has_no_rule_family_mapping(self) -> None:
        # Testing-readiness findings fire on absent test types, not a code term,
        # so they must not borrow a rule-family signal bucket.
        gap = make_gap(self.module, "testing-readiness")
        self.assertEqual(self.module.signal_categories_for_gap(gap), ())

    def test_unmapped_category_returns_no_signals(self) -> None:
        gap = make_gap(self.module, "generic")
        self.assertEqual(self.module.signal_categories_for_gap(gap), ())


class TestingCoverageSignalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_scanner_module()

    def test_names_each_missing_test_type_in_review_order(self) -> None:
        readiness = {"invariant_tests": False, "fuzz_tests": False, "handler_contracts": False}
        self.assertEqual(
            self.module.testing_coverage_signals(readiness),
            ["invariant_tests_missing", "fuzz_tests_missing", "handler_contracts_missing"],
        )

    def test_present_test_types_are_not_flagged(self) -> None:
        readiness = {"invariant_tests": True, "fuzz_tests": False, "handler_contracts": True}
        self.assertEqual(
            self.module.testing_coverage_signals(readiness), ["fuzz_tests_missing"]
        )

    def test_signals_are_testing_specific_not_protocol_terms(self) -> None:
        readiness = {"invariant_tests": False, "fuzz_tests": False, "handler_contracts": False}
        for token in self.module.testing_coverage_signals(readiness):
            self.assertTrue(token.endswith("_missing"))


class BackfillDetectedSignalsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_scanner_module()
        self.signals = {
            "oracle": {
                "terms": ["priceFeed", "latestRoundData"],
                "files": ["src/Market.sol"],
            },
            "amm": {"terms": ["swap", "mint"], "files": ["src/Pool.sol"]},
        }

    def test_empty_signal_list_is_backfilled_and_sorted(self) -> None:
        gap = make_gap(self.module, "oracle-pricing")
        self.module.backfill_detected_signals([gap], self.signals, "lending")
        # detected_terms de-duplicates and sorts for deterministic output.
        self.assertEqual(gap.detected, ["latestRoundData", "priceFeed"])
        self.assertTrue(gap.fingerprint, "fingerprint must be recomputed after backfill")

    def test_existing_signals_are_not_clobbered(self) -> None:
        gap = make_gap(self.module, "oracle-pricing", detected=["custom-signal"])
        self.module.backfill_detected_signals([gap], self.signals, "lending")
        self.assertEqual(gap.detected, ["custom-signal"])

    def test_unmapped_category_stays_empty(self) -> None:
        gap = make_gap(self.module, "generic")
        self.module.backfill_detected_signals([gap], self.signals, "amm")
        self.assertEqual(gap.detected, [])

    def test_testing_finding_names_missing_coverage_not_protocol_signals(self) -> None:
        # A testing finding must surface missing-coverage signals, never the
        # protocol vocabulary (swap/mint) it would otherwise inherit.
        gap = make_gap(self.module, "testing-readiness")
        readiness = {"invariant_tests": False, "fuzz_tests": False, "handler_contracts": False}
        self.module.backfill_detected_signals([gap], self.signals, "amm", readiness)
        self.assertEqual(
            gap.detected,
            ["invariant_tests_missing", "fuzz_tests_missing", "handler_contracts_missing"],
        )
        self.assertNotIn("swap", gap.detected)
        self.assertTrue(gap.fingerprint)


class RenderedSignalQualityTests(unittest.TestCase):
    def run_scanner(self, root: str, protocol_type: str):
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
            return (
                md_path.read_text(encoding="utf-8"),
                json.loads(json_path.read_text(encoding="utf-8")),
            )

    @staticmethod
    def finding(report, finding_id):
        for item in report["findings"]:
            if item["id"] == finding_id:
                return item
        return None

    def test_reports_never_emit_generic_scanner_signal(self) -> None:
        for root, ptype in (
            ("examples/amm-fixture", "amm"),
            ("examples/lending-fixture", "lending"),
            ("examples/oracle-staking-fixture", "auto"),
        ):
            markdown, report = self.run_scanner(root, ptype)
            self.assertNotIn(
                "- scanner signal",
                markdown,
                f"{root} still renders the generic scanner-signal placeholder",
            )
            # Any finding without discrete signal terms must state its detection
            # basis honestly rather than fabricate a placeholder signal.
            for item in report["findings"]:
                if not (item.get("detected_signals") or []):
                    self.assertIn("No discrete code-term signal", markdown)

    def test_rule_family_findings_name_their_signals(self) -> None:
        markdown, report = self.run_scanner("examples/amm-fixture", "amm")
        oracle = self.finding(report, "ARK-ORC-002")
        self.assertIsNotNone(oracle, "expected ARK-ORC-002 in the AMM fixture")
        signals = oracle.get("detected_signals") or []
        self.assertTrue(signals, "ARK-ORC-002 must name the oracle/reserve signals it matched")
        self.assertIn("getReserves", signals)

        reentrancy = self.finding(report, "ARK-REENT-001")
        self.assertIsNotNone(reentrancy, "expected ARK-REENT-001 in the AMM fixture")
        reentrancy_signals = reentrancy.get("detected_signals") or []
        self.assertIn("transferFrom", reentrancy_signals)
        # The named signal must also appear in the rendered Detected signals list.
        self.assertIn("`transferFrom`", markdown)

    def test_testing_finding_uses_coverage_signals_not_protocol_terms(self) -> None:
        # ARK-TST-002 ("no invariant tests for DeFi protocol shape") must point at
        # the missing test types, not borrow AMM/lending/oracle vocabulary.
        for root, ptype, protocol_terms in (
            ("examples/amm-fixture", "amm", {"swap", "addLiquidity", "getReserves"}),
            ("examples/lending-fixture", "lending", {"borrow", "liquidate", "collateral"}),
        ):
            _markdown, report = self.run_scanner(root, ptype)
            testing = self.finding(report, "ARK-TST-002")
            self.assertIsNotNone(testing, f"expected ARK-TST-002 in {root}")
            signals = testing.get("detected_signals") or []
            self.assertIn("invariant_tests_missing", signals)
            self.assertTrue(
                all(s.endswith("_missing") for s in signals),
                f"ARK-TST-002 should only carry testing-coverage signals: {signals}",
            )
            self.assertFalse(
                protocol_terms & set(signals),
                f"ARK-TST-002 must not inherit protocol terms {protocol_terms & set(signals)}",
            )

    def test_naming_signals_does_not_inflate_confidence(self) -> None:
        # ARK-ORC-002 in the lending fixture has strong oracle signals and
        # semantic support; naming those signals must not push it from medium to
        # high confidence (that would reorder Fix First). This locks the ordering
        # guarantee: signals are backfilled after the construction-time confidence
        # is fixed, so calibration is unchanged.
        _markdown, report = self.run_scanner("examples/lending-fixture", "lending")
        oracle = self.finding(report, "ARK-ORC-002")
        self.assertIsNotNone(oracle)
        self.assertTrue(oracle.get("detected_signals"))
        self.assertEqual(oracle["confidence"], "medium")

    def test_backfilled_signals_are_deterministic(self) -> None:
        _m1, r1 = self.run_scanner("examples/amm-fixture", "amm")
        _m2, r2 = self.run_scanner("examples/amm-fixture", "amm")
        a = self.finding(r1, "ARK-ORC-002")["detected_signals"]
        b = self.finding(r2, "ARK-ORC-002")["detected_signals"]
        self.assertEqual(a, b)


class SecondaryProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_scanner_module()

    def test_strong_secondary_named_when_scores_are_close(self) -> None:
        scores = {"amm": 102, "lending": 94, "oracle": 0, "staking": 0, "vault": 0}
        self.assertEqual(self.module.strong_secondary_protocols(scores, "amm"), ["lending"])

    def test_no_secondary_when_primary_dominates(self) -> None:
        scores = {"amm": 163, "lending": 0, "oracle": 0}
        self.assertEqual(self.module.strong_secondary_protocols(scores, "amm"), [])

    def test_secondary_sorted_by_score_then_name(self) -> None:
        scores = {"amm": 100, "lending": 90, "vault": 90}
        self.assertEqual(self.module.strong_secondary_protocols(scores, "amm"), ["lending", "vault"])

    def test_hybrid_report_names_strong_lending_secondary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "r.md"
            json_path = Path(tmp) / "r.json"
            subprocess.run(
                [
                    "python3", str(SCANNER),
                    "--root", str(REPO_ROOT / "examples/amm-lending-hybrid-fixture"),
                    "--protocol-type", "auto",
                    "--output", str(md), "--json-output", str(json_path),
                ],
                cwd=REPO_ROOT, check=True, text=True, capture_output=True,
            )
            text = md.read_text(encoding="utf-8")
        self.assertIn("strong secondary signals", text)
        self.assertIn("lending", text)

    def test_amm_report_has_no_secondary_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "r.md"
            json_path = Path(tmp) / "r.json"
            subprocess.run(
                [
                    "python3", str(SCANNER),
                    "--root", str(REPO_ROOT / "examples/amm-fixture"),
                    "--protocol-type", "amm",
                    "--output", str(md), "--json-output", str(json_path),
                ],
                cwd=REPO_ROOT, check=True, text=True, capture_output=True,
            )
            text = md.read_text(encoding="utf-8")
        self.assertNotIn("strong secondary signals", text)


if __name__ == "__main__":
    unittest.main()
