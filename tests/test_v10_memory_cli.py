"""V10 root-cause memory CLI: add / list / classify / export.

Acceptance: a repeated #567-like candidate becomes SAME_ROOT_CAUSE; a route-buffer
candidate with a different pool stays SAME_ROOT_CAUSE as the route-buffer root cause;
a genuinely different family is DISTINCT; an empty store is UNKNOWN; and export never
leaks the private notes field.
"""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from arkheionx.cli.main import build_parser, main


def _run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue()


class MemoryCliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _add_567(self):
        return _run([
            "memory", "add", "--memory-dir", self.dir,
            "--target", "acme", "--invariant-family", "DEBT_REPAYMENT_RECONCILIATION",
            "--entry-function", "LoanRouter.repay", "--attacker", "borrower",
            "--status", "submitted", "--finding-id", "567", "--severity", "VALID_BUT_LOW",
            "--notes", "PRIVATE_NOTE_DO_NOT_LEAK",
        ])

    def test_memory_registered(self):
        choices = []
        import argparse
        for action in build_parser()._actions:
            if isinstance(action, argparse._SubParsersAction):
                choices = list(action.choices.keys())
        self.assertIn("memory", choices)

    def test_add_then_list(self):
        code, _ = self._add_567()
        self.assertEqual(code, 0)
        code, out = _run(["memory", "list", "--memory-dir", self.dir])
        self.assertEqual(code, 0)
        self.assertIn("DEBT_REPAYMENT_RECONCILIATION", out)
        self.assertIn("567", out)

    def test_classify_same_root_cause_different_pool(self):
        self._add_567()
        # Same family + role + attacker but a DIFFERENT contract -> same root cause.
        code, out = _run([
            "memory", "classify", "--memory-dir", self.dir,
            "--invariant-family", "DEBT_REPAYMENT_RECONCILIATION",
            "--entry-function", "OtherMarket.repay", "--attacker", "borrower"])
        self.assertEqual(code, 0)
        self.assertIn("SAME_ROOT_CAUSE", out)

    def test_route_buffer_different_pool_same(self):
        _run(["memory", "add", "--memory-dir", self.dir,
              "--invariant-family", "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
              "--entry-function", "RouterA.borrow", "--attacker", "borrower",
              "--status", "parked"])
        code, out = _run([
            "memory", "classify", "--memory-dir", self.dir,
            "--invariant-family", "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
            "--entry-function", "RouterB.borrow", "--attacker", "borrower"])
        self.assertIn("SAME_ROOT_CAUSE", out)

    def test_classify_distinct_family(self):
        self._add_567()
        code, out = _run([
            "memory", "classify", "--memory-dir", self.dir,
            "--invariant-family", "CROSS_CHAIN_SUPPLY_CONSERVATION",
            "--entry-function", "Bridge.receiveMessage", "--attacker", "anyone"])
        self.assertIn("DISTINCT", out)

    def test_classify_empty_is_unknown(self):
        empty = tempfile.mkdtemp()
        code, out = _run([
            "memory", "classify", "--memory-dir", empty,
            "--invariant-family", "X", "--entry-function", "A.b", "--attacker", "anyone"])
        self.assertEqual(code, 0)
        self.assertIn("UNKNOWN", out)

    def test_export_does_not_leak_notes(self):
        self._add_567()
        code, out = _run(["memory", "export", "--memory-dir", self.dir])
        self.assertEqual(code, 0)
        self.assertNotIn("PRIVATE_NOTE_DO_NOT_LEAK", out)
        self.assertIn("DEBT_REPAYMENT_RECONCILIATION", out)  # fingerprint still present
        self.assertIn("redacted_fields", out)

    def test_add_writes_store_file(self):
        self._add_567()
        self.assertTrue((Path(self.dir) / "findings.json").is_file())

    def test_no_subcommand_returns_usage_code(self):
        code, out = _run(["memory"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
