import unittest
from pathlib import Path
from unittest import mock

from arkheionx.proof import runner as runner_mod
from arkheionx.proof.payloads import build_proof_payload, build_trace_payload, target_slug
from arkheionx.proof.runner import ExecResult, execute_target
from arkheionx.proof.trace import parse_forge_output
from arkheionx.protocol import foundry as foundry_mod

PASS_FAIL = """Ran 3 tests for test/Foo.t.sol:FooTest
[PASS] test_a() (gas: 100)
[PASS] test_b() (gas: 100)
[FAIL: revert: bad price] test_c() (gas: 100)
Suite result: FAILED. 2 passed; 1 failed; 0 skipped; finished in 1ms"""

SKIP_ONLY = """Ran 1 test for test/Foo.t.sol:FooTest
[SKIP] test_skipme()
Suite result: ok. 0 passed; 0 failed; 1 skipped; finished in 1ms"""

SUMMARY_ONLY = "Encountered a total of results: 4 passed; 1 failed; 0 skipped"


class TraceParserTests(unittest.TestCase):
    def test_pass_fail_markers(self) -> None:
        t = parse_forge_output(PASS_FAIL)
        self.assertEqual((t["passed"], t["failed"], t["skipped"]), (2, 1, 0))
        self.assertEqual(t["tests_run"], 3)
        self.assertIn("test_c", t["failing_tests"])
        self.assertTrue(any("bad price" in r for r in t["reverts"]))

    def test_skip_only(self) -> None:
        t = parse_forge_output(SKIP_ONLY)
        self.assertEqual((t["passed"], t["failed"], t["skipped"]), (0, 0, 1))

    def test_summary_fallback(self) -> None:
        t = parse_forge_output(SUMMARY_ONLY)
        self.assertEqual((t["passed"], t["failed"]), (4, 1))

    def test_no_inferred_state(self) -> None:
        t = parse_forge_output("")
        self.assertEqual(t["tests_run"], 0)
        self.assertTrue(any("not inferred" in l for l in t["limitations"]))


def _fs(status):
    return foundry_mod.FoundryStatus(status=status, forge_available=True, has_foundry_toml=True)


class ExecutionRunnerTests(unittest.TestCase):
    def _run(self, detect, build, test):
        with mock.patch.object(runner_mod.foundry_mod, "detect_foundry", return_value=detect), \
             mock.patch.object(runner_mod.foundry_mod, "run_build", return_value=build), \
             mock.patch.object(runner_mod.foundry_mod, "run_test", return_value=test):
            return execute_target(Path("/tmp/x"), "withdraw")

    def test_no_foundry(self) -> None:
        r = self._run(foundry_mod.FoundryStatus(status=foundry_mod.UNAVAILABLE), (False, ""), (0, "", ""))
        self.assertEqual(r.status, "no_foundry")
        self.assertEqual(r.evidence_level, "HEURISTIC")

    def test_build_failed(self) -> None:
        r = self._run(_fs(foundry_mod.AVAILABLE_NOT_BUILT), (False, "err"), (0, "", ""))
        self.assertEqual(r.status, "build_failed")
        self.assertEqual(r.evidence_level, "HEURISTIC")

    def test_no_tests_matched_is_compiler_confirmed(self) -> None:
        r = self._run(_fs(foundry_mod.AVAILABLE_NOT_BUILT), (True, "ok"), (0, "No tests to run", "cmd"))
        self.assertEqual(r.status, "no_tests_matched")
        self.assertEqual(r.evidence_level, "COMPILER_CONFIRMED")

    def test_skipped_is_not_proof(self) -> None:
        r = self._run(_fs(foundry_mod.AVAILABLE_NOT_BUILT), (True, "ok"), (0, SKIP_ONLY, "cmd"))
        self.assertEqual(r.status, "skipped_not_proof")
        self.assertEqual(r.evidence_level, "COMPILER_CONFIRMED")

    def test_executed_is_execution_confirmed(self) -> None:
        r = self._run(_fs(foundry_mod.AVAILABLE_NOT_BUILT), (True, "ok"), (1, PASS_FAIL, "cmd"))
        self.assertEqual(r.status, "tested_mixed")
        self.assertEqual(r.evidence_level, "EXECUTION_CONFIRMED")
        self.assertTrue(r.ran)


class PayloadTests(unittest.TestCase):
    def test_slug(self) -> None:
        self.assertEqual(target_slug("Vault.withdraw"), "Vault_withdraw")

    def test_proof_payload_shape(self) -> None:
        result = ExecResult(status="tested_passed", evidence_level="EXECUTION_CONFIRMED", build_status="build_passed")
        result.trace = parse_forge_output(PASS_FAIL)
        payload = build_proof_payload(
            "Vault.withdraw", "src/V.sol:Vault.withdraw()#L1-L2", "/r", "tested_passed",
            "EXECUTION_CONFIRMED", result, ["gen.sol"], "raw.txt", ("raw.txt", "trace.json"), ["next"],
        )
        for key in ["schema_version", "arkheionx_version", "target", "status", "evidence_level", "foundry", "test_result", "trace", "generated_files", "limitations", "next_commands"]:
            self.assertIn(key, payload)
        for key in ["proof_receipt_id", "review_map_target", "related_test_gap", "proof_suggestion_id"]:
            self.assertIn(key, payload)
        self.assertIn("test_command", payload["foundry"])
        self.assertEqual(payload["test_result"]["passed"], 2)
        self.assertEqual(payload["proof_receipt_id"], "proof:Vault_withdraw")

    def test_trace_payload_shape(self) -> None:
        payload = build_trace_payload(
            "Vault.withdraw",
            "tested_failed",
            "EXECUTION_CONFIRMED",
            "raw.txt",
            parse_forge_output(PASS_FAIL),
            target_id="src/V.sol:Vault.withdraw()#L1-L2",
            review_map_target="Vault.withdraw",
            source_proof_json="proof.json",
        )
        for key in ["schema_version", "target", "status", "evidence_level", "failing_tests", "reverts", "call_sequence", "limitations"]:
            self.assertIn(key, payload)
        for key in ["trace_receipt_id", "target_id", "review_map_target", "source_proof_json", "related_test_gap", "proof_suggestion_id"]:
            self.assertIn(key, payload)
        self.assertEqual(payload["trace_receipt_id"], "trace:Vault_withdraw")


if __name__ == "__main__":
    unittest.main()
