"""Tests for Real Protocol Fixture Set 3 (v3.9): source files + registry + suite."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import arkheionx.fixture_harness as fh
from arkheionx.fixture_harness import fixtures as reg

REPO_ROOT = Path(__file__).resolve().parents[1]
SET3_DIR = Path(__file__).parent / "fixtures" / "fixture_harness" / "set3"
README = SET3_DIR / "README.md"
BRIDGE = SET3_DIR / "bridge_message" / "BridgeMessageShape.sol"
LIQ = SET3_DIR / "liquidation_engine" / "LiquidationEngineShape.sol"
GOV = SET3_DIR / "governance_timelock" / "GovernanceTimelockShape.sol"
SOURCE_FILES = (BRIDGE, LIQ, GOV)
ALL_FILES = (README,) + SOURCE_FILES

# Dangerous machine patterns (case-insensitive); never present in a required
# negated disclaimer such as "no RPC" or "no private keys".
_FORBIDDEN = (
    "http://", "https://",
    "rpc-url", "rpc_url", "--rpc-url",
    "fork-url", "fork_url", "--fork-url",
    "privatekey", "private_key",
    "mnemonic",
    "seedphrase", "seed_phrase",
    "vm.broadcast", "startbroadcast", "vm.startbroadcast",
    "exploit",
    "confirmed vulnerability", "final severity", "audit passed", "bounty eligible",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class FixtureFileTests(unittest.TestCase):
    def test_readme_exists(self) -> None:  # 1
        self.assertTrue(README.is_file())

    def test_bridge_exists(self) -> None:  # 2
        self.assertTrue(BRIDGE.is_file())

    def test_liquidation_exists(self) -> None:  # 3
        self.assertTrue(LIQ.is_file())

    def test_governance_exists(self) -> None:  # 4
        self.assertTrue(GOV.is_file())

    def test_fixture_files_are_small(self) -> None:  # 5
        for path in ALL_FILES:
            self.assertLess(path.stat().st_size, 8000, path.name)

    def test_fixture_files_utf8_readable(self) -> None:  # 6
        for path in ALL_FILES:
            self.assertIsInstance(_text(path), str)

    def test_bridge_local_static_wording(self) -> None:  # 7
        self.assertIn("local/static", _text(BRIDGE).lower())

    def test_liquidation_local_static_wording(self) -> None:  # 8
        self.assertIn("local/static", _text(LIQ).lower())

    def test_governance_local_static_wording(self) -> None:  # 9
        self.assertIn("local/static", _text(GOV).lower())

    def test_readme_local_static_wording(self) -> None:  # 10
        self.assertIn("local/static", _text(README).lower())

    def test_bridge_no_forbidden_wording(self) -> None:  # 11
        low = _text(BRIDGE).lower()
        for token in _FORBIDDEN:
            self.assertNotIn(token, low, token)

    def test_liquidation_no_forbidden_wording(self) -> None:  # 12
        low = _text(LIQ).lower()
        for token in _FORBIDDEN:
            self.assertNotIn(token, low, token)

    def test_governance_no_forbidden_wording(self) -> None:  # 13
        low = _text(GOV).lower()
        for token in _FORBIDDEN:
            self.assertNotIn(token, low, token)

    def test_readme_no_forbidden_wording(self) -> None:  # 14
        low = _text(README).lower()
        for token in _FORBIDDEN:
            self.assertNotIn(token, low, token)

    def test_no_human_reviewed_token(self) -> None:  # 15
        for path in ALL_FILES:
            self.assertNotIn("HUMAN_REVIEWED", _text(path), path.name)

    def test_no_hardcoded_hex_addresses(self) -> None:  # 16
        for path in SOURCE_FILES:
            self.assertIsNone(re.search(r"0x[0-9a-fA-F]{40}", _text(path)), path.name)

    def test_files_have_spdx_and_pragma(self) -> None:  # 17
        for path in SOURCE_FILES:
            text = _text(path)
            self.assertIn("SPDX-License-Identifier", text, path.name)
            self.assertIn("pragma solidity", text, path.name)

    def test_files_declare_not_audited(self) -> None:  # 18
        for path in SOURCE_FILES:
            self.assertIn("NOT an audited contract", _text(path), path.name)


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.defs = reg.set3_fixture_definitions()

    def test_returns_exactly_three(self) -> None:  # 19
        self.assertEqual(len(self.defs), 3)

    def test_fixture_names(self) -> None:  # 20
        self.assertEqual([f.name for f in self.defs],
                         ["bridge_message", "liquidation_engine", "governance_timelock"])

    def test_fixture_ids_deterministic_across_calls(self) -> None:  # 21
        self.assertEqual([f.fixture_id for f in self.defs],
                         [f.fixture_id for f in reg.set3_fixture_definitions()])

    def test_fixture_ids_unique(self) -> None:  # 22
        ids = [f.fixture_id for f in self.defs]
        self.assertEqual(len(set(ids)), 3)
        self.assertTrue(all(i.startswith("fixture:") for i in ids))

    def test_fixture_categories(self) -> None:  # 23
        self.assertEqual([f.category for f in self.defs],
                         [fh.FIXTURE_CATEGORY_BRIDGE_MESSAGE,
                          fh.FIXTURE_CATEGORY_LIQUIDATION_BORROW_REPAY,
                          fh.FIXTURE_CATEGORY_MISC])

    def test_fixture_relative_paths_safe(self) -> None:  # 24
        for f in self.defs:
            self.assertTrue(f.relative_path.startswith("tests/fixtures/fixture_harness/set3/"))
            self.assertFalse(f.relative_path.startswith("/"))
            self.assertNotIn("\\", f.relative_path)
            self.assertNotIn("..", f.relative_path.split("/"))

    def test_source_files_safe(self) -> None:  # 25
        for f in self.defs:
            self.assertTrue(f.source_files)
            for sf in f.source_files:
                self.assertFalse(sf.startswith("/"))
                self.assertNotIn("\\", sf)
                self.assertNotIn("..", sf.split("/"))
                self.assertTrue(sf.endswith(".sol"))

    def test_expected_artifact_kinds_include_source(self) -> None:  # 26
        for f in self.defs:
            self.assertIn(fh.FIXTURE_ARTIFACT_SOURCE, f.expected_artifact_kinds)

    def test_expected_artifact_kinds_include_protocol_graph(self) -> None:  # 27
        for f in self.defs:
            self.assertIn(fh.FIXTURE_ARTIFACT_PROTOCOL_GRAPH, f.expected_artifact_kinds)

    def test_benchmark_dimensions_include_id_stability(self) -> None:  # 28
        for f in self.defs:
            self.assertIn(fh.BENCHMARK_DIMENSION_ID_STABILITY, f.benchmark_dimensions)

    def test_benchmark_dimensions_include_graph_counts(self) -> None:  # 29
        for f in self.defs:
            self.assertIn(fh.BENCHMARK_DIMENSION_GRAPH_COUNTS, f.benchmark_dimensions)

    def test_tags_include_set3(self) -> None:  # 30
        for f in self.defs:
            self.assertIn("set3", f.tags)

    def test_manual_review_required_true(self) -> None:  # 31
        for f in self.defs:
            self.assertIs(f.manual_review_required, True)

    def test_ready_for_submission_false(self) -> None:  # 32
        for f in self.defs:
            self.assertIs(f.ready_for_submission, False)

    def test_safety_boundary_local_static_only(self) -> None:  # 33
        for f in self.defs:
            self.assertIs(f.safety_boundary.local_static_only, True)

    def test_safety_boundary_no_rpc(self) -> None:  # 34
        for f in self.defs:
            self.assertIs(f.safety_boundary.no_rpc, True)

    def test_safety_boundary_no_fork_url(self) -> None:  # 35
        for f in self.defs:
            self.assertIs(f.safety_boundary.no_fork_url, True)

    def test_safety_boundary_no_private_keys(self) -> None:  # 36
        for f in self.defs:
            self.assertIs(f.safety_boundary.no_private_keys, True)

    def test_safety_boundary_no_seed_phrases(self) -> None:  # 37
        for f in self.defs:
            self.assertIs(f.safety_boundary.no_seed_phrases, True)

    def test_known_categories_do_not_warn(self) -> None:  # 38
        for f in self.defs:
            self.assertFalse(any("unknown fixture category" in w for w in f.warnings))

    def test_distinct_ids_from_set1_and_set2(self) -> None:  # 39
        set1_ids = {f.fixture_id for f in reg.set1_fixture_definitions()}
        set2_ids = {f.fixture_id for f in reg.set2_fixture_definitions()}
        set3_ids = {f.fixture_id for f in self.defs}
        self.assertTrue(set3_ids.isdisjoint(set1_ids))
        self.assertTrue(set3_ids.isdisjoint(set2_ids))


class ArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.arts = reg.set3_fixture_artifacts()
        self.fixture_ids = {f.fixture_id for f in reg.set3_fixture_definitions()}

    def test_one_source_artifact_per_fixture(self) -> None:  # 40
        self.assertEqual(len(self.arts), 3)

    def test_artifact_ids_deterministic(self) -> None:  # 41
        self.assertEqual([a.artifact_id for a in self.arts],
                         [a.artifact_id for a in reg.set3_fixture_artifacts()])

    def test_artifact_ids_unique(self) -> None:  # 42
        ids = [a.artifact_id for a in self.arts]
        self.assertEqual(len(set(ids)), 3)
        self.assertTrue(all(i.startswith("fixture-artifact:") for i in ids))

    def test_artifact_fixture_ids_resolve(self) -> None:  # 43
        for a in self.arts:
            self.assertIn(a.fixture_id, self.fixture_ids)

    def test_artifact_kind_is_source(self) -> None:  # 44
        for a in self.arts:
            self.assertEqual(a.artifact_kind, fh.FIXTURE_ARTIFACT_SOURCE)

    def test_artifact_relative_paths_safe(self) -> None:  # 45
        for a in self.arts:
            self.assertTrue(a.relative_path.endswith(".sol"))
            self.assertFalse(a.relative_path.startswith("/"))
            self.assertNotIn("\\", a.relative_path)
            self.assertNotIn("..", a.relative_path.split("/"))

    def test_artifact_checksum_empty(self) -> None:  # 46
        for a in self.arts:
            self.assertEqual(a.checksum_sha256, "")

    def test_artifact_size_zero(self) -> None:  # 47
        for a in self.arts:
            self.assertEqual(a.size_bytes, 0)

    def test_artifact_manual_review_required_true(self) -> None:  # 48
        for a in self.arts:
            self.assertIs(a.manual_review_required, True)

    def test_artifact_ready_for_submission_false(self) -> None:  # 49
        for a in self.arts:
            self.assertIs(a.ready_for_submission, False)

    def test_artifact_ids_distinct_from_prior_sets(self) -> None:  # 50
        prior = {a.artifact_id for a in reg.set1_fixture_artifacts()}
        prior |= {a.artifact_id for a in reg.set2_fixture_artifacts()}
        self.assertTrue({a.artifact_id for a in self.arts}.isdisjoint(prior))


class SuiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = reg.build_set3_fixture_suite()

    def test_returns_fixture_suite(self) -> None:  # 51
        self.assertIsInstance(self.suite, fh.FixtureSuite)

    def test_fixture_count_three(self) -> None:  # 52
        self.assertEqual(self.suite.fixture_count, 3)

    def test_result_count_zero(self) -> None:  # 53
        self.assertEqual(self.suite.result_count, 0)

    def test_drift_count_zero(self) -> None:  # 54
        self.assertEqual(self.suite.drift_count, 0)

    def test_suite_id_deterministic(self) -> None:  # 55
        self.assertEqual(self.suite.suite_id, reg.build_set3_fixture_suite().suite_id)
        self.assertTrue(self.suite.suite_id.startswith("fixture-suite:fixture-harness-set3:"))

    def test_suite_id_order_stable(self) -> None:  # 56
        defs = reg.set3_fixture_definitions()
        forward = fh.build_fixture_suite(reg.SET3_SUITE_NAME, fixtures=defs).suite_id
        reverse = fh.build_fixture_suite(reg.SET3_SUITE_NAME, fixtures=list(reversed(defs))).suite_id
        self.assertEqual(forward, reverse)

    def test_suite_id_distinct_from_prior_sets(self) -> None:  # 57
        self.assertNotEqual(self.suite.suite_id, reg.build_set1_fixture_suite().suite_id)
        self.assertNotEqual(self.suite.suite_id, reg.build_set2_fixture_suite().suite_id)

    def test_suite_manual_review_required_true(self) -> None:  # 58
        self.assertIs(self.suite.manual_review_required, True)

    def test_suite_ready_for_submission_false(self) -> None:  # 59
        self.assertIs(self.suite.ready_for_submission, False)

    def test_suite_serializes_to_json(self) -> None:  # 60
        json.dumps(fh.fixture_harness_to_dict(self.suite))

    def test_suite_serialization_no_overclaim(self) -> None:  # 61
        blob = json.dumps(fh.fixture_harness_to_dict(self.suite))
        low = blob.lower()
        self.assertNotIn("HUMAN_REVIEWED", blob)
        for token in ("confirmed vulnerability", "final severity", "audit passed",
                      "bounty eligible", "proves safety", "proves vulnerability",
                      "proves a vulnerability"):
            self.assertNotIn(token, low, token)


class ContentCoverageTests(unittest.TestCase):
    def test_bridge_send_message(self) -> None:  # 62
        self.assertIn("function sendMessage(", _text(BRIDGE))

    def test_bridge_receive_message(self) -> None:  # 63
        self.assertIn("function receiveMessage(", _text(BRIDGE))

    def test_bridge_verify_message(self) -> None:  # 64
        self.assertIn("function verifyMessage(", _text(BRIDGE))

    def test_bridge_mark_processed(self) -> None:  # 65
        self.assertIn("function markMessageProcessed(", _text(BRIDGE))

    def test_bridge_set_verifier_only_owner(self) -> None:  # 66
        text = _text(BRIDGE)
        self.assertIn("function setMessageVerifier(", text)
        self.assertIn("onlyOwner", text)

    def test_bridge_nonce_tracking(self) -> None:  # 67
        self.assertIn("Nonce", _text(BRIDGE))

    def test_bridge_pause(self) -> None:  # 68
        text = _text(BRIDGE)
        self.assertTrue("function pause(" in text or "function unpause(" in text)

    def test_liq_deposit_collateral(self) -> None:  # 69
        self.assertIn("function depositCollateral(", _text(LIQ))

    def test_liq_withdraw_collateral(self) -> None:  # 70
        self.assertIn("function withdrawCollateral(", _text(LIQ))

    def test_liq_borrow(self) -> None:  # 71
        self.assertIn("function borrow(", _text(LIQ))

    def test_liq_repay(self) -> None:  # 72
        self.assertIn("function repay(", _text(LIQ))

    def test_liq_get_account_liquidity(self) -> None:  # 73
        self.assertIn("function getAccountLiquidity(", _text(LIQ))

    def test_liq_is_liquidatable(self) -> None:  # 74
        self.assertIn("function isLiquidatable(", _text(LIQ))

    def test_liq_liquidate(self) -> None:  # 75
        self.assertIn("function liquidate(", _text(LIQ))

    def test_liq_set_liquidation_bonus_only_owner(self) -> None:  # 76
        text = _text(LIQ)
        self.assertIn("function setLiquidationBonus(", text)
        self.assertIn("onlyOwner", text)

    def test_liq_set_close_factor_only_owner(self) -> None:  # 77
        text = _text(LIQ)
        self.assertIn("function setCloseFactor(", text)
        self.assertIn("onlyOwner", text)

    def test_liq_oracle_reference(self) -> None:  # 78
        self.assertIn("oracle", _text(LIQ).lower())

    def test_gov_propose(self) -> None:  # 79
        self.assertIn("function propose(", _text(GOV))

    def test_gov_queue(self) -> None:  # 80
        self.assertIn("function queue(", _text(GOV))

    def test_gov_execute(self) -> None:  # 81
        self.assertIn("function execute(", _text(GOV))

    def test_gov_cancel(self) -> None:  # 82
        self.assertIn("function cancel(", _text(GOV))

    def test_gov_set_delay_only_admin(self) -> None:  # 83
        text = _text(GOV)
        self.assertIn("function setDelay(", text)
        self.assertIn("onlyAdmin", text)

    def test_gov_grant_and_revoke_role(self) -> None:  # 84
        text = _text(GOV)
        self.assertIn("function grantRole(", text)
        self.assertIn("function revokeRole(", text)

    def test_gov_get_proposal_state(self) -> None:  # 85
        self.assertIn("function getProposalState(", _text(GOV))


class RunnerBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = fh.run_fixture_benchmark_suite(reg.build_set3_fixture_suite())

    def test_benchmark_executes_set3(self) -> None:  # 86
        self.assertEqual(self.suite.fixture_count, 3)
        self.assertEqual(self.suite.run_count, 3)
        self.assertGreater(self.suite.result_count, 0)

    def test_benchmark_no_drift(self) -> None:  # 87
        self.assertEqual(self.suite.drift_count, 0)

    def test_benchmark_runs_executed(self) -> None:  # 88
        self.assertEqual({r.run_status for r in self.suite.runs}, {fh.FIXTURE_RUN_EXECUTED})

    def test_benchmark_source_checks_clean(self) -> None:  # 89
        kinds = {(r.fixture_id, r.result_kind): r for r in self.suite.results}
        for f in self.suite.fixtures:
            self.assertIs(kinds[(f.fixture_id, "source_text_no_dangerous_patterns")].observed_value, True)
            self.assertIs(kinds[(f.fixture_id, "source_text_local_static_wording")].observed_value, True)

    def test_benchmark_serialization_no_overclaim(self) -> None:  # 90
        blob = json.dumps(fh.fixture_harness_to_dict(self.suite)).lower()
        for token in ("confirmed vulnerability", "final severity", "audit passed",
                      "bounty eligible", "proves safety", "proves vulnerability"):
            self.assertNotIn(token, blob, token)


class ExportAndCompatibilityTests(unittest.TestCase):
    def test_package_exports_set3_helpers(self) -> None:  # 91
        for name in ("set3_fixture_definitions", "set3_fixture_artifacts",
                     "build_set3_fixture_suite", "SET3_ROOT", "SET3_SUITE_NAME"):
            self.assertIn(name, fh.__all__, name)
            self.assertTrue(hasattr(fh, name), name)

    def test_set1_registry_unaffected(self) -> None:  # 92
        self.assertEqual(fh.build_set1_fixture_suite().fixture_count, 3)

    def test_set2_registry_unaffected(self) -> None:  # 93
        self.assertEqual(fh.build_set2_fixture_suite().fixture_count, 3)

    def test_runner_set1_unaffected(self) -> None:  # 94
        self.assertEqual(fh.benchmark_set1_fixture_suite().result_count, 63)

    def test_snapshot_set1_unaffected(self) -> None:  # 95
        self.assertEqual(fh.build_set1_benchmark_snapshot(), fh.load_set1_benchmark_snapshot())

    def test_registry_import_side_effect_free(self) -> None:  # 96
        with tempfile.TemporaryDirectory() as tmp:
            code = (
                "import os; before=set(os.listdir('.'));"
                "import arkheionx.fixture_harness.fixtures as f;"
                "f.set3_fixture_definitions(); f.set3_fixture_artifacts(); f.build_set3_fixture_suite();"
                "assert set(os.listdir('.'))==before, 'created files';"
                "assert not os.path.exists('.arkheionx'), '.arkheionx created';"
                "print('clean')"
            )
            env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
            result = subprocess.run([sys.executable, "-c", code], cwd=tmp, text=True,
                                    capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("clean", result.stdout)


if __name__ == "__main__":
    unittest.main()
