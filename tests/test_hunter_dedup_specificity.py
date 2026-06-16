"""Tests for hunter dedup specificity: public-test kill and no-overclaim of duplicates."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def lead_for(res, needle):
    for l in res["pack"].leads:
        if needle in (l.surface or "") or needle in (l.contract or ""):
            return l
    raise AssertionError(f"no lead for {needle}: {[l.surface for l in res['pack'].leads]}")


class DedupSpecificityTests(unittest.TestCase):
    def test_public_test_covered_is_killed_before_poc(self) -> None:
        b = FX / "duplicate_public_test"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        lead = lead_for(res, "ShareVault")
        self.assertEqual(lead.known_match_status, M.PUBLIC_TEST_COVERED)
        self.assertEqual(lead.decision, M.KILL_PUBLIC_TEST_COVERED)
        # No PoC plan is made for a killed lead.
        self.assertNotIn(lead.lead_id, {p.lead_id for p in res["pack"].poc_plans})

    def test_generic_overlap_is_not_a_duplicate(self) -> None:
        # A blind/generic value surface must not be over-claimed as LIKELY_DUPLICATE.
        b = FX / "adapter_withdrawability"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        for km in res["pack"].known_matches:
            self.assertNotEqual(km.known_match_status, M.LIKELY_DUPLICATE)

    def test_public_test_lead_in_hard_kills(self) -> None:
        b = FX / "duplicate_public_test"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        self.assertTrue(any(k["decision"] == M.KILL_PUBLIC_TEST_COVERED for k in res["pack"].hard_kills))


if __name__ == "__main__":
    unittest.main()
