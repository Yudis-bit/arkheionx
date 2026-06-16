"""Tests for the hunter dedup corpus-quality model (BLIND/PARTIAL/USABLE/STRONG)."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


class DedupStatusTests(unittest.TestCase):
    def test_empty_corpus_is_blind(self) -> None:
        b = FX / "dedup_blind"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        self.assertEqual(res["pack"].dedup_quality.status, M.DEDUP_BLIND)
        self.assertEqual(res["triage"]["dedup_status"], M.DEDUP_BLIND)

    def test_blind_caps_normal_leads_to_park_dedup(self) -> None:
        b = FX / "dedup_blind"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        self.assertTrue(res["pack"].leads)
        for lead in res["pack"].leads:
            # No deployment mismatch and no baseline -> blind corpus parks the lead.
            self.assertEqual(lead.decision, M.PARK_DEDUP, lead.lead_id)

    def test_known_and_audits_raise_quality(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        self.assertIn(res["pack"].dedup_quality.status, (M.DEDUP_USABLE, M.DEDUP_STRONG))

    def test_blind_demotes_no_match_to_unknown(self) -> None:
        b = FX / "dedup_blind"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        for km in res["pack"].known_matches:
            self.assertNotEqual(km.known_match_status, M.NO_MATCH_FOUND,
                                "a blind corpus must not assert NO_MATCH_FOUND")


if __name__ == "__main__":
    unittest.main()
