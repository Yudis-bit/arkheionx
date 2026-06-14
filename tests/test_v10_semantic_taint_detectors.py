"""V10 semantic taint / dataflow detectors.

Asserts the named detectors fire on the benchmark fixtures per the acceptance
criteria: the consent fixture shows CALLDATA_NOT_IN_HASH_BUT_IN_VALUE_SINK and
CALLDATA_TO_REFUND_AFFECTING_ROUTE; the adapter shows
CREDIT_WRITE_FROM_NOMINAL_AMOUNT; the oracle shows ORACLE_RETURN_TO_BORROW_LIMIT;
the cross-chain fixture shows MESSAGE_ID_TO_MINT_WITHOUT_CONSUME. Also wired into
war-run as the 15-dataflow-taint artifact.
"""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map, build_taint_findings
from arkheionx.semantic import detectors as D
from arkheionx.defi import build_defi_entities
from arkheionx.warrun import run_war_run

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _detectors(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    findings = build_taint_findings(smap, emap)
    return {f.detector for f in findings}, findings


class TaintDetectorTest(unittest.TestCase):
    def test_consent_unbound_calldata_in_value_sink(self):
        dets, findings = _detectors("borrow_swapdata_consent_fixture")
        self.assertIn(D.CALLDATA_NOT_IN_HASH_BUT_IN_VALUE_SINK, dets)
        self.assertIn(D.CALLDATA_TO_REFUND_AFFECTING_ROUTE, dets)
        self.assertIn(D.CALLDATA_TO_SWAP_ROUTE, dets)
        nb = next(f for f in findings if f.detector == D.CALLDATA_NOT_IN_HASH_BUT_IN_VALUE_SINK)
        self.assertTrue(nb.missing_binding)
        self.assertEqual(nb.invariant_family, "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")

    def test_consent_hash_input_detected(self):
        dets, _ = _detectors("borrow_swapdata_consent_fixture")
        self.assertIn(D.CALLDATA_TO_HASH_INPUT, dets)

    def test_adapter_credit_from_nominal(self):
        dets, findings = _detectors("adapter_actual_received_vs_credited_fixture")
        self.assertIn(D.CREDIT_WRITE_FROM_NOMINAL_AMOUNT, dets)
        f = next(f for f in findings if f.detector == D.CREDIT_WRITE_FROM_NOMINAL_AMOUNT)
        self.assertEqual(f.invariant_family, "SWAP_ACTUAL_RECEIVED_VS_CREDITED")

    def test_oracle_return_to_borrow_limit(self):
        dets, _ = _detectors("oracle_decimal_normalization_fixture")
        self.assertIn(D.ORACLE_RETURN_TO_BORROW_LIMIT, dets)

    def test_cross_chain_message_id_to_mint(self):
        dets, findings = _detectors("cross_chain_supply_conservation_fixture")
        self.assertIn(D.MESSAGE_ID_TO_MINT_WITHOUT_CONSUME, dets)
        f = next(f for f in findings if f.detector == D.MESSAGE_ID_TO_MINT_WITHOUT_CONSUME)
        self.assertTrue(f.missing_binding)

    def test_deposit_status_write_after_external_call(self):
        dets, _ = _detectors("deposit_double_use_fixture")
        self.assertIn(D.STATUS_WRITE_AFTER_EXTERNAL_CALL, dets)

    def test_no_false_taint_on_trusted_role(self):
        # The trusted-role treasury has no attacker-controlled value-sink flow.
        dets, _ = _detectors("trusted_role_fixture")
        self.assertNotIn(D.CREDIT_WRITE_FROM_NOMINAL_AMOUNT, dets)
        self.assertNotIn(D.MESSAGE_ID_TO_MINT_WITHOUT_CONSUME, dets)

    def test_war_run_emits_taint_artifact(self):
        res = run_war_run(_GODEYE / "adapter_actual_received_vs_credited_fixture", write=False)
        self.assertIn("15-dataflow-taint.json", res["jsons"])
        self.assertIn("15-dataflow-taint.md", res["contents"])
        self.assertGreaterEqual(res["counts"]["taint_findings"], 1)
        self.assertTrue(res["triage"]["dataflow_taint"])


if __name__ == "__main__":
    unittest.main()
