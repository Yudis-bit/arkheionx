"""End-to-end reachability decision-policy tests."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter import reachability as R
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def build(name: str):
    root = FX / name
    return build_hunter_pack(
        root, scope_file=str(root / "scope.md"), strict_context=True, write=False)


class ReachabilityEndToEndTests(unittest.TestCase):
    def test_role_gated_leads_are_killed_and_have_no_poc(self) -> None:
        result = build("reachability_custom_modifier")
        leads = result["pack"].leads
        self.assertTrue(leads)
        self.assertTrue(all(l.decision == M.KILL_TRUSTED_ROLE for l in leads))
        self.assertFalse(any(l.decision == M.PURSUE_NOW for l in leads))
        self.assertFalse(result["pack"].poc_plans)
        self.assertTrue(all(r.submit == "NO" for r in result["pack"].report_filter))
        self.assertTrue(all(
            r.poc_status == M.POC_BLOCKED_TRUSTED_ROLE
            for r in result["pack"].report_filter))

    def test_unknown_modifier_parks_on_reachability(self) -> None:
        result = build("reachability_unknown_modifier")
        self.assertTrue(result["pack"].leads)
        self.assertTrue(all(
            l.decision == M.PARK_REACHABILITY for l in result["pack"].leads))
        self.assertFalse(result["pack"].poc_plans)
        self.assertTrue(all(
            r.poc_status == M.POC_NEEDS_REACHABILITY
            for r in result["pack"].report_filter))

    def test_non_auth_modifier_stays_attacker_reachable(self) -> None:
        result = build("reachability_non_auth_modifier")
        self.assertTrue(result["pack"].leads)
        self.assertTrue(all(
            l.attacker_reachability == R.UNPRIVILEGED_EXTERNAL
            for l in result["pack"].leads))
        self.assertFalse(any(
            l.decision == M.KILL_TRUSTED_ROLE for l in result["pack"].leads))

    def test_initializer_context_and_unguarded_initializer_are_distinct(self) -> None:
        guarded = build("reachability_initializer_context")["triage"]["function_reachability"]
        initialize = next(x for x in guarded if x["surface"] == "InitContext.initialize")
        self.assertEqual(initialize["final_reachability"], R.INITIALIZER_CONTEXT_EXTERNAL)
        self.assertIn(
            R.EV_INITIALIZER_CONTEXT_REQUIRES_DEPLOYMENT_STATE,
            initialize["evidence_types"],
        )

        unguarded = build("reachability_auth_bypass_candidate")["triage"]["function_reachability"]
        takeover = next(x for x in unguarded if x["surface"] == "BypassCandidate.initialize")
        self.assertEqual(takeover["final_reachability"], R.UNPRIVILEGED_EXTERNAL)
        self.assertIn(R.EV_UNGUARDED_INITIALIZER_SETS_ROLE, takeover["evidence_types"])

    def test_value_flow_uses_precise_role_gate(self) -> None:
        payout = build("reachability_custom_modifier")
        payout_paths = [
            p for p in payout["pack"].value_paths
            if "pushPayout" in (p.entry_function + p.exit_function)
        ]
        self.assertTrue(payout_paths)
        self.assertTrue(all(
            p.attacker_reachability == R.ORACLE_GATED_EXTERNAL for p in payout_paths))
        self.assertFalse(any(
            p.attacker_reachability == R.UNPRIVILEGED_EXTERNAL for p in payout_paths))

        assembly = build("reachability_inline_assembly_role")
        value_flow_md = assembly["contents"]["06-value-flow-map.md"]
        self.assertIn(
            "AssemblyOracleRate.updateRate — ORACLE_GATED_EXTERNAL", value_flow_md)
        self.assertNotIn(
            "AssemblyOracleRate.updateRate — UNPRIVILEGED_EXTERNAL", value_flow_md)


if __name__ == "__main__":
    unittest.main()
