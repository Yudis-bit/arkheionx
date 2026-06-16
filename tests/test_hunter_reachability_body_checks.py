"""Direct and helper-based caller authorization tests."""
import unittest
from pathlib import Path

from arkheionx.hunter import reachability as R

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def fixture(name: str):
    path = next((FX / name / "contracts").glob("*.sol"))
    return R.analyze_reachability(path.read_text(encoding="utf-8"))


class ReachabilityBodyCheckTests(unittest.TestCase):
    def test_direct_body_owner_check(self) -> None:
        reach = fixture("reachability_body_auth_check")["BodyAuth.setValue"]
        self.assertEqual(reach.final_label, R.OWNER_GATED_EXTERNAL)
        self.assertIn(R.EV_DIRECT_BODY_MSG_SENDER_CHECK, reach.evidence_types())

    def test_modifier_helper_resolves_admin(self) -> None:
        reach = fixture("reachability_nested_modifier_call")["NestedRole.setValue"]
        self.assertEqual(reach.final_label, R.ADMIN_GATED_EXTERNAL)
        self.assertIn(R.EV_HELPER_MSG_SENDER_CHECK, reach.evidence_types())

    def test_direct_function_helper_resolves_admin(self) -> None:
        source = """
        contract DirectHelper {
            address public admin;
            function setValue(uint256) external { _checkAdmin(); }
            function _checkAdmin() internal view {
                require(msg.sender == admin, "ONLY_ADMIN");
            }
        }
        """
        reach = R.analyze_reachability(source)["DirectHelper.setValue"]
        self.assertEqual(reach.final_label, R.ADMIN_GATED_EXTERNAL)
        self.assertIn(R.EV_HELPER_MSG_SENDER_CHECK, reach.evidence_types())

    def test_helper_cycle_fails_closed(self) -> None:
        source = """
        contract CyclicGate {
            modifier customGate() { _checkA(); _; }
            function _checkA() internal view { _checkB(); }
            function _checkB() internal view { _checkA(); }
            function setValue(uint256) external customGate { }
        }
        """
        reach = R.analyze_reachability(source)["CyclicGate.setValue"]
        self.assertEqual(reach.final_label, R.UNKNOWN_AUTH_HELPER_GATED_EXTERNAL)
        self.assertIn(R.EV_MODIFIER_CALL_GRAPH_CYCLE, reach.evidence_types())
        self.assertIn(R.W_MODIFIER_CALL_GRAPH_CYCLE, reach.warnings)

    def test_helper_depth_cap_fails_closed(self) -> None:
        source = """
        contract DeepGate {
            address owner;
            modifier customGate() { _a(); _; }
            function _a() internal view { _b(); }
            function _b() internal view { _c(); }
            function _c() internal view { _d(); }
            function _d() internal view { _e(); }
            function _e() internal view { require(msg.sender == owner, "OWNER"); }
            function setValue(uint256) external customGate {}
        }
        """
        reach = R.analyze_reachability(source)["DeepGate.setValue"]
        self.assertEqual(reach.final_label, R.UNKNOWN_AUTH_HELPER_GATED_EXTERNAL)
        self.assertIn(R.EV_PARSER_LIMITATION, reach.evidence_types())
        self.assertIn(R.W_AUTH_HELPER_UNRESOLVED, reach.warnings)


if __name__ == "__main__":
    unittest.main()
