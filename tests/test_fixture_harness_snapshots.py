"""Tests for the deterministic benchmark snapshot baselines (v3.9)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import arkheionx.fixture_harness as fh
from arkheionx.fixture_harness import snapshots as S

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_FILE = REPO_ROOT / S.SET1_SNAPSHOT_RELPATH

# Overclaim tokens that must never appear in a snapshot. (This file lives under
# tests/ and is not scanned by the safety-wording gate, so the literals are used
# directly here as negative assertions.)
_OVERCLAIM = (
    "confirmed vulnerability", "final severity", "audit passed", "bounty eligible",
    "bounty eligibility", "proves safety", "proves vulnerability", "proves a vulnerability",
)

_REQUIRED_KEYS = (
    "snapshot_schema_version", "fixture_suite_name", "fixture_suite_id",
    "fixture_count", "artifact_count", "result_count", "drift_count",
    "fixture_ids", "artifact_ids", "result_ids", "benchmark_dimensions",
    "expected_artifact_kinds", "safety_flags", "manual_review_required",
    "ready_for_submission", "neutral_notice",
)


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snap = S.build_set1_benchmark_snapshot()

    def test_build_returns_dict_with_required_keys(self) -> None:  # 1
        self.assertIsInstance(self.snap, dict)
        for key in _REQUIRED_KEYS:
            self.assertIn(key, self.snap, key)

    def test_build_counts(self) -> None:  # 2
        self.assertEqual(self.snap["fixture_count"], 3)
        self.assertEqual(self.snap["artifact_count"], 3)
        self.assertEqual(self.snap["result_count"], 63)
        self.assertEqual(self.snap["drift_count"], 0)

    def test_build_ids_sorted_and_unique(self) -> None:  # 3
        for key in ("fixture_ids", "artifact_ids", "result_ids"):
            ids = self.snap[key]
            self.assertEqual(ids, sorted(ids), key)
            self.assertEqual(len(ids), len(set(ids)), key)
        self.assertEqual(len(self.snap["fixture_ids"]), 3)
        self.assertEqual(len(self.snap["artifact_ids"]), 3)
        self.assertEqual(len(self.snap["result_ids"]), 63)

    def test_build_schema_version(self) -> None:  # 4
        self.assertEqual(self.snap["snapshot_schema_version"], S.SNAPSHOT_SCHEMA_VERSION)
        self.assertEqual(self.snap["fixture_suite_name"], "fixture-harness-set1")
        self.assertTrue(str(self.snap["fixture_suite_id"]).startswith("fixture-suite:"))

    def test_build_deterministic(self) -> None:  # 5
        self.assertEqual(self.snap, S.build_set1_benchmark_snapshot())
        a = json.dumps(self.snap, sort_keys=True)
        b = json.dumps(S.build_set1_benchmark_snapshot(), sort_keys=True)
        self.assertEqual(a, b)

    def test_build_json_serializable(self) -> None:  # 6
        json.dumps(self.snap)  # must not raise

    def test_safety_flags_all_true(self) -> None:  # 7
        flags = self.snap["safety_flags"]
        self.assertIsInstance(flags, dict)
        self.assertTrue(flags)  # non-empty
        self.assertTrue(all(v is True for v in flags.values()), flags)

    def test_review_state_booleans(self) -> None:  # 8
        self.assertIs(self.snap["manual_review_required"], True)
        self.assertIs(self.snap["ready_for_submission"], False)

    def test_neutral_notice_text(self) -> None:  # 9
        self.assertEqual(
            self.snap["neutral_notice"],
            "Snapshot is deterministic benchmark context only. Manual review remains required.",
        )

    def test_no_overclaim_wording(self) -> None:  # 10
        blob = json.dumps(self.snap)
        self.assertNotIn("HUMAN_REVIEWED", blob)
        low = blob.lower()
        for token in _OVERCLAIM:
            self.assertNotIn(token, low, token)

    def test_no_paths_or_host_data(self) -> None:  # 11
        blob = json.dumps(self.snap)
        self.assertNotIn(str(REPO_ROOT), blob)
        self.assertNotIn("/home/", blob)
        self.assertNotIn("/tmp/", blob)
        self.assertNotIn(".sol", blob)  # no source relative paths leak in


class CommittedBaselineTests(unittest.TestCase):
    def test_snapshot_file_exists(self) -> None:  # 12
        self.assertTrue(SNAPSHOT_FILE.is_file(), str(SNAPSHOT_FILE))

    def test_snapshot_file_valid_json(self) -> None:  # 13
        data = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)

    def test_load_returns_committed(self) -> None:  # 14
        loaded = S.load_set1_benchmark_snapshot()
        on_disk = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        self.assertEqual(loaded, on_disk)

    def test_generated_equals_committed(self) -> None:  # 15
        self.assertEqual(S.build_set1_benchmark_snapshot(), S.load_set1_benchmark_snapshot())

    def test_committed_has_required_keys(self) -> None:  # 16
        loaded = S.load_set1_benchmark_snapshot()
        for key in _REQUIRED_KEYS:
            self.assertIn(key, loaded, key)

    def test_committed_no_overclaim(self) -> None:  # 17
        blob = SNAPSHOT_FILE.read_text(encoding="utf-8")
        self.assertNotIn("HUMAN_REVIEWED", blob)
        low = blob.lower()
        for token in _OVERCLAIM:
            self.assertNotIn(token, low, token)


class CompareTests(unittest.TestCase):
    def test_compare_no_drift_against_committed(self) -> None:  # 18
        result = S.compare_set1_benchmark_snapshot()
        self.assertIs(result["matches"], True)
        self.assertEqual(result["drift_count"], 0)
        self.assertEqual(result["differences"], [])

    def test_compare_explicit_equal(self) -> None:  # 19
        snap = S.build_set1_benchmark_snapshot()
        result = S.compare_set1_benchmark_snapshot(observed=snap, baseline=snap)
        self.assertIs(result["matches"], True)
        self.assertEqual(result["drift_count"], 0)

    def test_compare_detects_count_drift(self) -> None:  # 20
        drifted = S.build_set1_benchmark_snapshot()
        drifted["result_count"] = 999
        result = S.compare_set1_benchmark_snapshot(observed=drifted)
        self.assertIs(result["matches"], False)
        self.assertGreaterEqual(result["drift_count"], 1)
        fields = {d["field"] for d in result["differences"]}
        self.assertIn("result_count", fields)

    def test_compare_detects_id_drift(self) -> None:  # 21
        drifted = S.build_set1_benchmark_snapshot()
        drifted["fixture_ids"] = list(drifted["fixture_ids"]) + ["fixture:extra:x:deadbeef"]
        result = S.compare_set1_benchmark_snapshot(observed=drifted)
        self.assertIs(result["matches"], False)
        self.assertIn("fixture_ids", {d["field"] for d in result["differences"]})

    def test_compare_result_is_neutral(self) -> None:  # 22
        result = S.compare_set1_benchmark_snapshot()
        self.assertIs(result["manual_review_required"], True)
        self.assertIs(result["ready_for_submission"], False)
        blob = json.dumps(result).lower()
        for token in _OVERCLAIM:
            self.assertNotIn(token, blob, token)
        self.assertNotIn("HUMAN_REVIEWED", json.dumps(result))


class JsonableTests(unittest.TestCase):
    def test_snapshot_to_jsonable_idempotent(self) -> None:  # 23
        snap = S.build_set1_benchmark_snapshot()
        self.assertEqual(S.snapshot_to_jsonable(snap), snap)

    def test_snapshot_to_jsonable_rejects_non_mapping(self) -> None:  # 24
        with self.assertRaises(TypeError):
            S.snapshot_to_jsonable([1, 2, 3])


class ExportAndImportTests(unittest.TestCase):
    def test_package_exports_snapshot_helpers(self) -> None:  # 25
        for name in ("build_set1_benchmark_snapshot", "load_set1_benchmark_snapshot",
                     "compare_set1_benchmark_snapshot", "snapshot_to_jsonable",
                     "SNAPSHOT_SCHEMA_VERSION", "SET1_SNAPSHOT_RELPATH"):
            self.assertIn(name, fh.__all__, name)
            self.assertTrue(hasattr(fh, name), name)

    def test_import_side_effect_free(self) -> None:  # 26
        with tempfile.TemporaryDirectory() as tmp:
            code = (
                "import os; before=set(os.listdir('.'));"
                "import arkheionx.fixture_harness.snapshots as s;"
                "assert set(os.listdir('.'))==before, 'created files on import';"
                "assert not os.path.exists('.arkheionx'), '.arkheionx created';"
                "print('clean')"
            )
            env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
            result = subprocess.run([sys.executable, "-c", code], cwd=tmp, text=True,
                                    capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("clean", result.stdout)


class CompatibilityTests(unittest.TestCase):
    def test_runner_unaffected(self) -> None:  # 27
        suite = fh.benchmark_set1_fixture_suite()
        self.assertEqual(suite.result_count, 63)
        self.assertEqual(suite.drift_count, 0)

    def test_set1_registry_unaffected(self) -> None:  # 28
        self.assertEqual(fh.build_set1_fixture_suite().fixture_count, 3)


if __name__ == "__main__":
    unittest.main()
