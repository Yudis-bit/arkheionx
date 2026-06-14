"""V10 GodEye benchmark: cross-chain supply conservation, end to end.

Covers the full chain on the cross-chain fixture: a destination bridge mints on an
incoming message id with no processed/consumed guard ->
CROSS_CHAIN_SUPPLY_CONSERVATION invariant (locally provable replay) -> attack
candidate -> economic severity (High, systemic supply inflation) -> PoC skeleton
(replay-mint assertion). Also asserts the bridged token is NOT misread as a vault.
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
_FIX = "cross_chain_supply_conservation_fixture"
_FAMILY = "CROSS_CHAIN_SUPPLY_CONSERVATION"


def _pipeline(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
    apply_gate(graph)
    return smap, emap, tmap, invset, graph


class CrossChainEndToEndTest(unittest.TestCase):
    def setUp(self):
        self.smap, self.emap, self.tmap, self.invset, self.graph = _pipeline(_FIX)

    def test_cross_chain_entity_detected(self):
        self.assertIn("CrossChainSupply", self.emap.types())

    def test_bridged_token_not_misread_as_vault(self):
        # A plain mintable/bridged token (balanceOf + totalSupply) must not be
        # detected as a vault, nor produce a vault-share candidate.
        self.assertNotIn("Vault", self.emap.types())
        self.assertNotIn("Share", self.emap.types())
        fams = [c.invariant_family for c in self.graph.candidates]
        self.assertNotIn("VAULT_SHARE_ASSET_RECONCILIATION", fams)

    def test_xchain_overmint_flag_on_receive(self):
        rec = self.tmap.for_function("DestinationBridge.receiveMessage")
        self.assertIsNotNone(rec)
        self.assertIn("xchain_overmint", rec.flags)

    def test_invariant_generated_and_suspicious(self):
        inv = [i for i in self.invset.invariants if i.family == _FAMILY]
        self.assertTrue(inv, "cross-chain invariant not generated")
        self.assertTrue(inv[0].suspicious)
        joined = " ".join(inv[0].suspicion_reasons).lower()
        self.assertTrue("replay" in joined or "consumed" in joined or "processed" in joined)

    def test_invariant_is_locally_testable(self):
        inv = next(i for i in self.invset.invariants if i.family == _FAMILY)
        self.assertEqual(inv.testability, "local")

    def test_candidate_present_with_complete_fields(self):
        cand = [c for c in self.graph.candidates if c.invariant_family == _FAMILY]
        self.assertTrue(cand, "no cross-chain candidate")
        c = cand[0]
        for field in (c.id, c.title, c.root_cause, c.broken_invariant,
                      c.attacker_capability, c.victim, c.asset, c.entry_function):
            self.assertTrue(field, "candidate field empty")
        self.assertFalse(c.role_gated)

    def test_severity_is_high(self):
        c = next(c for c in self.graph.candidates if c.invariant_family == _FAMILY)
        self.assertEqual(c.economic_severity, S.SUBMIT_HIGH_CANDIDATE)

    def test_poc_skeleton_asserts_replay_mint(self):
        skels = build_skeletons(self.graph, self.smap)
        sk = next(s for s in skels if s.family == _FAMILY)
        self.assertIn("receiveMessage", sk.source)
        self.assertIn("totalSupply", sk.source)
        self.assertIn("replay", sk.source.lower())

    def test_war_run_produces_high_candidate_no_report(self):
        res = run_war_run(_GODEYE / _FIX, write=False)
        fams = {c.invariant_family: c.economic_severity for c in res["graph"].candidates}
        self.assertEqual(fams.get(_FAMILY), S.SUBMIT_HIGH_CANDIDATE)
        self.assertFalse(res["triage"]["report_generated"])


if __name__ == "__main__":
    unittest.main()
