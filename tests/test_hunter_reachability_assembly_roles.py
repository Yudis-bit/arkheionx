"""Inline-assembly role getter tests."""
import unittest
from pathlib import Path

from arkheionx.hunter import reachability as R

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "hunter" / "reachability_inline_assembly_role"


class ReachabilityAssemblyRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = next((FIXTURE / "contracts").glob("*.sol")).read_text(encoding="utf-8")
        cls.result = R.analyze_reachability(source)

    def test_assembly_getter_emits_sload_evidence(self) -> None:
        getter = self.result["AssemblyOracleRate.oracle"]
        self.assertEqual(getter.final_label, R.VIEW_ONLY_NO_VALUE_EFFECT)
        self.assertIn(R.EV_ROLE_GETTER_ASSEMBLY_SLOAD, getter.evidence_types())

    def test_modifier_using_assembly_getter_is_oracle_gated(self) -> None:
        update = self.result["AssemblyOracleRate.updateRate"]
        self.assertEqual(update.final_label, R.ORACLE_GATED_EXTERNAL)
        self.assertIn(R.EV_ROLE_GETTER_ASSEMBLY_SLOAD, update.evidence_types())
        self.assertNotEqual(update.final_label, R.UNPRIVILEGED_EXTERNAL)


if __name__ == "__main__":
    unittest.main()
