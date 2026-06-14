"""V10 state transition engine: borrow lifecycle."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.state import transitions as T

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class BorrowTransitionTest(unittest.TestCase):
    def setUp(self):
        smap = build_semantic_map(_GODEYE / "borrow_swapdata_consent_fixture")
        emap = build_defi_entities(smap)
        self.tmap = build_transitions(smap, emap)
        self.borrow = self.tmap.for_function("OriginationRouter.borrow")

    def test_borrow_transition_exists(self):
        self.assertIsNotNone(self.borrow)
        self.assertEqual(self.borrow.lifecycle, T.LC_BORROW)

    def test_actor_bound_to_borrower(self):
        self.assertIn("borrower", self.borrow.actor)

    def test_precondition_msg_sender_borrower(self):
        joined = " ".join(self.borrow.preconditions)
        self.assertIn("msg.sender", joined)
        self.assertIn("terms.borrower", joined)

    def test_calldata_route_flag_and_consent_invariant(self):
        self.assertIn("calldata_route", self.borrow.flags)
        self.assertIn("LENDER_CONSENT_VALUE_AFFECTING_CALLDATA", self.borrow.possible_invariants)
        self.assertIn("BORROW_CONSERVATION", self.borrow.possible_invariants)


if __name__ == "__main__":
    unittest.main()
