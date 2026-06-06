"""Tests for the fixture benchmark runner (v3.9): runs, results, suite, safety."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import arkheionx.fixture_harness as fh
from arkheionx.fixture_harness import model as M
from arkheionx.fixture_harness import runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_SRC = REPO_ROOT / "arkheionx" / "fixture_harness" / "runner.py"

# Overclaim tokens that must never appear in serialized benchmark output. (This
# test file lives under tests/ and is not scanned by the safety-wording gate, so
# the literal forms are used directly here as negative assertions.)
_OVERCLAIM = (
    "confirmed vulnerability", "final severity", "audit passed", "bounty eligible",
    "bounty eligibility", "proves safety", "proves vulnerability", "proves a vulnerability",
    "benchmark pass proves", "benchmark failure proves", "fixture pass proves",
    "fixture failure proves",
)


def _blob(suite: M.FixtureSuite) -> str:
    return json.dumps(fh.fixture_harness_to_dict(suite), sort_keys=True)


class SuiteBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = fh.benchmark_set1_fixture_suite()

    def test_returns_fixture_suite(self) -> None:  # 1
        self.assertIsInstance(self.suite, M.FixtureSuite)

    def test_fixture_count_three(self) -> None:  # 2
        self.assertEqual(self.suite.fixture_count, 3)

    def test_run_count_three(self) -> None:  # 3
        self.assertEqual(self.suite.run_count, 3)

    def test_result_count_positive(self) -> None:  # 4
        self.assertGreater(self.suite.result_count, 0)
        self.assertEqual(self.suite.result_count, len(self.suite.results))

    def test_drift_count_zero(self) -> None:  # 5
        self.assertEqual(self.suite.drift_count, 0)
        self.assertTrue(all(r.drift_detected is False for r in self.suite.results))

    def test_no_snapshots(self) -> None:  # 6
        self.assertEqual(self.suite.snapshots, [])

    def test_manual_review_required_true(self) -> None:  # 7
        self.assertIs(self.suite.manual_review_required, True)
        self.assertTrue(all(r.manual_review_required is True for r in self.suite.results))
        self.assertTrue(all(r.manual_review_required is True for r in self.suite.runs))

    def test_ready_for_submission_false(self) -> None:  # 8
        self.assertIs(self.suite.ready_for_submission, False)
        self.assertTrue(all(r.ready_for_submission is False for r in self.suite.results))
        self.assertTrue(all(r.ready_for_submission is False for r in self.suite.runs))

    def test_fixture_ids_present(self) -> None:  # 9
        self.assertEqual(len(self.suite.fixtures), 3)
        for f in self.suite.fixtures:
            self.assertTrue(f.fixture_id.startswith("fixture:"))

    def test_artifact_ids_present(self) -> None:  # 10
        self.assertEqual(len(self.suite.artifact_refs), 3)
        for a in self.suite.artifact_refs:
            self.assertTrue(a.artifact_id.startswith("fixture-artifact:"))

    def test_runs_reference_known_fixtures(self) -> None:  # 11
        fixture_ids = {f.fixture_id for f in self.suite.fixtures}
        for run in self.suite.runs:
            self.assertIn(run.fixture_id, fixture_ids)
            self.assertTrue(run.run_id.startswith("fixture-run:"))

    def test_results_reference_known_runs(self) -> None:  # 12
        run_ids = {r.run_id for r in self.suite.runs}
        for res in self.suite.results:
            self.assertIn(res.run_id, run_ids)
            self.assertTrue(res.result_id.startswith("fixture-result:"))

    def test_result_ids_unique(self) -> None:  # 13
        ids = [r.result_id for r in self.suite.results]
        self.assertEqual(len(set(ids)), len(ids))

    def test_runs_executed_for_present_sources(self) -> None:  # 14
        # Set 1 source files exist and are read as text, so every run is EXECUTED.
        self.assertEqual({r.run_status for r in self.suite.runs}, {M.FIXTURE_RUN_EXECUTED})

    def test_all_results_observed(self) -> None:  # 15
        self.assertEqual({r.result_status for r in self.suite.results}, {M.FIXTURE_RESULT_OBSERVED})

    def test_source_text_checks_present_and_clean(self) -> None:  # 16
        kinds = {(r.fixture_id, r.result_kind): r for r in self.suite.results}
        for f in self.suite.fixtures:
            marker = kinds[(f.fixture_id, "source_text_local_static_wording")]
            self.assertIs(marker.observed_value, True)
            danger = kinds[(f.fixture_id, "source_text_no_dangerous_patterns")]
            self.assertIs(danger.observed_value, True)
            present = kinds[(f.fixture_id, "artifact_source_present")]
            self.assertIs(present.observed_value, True)


class SerializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = fh.benchmark_set1_fixture_suite()

    def test_serialization_json_safe(self) -> None:  # 17
        json.dumps(fh.fixture_harness_to_dict(self.suite))  # must not raise

    def test_repeated_serialization_deterministic(self) -> None:  # 18
        self.assertEqual(_blob(self.suite), _blob(fh.benchmark_set1_fixture_suite()))

    def test_suite_id_deterministic(self) -> None:  # 19
        self.assertEqual(self.suite.suite_id, fh.benchmark_set1_fixture_suite().suite_id)
        self.assertTrue(self.suite.suite_id.startswith("fixture-suite:fixture-harness-set1:"))

    def test_suite_id_matches_unbenchmarked_suite(self) -> None:  # 20
        # Benchmarking adds runs/results but does not change the suite identity.
        self.assertEqual(self.suite.suite_id, fh.build_set1_fixture_suite().suite_id)

    def test_no_human_reviewed(self) -> None:  # 21
        self.assertNotIn("HUMAN_REVIEWED", _blob(self.suite))

    def test_no_overclaim_wording(self) -> None:  # 22
        low = _blob(self.suite).lower()
        for token in _OVERCLAIM:
            self.assertNotIn(token, low, token)

    def test_no_absolute_paths_in_output(self) -> None:  # 23
        blob = _blob(self.suite)
        self.assertNotIn(str(REPO_ROOT), blob)
        self.assertNotIn("/home/", blob)


class PerFixtureRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = fh.set1_fixture_definitions()[0]
        self.arts = [a for a in fh.set1_fixture_artifacts()
                     if a.fixture_id == self.fixture.fixture_id]

    def test_returns_fixture_run(self) -> None:  # 24
        run = fh.run_fixture_benchmark(self.fixture, self.arts)
        self.assertIsInstance(run, M.FixtureRun)

    def test_preserves_fixture_id(self) -> None:  # 25
        run = fh.run_fixture_benchmark(self.fixture, self.arts)
        self.assertEqual(run.fixture_id, self.fixture.fixture_id)

    def test_deterministic_per_fixture(self) -> None:  # 26
        a = fh.run_fixture_benchmark(self.fixture, self.arts)
        b = fh.run_fixture_benchmark(self.fixture, self.arts)
        self.assertEqual(a.run_id, b.run_id)
        self.assertEqual(a.run_status, b.run_status)
        self.assertEqual(a.input_artifact_ids, b.input_artifact_ids)
        self.assertEqual(a.warnings, b.warnings)

    def test_does_not_mutate_input(self) -> None:  # 27
        before_f = json.dumps(fh.fixture_harness_to_dict(self.fixture), sort_keys=True)
        before_a = [json.dumps(fh.fixture_harness_to_dict(a), sort_keys=True) for a in self.arts]
        fh.run_fixture_benchmark(self.fixture, self.arts)
        self.assertEqual(json.dumps(fh.fixture_harness_to_dict(self.fixture), sort_keys=True), before_f)
        self.assertEqual([json.dumps(fh.fixture_harness_to_dict(a), sort_keys=True) for a in self.arts],
                         before_a)
        self.assertEqual(self.fixture.warnings, [])

    def test_run_without_artifacts_is_neutral(self) -> None:  # 28
        run = fh.run_fixture_benchmark(self.fixture, None)
        self.assertIsInstance(run, M.FixtureRun)
        self.assertEqual(run.input_artifact_ids, [])

    def test_run_status_executed_for_set1(self) -> None:  # 29
        run = fh.run_fixture_benchmark(self.fixture, self.arts)
        self.assertEqual(run.run_status, M.FIXTURE_RUN_EXECUTED)

    def test_run_metadata_deterministic_and_clean(self) -> None:  # 30
        run = fh.run_fixture_benchmark(self.fixture, self.arts)
        self.assertEqual(run.metadata["benchmark_version"], "v1")
        self.assertEqual(run.metadata["needs_review_count"], 0)
        self.assertNotIn(str(REPO_ROOT), json.dumps(fh.fixture_harness_to_dict(run)))


class SuiteRunnerGenericTests(unittest.TestCase):
    def test_run_suite_preserves_identity_and_adds_records(self) -> None:  # 31
        base = fh.build_set1_fixture_suite()
        out = fh.run_fixture_benchmark_suite(base)
        self.assertEqual(out.suite_id, base.suite_id)
        self.assertEqual(out.name, base.name)
        self.assertEqual(out.fixture_count, base.fixture_count)
        self.assertGreater(out.result_count, 0)
        self.assertEqual(out.run_count, 3)

    def test_run_suite_does_not_mutate_input(self) -> None:  # 32
        base = fh.build_set1_fixture_suite()
        before = json.dumps(fh.fixture_harness_to_dict(base), sort_keys=True)
        fh.run_fixture_benchmark_suite(base)
        self.assertEqual(json.dumps(fh.fixture_harness_to_dict(base), sort_keys=True), before)
        self.assertEqual(base.run_count, 0)
        self.assertEqual(base.result_count, 0)

    def test_empty_suite_benchmarks_to_empty(self) -> None:  # 33
        empty = fh.build_fixture_suite("empty-suite")
        out = fh.run_fixture_benchmark_suite(empty)
        self.assertEqual(out.fixture_count, 0)
        self.assertEqual(out.result_count, 0)
        self.assertEqual(out.run_count, 0)
        self.assertEqual(out.drift_count, 0)


class SourceFingerprintTests(unittest.TestCase):
    def test_all_fixture_source_fingerprints_present(self) -> None:
        suite = fh.build_all_fixture_suite()
        artifacts = fh.build_fixture_source_fingerprints(suite)
        self.assertEqual(len(artifacts), 9)
        for artifact in artifacts:
            self.assertEqual(artifact.artifact_kind, M.FIXTURE_ARTIFACT_SOURCE)
            self.assertTrue(artifact.relative_path.startswith("tests/fixtures/fixture_harness/"))
            self.assertNotIn(str(REPO_ROOT), artifact.relative_path)
            self.assertNotIn("/home/", json.dumps(fh.fixture_harness_to_dict(artifact)))
            self.assertRegex(artifact.checksum_sha256, r"^[0-9a-f]{64}$")
            self.assertGreater(artifact.size_bytes, 0)
            self.assertEqual(artifact.warnings, [])
            self.assertIs(artifact.manual_review_required, True)
            self.assertIs(artifact.ready_for_submission, False)

    def test_source_fingerprints_deterministic(self) -> None:
        suite = fh.build_all_fixture_suite()
        a = [fh.fixture_harness_to_dict(x) for x in fh.build_fixture_source_fingerprints(suite)]
        b = [fh.fixture_harness_to_dict(x) for x in fh.build_fixture_source_fingerprints(suite)]
        self.assertEqual(a, b)

    def test_source_fingerprints_do_not_mutate_suite(self) -> None:
        suite = fh.build_all_fixture_suite()
        before = json.dumps(fh.fixture_harness_to_dict(suite), sort_keys=True)
        fh.build_fixture_source_fingerprints(suite)
        after = json.dumps(fh.fixture_harness_to_dict(suite), sort_keys=True)
        self.assertEqual(after, before)
        self.assertTrue(all(a.checksum_sha256 == "" for a in suite.artifact_refs))
        self.assertTrue(all(a.size_bytes == 0 for a in suite.artifact_refs))

    def test_source_fingerprints_skip_unregistered_paths(self) -> None:
        fixture = M.build_protocol_fixture("readme", M.FIXTURE_CATEGORY_MISC, "README.md")
        fixture.source_files = ["README.md", "/etc/passwd", "tests\\fixtures\\bad.sol"]
        suite = fh.build_fixture_suite("bad-paths", fixtures=[fixture])
        self.assertEqual(fh.build_fixture_source_fingerprints(suite), [])

    def test_source_fingerprints_warn_for_missing_registered_source(self) -> None:
        fixture = M.build_protocol_fixture(
            "missing",
            M.FIXTURE_CATEGORY_MISC,
            "tests/fixtures/fixture_harness/set1/nope/Nope.sol",
        )
        fixture.source_files = [fixture.relative_path]
        suite = fh.build_fixture_suite("missing-source", fixtures=[fixture])
        artifacts = fh.build_fixture_source_fingerprints(suite)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].checksum_sha256, "")
        self.assertEqual(artifacts[0].size_bytes, 0)
        self.assertIn("source fingerprint unavailable: missing", artifacts[0].warnings)


class DefensivePathTests(unittest.TestCase):
    def _fixture_with_path(self, name: str, path: str) -> M.ProtocolFixture:
        f = M.build_protocol_fixture(name, M.FIXTURE_CATEGORY_MISC,
                                     fixture_id=f"fixture:misc:{name}:deadbeef0000")
        f.relative_path = path
        f.source_files = [path]
        return f

    def test_rejects_absolute_path_safely(self) -> None:  # 34
        f = self._fixture_with_path("evilabs", "/etc/passwd")
        run = fh.run_fixture_benchmark(f)  # must not raise
        self.assertIsInstance(run, M.FixtureRun)
        self.assertEqual(run.run_status, M.FIXTURE_RUN_PARTIAL)

    def test_rejects_parent_traversal_safely(self) -> None:  # 35
        f = self._fixture_with_path("travy", "tests/fixtures/fixture_harness/../../../secret.sol")
        run = fh.run_fixture_benchmark(f)  # must not raise
        self.assertIsInstance(run, M.FixtureRun)
        self.assertEqual(run.run_status, M.FIXTURE_RUN_PARTIAL)

    def test_rejects_backslash_path_safely(self) -> None:  # 36
        f = self._fixture_with_path("backy", "tests\\fixtures\\x.sol")
        run = fh.run_fixture_benchmark(f)  # must not raise
        self.assertIsInstance(run, M.FixtureRun)

    def test_handles_missing_source_neutrally(self) -> None:  # 37
        f = self._fixture_with_path(
            "missy", "tests/fixtures/fixture_harness/set1/nope/Nope.sol")
        run = fh.run_fixture_benchmark(f)  # must not raise
        self.assertEqual(run.run_status, M.FIXTURE_RUN_PARTIAL)
        self.assertTrue(any("source not readable" in w or "source not evaluated" in w
                            for w in run.warnings))

    def test_outside_root_path_is_not_read(self) -> None:  # 38
        # A safe, relative path outside the fixtures subtree is never read.
        f = self._fixture_with_path("readmey", "README.md")
        run = fh.run_fixture_benchmark(f)  # must not raise even though README exists
        self.assertEqual(run.run_status, M.FIXTURE_RUN_PARTIAL)

    def test_defensive_runs_serialize_without_overclaim(self) -> None:  # 39
        for path in ("/etc/passwd", "tests/fixtures/fixture_harness/../x.sol",
                     "tests/fixtures/fixture_harness/set1/nope/Nope.sol"):
            f = self._fixture_with_path("d", path)
            blob = json.dumps(fh.fixture_harness_to_dict(fh.run_fixture_benchmark(f)))
            self.assertNotIn("HUMAN_REVIEWED", blob)
            for token in _OVERCLAIM:
                self.assertNotIn(token, blob.lower())


class NoExecutionTests(unittest.TestCase):
    def test_does_not_use_subprocess_socket_or_os_system(self) -> None:  # 40
        # If the runner shelled out, opened a socket, or called os.system, these
        # patched raisers would fire. Benchmarking must succeed without them.
        def boom(*_a, **_k):  # pragma: no cover - only fires on misuse
            raise AssertionError("runner must not spawn processes or sockets")

        import socket as _socket
        with mock.patch.object(subprocess, "run", boom), \
                mock.patch.object(subprocess, "Popen", boom), \
                mock.patch.object(subprocess, "call", boom), \
                mock.patch.object(subprocess, "check_output", boom), \
                mock.patch.object(os, "system", boom), \
                mock.patch.object(_socket, "socket", boom):
            suite = fh.benchmark_set1_fixture_suite()
        self.assertEqual(suite.result_count, 63)

    def test_runner_source_has_no_execution_or_network_imports(self) -> None:  # 41
        src = RUNNER_SRC.read_text(encoding="utf-8")
        for bad in ("import subprocess", "import socket", "import requests",
                    "import urllib", "os.system(", "subprocess.", "eval(", "exec("):
            self.assertNotIn(bad, src, bad)

    def test_does_not_invoke_foundry_tools(self) -> None:  # 42
        # The runner never shells out to Foundry. (The module may say "no Foundry"
        # as a disclaimer; what must be absent are actual tool invocations.)
        src = RUNNER_SRC.read_text(encoding="utf-8")
        for bad in ("forge test", "forge build", "forge script", "forge install",
                    "cast send", "cast call", "cast rpc", '"forge"', "'forge'",
                    '"cast"', "'cast'"):
            self.assertNotIn(bad, src, bad)

    def test_import_side_effect_free(self) -> None:  # 43
        with tempfile.TemporaryDirectory() as tmp:
            code = (
                "import os; before=set(os.listdir('.'));"
                "import arkheionx.fixture_harness.runner as r;"
                "assert set(os.listdir('.'))==before, 'created files on import';"
                "assert not os.path.exists('.arkheionx'), '.arkheionx created';"
                "print('clean')"
            )
            env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
            result = subprocess.run([sys.executable, "-c", code], cwd=tmp, text=True,
                                    capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("clean", result.stdout)

    def test_runs_in_clean_subprocess_without_network(self) -> None:  # 44
        # A from-scratch interpreter (no network access needed) can benchmark Set 1.
        with tempfile.TemporaryDirectory() as tmp:
            code = (
                "import arkheionx.fixture_harness as fh;"
                "s=fh.benchmark_set1_fixture_suite();"
                "assert s.fixture_count==3 and s.result_count>0 and s.drift_count==0;"
                "print('ok')"
            )
            env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
            result = subprocess.run([sys.executable, "-c", code], cwd=tmp, text=True,
                                    capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("ok", result.stdout)


class PackageExportTests(unittest.TestCase):
    def test_package_exports_runner_helpers(self) -> None:  # 45
        for name in ("run_fixture_benchmark", "run_fixture_benchmark_suite",
                     "benchmark_set1_fixture_suite", "build_fixture_source_fingerprints"):
            self.assertIn(name, fh.__all__, name)
            self.assertTrue(hasattr(fh, name), name)


class CompatibilityTests(unittest.TestCase):
    def test_existing_set1_registry_unaffected(self) -> None:  # 46
        suite = fh.build_set1_fixture_suite()
        self.assertEqual(suite.fixture_count, 3)
        self.assertEqual(suite.result_count, 0)

    def test_existing_model_unaffected(self) -> None:  # 47
        self.assertIs(M.ProtocolFixture().manual_review_required, True)
        self.assertIs(M.ProtocolFixture().ready_for_submission, False)

    def test_existing_intelligence_unaffected(self) -> None:  # 48
        from arkheionx.intelligence.graph import build_protocol_intelligence_graph
        g = build_protocol_intelligence_graph("demo", local_validation_ids=["local-test-result:t1"])
        self.assertIs(g.manual_review_required, True)

    def test_existing_local_validation_unaffected(self) -> None:  # 49
        from arkheionx.local_validation import model as lv_model
        self.assertIs(lv_model.LocalValidationSummary().ready_for_submission, False)


if __name__ == "__main__":
    unittest.main()
