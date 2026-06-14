"""V10 war-run orchestrator: end-to-end smoke test + CLI registration."""
import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.warrun import run_war_run
from arkheionx.cli.main import build_parser, main

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"

_GOLDEN = [
    "01-scope-map.md", "02-semantic-map.json", "03-call-graph.json",
    "04-storage-access-map.json", "05-defi-entities.json", "06-state-transitions.json",
    "07-invariants.md", "08-invariants.json", "09-attack-graph.json",
    "10-candidate-ranking.md", "12-fork-plan.md", "13-economic-severity.md",
    "14-dedup-scope-risk.md",
]


class WarRunSmokeTest(unittest.TestCase):
    def test_borrow_run_in_memory(self):
        scope = _GODEYE / "borrow_swapdata_consent_fixture" / "scope.yaml"
        res = run_war_run(_GODEYE / "borrow_swapdata_consent_fixture",
                          scope_file=str(scope), write=False)
        self.assertGreaterEqual(res["counts"]["candidates"], 1)
        # Golden artifacts present in memory.
        keys = set(res["contents"]) | set(res["jsons"])
        for g in _GOLDEN:
            self.assertIn(g, keys, f"missing artifact {g}")
        # Consent candidate must be NEEDS_FORK_PROOF, never fake-high.
        labels = {c.invariant_family: c.economic_severity for c in res["graph"].candidates}
        self.assertEqual(labels["LENDER_CONSENT_VALUE_AFFECTING_CALLDATA"], "NEEDS_FORK_PROOF")
        # No report; safety flags set.
        self.assertFalse(res["triage"]["report_generated"])
        self.assertTrue(res["triage"]["safety_flags"]["no_signing_keys"])
        self.assertIn("No report generated.", "\n".join(res["console"]))

    def test_poc_skeleton_generated_for_fixture(self):
        res = run_war_run(_GODEYE / "deposit_double_use_fixture", write=False)
        self.assertTrue(res["skeletons"], "expected at least one PoC skeleton")
        self.assertIn("assert", res["skeletons"][0].source)

    def test_567_like_is_capped_not_high(self):
        res = run_war_run(_GODEYE / "loan_repay_rounding_fixture",
                          asset_decimals=18, write=False)
        labels = {c.invariant_family: c.economic_severity for c in res["graph"].candidates}
        self.assertEqual(labels["DEBT_REPAYMENT_RECONCILIATION"], "KILL_DUST")

    def test_trusted_role_killed(self):
        res = run_war_run(_GODEYE / "trusted_role_fixture", write=False)
        labels = [c.economic_severity for c in res["graph"].candidates]
        self.assertIn("KILL_TRUSTED_ROLE", labels)

    def test_writes_golden_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            res = run_war_run(_GODEYE / "loan_repay_rounding_fixture",
                              out_dir=d, write=True)
            for g in _GOLDEN + ["triage.json", "manifest.json"]:
                self.assertTrue((Path(d) / g).is_file(), f"missing written {g}")
            self.assertTrue((Path(d) / "11-poc-skeletons").is_dir())
            triage = json.loads((Path(d) / "triage.json").read_text())
            self.assertEqual(triage["artifact_type"], "godeye_war_run")
            self.assertFalse(triage["report_generated"])

    def test_unscoped_run_warns_but_works(self):
        res = run_war_run(_GODEYE / "vault_share_inflation_fixture", write=False)
        self.assertTrue(res["scope"].warnings)  # unscoped warning
        self.assertGreaterEqual(res["counts"]["candidates"], 1)


class WarRunCliTest(unittest.TestCase):
    def test_war_run_registered(self):
        parser = build_parser()
        import argparse
        choices = []
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                choices = list(action.choices.keys())
        self.assertIn("war-run", choices)

    def test_cli_json_returns_zero(self):
        code = main(["war-run", str(_GODEYE / "deposit_double_use_fixture"),
                     "--no-write", "--json"])
        self.assertEqual(code, 0)

    def test_cli_missing_target_is_invalid_args(self):
        code = main(["war-run", "/nonexistent/path/xyz", "--no-write"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
