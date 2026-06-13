"""Tests for the hunter value-flow engine."""
import unittest
from pathlib import Path

from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def paths(name):
    b = FX / name
    res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
    return res["pack"].value_paths


class ValueFlowTests(unittest.TestCase):
    def test_value_out_path_extracted(self) -> None:
        vps = paths("adapter_withdrawability")
        exits = [vp for vp in vps if vp.exit_function]
        self.assertTrue(exits, "expected a value-out path for the adapter")
        vp = exits[0]
        self.assertTrue(vp.external_calls or vp.exit_function)
        self.assertEqual(vp.attacker_reachability, "UNPRIVILEGED_EXTERNAL")

    def test_accounting_variables_detected(self) -> None:
        vps = paths("queue_double_claim")
        joined = {v for vp in vps for v in vp.accounting_variables}
        self.assertTrue(joined, "expected accounting/state variables in the queue value paths")

    def test_state_update_ordering_present(self) -> None:
        vps = paths("fee_dispatch_value_flow")
        self.assertTrue(vps)
        for vp in vps:
            self.assertTrue(vp.state_update_ordering)

    def test_trusted_path_marked(self) -> None:
        b = FX / "trusted_role_only"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        sweep = [vp for vp in res["pack"].value_paths if "sweep" in (vp.exit_function or "").lower()]
        self.assertTrue(sweep)
        self.assertTrue(sweep[0].trusted_role_required)
        self.assertEqual(sweep[0].attacker_reachability, "TRUSTED_ROLE")

    def test_value_paths_in_triage_json(self) -> None:
        b = FX / "adapter_withdrawability"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        self.assertTrue(res["triage"]["value_paths"])


if __name__ == "__main__":
    unittest.main()
