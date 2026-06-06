"""Repo-wide fixture-harness safety-consistency QA gate (v3.9).

This module lives under tests/ and is not scanned by the safety-wording gate, so
the forbidden phrases below are used directly as negative assertions. It must not
be weakened merely to pass a grep.
"""
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
from arkheionx.fixture_harness import crossref as X
from arkheionx.fixture_harness import snapshots as S

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TREE = REPO_ROOT / "tests" / "fixtures" / "fixture_harness"

# Overclaim phrases that must never appear in any serialized harness output or
# snapshot. HUMAN_REVIEWED is checked case-sensitively; the rest case-insensitively.
_OVERCLAIM = (
    "confirmed vulnerability", "final severity", "audit passed", "bounty eligible",
    "bounty eligibility", "proves safety", "proves vulnerability", "proves a vulnerability",
    "benchmark pass proves", "benchmark failure proves", "fixture pass proves",
    "fixture failure proves",
)

# Dangerous machine patterns that must never appear in a fixture source. The
# required negated disclaimers ("no RPC", "no fork url", "no private keys", "no
# seed phrases") are deliberately not in this list.
_DANGEROUS = (
    "http://", "https://",
    "rpc-url", "rpc_url", "--rpc-url",
    "fork-url", "fork_url", "--fork-url",
    "privatekey", "private_key",
    "mnemonic",
    "seedphrase", "seed_phrase",
    "vm.broadcast", "startbroadcast", "vm.startbroadcast",
    "exploit",
)


def _benchmarked_suites() -> list[fh.FixtureSuite]:
    return [
        fh.run_fixture_benchmark_suite(fh.build_set1_fixture_suite()),
        fh.run_fixture_benchmark_suite(fh.build_set2_fixture_suite()),
        fh.run_fixture_benchmark_suite(fh.build_set3_fixture_suite()),
        fh.benchmark_all_fixture_suite(),
    ]


def _built_suites() -> list[fh.FixtureSuite]:
    return [
        fh.build_set1_fixture_suite(),
        fh.build_set2_fixture_suite(),
        fh.build_set3_fixture_suite(),
        fh.build_all_fixture_suite(),
    ]


def _records(suite: fh.FixtureSuite) -> list[object]:
    """Every record in a suite that carries the review-state flags."""

    records: list[object] = [suite]
    records += list(suite.fixtures)
    records += list(suite.artifact_refs)
    records += list(suite.runs)
    records += list(suite.results)
    records += list(suite.snapshots)
    return records


class ReviewFlagConsistencyTests(unittest.TestCase):
    def test_every_record_manual_review_required_true(self) -> None:
        for suite in _built_suites() + _benchmarked_suites():
            for rec in _records(suite):
                self.assertIs(rec.manual_review_required, True,
                              f"{type(rec).__name__} in {suite.name}")

    def test_every_record_ready_for_submission_false(self) -> None:
        for suite in _built_suites() + _benchmarked_suites():
            for rec in _records(suite):
                self.assertIs(rec.ready_for_submission, False,
                              f"{type(rec).__name__} in {suite.name}")

    def test_snapshots_review_flags(self) -> None:
        for snap in (S.build_set1_benchmark_snapshot(), S.build_all_benchmark_snapshot()):
            self.assertIs(snap["manual_review_required"], True)
            self.assertIs(snap["ready_for_submission"], False)

    def test_crossrefs_review_flags(self) -> None:
        for cx in (X.build_set1_fixture_crossref(), X.build_all_fixture_crossref()):
            self.assertIs(cx["manual_review_required"], True)
            self.assertIs(cx["ready_for_submission"], False)
            for key in ("benchmark_is_not_audit", "benchmark_is_not_submission",
                        "benchmark_does_not_confirm_vulnerabilities", "manual_review_required"):
                self.assertIs(cx["no_overclaim_context"][key], True, key)


class NoOverclaimTests(unittest.TestCase):
    def _assert_clean(self, blob: str, label: str) -> None:
        self.assertNotIn("HUMAN_REVIEWED", blob, label)
        low = blob.lower()
        for token in _OVERCLAIM:
            self.assertNotIn(token, low, f"{label}: {token}")

    def test_benchmarked_suites_serialized_clean(self) -> None:
        for suite in _benchmarked_suites():
            self._assert_clean(json.dumps(fh.fixture_harness_to_dict(suite)), suite.name)

    def test_snapshots_clean(self) -> None:
        self._assert_clean(json.dumps(S.build_set1_benchmark_snapshot()), "set1-snapshot")
        self._assert_clean(json.dumps(S.build_all_benchmark_snapshot()), "all-snapshot")

    def test_committed_snapshot_files_clean(self) -> None:
        for relpath in (S.SET1_SNAPSHOT_RELPATH, S.ALL_SNAPSHOT_RELPATH):
            self._assert_clean((REPO_ROOT / relpath).read_text(encoding="utf-8"), relpath)

    def test_crossrefs_clean(self) -> None:
        self._assert_clean(json.dumps(X.build_set1_fixture_crossref()), "set1-crossref")
        self._assert_clean(json.dumps(X.build_all_fixture_crossref()), "all-crossref")


class FixtureSourceSafetyTests(unittest.TestCase):
    def _source_files(self) -> list[Path]:
        return sorted(FIXTURE_TREE.rglob("*.sol"))

    def test_nine_source_files_present(self) -> None:
        self.assertEqual(len(self._source_files()), 9)

    def test_sources_have_no_dangerous_patterns(self) -> None:
        for path in self._source_files():
            low = path.read_text(encoding="utf-8").lower()
            for token in _DANGEROUS:
                self.assertNotIn(token, low, f"{path.name}: {token}")

    def test_sources_have_no_hex_addresses(self) -> None:
        for path in self._source_files():
            self.assertIsNone(re.search(r"0x[0-9a-fA-F]{40}", path.read_text(encoding="utf-8")),
                              path.name)

    def test_sources_have_local_static_and_no_human_reviewed(self) -> None:
        for path in self._source_files():
            text = path.read_text(encoding="utf-8")
            self.assertIn("local/static", text.lower(), path.name)
            self.assertNotIn("HUMAN_REVIEWED", text, path.name)

    def test_readmes_clean(self) -> None:
        for readme in sorted(FIXTURE_TREE.rglob("README.md")):
            low = readme.read_text(encoding="utf-8").lower()
            for token in _DANGEROUS:
                self.assertNotIn(token, low, f"{readme}: {token}")


class IdUniquenessAndDeterminismTests(unittest.TestCase):
    def test_all_fixture_ids_unique(self) -> None:
        ids = [f.fixture_id for f in fh.all_fixture_definitions()]
        self.assertEqual(len(set(ids)), 9)

    def test_all_artifact_ids_unique(self) -> None:
        ids = [a.artifact_id for a in fh.all_fixture_artifacts()]
        self.assertEqual(len(set(ids)), 9)

    def test_benchmark_result_ids_unique_per_suite(self) -> None:
        for suite in _benchmarked_suites():
            ids = [r.result_id for r in suite.results]
            self.assertEqual(len(set(ids)), len(ids), suite.name)

    def test_benchmark_run_ids_unique_per_suite(self) -> None:
        for suite in _benchmarked_suites():
            ids = [r.run_id for r in suite.runs]
            self.assertEqual(len(set(ids)), len(ids), suite.name)

    def test_suite_ids_deterministic(self) -> None:
        self.assertEqual(fh.build_set1_fixture_suite().suite_id, fh.build_set1_fixture_suite().suite_id)
        self.assertEqual(fh.build_set2_fixture_suite().suite_id, fh.build_set2_fixture_suite().suite_id)
        self.assertEqual(fh.build_set3_fixture_suite().suite_id, fh.build_set3_fixture_suite().suite_id)
        self.assertEqual(fh.build_all_fixture_suite().suite_id, fh.build_all_fixture_suite().suite_id)

    def test_set_suite_ids_distinct(self) -> None:
        ids = {
            fh.build_set1_fixture_suite().suite_id,
            fh.build_set2_fixture_suite().suite_id,
            fh.build_set3_fixture_suite().suite_id,
            fh.build_all_fixture_suite().suite_id,
        }
        self.assertEqual(len(ids), 4)


class JsonSafetyTests(unittest.TestCase):
    def test_suites_json_safe(self) -> None:
        for suite in _benchmarked_suites():
            json.dumps(fh.fixture_harness_to_dict(suite))

    def test_snapshots_json_safe(self) -> None:
        json.dumps(S.build_set1_benchmark_snapshot())
        json.dumps(S.build_all_benchmark_snapshot())

    def test_crossrefs_json_safe(self) -> None:
        json.dumps(X.build_set1_fixture_crossref())
        json.dumps(X.build_all_fixture_crossref())

    def test_outputs_have_no_absolute_or_home_paths(self) -> None:
        blobs = [json.dumps(fh.fixture_harness_to_dict(s)) for s in _benchmarked_suites()]
        blobs += [json.dumps(S.build_all_benchmark_snapshot()), json.dumps(X.build_all_fixture_crossref())]
        for blob in blobs:
            self.assertNotIn(str(REPO_ROOT), blob)
            self.assertNotIn("/home/", blob)
            self.assertNotIn("/tmp/", blob)


class ImportSideEffectTests(unittest.TestCase):
    def test_full_package_import_side_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code = (
                "import os; before=set(os.listdir('.'));"
                "import arkheionx.fixture_harness as fh;"
                "fh.benchmark_all_fixture_suite(); fh.build_all_benchmark_snapshot();"
                "fh.build_all_fixture_crossref();"
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
