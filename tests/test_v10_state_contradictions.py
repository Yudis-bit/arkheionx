"""V10 state-machine contradiction detector.

Acceptance: the #567-like fixture maps to REPAID_BUT_LENDER_NOT_SETTLED, the adapter
maps to CREDIT_EXCEEDS_ACTUAL_RECEIVED, and the cross-chain fixture maps to
MESSAGE_PROCESSED_NONCE_NOT_CONSUMED / DESTINATION_MINT_EXCEEDS_SOURCE_LOCK. Wired
into war-run as the 16-state-contradictions artifact.
"""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions, find_contradictions
from arkheionx.state import contradictions as C
from arkheionx.warrun import run_war_run

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _families(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    cset = find_contradictions(smap, emap, tmap)
    return cset.families(), cset


class ContradictionTest(unittest.TestCase):
    def test_repay_maps_to_repaid_but_lender_not_settled(self):
        fams, cset = _families("loan_repay_rounding_fixture")
        self.assertIn(C.REPAID_BUT_LENDER_NOT_SETTLED, fams)
        c = next(x for x in cset.contradictions
                 if x.family == C.REPAID_BUT_LENDER_NOT_SETTLED)
        self.assertEqual(c.likely_invariant, "DEBT_REPAYMENT_RECONCILIATION")
        self.assertTrue(c.poc_family)

    def test_adapter_maps_to_credit_exceeds_actual(self):
        fams, _ = _families("adapter_actual_received_vs_credited_fixture")
        self.assertIn(C.CREDIT_EXCEEDS_ACTUAL_RECEIVED, fams)

    def test_cross_chain_maps_to_message_not_consumed(self):
        fams, _ = _families("cross_chain_supply_conservation_fixture")
        self.assertTrue(
            {C.MESSAGE_PROCESSED_NONCE_NOT_CONSUMED,
             C.DESTINATION_MINT_EXCEEDS_SOURCE_LOCK} & fams)

    def test_oracle_maps_to_decimal_mismatch(self):
        fams, _ = _families("oracle_decimal_normalization_fixture")
        self.assertIn(C.ORACLE_DECIMAL_MISMATCH, fams)

    def test_deposit_maps_to_consumed_still_withdrawable(self):
        fams, _ = _families("deposit_double_use_fixture")
        self.assertIn(C.DEPOSIT_CONSUMED_STILL_WITHDRAWABLE, fams)

    def test_trusted_role_has_no_contradiction(self):
        fams, _ = _families("trusted_role_fixture")
        self.assertEqual(fams, set())

    def test_war_run_emits_contradiction_artifact(self):
        res = run_war_run(_GODEYE / "loan_repay_rounding_fixture", write=False)
        self.assertIn("16-state-contradictions.json", res["jsons"])
        self.assertIn("16-state-contradictions.md", res["contents"])
        self.assertGreaterEqual(res["counts"]["contradictions"], 1)
        self.assertTrue(res["triage"]["state_contradictions"])


if __name__ == "__main__":
    unittest.main()
