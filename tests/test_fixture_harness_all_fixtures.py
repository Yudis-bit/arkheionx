"""Tests for the combined all-fixtures benchmark integration (v3.9)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import arkheionx.fixture_harness as fh
from arkheionx.fixture_harness import fixtures as reg
from arkheionx.fixture_harness import snapshots as S

REPO_ROOT = Path(__file__).resolve().parents[1]
ALL_SNAPSHOT_FILE = REPO_ROOT / S.ALL_SNAPSHOT_RELPATH
SET1_SNAPSHOT_FILE = REPO_ROOT / S.SET1_SNAPSHOT_RELPATH

_OVERCLAIM = (
    "confirmed vulnerability", "final severity", "audit passed", "bounty eligible",
    "bounty eligibility", "proves safety", "proves vulnerability", "proves a vulnerability",
)


class AllRegistryTests(unittest.TestCase):
    def test_all_definitions_returns_nine(self) -> None:  # 1
        self.assertEqual(len(fh.all_fixture_definitions()), 9)

    def test_all_artifacts_returns_nine(self) -> None:  # 2
        self.assertEqual(len(fh.all_fixture_artifacts()), 9)

    def test_set_order_is_set1_set2_set3(self) -> None:  # 3
        names = [f.name for f in fh.all_fixture_definitions()]
        self.assertEqual(names, [
            "erc20_like", "lending_vault", "staking_reward",
            "amm_swap", "oracle_dependent", "upgradeable_proxy",
            "bridge_message", "liquidation_engine", "governance_timelock",
        ])

    def test_all_fixture_ids_unique(self) -> None:  # 4
        ids = [f.fixture_id for f in fh.all_fixture_definitions()]
        self.assertEqual(len(set(ids)), 9)

    def test_all_artifact_ids_unique(self) -> None:  # 5
        ids = [a.artifact_id for a in fh.all_fixture_artifacts()]
        self.assertEqual(len(set(ids)), 9)

    def test_all_definitions_deterministic(self) -> None:  # 6
        self.assertEqual([f.fixture_id for f in fh.all_fixture_definitions()],
                         [f.fixture_id for f in fh.all_fixture_definitions()])

    def test_all_ids_are_union_of_sets(self) -> None:  # 7
        union = ({f.fixture_id for f in reg.set1_fixture_definitions()}
                 | {f.fixture_id for f in reg.set2_fixture_definitions()}
                 | {f.fixture_id for f in reg.set3_fixture_definitions()})
        self.assertEqual({f.fixture_id for f in fh.all_fixture_definitions()}, union)


class AllSuiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = fh.build_all_fixture_suite()

    def test_fixture_count_nine(self) -> None:  # 8
        self.assertEqual(self.suite.fixture_count, 9)

    def test_artifact_count_nine(self) -> None:  # 9
        self.assertEqual(len(self.suite.artifact_refs), 9)

    def test_suite_id_deterministic(self) -> None:  # 10
        self.assertEqual(self.suite.suite_id, fh.build_all_fixture_suite().suite_id)
        self.assertTrue(self.suite.suite_id.startswith("fixture-suite:fixture-harness-all:"))

    def test_suite_id_order_stable(self) -> None:  # 11
        defs = fh.all_fixture_definitions()
        forward = fh.build_fixture_suite(reg.ALL_SUITE_NAME, fixtures=defs).suite_id
        reverse = fh.build_fixture_suite(reg.ALL_SUITE_NAME, fixtures=list(reversed(defs))).suite_id
        self.assertEqual(forward, reverse)

    def test_suite_id_distinct_from_sets(self) -> None:  # 12
        self.assertNotIn(self.suite.suite_id, {
            reg.build_set1_fixture_suite().suite_id,
            reg.build_set2_fixture_suite().suite_id,
            reg.build_set3_fixture_suite().suite_id,
        })

    def test_suite_review_flags(self) -> None:  # 13
        self.assertIs(self.suite.manual_review_required, True)
        self.assertIs(self.suite.ready_for_submission, False)

    def test_result_count_zero_before_benchmark(self) -> None:  # 14
        self.assertEqual(self.suite.result_count, 0)


class AllBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = fh.benchmark_all_fixture_suite()

    def test_returns_fixture_suite(self) -> None:  # 15
        self.assertIsInstance(self.suite, fh.FixtureSuite)

    def test_fixture_and_run_counts(self) -> None:  # 16
        self.assertEqual(self.suite.fixture_count, 9)
        self.assertEqual(self.suite.run_count, 9)

    def test_result_count_exceeds_set1(self) -> None:  # 17
        self.assertGreater(self.suite.result_count, fh.benchmark_set1_fixture_suite().result_count)

    def test_drift_count_zero(self) -> None:  # 18
        self.assertEqual(self.suite.drift_count, 0)

    def test_runs_executed(self) -> None:  # 19
        self.assertEqual({r.run_status for r in self.suite.runs}, {fh.FIXTURE_RUN_EXECUTED})

    def test_result_ids_unique(self) -> None:  # 20
        ids = [r.result_id for r in self.suite.results]
        self.assertEqual(len(set(ids)), len(ids))

    def test_deterministic_serialization(self) -> None:  # 21
        a = json.dumps(fh.fixture_harness_to_dict(self.suite), sort_keys=True)
        b = json.dumps(fh.fixture_harness_to_dict(fh.benchmark_all_fixture_suite()), sort_keys=True)
        self.assertEqual(a, b)

    def test_no_overclaim(self) -> None:  # 22
        blob = json.dumps(fh.fixture_harness_to_dict(self.suite))
        self.assertNotIn("HUMAN_REVIEWED", blob)
        low = blob.lower()
        for token in _OVERCLAIM:
            self.assertNotIn(token, low, token)


class AllSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snap = S.build_all_benchmark_snapshot()

    def test_snapshot_file_exists(self) -> None:  # 23
        self.assertTrue(ALL_SNAPSHOT_FILE.is_file(), str(ALL_SNAPSHOT_FILE))

    def test_snapshot_file_valid_json(self) -> None:  # 24
        self.assertIsInstance(json.loads(ALL_SNAPSHOT_FILE.read_text(encoding="utf-8")), dict)

    def test_generated_equals_committed(self) -> None:  # 25
        self.assertEqual(self.snap, S.load_all_benchmark_snapshot())

    def test_snapshot_counts(self) -> None:  # 26
        self.assertEqual(self.snap["fixture_count"], 9)
        self.assertEqual(self.snap["artifact_count"], 9)
        self.assertEqual(self.snap["drift_count"], 0)
        self.assertEqual(self.snap["fixture_suite_name"], "fixture-harness-all")

    def test_snapshot_result_count_exceeds_set1(self) -> None:  # 27
        self.assertGreater(self.snap["result_count"], S.build_set1_benchmark_snapshot()["result_count"])

    def test_snapshot_id_lists_lengths(self) -> None:  # 28
        self.assertEqual(len(self.snap["fixture_ids"]), 9)
        self.assertEqual(len(self.snap["artifact_ids"]), 9)

    def test_snapshot_review_flags(self) -> None:  # 29
        self.assertIs(self.snap["manual_review_required"], True)
        self.assertIs(self.snap["ready_for_submission"], False)

    def test_snapshot_no_overclaim_or_paths(self) -> None:  # 30
        blob = ALL_SNAPSHOT_FILE.read_text(encoding="utf-8")
        self.assertNotIn("HUMAN_REVIEWED", blob)
        self.assertNotIn(str(REPO_ROOT), blob)
        self.assertNotIn("/home/", blob)
        self.assertNotIn(".sol", blob)
        low = blob.lower()
        for token in _OVERCLAIM:
            self.assertNotIn(token, low, token)

    def test_compare_no_drift(self) -> None:  # 31
        result = S.compare_all_benchmark_snapshot()
        self.assertIs(result["matches"], True)
        self.assertEqual(result["drift_count"], 0)

    def test_compare_detects_drift(self) -> None:  # 32
        drifted = S.build_all_benchmark_snapshot()
        drifted["result_count"] = 1
        result = S.compare_all_benchmark_snapshot(observed=drifted)
        self.assertIs(result["matches"], False)
        self.assertIn("result_count", {d["field"] for d in result["differences"]})

    def test_compare_result_neutral(self) -> None:  # 33
        result = S.compare_all_benchmark_snapshot()
        self.assertIs(result["manual_review_required"], True)
        self.assertIs(result["ready_for_submission"], False)


class Set1UnchangedTests(unittest.TestCase):
    def test_set1_snapshot_still_matches_build(self) -> None:  # 34
        self.assertEqual(S.build_set1_benchmark_snapshot(), S.load_set1_benchmark_snapshot())

    def test_set1_snapshot_file_distinct_from_all(self) -> None:  # 35
        self.assertNotEqual(SET1_SNAPSHOT_FILE, ALL_SNAPSHOT_FILE)
        self.assertTrue(SET1_SNAPSHOT_FILE.is_file())

    def test_set1_benchmark_result_count_unchanged(self) -> None:  # 36
        self.assertEqual(fh.benchmark_set1_fixture_suite().result_count, 63)

    def test_set1_suite_id_unchanged(self) -> None:  # 37
        self.assertEqual(reg.build_set1_fixture_suite().suite_id,
                         "fixture-suite:fixture-harness-set1:6a60a898b566")


class ExportAndImportTests(unittest.TestCase):
    def test_package_exports_all_helpers(self) -> None:  # 38
        for name in ("ALL_SUITE_NAME", "all_fixture_definitions", "all_fixture_artifacts",
                     "build_all_fixture_suite", "benchmark_all_fixture_suite",
                     "ALL_SNAPSHOT_RELPATH", "build_all_benchmark_snapshot",
                     "load_all_benchmark_snapshot", "compare_all_benchmark_snapshot"):
            self.assertIn(name, fh.__all__, name)
            self.assertTrue(hasattr(fh, name), name)

    def test_import_side_effect_free(self) -> None:  # 39
        with tempfile.TemporaryDirectory() as tmp:
            code = (
                "import os; before=set(os.listdir('.'));"
                "import arkheionx.fixture_harness as fh;"
                "fh.build_all_fixture_suite(); fh.benchmark_all_fixture_suite();"
                "fh.build_all_benchmark_snapshot();"
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
