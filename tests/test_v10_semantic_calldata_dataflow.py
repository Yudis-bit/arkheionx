"""V10 semantic core: calldata -> value-affecting-sink data flow."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.semantic import models as M

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class CalldataToExternalCallTest(unittest.TestCase):
    def setUp(self):
        self.smap = build_semantic_map(_GODEYE / "borrow_swapdata_consent_fixture")

    def test_borrower_controlled_calldata_reaches_swap_route(self):
        flagged = [h for h in self.smap.dataflow_hints
                   if h.tag == M.TAG_CALLDATA_TO_SWAP_ROUTE]
        self.assertTrue(flagged, "expected a swap-route data-flow hint")
        h = flagged[0]
        self.assertEqual(h.function, "OriginationRouter._borrowFunds")
        self.assertIn("data", h.source_expr)
        self.assertIn("withdraw", h.sink_expr)

    def test_borrow_requires_msg_sender_equals_borrower(self):
        fn = self.smap.function("OriginationRouter.borrow")
        self.assertIsNotNone(fn)
        self.assertTrue(fn.uses_msg_sender)
        self.assertIn("terms.borrower", fn.calldata_fields)

    def test_consent_hash_binds_terms_but_not_info_data(self):
        # The terms hash is built over `terms`, and the swap calldata is a
        # separate calldata field that is never bound into a hash.
        hash_hints = [h for h in self.smap.dataflow_hints if h.sink_kind == M.SINK_HASH_INPUT]
        self.assertTrue(any("terms" in h.source_expr for h in hash_hints))
        self.assertFalse(any("data" in h.source_expr for h in hash_hints),
                         "info.data must NOT be bound into the consent hash")

    def test_hints_carry_confidence(self):
        for h in self.smap.dataflow_hints:
            self.assertIn(h.confidence, (M.LOW, M.MEDIUM, M.HIGH))


if __name__ == "__main__":
    unittest.main()
