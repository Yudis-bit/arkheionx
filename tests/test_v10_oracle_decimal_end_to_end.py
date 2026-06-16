"""V10 GodEye benchmark: oracle decimal normalization, end to end.

Covers the full chain on the oracle fixture: a borrow path reads an oracle price
through an internal view (maxBorrow) and applies a hardcoded 1e18 scale while
ignoring feed/token decimals -> ORACLE_DECIMAL_NORMALIZATION invariant -> attack
candidate -> economic severity (High, unprivileged over-borrow) -> PoC skeleton
(normalized-value assertion).
"""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.pocgen import build_skeletons
from arkheionx.severity import apply_gate
from arkheionx.severity import models as S
from arkheionx.warrun import run_war_run

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"
_FIX = "oracle_decimal_normalization_fixture"
_FAMILY = "ORACLE_DECIMAL_NORMALIZATION"


def _pipeline(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
    apply_gate(graph)
    return smap, emap, tmap, invset, graph


class OracleDecimalEndToEndTest(unittest.TestCase):
    def setUp(self):
        self.smap, self.emap, self.tmap, self.invset, self.graph = _pipeline(_FIX)

    def test_oracle_entity_detected(self):
        self.assertIn("OraclePrice", self.emap.types())

    def test_oracle_value_math_flag_on_borrow_closure(self):
        # maxBorrow is a view (skipped as its own transition) but is in borrow's
        # internal-call closure, so the price math is visible on the borrow transition.
        borrow = self.tmap.for_function("OracleLoanMarket.borrow")
        self.assertIsNotNone(borrow)
        self.assertIn("oracle_value_math", borrow.flags)
        self.assertIn("oracle_hardcoded_scale", borrow.flags)

    def test_invariant_generated_and_suspicious(self):
        inv = [i for i in self.invset.invariants if i.family == _FAMILY]
        self.assertTrue(inv, "oracle invariant not generated")
        self.assertTrue(inv[0].suspicious)
        joined = " ".join(inv[0].suspicion_reasons).lower()
        self.assertIn("decimals", joined)

    def test_candidate_present_with_complete_fields(self):
        cand = [c for c in self.graph.candidates if c.invariant_family == _FAMILY]
        self.assertTrue(cand, "no oracle candidate")
        c = cand[0]
        for field in (c.id, c.title, c.root_cause, c.broken_invariant,
                      c.attacker_capability, c.victim, c.asset, c.entry_function):
            self.assertTrue(field, "candidate field empty")
        self.assertFalse(c.role_gated)

    def test_severity_is_high(self):
        c = next(c for c in self.graph.candidates if c.invariant_family == _FAMILY)
        self.assertEqual(c.economic_severity, S.SUBMIT_HIGH_CANDIDATE)

    def test_poc_skeleton_asserts_normalized_value(self):
        skels = build_skeletons(self.graph, self.smap)
        sk = next(s for s in skels if s.family == _FAMILY)
        self.assertIn("maxBorrow", sk.source)
        self.assertIn("decimals", sk.source.lower())
        self.assertIn("safeMax", sk.source)

    def test_war_run_produces_high_candidate_no_report(self):
        res = run_war_run(_GODEYE / _FIX, write=False)
        fams = {c.invariant_family: c.economic_severity for c in res["graph"].candidates}
        self.assertEqual(fams.get(_FAMILY), S.SUBMIT_HIGH_CANDIDATE)
        self.assertFalse(res["triage"]["report_generated"])


if __name__ == "__main__":
    unittest.main()
