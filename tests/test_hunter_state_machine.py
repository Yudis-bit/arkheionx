"""Tests for the hunter state-machine value-flow detector."""
import tempfile
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"

BENIGN = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Benign {
    enum Phase { Open, Paused, Closed }
    Phase public phase;

    function setPhase(Phase p) external { phase = p; }
    function isOpen() external view returns (bool) { return phase == Phase.Open; }
}
"""


class StateMachineTests(unittest.TestCase):
    def test_value_gating_state_machine_surfaced(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        sms = res["pack"].state_machines
        value_gating = [s for s in sms if s.touches_value]
        self.assertTrue(value_gating, "a value-gating state machine should be surfaced")
        self.assertTrue(any(s.contract == "WithdrawalQueue" for s in value_gating))
        self.assertTrue(any(l.lead_type == M.STATE_MACHINE_VALUE_FLOW for l in res["pack"].leads))

    def test_benign_state_machine_without_value_not_boosted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "contracts").mkdir()
            (root / "contracts" / "Benign.sol").write_text(BENIGN, encoding="utf-8")
            (root / "scope.md").write_text("# Scope\n## In scope\n- Benign phase machine.\n", encoding="utf-8")
            res = build_hunter_pack(root, scope_file=str(root / "scope.md"), write=False)
            for sm in res["pack"].state_machines:
                if sm.contract == "Benign":
                    self.assertFalse(sm.touches_value, "a benign status enum must not be boosted")
            for lead in res["pack"].leads:
                self.assertNotEqual(lead.lead_type, M.STATE_MACHINE_VALUE_FLOW)


if __name__ == "__main__":
    unittest.main()
