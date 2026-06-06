"""Tests for the standalone fixture benchmark crossref module (v3.9)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import arkheionx.fixture_harness as fh
from arkheionx.fixture_harness import crossref as X

REPO_ROOT = Path(__file__).resolve().parents[1]

_OVERCLAIM = (
    "confirmed vulnerability", "final severity", "audit passed", "bounty eligible",
    "bounty eligibility", "proves safety", "proves vulnerability", "proves a vulnerability",
)
_REQUIRED_KEYS = (
    "fixture_suite_id", "fixture_count", "artifact_count", "result_count",
    "fixture_ids", "artifact_ids", "benchmark_result_ids",
    "manual_review_required", "ready_for_submission",
    "review_context_available", "local_validation_context_available",
    "evidence_context_available", "no_overclaim_context",
)
_NO_OVERCLAIM_KEYS = (
    "benchmark_is_not_audit", "benchmark_is_not_submission",
    "benchmark_does_not_confirm_vulnerabilities", "manual_review_required",
)


class Set1CrossrefTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cx = X.build_set1_fixture_crossref()

    def test_required_keys_present(self) -> None:  # 1
        for key in _REQUIRED_KEYS:
            self.assertIn(key, self.cx, key)

    def test_counts(self) -> None:  # 2
        self.assertEqual(self.cx["fixture_count"], 3)
        self.assertEqual(self.cx["artifact_count"], 3)
        self.assertEqual(self.cx["result_count"], 63)

    def test_id_lists(self) -> None:  # 3
        self.assertEqual(len(self.cx["fixture_ids"]), 3)
        self.assertEqual(len(self.cx["artifact_ids"]), 3)
        self.assertEqual(len(self.cx["benchmark_result_ids"]), 63)
        for key in ("fixture_ids", "artifact_ids", "benchmark_result_ids"):
            self.assertEqual(self.cx[key], sorted(self.cx[key]), key)

    def test_suite_id(self) -> None:  # 4
        self.assertTrue(str(self.cx["fixture_suite_id"]).startswith("fixture-suite:fixture-harness-set1:"))

    def test_review_flags(self) -> None:  # 5
        self.assertIs(self.cx["manual_review_required"], True)
        self.assertIs(self.cx["ready_for_submission"], False)

    def test_context_available_flags_are_bool(self) -> None:  # 6
        for key in ("review_context_available", "local_validation_context_available",
                    "evidence_context_available"):
            self.assertIsInstance(self.cx[key], bool)

    def test_no_overclaim_context_block(self) -> None:  # 7
        block = self.cx["no_overclaim_context"]
        self.assertIsInstance(block, dict)
        for key in _NO_OVERCLAIM_KEYS:
            self.assertIs(block[key], True, key)

    def test_deterministic(self) -> None:  # 8
        self.assertEqual(self.cx, X.build_set1_fixture_crossref())

    def test_json_safe(self) -> None:  # 9
        json.dumps(self.cx)  # must not raise

    def test_no_overclaim_wording(self) -> None:  # 10
        blob = json.dumps(self.cx)
        self.assertNotIn("HUMAN_REVIEWED", blob)
        low = blob.lower()
        for token in _OVERCLAIM:
            self.assertNotIn(token, low, token)

    def test_no_paths(self) -> None:  # 11
        blob = json.dumps(self.cx)
        self.assertNotIn(str(REPO_ROOT), blob)
        self.assertNotIn("/home/", blob)
        self.assertNotIn("/tmp/", blob)
        self.assertNotIn(".sol", blob)


class AllCrossrefTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cx = X.build_all_fixture_crossref()

    def test_counts(self) -> None:  # 12
        self.assertEqual(self.cx["fixture_count"], 9)
        self.assertEqual(self.cx["artifact_count"], 9)
        self.assertEqual(self.cx["result_count"], 189)
        self.assertEqual(len(self.cx["benchmark_result_ids"]), 189)

    def test_suite_id(self) -> None:  # 13
        self.assertTrue(str(self.cx["fixture_suite_id"]).startswith("fixture-suite:fixture-harness-all:"))

    def test_deterministic(self) -> None:  # 14
        self.assertEqual(self.cx, X.build_all_fixture_crossref())

    def test_distinct_from_set1(self) -> None:  # 15
        self.assertNotEqual(self.cx["fixture_suite_id"],
                            X.build_set1_fixture_crossref()["fixture_suite_id"])

    def test_review_flags_and_no_overclaim(self) -> None:  # 16
        self.assertIs(self.cx["manual_review_required"], True)
        self.assertIs(self.cx["ready_for_submission"], False)
        for key in _NO_OVERCLAIM_KEYS:
            self.assertIs(self.cx["no_overclaim_context"][key], True, key)

    def test_no_overclaim_wording(self) -> None:  # 17
        blob = json.dumps(self.cx)
        self.assertNotIn("HUMAN_REVIEWED", blob)
        low = blob.lower()
        for token in _OVERCLAIM:
            self.assertNotIn(token, low, token)


class GenericCrossrefTests(unittest.TestCase):
    def test_build_from_unbenchmarked_suite_has_empty_results(self) -> None:  # 18
        cx = X.build_fixture_benchmark_crossref(fh.build_set1_fixture_suite())
        self.assertEqual(cx["result_count"], 0)
        self.assertEqual(cx["benchmark_result_ids"], [])
        self.assertEqual(cx["fixture_count"], 3)

    def test_does_not_mutate_input_suite(self) -> None:  # 19
        suite = fh.benchmark_all_fixture_suite()
        before = json.dumps(fh.fixture_harness_to_dict(suite), sort_keys=True)
        X.build_fixture_benchmark_crossref(suite)
        self.assertEqual(json.dumps(fh.fixture_harness_to_dict(suite), sort_keys=True), before)

    def test_benchmark_result_ids_match_suite(self) -> None:  # 20
        suite = fh.benchmark_set1_fixture_suite()
        cx = X.build_fixture_benchmark_crossref(suite)
        self.assertEqual(set(cx["benchmark_result_ids"]), {r.result_id for r in suite.results})


class ExportImportTests(unittest.TestCase):
    def test_package_exports_crossref_helpers(self) -> None:  # 21
        for name in ("build_fixture_benchmark_crossref", "build_set1_fixture_crossref",
                     "build_all_fixture_crossref"):
            self.assertIn(name, fh.__all__, name)
            self.assertTrue(hasattr(fh, name), name)

    def test_import_side_effect_free(self) -> None:  # 22
        with tempfile.TemporaryDirectory() as tmp:
            code = (
                "import os; before=set(os.listdir('.'));"
                "import arkheionx.fixture_harness.crossref as c;"
                "c.build_set1_fixture_crossref(); c.build_all_fixture_crossref();"
                "assert set(os.listdir('.'))==before, 'created files';"
                "assert not os.path.exists('.arkheionx'), '.arkheionx created';"
                "print('clean')"
            )
            env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
            result = subprocess.run([sys.executable, "-c", code], cwd=tmp, text=True,
                                    capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("clean", result.stdout)


class CompatibilityTests(unittest.TestCase):
    def test_runner_and_snapshot_unaffected(self) -> None:  # 23
        self.assertEqual(fh.benchmark_all_fixture_suite().result_count, 189)
        self.assertEqual(fh.build_set1_benchmark_snapshot(), fh.load_set1_benchmark_snapshot())

    def test_review_package_import_unaffected(self) -> None:  # 24
        from arkheionx.review_package import collector
        self.assertEqual(collector._REQUIRED_KINDS, {"review_map", "evidence_links", "artifacts_index"})

    def test_local_validation_import_unaffected(self) -> None:  # 25
        from arkheionx.local_validation import model as lv_model
        self.assertIs(lv_model.LocalValidationSummary().ready_for_submission, False)


if __name__ == "__main__":
    unittest.main()
