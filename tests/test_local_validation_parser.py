"""Tests for the Foundry / local validation output parser (v3.7, internal)."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from arkheionx import local_validation as lv
from arkheionx.local_validation import model, parser

_FIXTURES = Path(__file__).parent / "fixtures" / "local_validation" / "foundry"
_BASIC_JSON = _FIXTURES / "forge-test-json-basic.json"
_BASIC_TEXT = _FIXTURES / "forge-test-text-basic.txt"
_MIXED_JSON = _FIXTURES / "forge-test-json-mixed.json"
_MIXED_TEXT = _FIXTURES / "forge-test-text-mixed.txt"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class DispatchTests(unittest.TestCase):
    def test_rejects_empty_text(self) -> None:
        for bad in ("", "   ", "\n"):
            with self.assertRaises(ValueError):
                parser.parse_foundry_output(bad)

    def test_detects_json_input(self) -> None:
        out = parser.parse_foundry_output(_read(_BASIC_JSON))
        self.assertEqual(out.source_format, parser.FOUNDRY_JSON)

    def test_falls_back_to_text_input(self) -> None:
        out = parser.parse_foundry_output(_read(_BASIC_TEXT))
        self.assertEqual(out.source_format, parser.FOUNDRY_TEXT)


class BasicJsonFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.out = parser.parse_foundry_output(_read(_BASIC_JSON), run_id="run:1")

    def test_parses(self) -> None:
        self.assertEqual(self.out.source_format, parser.FOUNDRY_JSON)

    def test_yields_two_tests(self) -> None:
        self.assertEqual(len(self.out.test_results), 2)

    def test_statuses_passed(self) -> None:
        self.assertTrue(all(t.status == model.TEST_PASSED for t in self.out.test_results))

    def test_parses_gas(self) -> None:
        gas = {t.test_name: t.gas_used for t in self.out.test_results}
        self.assertEqual(gas["testDeposit()"], 42111)
        self.assertEqual(gas["testWithdraw()"], 58721)

    def test_parses_duration(self) -> None:
        durations = {t.test_name: t.duration_ms for t in self.out.test_results}
        self.assertEqual(durations["testDeposit()"], 12)
        self.assertIsNotNone(durations["testWithdraw()"])

    def test_preserves_exact_test_names(self) -> None:
        self.assertEqual({t.test_name for t in self.out.test_results},
                         {"testDeposit()", "testWithdraw()"})

    def test_assigns_run_id_and_tool(self) -> None:
        self.assertTrue(all(t.run_id == "run:1" and t.tool == "foundry" for t in self.out.test_results))

    def test_parses_contract_and_function(self) -> None:
        t = next(t for t in self.out.test_results if t.test_name == "testDeposit()")
        self.assertEqual(t.contract_name, "LendingVaultTest")
        self.assertEqual(t.function_name, "testDeposit")


class BasicTextFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.out = parser.parse_foundry_output(_read(_BASIC_TEXT))

    def test_parses(self) -> None:
        self.assertEqual(self.out.source_format, parser.FOUNDRY_TEXT)

    def test_yields_two_tests(self) -> None:
        self.assertEqual(len(self.out.test_results), 2)

    def test_statuses_passed(self) -> None:
        self.assertTrue(all(t.status == model.TEST_PASSED for t in self.out.test_results))

    def test_parses_gas(self) -> None:
        self.assertEqual(self.out.test_results[0].gas_used, 42111)

    def test_parses_contract_from_suite_line(self) -> None:
        self.assertTrue(all(t.contract_name == "LendingVaultTest" for t in self.out.test_results))


class MixedJsonFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.out = parser.parse_foundry_output(_read(_MIXED_JSON))
        self.by_name = {t.test_name: t for t in self.out.test_results}

    def test_includes_passed(self) -> None:
        self.assertEqual(self.by_name["testDeposit()"].status, model.TEST_PASSED)

    def test_includes_failed(self) -> None:
        self.assertEqual(self.by_name["testLiquidationEdgeCase()"].status, model.TEST_FAILED)

    def test_includes_skipped(self) -> None:
        self.assertEqual(self.by_name["testOracleStalePrice()"].status, model.TEST_SKIPPED)

    def test_includes_error_or_unknown(self) -> None:
        self.assertEqual(self.by_name["testMalformedSetup()"].status, model.TEST_ERROR)

    def test_missing_gas_is_none(self) -> None:
        self.assertIsNone(self.by_name["testOracleStalePrice()"].gas_used)

    def test_missing_duration_is_none(self) -> None:
        self.assertIsNone(self.by_name["testLiquidationEdgeCase()"].duration_ms)


class MixedTextFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.out = parser.parse_foundry_output(_read(_MIXED_TEXT))
        self.statuses = [t.status for t in self.out.test_results]

    def test_includes_passed(self) -> None:
        self.assertIn(model.TEST_PASSED, self.statuses)

    def test_includes_failed(self) -> None:
        self.assertIn(model.TEST_FAILED, self.statuses)

    def test_includes_skipped(self) -> None:
        self.assertIn(model.TEST_SKIPPED, self.statuses)

    def test_unknown_line_creates_warning(self) -> None:
        self.assertTrue(self.out.warnings)
        self.assertTrue(any("unrecognized result marker" in w for w in self.out.warnings))


class StatusMappingTests(unittest.TestCase):
    def test_pass_variants(self) -> None:
        for value in ("pass", "passed", "Success", "ok", "PASS"):
            self.assertEqual(parser.foundry_status_to_local_status(value), model.TEST_PASSED)

    def test_fail_variants(self) -> None:
        for value in ("fail", "failed", "Failure", "FAIL"):
            self.assertEqual(parser.foundry_status_to_local_status(value), model.TEST_FAILED)

    def test_skip_variants(self) -> None:
        for value in ("skip", "Skipped", "SKIP"):
            self.assertEqual(parser.foundry_status_to_local_status(value), model.TEST_SKIPPED)

    def test_error_variants(self) -> None:
        for value in ("error", "errored", "ERROR"):
            self.assertEqual(parser.foundry_status_to_local_status(value), model.TEST_ERROR)

    def test_unknown_status(self) -> None:
        for value in ("weird", "", None):
            self.assertEqual(parser.foundry_status_to_local_status(value), model.TEST_UNKNOWN)


class ExtractionTests(unittest.TestCase):
    def test_gas_int(self) -> None:
        self.assertEqual(parser.extract_gas_used(42111), 42111)

    def test_gas_numeric_string(self) -> None:
        self.assertEqual(parser.extract_gas_used("58721"), 58721)
        self.assertIsNone(parser.extract_gas_used("not-a-number"))

    def test_gas_missing(self) -> None:
        self.assertIsNone(parser.extract_gas_used(None))

    def test_gas_from_kind_dict(self) -> None:
        self.assertEqual(parser.extract_gas_used({"Unit": {"gas": 7}}), 7)

    def test_duration_ms_string(self) -> None:
        self.assertEqual(parser.extract_duration_ms("8.12ms"), 8)

    def test_duration_seconds_string(self) -> None:
        self.assertEqual(parser.extract_duration_ms("1s"), 1000)

    def test_duration_numeric_ms(self) -> None:
        self.assertEqual(parser.extract_duration_ms(8), 8)

    def test_duration_secs_nanos_dict(self) -> None:
        self.assertEqual(parser.extract_duration_ms({"secs": 0, "nanos": 12000000}), 12)

    def test_duration_missing(self) -> None:
        self.assertIsNone(parser.extract_duration_ms(None))


class SplitIdentifierTests(unittest.TestCase):
    def test_plain_function(self) -> None:
        self.assertEqual(parser.split_foundry_test_identifier("testDeposit()"), ("", "testDeposit"))

    def test_contract_dot_test(self) -> None:
        self.assertEqual(parser.split_foundry_test_identifier("LendingVaultTest.testDeposit()"),
                         ("LendingVaultTest", "testDeposit"))

    def test_file_contract_test(self) -> None:
        self.assertEqual(
            parser.split_foundry_test_identifier("test/LendingVault.t.sol:LendingVaultTest.testDeposit()"),
            ("LendingVaultTest", "testDeposit"))

    def test_file_contract_only(self) -> None:
        self.assertEqual(parser.split_foundry_test_identifier("test/LendingVault.t.sol:LendingVaultTest"),
                         ("LendingVaultTest", ""))


class NoOverclaimTests(unittest.TestCase):
    def setUp(self) -> None:
        self.out = parser.parse_foundry_output(_read(_MIXED_JSON), run_id="run:1")

    def test_does_not_assign_linked_ids(self) -> None:
        for t in self.out.test_results:
            self.assertEqual(t.linked_function_ids, [])
            self.assertEqual(t.linked_value_path_ids, [])
            self.assertEqual(t.linked_assumption_ids, [])
            self.assertEqual(t.linked_test_gap_ids, [])

    def test_does_not_assign_test_result_id(self) -> None:
        self.assertTrue(all(t.test_result_id == "" for t in self.out.test_results))

    def test_keeps_support_none(self) -> None:
        self.assertTrue(all(t.evidence_support == model.SUPPORT_NONE for t in self.out.test_results))

    def test_output_json_serializable(self) -> None:
        json.dumps(parser.parsed_foundry_output_to_dict(self.out))

    def test_dict_preserves_warnings(self) -> None:
        out = parser.parse_foundry_output(_read(_MIXED_TEXT))
        data = parser.parsed_foundry_output_to_dict(out)
        self.assertEqual(data["warnings"], out.warnings)

    def test_no_overclaim_tokens(self) -> None:
        blob = json.dumps(parser.parsed_foundry_output_to_dict(self.out)).lower()
        for token in ("human_reviewed", "ready_for_submission", "confirmed vulnerab",
                      "final severity", "audit passed", "bounty"):
            self.assertNotIn(token, blob)


class JsonShapeTests(unittest.TestCase):
    def test_top_level_tests_list(self) -> None:
        payload = {"tests": [{"name": "testA()", "status": "Success", "gas": 10}]}
        out = parser.parse_foundry_json_payload(payload)
        self.assertEqual(len(out.test_results), 1)
        self.assertEqual(out.test_results[0].status, model.TEST_PASSED)

    def test_bare_list(self) -> None:
        out = parser.parse_foundry_json_payload([{"name": "testA()", "status": "fail"}])
        self.assertEqual(out.test_results[0].status, model.TEST_FAILED)

    def test_unknown_structure_warns(self) -> None:
        out = parser.parse_foundry_json_payload({"unexpected": 1})
        self.assertEqual(out.test_results, [])
        self.assertTrue(out.warnings)


class HygieneAndSafetyTests(unittest.TestCase):
    def test_fixture_files_exist(self) -> None:
        for path in (_BASIC_JSON, _BASIC_TEXT, _MIXED_JSON, _MIXED_TEXT):
            self.assertTrue(path.is_file(), path)

    def test_fixtures_have_no_secrets_or_rpc_or_abs_paths(self) -> None:
        for path in (_BASIC_JSON, _BASIC_TEXT, _MIXED_JSON, _MIXED_TEXT):
            text = _read(path).lower()
            self.assertNotIn("private key", text)
            self.assertNotIn("-----begin", text)
            self.assertNotIn("seed phrase", text)
            self.assertNotIn("http://", text)
            self.assertNotIn("https://", text)
            self.assertNotIn("rpc", text)
            self.assertNotIn("/home/", text)
            self.assertNotIn("/users/", text)
            self.assertNotIn("--fork-url", text)

    def test_fixtures_are_small(self) -> None:
        for path in (_BASIC_JSON, _BASIC_TEXT, _MIXED_JSON, _MIXED_TEXT):
            self.assertLess(path.stat().st_size, 4096, path)

    def test_json_fixtures_load(self) -> None:
        for path in (_BASIC_JSON, _MIXED_JSON):
            json.loads(_read(path))

    def test_text_fixtures_load_utf8(self) -> None:
        for path in (_BASIC_TEXT, _MIXED_TEXT):
            self.assertIsInstance(path.read_text(encoding="utf-8"), str)

    def test_parser_import_has_no_filesystem_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                import importlib

                importlib.reload(parser)
                parser.parse_foundry_text_output("[PASS] testA() (gas: 1)")
                entries = list(Path(tmp).iterdir())
            finally:
                os.chdir(cwd)
            self.assertEqual(entries, [])

    def test_text_parser_ignores_trace_lines(self) -> None:
        text = (
            "Ran 1 test for test/X.t.sol:XTest\n"
            "[PASS] testA() (gas: 100)\n"
            "    [12345] SomeContract::call()\n"
            "    \u2514\u2500 \u2190 ()\n"
        )
        out = parser.parse_foundry_text_output(text)
        self.assertEqual(len(out.test_results), 1)
        self.assertEqual(out.test_results[0].test_name, "testA()")

    def test_package_exports_parser_symbols(self) -> None:
        for name in ("ParsedFoundryOutput", "parse_foundry_output",
                     "parse_foundry_json_payload", "parse_foundry_text_output",
                     "parsed_foundry_output_to_dict", "foundry_status_to_local_status",
                     "extract_gas_used", "extract_duration_ms",
                     "split_foundry_test_identifier", "FOUNDRY_JSON", "FOUNDRY_TEXT"):
            self.assertTrue(hasattr(lv, name), name)


if __name__ == "__main__":
    unittest.main()
