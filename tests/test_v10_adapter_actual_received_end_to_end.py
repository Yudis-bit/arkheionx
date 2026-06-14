"""V10 GodEye benchmark: adapter actual-received-vs-credited, end to end.

Covers the full chain on the adapter fixture: entities -> transitions ->
invariant (suspicious, locally testable) -> attack candidate (complete fields) ->
economic severity (Medium, not fork) -> Foundry PoC skeleton (balance-delta
assertions) -> war-run (candidate present, no report).
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
_FIX = "adapter_actual_received_vs_credited_fixture"
_FAMILY = "SWAP_ACTUAL_RECEIVED_VS_CREDITED"


def _pipeline(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
    apply_gate(graph)
    return smap, emap, tmap, invset, graph


class AdapterEndToEndTest(unittest.TestCase):
    def setUp(self):
        self.smap, self.emap, self.tmap, self.invset, self.graph = _pipeline(_FIX)

    def test_adapter_entity_detected(self):
        self.assertIn("Adapter", self.emap.types())

    def test_credit_no_balance_delta_flag_on_deposit(self):
        dep = self.tmap.for_function("CreditAdapter.deposit")
        self.assertIsNotNone(dep)
        self.assertIn("credit_no_balance_delta", dep.flags)

    def test_invariant_generated_and_suspicious(self):
        inv = [i for i in self.invset.invariants if i.family == _FAMILY]
        self.assertTrue(inv, "adapter invariant not generated")
        self.assertTrue(inv[0].suspicious)
        joined = " ".join(inv[0].suspicion_reasons).lower()
        self.assertIn("nominal", joined)
        self.assertTrue("balance delta" in joined or "balanceof" in joined)

    def test_invariant_is_locally_testable_not_fork(self):
        inv = next(i for i in self.invset.invariants if i.family == _FAMILY)
        self.assertEqual(inv.testability, "local")

    def test_candidate_present_with_complete_fields(self):
        cand = [c for c in self.graph.candidates if c.invariant_family == _FAMILY]
        self.assertTrue(cand, "no adapter candidate")
        c = cand[0]
        for field in (c.id, c.title, c.root_cause, c.broken_invariant,
                      c.attacker_capability, c.victim, c.asset, c.entry_function):
            self.assertTrue(field, "candidate field empty")
        self.assertFalse(c.role_gated)

    def test_not_misclassified_as_reentrancy_high(self):
        # The adapter deposit must NOT surface as a DEPOSIT_CONSUMPTION high; the root
        # cause is over-crediting, not a double-use window.
        fams = [c.invariant_family for c in self.graph.candidates]
        self.assertNotIn("DEPOSIT_CONSUMPTION", fams)

    def test_severity_is_medium(self):
        c = next(c for c in self.graph.candidates if c.invariant_family == _FAMILY)
        self.assertEqual(c.economic_severity, S.SUBMIT_MEDIUM_CANDIDATE)

    def test_poc_skeleton_asserts_balance_delta(self):
        skels = build_skeletons(self.graph, self.smap)
        sk = next(s for s in skels if s.family == _FAMILY)
        self.assertIn("balanceOf", sk.source)
        self.assertIn("credited", sk.source)
        self.assertIn("actual", sk.source)

    def test_war_run_produces_candidate_no_report(self):
        res = run_war_run(_GODEYE / _FIX, write=False)
        fams = {c.invariant_family: c.economic_severity for c in res["graph"].candidates}
        self.assertEqual(fams.get(_FAMILY), S.SUBMIT_MEDIUM_CANDIDATE)
        self.assertFalse(res["triage"]["report_generated"])


if __name__ == "__main__":
    unittest.main()
