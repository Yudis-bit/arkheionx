"""Tests for Real Protocol Fixture Set 1 (v3.9): source files + registry + suite."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import arkheionx.fixture_harness as fh
from arkheionx.fixture_harness import fixtures as set1

REPO_ROOT = Path(__file__).resolve().parents[1]
SET1_DIR = Path(__file__).parent / "fixtures" / "fixture_harness" / "set1"
README = SET1_DIR / "README.md"
ERC20 = SET1_DIR / "erc20_like" / "ERC20Like.sol"
VAULT = SET1_DIR / "lending_vault" / "LendingVault.sol"
STAKING = SET1_DIR / "staking_reward" / "StakingReward.sol"
SOURCE_FILES = (ERC20, VAULT, STAKING)
ALL_FILES = (README,) + SOURCE_FILES

# Forbidden DANGEROUS machine patterns (case-insensitive). These are the forms
# that only appear in genuinely unsafe content (real endpoints, secrets, Foundry
# flags/cheatcodes), never in a required negated disclaimer such as "no RPC" or
# "no private keys". Disclaimer words ("no fork url", "no seed phrases") are kept
# in the fixtures on purpose and are NOT scanned here.
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

    def test_erc20_exists(self) -> None:  # 2
        self.assertTrue(ERC20.is_file())

    def test_lending_vault_exists(self) -> None:  # 3
        self.assertTrue(VAULT.is_file())

    def test_staking_reward_exists(self) -> None:  # 4
        self.assertTrue(STAKING.is_file())

    def test_fixture_files_are_small(self) -> None:  # 5
        for path in ALL_FILES:
            self.assertLess(path.stat().st_size, 8000, path.name)

    def test_fixture_files_utf8_readable(self) -> None:  # 6
        for path in ALL_FILES:
            self.assertIsInstance(_text(path), str)

    def test_fixture_files_have_local_static_wording(self) -> None:  # 7
        for path in SOURCE_FILES:
            self.assertIn("local/static", _text(path).lower(), path.name)
        self.assertIn("local/static", _text(README).lower())

    def test_no_forbidden_wording_in_fixture_files(self) -> None:  # 8-18
        for path in ALL_FILES:
            low = _text(path).lower()
            for token in _FORBIDDEN:
                self.assertNotIn(token, low, f"{path.name}: {token}")
            self.assertNotIn("HUMAN_REVIEWED", _text(path), path.name)

    def test_no_hardcoded_hex_addresses(self) -> None:
        import re
        for path in SOURCE_FILES:
            self.assertIsNone(re.search(r"0x[0-9a-fA-F]{40}", _text(path)), path.name)


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.defs = set1.set1_fixture_definitions()

    def test_returns_exactly_three(self) -> None:  # 19
        self.assertEqual(len(self.defs), 3)

    def test_fixture_names_deterministic(self) -> None:  # 20
        self.assertEqual([f.name for f in self.defs], ["erc20_like", "lending_vault", "staking_reward"])

    def test_fixture_ids_deterministic_across_calls(self) -> None:  # 21
        self.assertEqual([f.fixture_id for f in self.defs],
                         [f.fixture_id for f in set1.set1_fixture_definitions()])

    def test_fixture_ids_unique(self) -> None:  # 22
        ids = [f.fixture_id for f in self.defs]
        self.assertEqual(len(set(ids)), 3)
        self.assertTrue(all(i.startswith("fixture:") for i in ids))

    def test_fixture_categories(self) -> None:  # 23
        self.assertEqual([f.category for f in self.defs],
                         [fh.FIXTURE_CATEGORY_ERC20, fh.FIXTURE_CATEGORY_LENDING_VAULT,
                          fh.FIXTURE_CATEGORY_STAKING_REWARD])

    def test_fixture_relative_paths_safe(self) -> None:  # 24
        for f in self.defs:
            self.assertTrue(f.relative_path.startswith("tests/fixtures/fixture_harness/set1/"))
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

    def test_tags_include_set1(self) -> None:  # 30
        for f in self.defs:
            self.assertIn("set1", f.tags)

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

    def test_known_categories_do_not_warn(self) -> None:
        for f in self.defs:
            self.assertFalse(any("unknown fixture category" in w for w in f.warnings))


class ArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.arts = set1.set1_fixture_artifacts()
        self.fixture_ids = {f.fixture_id for f in set1.set1_fixture_definitions()}

    def test_one_source_artifact_per_fixture(self) -> None:  # 38
        self.assertEqual(len(self.arts), 3)

    def test_artifact_ids_deterministic(self) -> None:  # 39
        self.assertEqual([a.artifact_id for a in self.arts],
                         [a.artifact_id for a in set1.set1_fixture_artifacts()])

    def test_artifact_ids_unique(self) -> None:  # 40
        ids = [a.artifact_id for a in self.arts]
        self.assertEqual(len(set(ids)), 3)
        self.assertTrue(all(i.startswith("fixture-artifact:") for i in ids))

    def test_artifact_fixture_ids_resolve(self) -> None:  # 41
        for a in self.arts:
            self.assertIn(a.fixture_id, self.fixture_ids)

    def test_artifact_kind_is_source(self) -> None:  # 42
        for a in self.arts:
            self.assertEqual(a.artifact_kind, fh.FIXTURE_ARTIFACT_SOURCE)

    def test_artifact_relative_paths_safe(self) -> None:  # 43
        for a in self.arts:
            self.assertTrue(a.relative_path.endswith(".sol"))
            self.assertFalse(a.relative_path.startswith("/"))
            self.assertNotIn("\\", a.relative_path)
            self.assertNotIn("..", a.relative_path.split("/"))

    def test_artifact_checksum_empty(self) -> None:  # 44
        for a in self.arts:
            self.assertEqual(a.checksum_sha256, "")

    def test_artifact_size_zero(self) -> None:  # 45
        for a in self.arts:
            self.assertEqual(a.size_bytes, 0)

    def test_artifact_manual_review_required_true(self) -> None:  # 46
        for a in self.arts:
            self.assertIs(a.manual_review_required, True)

    def test_artifact_ready_for_submission_false(self) -> None:  # 47
        for a in self.arts:
            self.assertIs(a.ready_for_submission, False)


class SuiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = set1.build_set1_fixture_suite()

    def test_returns_fixture_suite(self) -> None:  # 48
        self.assertIsInstance(self.suite, fh.FixtureSuite)

    def test_fixture_count_three(self) -> None:  # 49
        self.assertEqual(self.suite.fixture_count, 3)

    def test_result_count_zero(self) -> None:  # 50
        self.assertEqual(self.suite.result_count, 0)

    def test_drift_count_zero(self) -> None:  # 51
        self.assertEqual(self.suite.drift_count, 0)

    def test_suite_id_deterministic(self) -> None:  # 52
        self.assertEqual(self.suite.suite_id, set1.build_set1_fixture_suite().suite_id)
        self.assertTrue(self.suite.suite_id.startswith("fixture-suite:fixture-harness-set1:"))

    def test_suite_id_order_stable(self) -> None:  # 53
        defs = set1.set1_fixture_definitions()
        forward = fh.build_fixture_suite(set1.SET1_SUITE_NAME, fixtures=defs).suite_id
        reverse = fh.build_fixture_suite(set1.SET1_SUITE_NAME, fixtures=list(reversed(defs))).suite_id
        self.assertEqual(forward, reverse)

    def test_suite_manual_review_required_true(self) -> None:  # 54
        self.assertIs(self.suite.manual_review_required, True)

    def test_suite_ready_for_submission_false(self) -> None:  # 55
        self.assertIs(self.suite.ready_for_submission, False)

    def test_suite_serializes_to_json(self) -> None:  # 56
        json.dumps(fh.fixture_harness_to_dict(self.suite))

    def test_suite_serialization_no_overclaim(self) -> None:  # 57-63
        blob = json.dumps(fh.fixture_harness_to_dict(self.suite))
        low = blob.lower()
        self.assertNotIn("HUMAN_REVIEWED", blob)
        for token in ("confirmed vulnerability", "final severity", "audit passed",
                      "bounty eligible", "proves safety", "proves vulnerability",
                      "proves a vulnerability"):
            self.assertNotIn(token, low, token)


class ContentCoverageTests(unittest.TestCase):
    def test_erc20_transfer(self) -> None:  # 64
        self.assertIn("function transfer(", _text(ERC20))

    def test_erc20_transfer_from(self) -> None:  # 65
        self.assertIn("transferFrom(", _text(ERC20))

    def test_erc20_approve(self) -> None:  # 66
        self.assertIn("function approve(", _text(ERC20))

    def test_erc20_mint_or_burn(self) -> None:  # 67
        text = _text(ERC20)
        self.assertTrue("function mint(" in text or "function burn(" in text)

    def test_vault_deposit(self) -> None:  # 68
        self.assertIn("function deposit(", _text(VAULT))

    def test_vault_withdraw(self) -> None:  # 69
        self.assertIn("function withdraw(", _text(VAULT))

    def test_vault_borrow(self) -> None:  # 70
        self.assertIn("function borrow(", _text(VAULT))

    def test_vault_repay(self) -> None:  # 71
        self.assertIn("function repay(", _text(VAULT))

    def test_vault_liquidate(self) -> None:  # 72
        self.assertIn("function liquidate(", _text(VAULT))

    def test_vault_oracle_reference(self) -> None:  # 73
        self.assertIn("oracle", _text(VAULT).lower())

    def test_staking_stake(self) -> None:  # 74
        self.assertIn("function stake(", _text(STAKING))

    def test_staking_withdraw(self) -> None:  # 75
        self.assertIn("function withdraw(", _text(STAKING))

    def test_staking_claim_reward(self) -> None:  # 76
        self.assertIn("function claimReward(", _text(STAKING))

    def test_staking_notify_or_reward_rate(self) -> None:  # 77
        text = _text(STAKING)
        self.assertTrue("notifyRewardAmount" in text or "rewardRate" in text)

    def test_at_least_one_only_owner(self) -> None:  # 78
        self.assertTrue(any("onlyOwner" in _text(p) for p in SOURCE_FILES))

    def test_at_least_one_pause(self) -> None:  # 79
        self.assertTrue(any(("function pause(" in _text(p) or "function unpause(" in _text(p))
                            for p in SOURCE_FILES))


class ImportCompatibilityTests(unittest.TestCase):
    def test_fixtures_import_no_filesystem_side_effect(self) -> None:  # 80
        with tempfile.TemporaryDirectory() as tmp:
            code = (
                "import os; before=set(os.listdir('.'));"
                "import arkheionx.fixture_harness.fixtures as f;"
                "f.set1_fixture_definitions(); f.set1_fixture_artifacts(); f.build_set1_fixture_suite();"
                "assert set(os.listdir('.'))==before, 'created files';"
                "assert not os.path.exists('.arkheionx'), '.arkheionx created';"
                "print('clean')"
            )
            env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
            result = subprocess.run([sys.executable, "-c", code], cwd=tmp, text=True,
                                    capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("clean", result.stdout)

    def test_package_exports_set1_helpers(self) -> None:  # 81
        for name in ("set1_fixture_definitions", "set1_fixture_artifacts", "build_set1_fixture_suite"):
            self.assertIn(name, fh.__all__, name)
            self.assertTrue(hasattr(fh, name), name)

    def test_existing_fixture_harness_ids_unaffected(self) -> None:  # 82
        from arkheionx.fixture_harness import ids
        self.assertTrue(ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT").startswith("fixture:"))

    def test_existing_fixture_harness_model_unaffected(self) -> None:  # 83
        from arkheionx.fixture_harness import model
        self.assertIs(model.ProtocolFixture().manual_review_required, True)
        self.assertIs(model.ProtocolFixture().ready_for_submission, False)

    def test_existing_intelligence_unaffected(self) -> None:  # 84
        from arkheionx.intelligence.graph import build_protocol_intelligence_graph
        g = build_protocol_intelligence_graph("demo", local_validation_ids=["local-test-result:t1"])
        self.assertIs(g.manual_review_required, True)

    def test_existing_review_package_graph_unaffected(self) -> None:  # 85
        from arkheionx.review_package import collector
        self.assertEqual(collector._REQUIRED_KINDS, {"review_map", "evidence_links", "artifacts_index"})

    def test_existing_local_validation_unaffected(self) -> None:  # 86
        from arkheionx.local_validation import model as lv_model
        self.assertIs(lv_model.LocalValidationSummary().ready_for_submission, False)


if __name__ == "__main__":
    unittest.main()
