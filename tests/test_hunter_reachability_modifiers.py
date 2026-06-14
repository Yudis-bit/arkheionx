"""Modifier classification tests for the Reachability Truth Engine."""
import unittest
from pathlib import Path

from arkheionx.hunter import reachability as R

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def fixture(name: str):
    path = next((FX / name / "contracts").glob("*.sol"))
    return R.analyze_reachability(path.read_text(encoding="utf-8"))


class ReachabilityModifierTests(unittest.TestCase):
    def test_custom_only_oracle_is_role_gated(self) -> None:
        result = fixture("reachability_custom_modifier")
        update = result["OracleRate.updateRate"]
        self.assertEqual(update.final_label, R.ORACLE_GATED_EXTERNAL)
        self.assertNotEqual(update.final_label, R.UNPRIVILEGED_EXTERNAL)
        self.assertIn(R.EV_MODIFIER_BODY_MSG_SENDER_CHECK, update.evidence_types())

    def test_unknown_custom_modifier_fails_closed(self) -> None:
        result = fixture("reachability_unknown_modifier")
        for surface in ("UnknownGate.setValue", "UnknownGate.withdraw"):
            reach = result[surface]
            self.assertEqual(reach.final_label, R.UNKNOWN_MODIFIER_GATED_EXTERNAL)
            self.assertNotEqual(reach.final_label, R.UNPRIVILEGED_EXTERNAL)
            self.assertIn(R.EV_UNKNOWN_CUSTOM_MODIFIER, reach.evidence_types())

    def test_known_non_auth_modifier_remains_unprivileged(self) -> None:
        result = fixture("reachability_non_auth_modifier")
        self.assertEqual(
            result["NonAuthOnly.setValue"].final_label, R.UNPRIVILEGED_EXTERNAL)
        self.assertIn(
            R.EV_NON_AUTH_MODIFIER_ONLY,
            result["NonAuthOnly.setValue"].evidence_types(),
        )

    def test_auth_modifier_dominates_non_auth_modifier(self) -> None:
        result = fixture("reachability_mixed_modifiers")
        reach = result["MixedModifiers.setValue"]
        self.assertEqual(reach.final_label, R.OWNER_GATED_EXTERNAL)
        self.assertIn(R.EV_MIXED_AUTH_AND_NON_AUTH, reach.evidence_types())
        self.assertIn(R.W_MIXED_AUTH_AND_NON_AUTH, reach.warnings)

    def test_only_initializing_is_non_auth_by_itself(self) -> None:
        source = """
        contract InitializingHook {
            modifier onlyInitializing() { require(true); _; }
            function hook() external onlyInitializing { }
        }
        """
        reach = R.analyze_reachability(source)["InitializingHook.hook"]
        self.assertEqual(reach.final_label, R.UNPRIVILEGED_EXTERNAL)


if __name__ == "__main__":
    unittest.main()
