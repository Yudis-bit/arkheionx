"""Tests for internal local validation dataclasses and serialization (v3.7)."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path, PurePosixPath

from arkheionx import local_validation as lv
from arkheionx.local_validation import model


class ConstructionTests(unittest.TestCase):
    def test_minimal_run(self) -> None:
        run = model.LocalValidationRun()
        self.assertEqual(run.tool, "foundry")
        self.assertEqual(run.status, model.LOCAL_VALIDATION_NOT_RUN)
        self.assertIsNone(run.exit_code)
        self.assertEqual(run.command, [])
        self.assertEqual(run.metadata, {})

    def test_run_defaults_safety_boundary(self) -> None:
        run = model.LocalValidationRun()
        self.assertIs(run.safety_boundary["manual_review_required"], True)
        self.assertIs(run.safety_boundary["ready_for_submission"], False)
        # Independent copy per instance (mutable default safety).
        run.safety_boundary["no_rpc"] = "changed"
        self.assertIs(model.LocalValidationRun().safety_boundary["no_rpc"], True)

    def test_minimal_test_result(self) -> None:
        tr = model.LocalTestResult()
        self.assertEqual(tr.status, model.TEST_UNKNOWN)
        self.assertEqual(tr.evidence_support, model.SUPPORT_NONE)
        self.assertIsNone(tr.duration_ms)
        self.assertIsNone(tr.gas_used)
        self.assertEqual(tr.linked_function_ids, [])

    def test_minimal_trace_receipt(self) -> None:
        rec = model.LocalTraceReceipt()
        self.assertEqual(rec.trace_status, model.TRACE_NOT_AVAILABLE)
        self.assertEqual(rec.evidence_support, model.SUPPORT_NONE)
        self.assertEqual(rec.call_count, 0)
        self.assertEqual(rec.events_count, 0)

    def test_minimal_artifact(self) -> None:
        art = model.LocalValidationArtifact()
        self.assertFalse(art.exists)
        self.assertEqual(art.size_bytes, 0)
        self.assertEqual(art.linked_ids, [])

    def test_minimal_summary(self) -> None:
        s = model.LocalValidationSummary()
        self.assertEqual(s.status, model.LOCAL_VALIDATION_NOT_RUN)
        self.assertEqual(s.total_tests, 0)
        self.assertTrue(len(s.limitations) >= 1)

    def test_summary_manual_review_and_not_ready(self) -> None:
        s = model.LocalValidationSummary()
        self.assertIs(s.manual_review_required, True)
        self.assertIs(s.ready_for_submission, False)


class SafetyBoundaryTests(unittest.TestCase):
    def test_all_required_flags_true(self) -> None:
        sb = model.DEFAULT_LOCAL_VALIDATION_SAFETY_BOUNDARY
        for flag in (
            "local_static_only", "no_rpc", "no_fork_url", "no_live_chain_calls",
            "no_private_keys", "no_seed_phrases", "no_transaction_broadcasting",
            "no_exploit_automation", "no_auto_submit", "no_automatic_human_reviewed",
            "no_confirmed_vulnerabilities", "no_final_severity",
            "no_audit_passed_claim", "no_bounty_eligibility", "manual_review_required",
        ):
            self.assertIs(sb[flag], True, flag)
        self.assertIs(sb["ready_for_submission"], False)

    def test_no_human_reviewed_positive_state(self) -> None:
        self.assertNotIn("HUMAN_REVIEWED", json.dumps(model.DEFAULT_LOCAL_VALIDATION_SAFETY_BOUNDARY))
        self.assertNotIn("HUMAN_REVIEWED", json.dumps(model.to_dict(model.LocalValidationSummary())))


class SerializationTests(unittest.TestCase):
    def test_to_dict_serializes_nested_dataclasses(self) -> None:
        run = model.LocalValidationRun(run_id="local-validation-run:foundry:h:s",
                                       test_result_ids=["local-test-result:foundry:a:b"])
        data = model.to_dict(run)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["run_id"], "local-validation-run:foundry:h:s")
        self.assertEqual(data["test_result_ids"], ["local-test-result:foundry:a:b"])

    def test_to_dict_serializes_path_as_posix(self) -> None:
        art = model.LocalValidationArtifact(artifact_id="a", metadata={"src": PurePosixPath("a/b.json")})
        data = model.to_dict(art)
        self.assertEqual(data["metadata"]["src"], "a/b.json")
        json.dumps(data)

    def test_to_dict_preserves_false_booleans(self) -> None:
        data = model.to_dict(model.LocalValidationArtifact())
        self.assertIs(data["exists"], False)

    def test_to_dict_preserves_none(self) -> None:
        data = model.to_dict(model.LocalTestResult())
        self.assertIsNone(data["duration_ms"])
        self.assertIsNone(data["line"])

    def test_to_dict_preserves_empty_containers(self) -> None:
        data = model.to_dict(model.LocalValidationRun())
        self.assertEqual(data["command"], [])
        self.assertEqual(data["metadata"], {})

    def test_to_dict_does_not_mutate_source(self) -> None:
        run = model.LocalValidationRun()
        model.to_dict(run)
        self.assertEqual(run.command, [])
        self.assertTrue(hasattr(run, "__dataclass_fields__"))

    def test_to_dict_rejects_unsupported(self) -> None:
        with self.assertRaises(TypeError):
            model.to_dict({1, 2, 3})

    def test_to_dict_output_is_json_serializable(self) -> None:
        for obj in (model.LocalValidationRun(), model.LocalTestResult(),
                    model.LocalTraceReceipt(), model.LocalValidationArtifact(),
                    model.LocalValidationSummary()):
            json.dumps(model.to_dict(obj))


class StatusHelperTests(unittest.TestCase):
    def test_zero_total_is_not_run(self) -> None:
        self.assertEqual(model.local_validation_status_from_counts(0, 0, 0, 0, 0),
                         model.LOCAL_VALIDATION_NOT_RUN)

    def test_passed_only(self) -> None:
        self.assertEqual(model.local_validation_status_from_counts(3, 0, 0, 0, 0),
                         model.LOCAL_VALIDATION_PASSED)

    def test_failed_only(self) -> None:
        self.assertEqual(model.local_validation_status_from_counts(0, 2, 0, 0, 0),
                         model.LOCAL_VALIDATION_FAILED)

    def test_error_dominates(self) -> None:
        self.assertEqual(model.local_validation_status_from_counts(5, 1, 0, 1, 0),
                         model.LOCAL_VALIDATION_ERROR)

    def test_skipped_only(self) -> None:
        self.assertEqual(model.local_validation_status_from_counts(0, 0, 4, 0, 0),
                         model.LOCAL_VALIDATION_SKIPPED)

    def test_failed_with_passed_is_partial(self) -> None:
        self.assertEqual(model.local_validation_status_from_counts(2, 1, 0, 0, 0),
                         model.LOCAL_VALIDATION_PARTIAL)

    def test_mixed_passed_skipped_is_partial(self) -> None:
        # Documented: passed + skipped (no fail/error) is PARTIAL; skips are not proof.
        self.assertEqual(model.local_validation_status_from_counts(2, 0, 1, 0, 0),
                         model.LOCAL_VALIDATION_PARTIAL)

    def test_unknown_only_is_partial(self) -> None:
        self.assertEqual(model.local_validation_status_from_counts(0, 0, 0, 0, 3),
                         model.LOCAL_VALIDATION_PARTIAL)


class PackageExportTests(unittest.TestCase):
    def test_package_exposes_expected_symbols(self) -> None:
        for name in (
            "LocalValidationRun", "LocalTestResult", "LocalTraceReceipt",
            "LocalValidationArtifact", "LocalValidationSummary", "to_dict",
            "local_validation_status_from_counts", "canonical_json_dumps",
            "short_hash", "normalize_id_path", "slugify_token", "repo_fingerprint",
            "local_validation_run_id", "local_test_result_id",
            "local_trace_receipt_id", "local_validation_artifact_id",
            "local_validation_summary_id", "DEFAULT_LOCAL_VALIDATION_SAFETY_BOUNDARY",
            "DEFAULT_LOCAL_VALIDATION_LIMITATIONS", "LOCAL_VALIDATION_NOT_RUN",
            "TEST_UNKNOWN", "TRACE_NOT_AVAILABLE", "SUPPORT_NONE",
            "ARTIFACT_KIND_RUN", "SCHEMA_VERSION",
        ):
            self.assertTrue(hasattr(lv, name), name)

    def test_import_has_no_filesystem_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                import importlib

                importlib.reload(lv)
                lv.to_dict(model.LocalValidationSummary())
                entries = list(Path(tmp).iterdir())
            finally:
                os.chdir(cwd)
            self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
