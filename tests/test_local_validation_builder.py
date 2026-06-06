"""Tests for the local validation builder (v3.7, internal)."""
from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

from arkheionx import local_validation as lv
from arkheionx.local_validation import builder, model, parser

_FIXTURES = Path(__file__).parent / "fixtures" / "local_validation" / "foundry"
_FP = lv.repo_fingerprint("/repo/demo")


def _parse(name: str) -> parser.ParsedFoundryOutput:
    return parser.parse_foundry_output((_FIXTURES / name).read_text(encoding="utf-8"))


def _build(name: str, **kw):
    return builder.build_local_validation_from_parsed(_parse(name), repo_fingerprint=_FP, **kw)


def _result(test_name: str, **kw) -> model.LocalTestResult:
    return model.LocalTestResult(test_name=test_name, **kw)


def _parsed(*results) -> parser.ParsedFoundryOutput:
    return parser.ParsedFoundryOutput(test_results=list(results))


_MODEL = {
    "protocol_id": "protocol:x",
    "contracts": [{"contract_id": "contract:c1", "name": "LendingVault",
                   "aliases": {"contract_name": "LendingVault"}}],
    "functions": [
        {"function_id": "function:dep", "contract_id": "contract:c1", "signature": "deposit(uint256)",
         "display_name": "LendingVault.deposit", "aliases": {"review_map_target": "LendingVault.deposit"},
         "metadata": {"selector": "0xb6b55f25"}},
        {"function_id": "function:wd", "contract_id": "contract:c1", "signature": "withdraw(uint256)",
         "display_name": "LendingVault.withdraw", "aliases": {}},
    ],
    "value_paths": [{"value_path_id": "value-path:vp1", "entry_function_id": "function:dep",
                     "exit_function_id": "function:wd"}],
    "assumptions": [{"assumption_id": "assumption:a1", "linked_function_ids": ["function:dep"]}],
    "test_gaps": [{"test_gap_id": "test-gap:g1", "linked_function_id": "function:dep"}],
}


class BuildFromFixturesTests(unittest.TestCase):
    def test_build_basic_json(self) -> None:
        self.assertEqual(_build("forge-test-json-basic.json").summary.total_tests, 2)

    def test_build_basic_text(self) -> None:
        self.assertEqual(_build("forge-test-text-basic.txt").summary.total_tests, 2)

    def test_build_mixed_json(self) -> None:
        self.assertEqual(_build("forge-test-json-mixed.json").summary.total_tests, 5)

    def test_build_mixed_text(self) -> None:
        out = _build("forge-test-text-mixed.txt")
        self.assertEqual(out.summary.total_tests, 4)


class IdTests(unittest.TestCase):
    def test_run_id_deterministic_and_prefixed(self) -> None:
        a, b = _build("forge-test-json-basic.json").run, _build("forge-test-json-basic.json").run
        self.assertTrue(a.run_id.startswith("local-validation-run:foundry:"))
        self.assertEqual(a.run_id, b.run_id)

    def test_run_id_changes_with_command(self) -> None:
        a = _build("forge-test-json-basic.json").run.run_id
        b = _build("forge-test-json-basic.json", command=["forge", "test"]).run.run_id
        self.assertNotEqual(a, b)

    def test_run_id_preserves_command_order(self) -> None:
        a = _build("forge-test-json-basic.json", command=["forge", "test", "a", "b"]).run.run_id
        b = _build("forge-test-json-basic.json", command=["forge", "test", "b", "a"]).run.run_id
        self.assertNotEqual(a, b)

    def test_test_result_ids_deterministic_and_assigned(self) -> None:
        a = [t.test_result_id for t in _build("forge-test-json-mixed.json").test_results]
        b = [t.test_result_id for t in _build("forge-test-json-mixed.json").test_results]
        self.assertEqual(a, b)
        self.assertTrue(all(tid.startswith("local-test-result:") for tid in a))

    def test_run_records_test_result_ids(self) -> None:
        out = _build("forge-test-json-mixed.json")
        self.assertEqual(out.run.test_result_ids, [t.test_result_id for t in out.test_results])

    def test_duplicate_test_names_disambiguated(self) -> None:
        out = builder.build_local_validation_from_parsed(
            _parsed(_result("testD()", contract_name="A", status=model.TEST_PASSED),
                    _result("testD()", contract_name="B", status=model.TEST_FAILED)),
            repo_fingerprint=_FP)
        ids = [t.test_result_id for t in out.test_results]
        self.assertNotEqual(ids[0], ids[1])
        self.assertTrue(any("duplicate" in w for w in out.summary.warnings))

    def test_empty_repo_fingerprint_raises(self) -> None:
        with self.assertRaises(ValueError):
            builder.build_local_validation_from_parsed(_parsed(), repo_fingerprint="")


class SupportAndMutationTests(unittest.TestCase):
    def test_support_by_status(self) -> None:
        out = _build("forge-test-json-mixed.json")
        by_name = {t.test_name: t for t in out.test_results}
        self.assertEqual(by_name["testDeposit()"].evidence_support, model.SUPPORT_TESTED)
        for name in ("testLiquidationEdgeCase()", "testOracleStalePrice()", "testMalformedSetup()"):
            self.assertEqual(by_name[name].evidence_support, model.SUPPORT_NONE)

    def test_parsed_source_not_mutated(self) -> None:
        parsed = _parse("forge-test-json-mixed.json")
        snapshot = copy.deepcopy(parsed)
        builder.build_local_validation_from_parsed(parsed, repo_fingerprint=_FP, protocol_model=_MODEL)
        self.assertEqual(parsed, snapshot)


class SummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.summary = _build("forge-test-json-mixed.json").summary

    def test_counts(self) -> None:
        self.assertEqual(
            (self.summary.total_tests, self.summary.passed_tests, self.summary.failed_tests,
             self.summary.skipped_tests, self.summary.errored_tests, self.summary.unknown_tests),
            (5, 2, 1, 1, 1, 0))

    def test_status_error_present(self) -> None:
        self.assertEqual(self.summary.status, model.LOCAL_VALIDATION_ERROR)

    def test_all_passed_status(self) -> None:
        self.assertEqual(_build("forge-test-json-basic.json").summary.status, model.LOCAL_VALIDATION_PASSED)

    def test_manual_review_and_not_ready(self) -> None:
        self.assertIs(self.summary.manual_review_required, True)
        self.assertIs(self.summary.ready_for_submission, False)

    def test_safety_boundary_preserved(self) -> None:
        self.assertIs(self.summary.safety_boundary["local_static_only"], True)
        self.assertIs(self.summary.safety_boundary["no_rpc"], True)

    def test_summary_id_deterministic(self) -> None:
        self.assertEqual(_build("forge-test-json-mixed.json").summary.summary_id, self.summary.summary_id)


class LinkingTests(unittest.TestCase):
    def _link(self, result, model_dict=_MODEL):
        out = builder.build_local_validation_from_parsed(
            _parsed(result), repo_fingerprint=_FP, protocol_model=model_dict)
        return out.test_results[0], out

    def test_none_model_no_links(self) -> None:
        tr, _ = self._link(_result("deposit()", contract_name="LendingVault",
                                   function_name="deposit", status=model.TEST_PASSED), None)
        self.assertEqual(tr.linked_function_ids, [])

    def test_contract_function_match_and_edges(self) -> None:
        tr, out = self._link(_result("deposit()", contract_name="LendingVault",
                                     function_name="deposit", status=model.TEST_PASSED))
        self.assertEqual(tr.linked_function_ids, ["function:dep"])
        self.assertEqual(tr.linked_value_path_ids, ["value-path:vp1"])
        self.assertEqual(tr.linked_assumption_ids, ["assumption:a1"])
        self.assertEqual(tr.linked_test_gap_ids, ["test-gap:g1"])
        self.assertEqual(out.summary.linked_function_count, 1)

    def test_selector_match(self) -> None:
        tr, _ = self._link(_result("x()", selector="0xb6b55f25", status=model.TEST_PASSED))
        self.assertEqual(tr.linked_function_ids, ["function:dep"])

    def test_signature_match(self) -> None:
        tr, _ = self._link(_result("x()", status=model.TEST_PASSED, metadata={"signature": "withdraw(uint256)"}))
        self.assertEqual(tr.linked_function_ids, ["function:wd"])

    def test_alias_match(self) -> None:
        tr, _ = self._link(_result("LendingVault.deposit", status=model.TEST_PASSED))
        self.assertEqual(tr.linked_function_ids, ["function:dep"])

    def test_unresolved_warns_and_no_link(self) -> None:
        tr, out = self._link(_result("testNope()", contract_name="Other",
                                     function_name="nope", status=model.TEST_PASSED))
        self.assertEqual(tr.linked_function_ids, [])
        self.assertTrue(any("unresolved" in w for w in out.summary.warnings))

    def test_ambiguous_contract_function_no_link(self) -> None:
        amb = {"protocol_id": "p",
               "contracts": [{"contract_id": "c", "name": "C", "aliases": {"contract_name": "C"}}],
               "functions": [
                   {"function_id": "function:1", "contract_id": "c", "signature": "f()",
                    "display_name": "C.f", "aliases": {}},
                   {"function_id": "function:2", "contract_id": "c", "signature": "f(uint256)",
                    "display_name": "C.f", "aliases": {}}]}
        tr, out = self._link(_result("f()", contract_name="C", function_name="f",
                                     status=model.TEST_PASSED), amb)
        self.assertEqual(tr.linked_function_ids, [])
        self.assertTrue(any("ambiguous" in w for w in out.summary.warnings))

    def test_similar_name_does_not_link(self) -> None:
        # "deposi" / "deposits" are not exact and must not match "deposit".
        for fn in ("deposi", "deposits", "Deposit"):
            tr, _ = self._link(_result("x()", contract_name="LendingVault",
                                       function_name=fn, status=model.TEST_PASSED))
            self.assertEqual(tr.linked_function_ids, [], fn)

    def test_protocol_model_not_mutated(self) -> None:
        snapshot = copy.deepcopy(_MODEL)
        self._link(_result("deposit()", contract_name="LendingVault",
                           function_name="deposit", status=model.TEST_PASSED))
        self.assertEqual(_MODEL, snapshot)

    def test_no_invented_edge_ids(self) -> None:
        # withdraw has no test_gap/assumption edge -> empty, not invented.
        tr, _ = self._link(_result("withdraw()", contract_name="LendingVault",
                                   function_name="withdraw", status=model.TEST_PASSED))
        self.assertEqual(tr.linked_function_ids, ["function:wd"])
        self.assertEqual(tr.linked_assumption_ids, [])
        self.assertEqual(tr.linked_test_gap_ids, [])


class TraceReceiptTests(unittest.TestCase):
    def test_no_trace_receipt_by_default(self) -> None:
        self.assertEqual(_build("forge-test-json-mixed.json").trace_receipts, [])

    def test_explicit_trace_receipt(self) -> None:
        out = builder.build_local_validation_from_parsed(
            _parsed(_result("testT()", status=model.TEST_PASSED,
                            metadata={"trace": {"call_count": 3, "kind": "call"}})),
            repo_fingerprint=_FP)
        self.assertEqual(len(out.trace_receipts), 1)
        receipt = out.trace_receipts[0]
        self.assertTrue(receipt.trace_receipt_id.startswith("local-trace-receipt:"))
        self.assertEqual(receipt.evidence_support, model.SUPPORT_TRACE_BOUND)
        self.assertEqual(receipt.trace_status, model.TRACE_AVAILABLE)
        self.assertEqual(receipt.call_count, 3)
        self.assertEqual(out.run.trace_receipt_ids, [receipt.trace_receipt_id])

    def test_trace_receipt_id_deterministic(self) -> None:
        def run():
            return builder.build_local_validation_from_parsed(
                _parsed(_result("testT()", status=model.TEST_PASSED,
                                metadata={"trace": {"call_count": 1}})),
                repo_fingerprint=_FP).trace_receipts[0].trace_receipt_id
        self.assertEqual(run(), run())


class SerializationAndSafetyTests(unittest.TestCase):
    def test_build_result_json_serializable(self) -> None:
        json.dumps(builder.local_validation_build_result_to_dict(_build("forge-test-json-mixed.json")))

    def test_to_dict_does_not_mutate(self) -> None:
        out = _build("forge-test-json-mixed.json")
        before = copy.deepcopy(out)
        builder.local_validation_build_result_to_dict(out)
        self.assertEqual(out, before)

    def test_no_human_reviewed_status(self) -> None:
        blob = json.dumps(builder.local_validation_build_result_to_dict(
            _build("forge-test-json-mixed.json", protocol_model=_MODEL)))
        self.assertNotIn("HUMAN_REVIEWED", blob)

    def test_not_ready_for_submission_everywhere(self) -> None:
        data = builder.local_validation_build_result_to_dict(_build("forge-test-json-mixed.json"))
        self.assertIs(data["summary"]["ready_for_submission"], False)
        self.assertIs(data["summary"]["manual_review_required"], True)
        self.assertIs(data["run"]["safety_boundary"]["ready_for_submission"], False)


class ImportAndExportTests(unittest.TestCase):
    def test_package_exports_builder_symbols(self) -> None:
        for name in ("LocalValidationBuildResult", "build_local_validation_from_parsed",
                     "build_local_validation_run", "assign_test_result_ids",
                     "build_local_validation_summary", "extract_protocol_function_index",
                     "link_test_result_to_protocol", "link_test_results_to_protocol",
                     "local_validation_build_result_to_dict"):
            self.assertTrue(hasattr(lv, name), name)

    def test_import_has_no_filesystem_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                import importlib

                importlib.reload(builder)
                builder.build_local_validation_from_parsed(_parsed(), repo_fingerprint=_FP)
                entries = list(Path(tmp).iterdir())
            finally:
                os.chdir(cwd)
            self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
