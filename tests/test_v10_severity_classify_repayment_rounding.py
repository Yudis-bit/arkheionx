"""V10 economic severity gate: #567-like repayment rounding classification."""
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


class RepaymentRoundingSeverityTest(unittest.TestCase):
    def test_valid_but_low_not_high(self):
        c = _gated("loan_repay_rounding_fixture")["DEBT_REPAYMENT_RECONCILIATION"]
        self.assertEqual(c.economic_severity, S.VALID_BUT_LOW)
        self.assertNotIn(c.economic_severity, S.SUBMIT_LABELS[:2])  # not High/Medium

    def test_no_attacker_profit_and_cap_noted(self):
        c = _gated("loan_repay_rounding_fixture")["DEBT_REPAYMENT_RECONCILIATION"]
        d = c.severity_detail
        self.assertIn("rounding", d["cap"].lower())
        self.assertIn("not gas-profitable", d["gas"].lower())
        self.assertIn("immune", d["realism"].lower())


if __name__ == "__main__":
    unittest.main()
