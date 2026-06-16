"""V10 DeFi entity detection: confidence and serialization."""
import json
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.defi import entities as E

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class DefiEntityConfidenceTest(unittest.TestCase):
    def test_multi_evidence_is_high_confidence(self):
        smap = build_semantic_map(_GODEYE / "loan_repay_rounding_fixture")
        emap = build_defi_entities(smap)
        loan = emap.by_type(E.LOAN)
        self.assertIsNotNone(loan)
        # Loan is evidenced by the `loans` mapping AND the `Loan` struct.
        self.assertEqual(loan.confidence, E.HIGH)

    def test_all_entities_have_confidence(self):
        smap = build_semantic_map(_GODEYE / "borrow_swapdata_consent_fixture")
        emap = build_defi_entities(smap)
        for e in emap.entities:
            self.assertIn(e.confidence, (E.LOW, E.MEDIUM, E.HIGH))

    def test_entity_map_json_safe(self):
        smap = build_semantic_map(_GODEYE / "vault_share_inflation_fixture")
        emap = build_defi_entities(smap)
        payload = json.dumps(emap.to_dict())
        self.assertIn("entities", payload)


if __name__ == "__main__":
    unittest.main()
