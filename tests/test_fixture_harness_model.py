"""Tests for the internal fixture-harness dataclasses, builders, and serializer (v3.9)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import arkheionx.fixture_harness as fh
from arkheionx.fixture_harness import model as M

REPO_ROOT = Path(__file__).resolve().parents[1]


class SafetyBoundaryTests(unittest.TestCase):
    def test_safety_boundary_defaults(self) -> None:  # 1
        b = M.FixtureSafetyBoundary()
        for flag in ("local_static_only", "no_rpc", "no_fork_url", "no_live_chain_calls",
                     "no_private_keys", "no_seed_phrases", "no_transaction_broadcasting",
                     "no_exploit_automation", "no_auto_submit", "no_automatic_human_reviewed",
                     "no_confirmed_vulnerabilities", "no_final_severity", "no_audit_passed_claim",
                     "no_bounty_eligibility", "manual_review_required"):
            self.assertIs(getattr(b, flag), True, flag)
        self.assertIs(b.ready_for_submission, False)


class MinimalConstructionTests(unittest.TestCase):
    def test_protocol_fixture_minimal(self) -> None:  # 2
        f = M.ProtocolFixture()
        self.assertEqual(f.category, M.FIXTURE_CATEGORY_MISC)
        self.assertIsInstance(f.safety_boundary, M.FixtureSafetyBoundary)

    def test_fixture_artifact_ref_minimal(self) -> None:  # 3
        a = M.FixtureArtifactRef()
        self.assertEqual(a.artifact_kind, M.FIXTURE_ARTIFACT_UNKNOWN)

    def test_fixture_run_minimal(self) -> None:  # 4
        r = M.FixtureRun()
        self.assertEqual(r.run_status, M.FIXTURE_RUN_PLANNED)

    def test_fixture_result_minimal(self) -> None:  # 5
        r = M.FixtureResult()
        self.assertEqual(r.result_status, M.FIXTURE_RESULT_OBSERVED)
        self.assertIs(r.drift_detected, False)
        self.assertIsNone(r.observed_value)

    def test_fixture_snapshot_ref_minimal(self) -> None:  # 6
        s = M.FixtureSnapshotRef()
        self.assertEqual(s.subject_ids, [])

    def test_fixture_suite_minimal(self) -> None:  # 7
        s = M.FixtureSuite()
        self.assertEqual(s.fixture_count, 0)
        self.assertEqual(s.fixtures, [])

    def test_mutable_defaults_independent(self) -> None:  # 8
        a, b = M.ProtocolFixture(), M.ProtocolFixture()
        a.source_files.append("x.sol")
        a.warnings.append("w")
        a.metadata["k"] = "v"
        self.assertEqual(b.source_files, [])
        self.assertEqual(b.warnings, [])
        self.assertEqual(b.metadata, {})

    def test_manual_review_required_true_by_default(self) -> None:  # 9
        for obj in (M.ProtocolFixture(), M.FixtureArtifactRef(), M.FixtureRun(),
                    M.FixtureResult(), M.FixtureSnapshotRef(), M.FixtureSuite()):
            self.assertIs(obj.manual_review_required, True, type(obj).__name__)

    def test_ready_for_submission_false_by_default(self) -> None:  # 10
        for obj in (M.ProtocolFixture(), M.FixtureArtifactRef(), M.FixtureRun(),
                    M.FixtureResult(), M.FixtureSnapshotRef(), M.FixtureSuite()):
            self.assertIs(obj.ready_for_submission, False, type(obj).__name__)


class VocabularyTests(unittest.TestCase):
    def test_all_fixture_categories_present(self) -> None:  # 11
        for cat in ("FIXTURE_CATEGORY_ERC20", "FIXTURE_CATEGORY_LENDING_VAULT",
                    "FIXTURE_CATEGORY_STAKING_REWARD", "FIXTURE_CATEGORY_AMM_SWAP",
                    "FIXTURE_CATEGORY_ORACLE_DEPENDENT", "FIXTURE_CATEGORY_UPGRADEABLE_PROXY",
                    "FIXTURE_CATEGORY_BRIDGE_MESSAGE", "FIXTURE_CATEGORY_LIQUIDATION_BORROW_REPAY",
                    "FIXTURE_CATEGORY_MISC"):
            self.assertTrue(hasattr(M, cat))
            self.assertIn(getattr(M, cat), M.FIXTURE_CATEGORY_VALUES)
        self.assertEqual(len(M.FIXTURE_CATEGORY_VALUES), 9)
        self.assertEqual(set(M.FIXTURE_CATEGORY_DESCRIPTIONS), set(M.FIXTURE_CATEGORY_VALUES))

    def test_all_artifact_kinds_present(self) -> None:  # 12
        for kind in ("FIXTURE_ARTIFACT_SOURCE", "FIXTURE_ARTIFACT_REVIEW_MAP",
                     "FIXTURE_ARTIFACT_PROTOCOL_MODEL", "FIXTURE_ARTIFACT_LOCAL_VALIDATION",
                     "FIXTURE_ARTIFACT_PROTOCOL_GRAPH", "FIXTURE_ARTIFACT_EVIDENCE",
                     "FIXTURE_ARTIFACT_REPORT", "FIXTURE_ARTIFACT_REVIEW_PACKAGE",
                     "FIXTURE_ARTIFACT_SNAPSHOT", "FIXTURE_ARTIFACT_UNKNOWN"):
            self.assertIn(getattr(M, kind), M.FIXTURE_ARTIFACT_KIND_VALUES)
        self.assertEqual(len(M.FIXTURE_ARTIFACT_KIND_VALUES), 10)

    def test_all_benchmark_dimensions_present(self) -> None:  # 13
        for dim in ("BENCHMARK_DIMENSION_ID_STABILITY", "BENCHMARK_DIMENSION_JSON_STABILITY",
                    "BENCHMARK_DIMENSION_GRAPH_COUNTS", "BENCHMARK_DIMENSION_CROSSREF_OUTCOMES",
                    "BENCHMARK_DIMENSION_EXPORT_CHECKSUM", "BENCHMARK_DIMENSION_JSON_PURITY",
                    "BENCHMARK_DIMENSION_NO_OVERCLAIM", "BENCHMARK_DIMENSION_REVIEW_CONTEXT"):
            self.assertIn(getattr(M, dim), M.BENCHMARK_DIMENSION_VALUES)
        self.assertEqual(len(M.BENCHMARK_DIMENSION_VALUES), 8)

    def test_run_and_result_status_vocabularies(self) -> None:
        self.assertEqual(len(M.FIXTURE_RUN_STATUS_VALUES), 6)
        self.assertEqual(len(M.FIXTURE_RESULT_STATUS_VALUES), 6)


class BuilderTests(unittest.TestCase):
    def test_build_protocol_fixture_mints_deterministic_id(self) -> None:  # 14
        a = M.build_protocol_fixture("Vault", M.FIXTURE_CATEGORY_LENDING_VAULT, "contracts/Vault.sol")
        b = M.build_protocol_fixture("Vault", M.FIXTURE_CATEGORY_LENDING_VAULT, "contracts/Vault.sol")
        self.assertTrue(a.fixture_id.startswith("fixture:"))
        self.assertEqual(a.fixture_id, b.fixture_id)

    def test_build_protocol_fixture_preserves_supplied_id(self) -> None:  # 15
        f = M.build_protocol_fixture("X", M.FIXTURE_CATEGORY_MISC, fixture_id="fixture:custom:x:abc123")
        self.assertEqual(f.fixture_id, "fixture:custom:x:abc123")

    def test_build_protocol_fixture_unknown_category_warns(self) -> None:  # 16
        f = M.build_protocol_fixture("X", "NOT_A_CATEGORY")
        self.assertTrue(any("unknown fixture category" in w for w in f.warnings))
        # Known category does not warn.
        g = M.build_protocol_fixture("X", M.FIXTURE_CATEGORY_ERC20)
        self.assertFalse(any("unknown fixture category" in w for w in g.warnings))

    def test_build_fixture_suite_deterministic_suite_id(self) -> None:  # 17
        f = M.build_protocol_fixture("Vault", M.FIXTURE_CATEGORY_LENDING_VAULT)
        a = M.build_fixture_suite("set1", [f])
        b = M.build_fixture_suite("set1", [f])
        self.assertEqual(a.suite_id, b.suite_id)
        self.assertTrue(a.suite_id.startswith("fixture-suite:set1:"))

    def test_build_fixture_suite_fixture_order_stable(self) -> None:  # 18
        f1 = M.build_protocol_fixture("A", M.FIXTURE_CATEGORY_ERC20)
        f2 = M.build_protocol_fixture("B", M.FIXTURE_CATEGORY_AMM_SWAP)
        self.assertEqual(
            M.build_fixture_suite("set1", [f1, f2]).suite_id,
            M.build_fixture_suite("set1", [f2, f1]).suite_id,
        )

    def test_build_fixture_suite_counts_fixtures(self) -> None:  # 19
        fixtures = [M.build_protocol_fixture(f"F{i}", M.FIXTURE_CATEGORY_MISC) for i in range(3)]
        self.assertEqual(M.build_fixture_suite("s", fixtures).fixture_count, 3)

    def test_build_fixture_suite_counts_runs(self) -> None:  # 20
        runs = [M.FixtureRun(run_id=f"r{i}") for i in range(4)]
        self.assertEqual(M.build_fixture_suite("s", [], [], runs).run_count, 4)

    def test_build_fixture_suite_counts_results(self) -> None:  # 21
        results = [M.FixtureResult(result_id=f"x{i}") for i in range(5)]
        self.assertEqual(M.build_fixture_suite("s", [], [], [], results).result_count, 5)

    def test_build_fixture_suite_counts_drift(self) -> None:  # 22
        results = [M.FixtureResult(drift_detected=True), M.FixtureResult(drift_detected=False),
                   M.FixtureResult(drift_detected=True)]
        self.assertEqual(M.build_fixture_suite("s", [], [], [], results).drift_count, 2)

    def test_build_fixture_suite_merges_warnings_deterministically(self) -> None:  # 23
        f = M.build_protocol_fixture("X", "NOT_A_CATEGORY")  # produces a warning
        run = M.FixtureRun(warnings=["zeta warning", "alpha warning"])
        suite = M.build_fixture_suite("s", [f], runs=[run])
        self.assertEqual(suite.warnings, sorted(set(suite.warnings)))  # sorted + unique
        self.assertIn("alpha warning", suite.warnings)
        self.assertTrue(any("unknown fixture category" in w for w in suite.warnings))
        # Deterministic across rebuilds.
        self.assertEqual(M.build_fixture_suite("s", [f], runs=[run]).warnings, suite.warnings)


class SerializationTests(unittest.TestCase):
    def _full_suite(self) -> M.FixtureSuite:
        f = M.build_protocol_fixture("Vault", M.FIXTURE_CATEGORY_LENDING_VAULT, "contracts/Vault.sol",
                                     benchmark_dimensions=[M.BENCHMARK_DIMENSION_ID_STABILITY])
        art = M.FixtureArtifactRef(artifact_id="fixture-artifact:source:abc", fixture_id=f.fixture_id,
                                   artifact_kind=M.FIXTURE_ARTIFACT_SOURCE, relative_path="contracts/Vault.sol")
        run = M.FixtureRun(run_id="fixture-run:pipeline:abc", fixture_id=f.fixture_id, runner="pipeline")
        res = M.FixtureResult(result_id="fixture-result:graph:abc", fixture_id=f.fixture_id,
                              run_id=run.run_id, result_kind="graph_counts", observed_value={"nodes": 3})
        snap = M.FixtureSnapshotRef(snapshot_id="fixture-snapshot:graph:abc", fixture_id=f.fixture_id,
                                    snapshot_kind="graph", subject_ids=["a", "b"])
        return M.build_fixture_suite("set1", [f], [art], [run], [res], [snap])

    def test_to_dict_json_serializable(self) -> None:  # 24
        data = M.fixture_harness_to_dict(self._full_suite())
        json.dumps(data)  # must not raise
        self.assertIsInstance(data["fixtures"], list)
        self.assertIsInstance(data["fixtures"][0]["safety_boundary"], dict)

    def test_to_dict_does_not_mutate_source(self) -> None:  # 25
        suite = self._full_suite()
        before = json.dumps(M.fixture_harness_to_dict(suite))
        M.fixture_harness_to_dict(suite)
        self.assertEqual(json.dumps(M.fixture_harness_to_dict(suite)), before)
        self.assertIsInstance(suite.fixtures[0], M.ProtocolFixture)  # still dataclass, not dict

    def test_to_dict_unsupported_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            M.fixture_harness_to_dict(object())


class ImportSideEffectTests(unittest.TestCase):
    def test_no_filesystem_side_effect_on_import(self) -> None:  # 26
        with tempfile.TemporaryDirectory() as tmp:
            code = (
                "import os; before=set(os.listdir('.'));"
                "import arkheionx.fixture_harness as fh;"
                "import arkheionx.fixture_harness.ids, arkheionx.fixture_harness.model;"
                "assert set(os.listdir('.'))==before, 'created files on import';"
                "assert not os.path.exists('.arkheionx'), '.arkheionx created';"
                "print('clean')"
            )
            env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))
            result = subprocess.run([sys.executable, "-c", code], cwd=tmp, text=True,
                                    capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("clean", result.stdout)

    def test_package_exports_expected_names(self) -> None:  # 27
        for name in ("canonical_fixture_seed", "short_fixture_hash", "slugify_fixture_token",
                     "normalize_fixture_path", "fixture_id", "fixture_artifact_id", "fixture_run_id",
                     "fixture_result_id", "fixture_snapshot_id", "FixtureSafetyBoundary",
                     "ProtocolFixture", "FixtureArtifactRef", "FixtureRun", "FixtureResult",
                     "FixtureSnapshotRef", "FixtureSuite", "build_protocol_fixture",
                     "build_fixture_suite", "fixture_suite_id", "fixture_harness_to_dict",
                     "FIXTURE_CATEGORY_VALUES", "FIXTURE_ARTIFACT_KIND_VALUES",
                     "BENCHMARK_DIMENSION_VALUES"):
            self.assertIn(name, fh.__all__, name)
            self.assertTrue(hasattr(fh, name), name)


class NoOverclaimTests(unittest.TestCase):
    def _blob(self) -> str:
        f = M.build_protocol_fixture("Vault", M.FIXTURE_CATEGORY_LENDING_VAULT, "contracts/Vault.sol")
        suite = M.build_fixture_suite("set1", [f], runs=[M.FixtureRun(run_id="r")],
                                      results=[M.FixtureResult(result_id="x")])
        return json.dumps(M.fixture_harness_to_dict(suite))

    def test_no_human_reviewed(self) -> None:  # 28
        self.assertNotIn("HUMAN_REVIEWED", self._blob())

    def test_no_confirmed_vulnerability(self) -> None:  # 29
        self.assertNotIn("confirmed vulnerability", self._blob().lower())

    def test_no_final_severity(self) -> None:  # 30
        self.assertNotIn("final severity", self._blob().lower())

    def test_no_audit_passed(self) -> None:  # 31
        self.assertNotIn("audit passed", self._blob().lower())

    def test_no_bounty_eligibility(self) -> None:  # 32
        self.assertNotIn("bounty eligible", self._blob().lower())

    def test_no_fixture_pass_proves_safety(self) -> None:  # 33
        low = self._blob().lower()
        self.assertNotIn("proves safety", low)
        self.assertNotIn("fixture pass proves", low)

    def test_no_fixture_failure_proves_vulnerability(self) -> None:  # 34
        low = self._blob().lower()
        self.assertNotIn("proves vulnerability", low)
        self.assertNotIn("proves a vulnerability", low)

    def test_module_source_has_no_forbidden_state_constants(self) -> None:
        # The controlled vocabulary must not include finality state names.
        names = set(dir(M))
        for forbidden in ("SAFE", "VERIFIED_SAFE", "CONFIRMED_VULNERABILITY",
                          "AUDIT_PASSED", "FINAL_SEVERITY"):
            self.assertNotIn(forbidden, names, forbidden)


class CompatibilityTests(unittest.TestCase):
    def test_existing_intelligence_imports_unaffected(self) -> None:  # 35
        from arkheionx.intelligence.graph import build_protocol_intelligence_graph
        g = build_protocol_intelligence_graph("demo", local_validation_ids=["local-test-result:t1"])
        self.assertIs(g.manual_review_required, True)
        self.assertIs(g.ready_for_submission, False)

    def test_existing_review_package_imports_unaffected(self) -> None:  # 36
        from arkheionx.review_package import collector
        self.assertEqual(collector._REQUIRED_KINDS, {"review_map", "evidence_links", "artifacts_index"})

    def test_existing_local_validation_imports_unaffected(self) -> None:  # 37
        from arkheionx.local_validation import model as lv_model
        self.assertIs(lv_model.LocalValidationSummary().manual_review_required, True)
        self.assertIs(lv_model.LocalValidationSummary().ready_for_submission, False)


if __name__ == "__main__":
    unittest.main()
