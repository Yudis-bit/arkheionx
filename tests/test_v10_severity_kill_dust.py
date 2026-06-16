"""V10 economic severity gate: dust and trusted-role kills."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.severity import apply_gate
from arkheionx.severity import models as S

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _gated(name, context=None):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
    apply_gate(graph, context=context or {})
    return {c.invariant_family: c for c in graph.candidates}


class KillSeverityTest(unittest.TestCase):
    def test_kill_dust_for_18_decimal_reconciliation(self):
        c = _gated("loan_repay_rounding_fixture", {"asset_decimals": 18})[
            "DEBT_REPAYMENT_RECONCILIATION"]
        self.assertEqual(c.economic_severity, S.KILL_DUST)

    def test_dust_only_context_kills(self):
        c = _gated("loan_repay_rounding_fixture", {"dust_only": True})[
            "DEBT_REPAYMENT_RECONCILIATION"]
        self.assertEqual(c.economic_severity, S.KILL_DUST)

    def test_kill_trusted_role(self):
        c = _gated("trusted_role_fixture")["ACCESS_CONTROLLED_VALUE_MOVEMENT"]
        self.assertEqual(c.economic_severity, S.KILL_TRUSTED_ROLE)


if __name__ == "__main__":
    unittest.main()
