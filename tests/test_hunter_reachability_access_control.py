"""AccessControl role classification tests."""
import unittest
from pathlib import Path

from arkheionx.hunter import reachability as R

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "hunter" / "reachability_access_control_role"


class ReachabilityAccessControlTests(unittest.TestCase):
    def test_only_role_minter_maps_to_minter_gate(self) -> None:
        source = next((FIXTURE / "contracts").glob("*.sol")).read_text(encoding="utf-8")
        reach = R.analyze_reachability(source)["AccessControlled.mint"]
        self.assertIn(
            reach.final_label, (R.MINTER_GATED_EXTERNAL, R.ROLE_GATED_EXTERNAL))
        self.assertIn(R.EV_ACCESS_CONTROL_ONLY_ROLE, reach.evidence_types())
        self.assertIn(R.EV_ACCESS_CONTROL_HAS_ROLE, reach.evidence_types())
        self.assertFalse(R.is_attacker_reachable(reach.final_label))

    def test_direct_has_role_maps_named_role(self) -> None:
        source = """
        contract DirectRole {
            bytes32 constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
            function hasRole(bytes32, address) public view returns (bool) { return true; }
            function pause() external {
                require(hasRole(PAUSER_ROLE, msg.sender), "NO_ROLE");
            }
        }
        """
        reach = R.analyze_reachability(source)["DirectRole.pause"]
        self.assertEqual(reach.final_label, R.PAUSER_GATED_EXTERNAL)
        self.assertIn(R.EV_ACCESS_CONTROL_HAS_ROLE, reach.evidence_types())

    def test_direct_allowlist_mapping_is_caller_gate(self) -> None:
        source = """
        contract DirectAllowlist {
            mapping(address => bool) allowed;
            function execute() external { require(allowed[msg.sender], "NOT_ALLOWED"); }
        }
        """
        reach = R.analyze_reachability(source)["DirectAllowlist.execute"]
        self.assertEqual(reach.final_label, R.ALLOWLIST_GATED_EXTERNAL)
        self.assertIn(R.EV_ALLOWLIST_MAPPING_CHECK, reach.evidence_types())

    def test_unresolved_inherited_only_role_keeps_named_role(self) -> None:
        source = """
        contract InheritedSurface {
            bytes32 constant MINTER_ROLE = keccak256("MINTER_ROLE");
            function mint() external onlyRole(MINTER_ROLE) {}
        }
        """
        reach = R.analyze_reachability(source)["InheritedSurface.mint"]
        self.assertEqual(reach.final_label, R.MINTER_GATED_EXTERNAL)
        self.assertIn(R.EV_ACCESS_CONTROL_ONLY_ROLE, reach.evidence_types())
        self.assertIn(R.EV_PARSER_LIMITATION, reach.evidence_types())


if __name__ == "__main__":
    unittest.main()
