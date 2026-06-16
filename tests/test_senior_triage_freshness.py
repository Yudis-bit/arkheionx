"""Freshness-diff tests for `arkheionx triage`."""
import unittest
from pathlib import Path

from arkheionx.senior_triage import freshness, models as M
from arkheionx.senior_triage.corpus import Doc
from arkheionx.senior_triage.pack import build_senior_triage_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "senior_triage_toy"


def build():
    return build_senior_triage_pack(
        FIXTURE,
        scope_file=str(FIXTURE / "scope.md"),
        known_path=str(FIXTURE / "known"),
        audits_path=str(FIXTURE / "audits"),
        write=False,
    )


class FreshnessFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = build()
        cls.leads = {lead.surface: lead for lead in result["pack"].leads}
        cls.fresh = {f.lead_id: f for f in result["pack"].freshness_diff}
        cls.by_id = {lead.id: lead for lead in result["pack"].leads}

    def _fresh_for(self, surface):
        for s, lead in self.leads.items():
            if s.endswith(surface):
                return self.fresh[lead.id], lead
        raise AssertionError(f"no lead for {surface}")

    def test_new_adapter_is_high_freshness(self) -> None:
        sig, _ = self._fresh_for("FreshAdapter.withdrawTo")
        self.assertEqual(sig.status, M.NEW_ADAPTER)
        self.assertGreaterEqual(sig.score, 80)

    def test_audited_surface_is_stale(self) -> None:
        sig, _ = self._fresh_for("OldVault.redeem")
        self.assertEqual(sig.status, M.STALE)
        self.assertLessEqual(sig.score, 40)

    def test_fresh_outranks_stale(self) -> None:
        fresh_sig, _ = self._fresh_for("FreshAdapter.withdrawTo")
        stale_sig, _ = self._fresh_for("OldVault.redeem")
        self.assertGreater(fresh_sig.score, stale_sig.score)


class FreshnessUnitTests(unittest.TestCase):
    def _lead(self, lead_id, surface, files, materiality=85, notes=None):
        return M.LeadCandidate(id=lead_id, title=surface, surface=surface,
                               linked_files=files, materiality_score=materiality,
                               notes=notes or ["value-out"])

    def test_new_signal_filename_detected(self) -> None:
        ctx = M.TriageContext(repo_path=".")
        leads = [self._lead("LEAD-001", "NewAdapter.pull", ["contracts/NewAdapter.sol"])]
        sigs = freshness.assess_freshness(ctx, Path("."), leads, [])
        self.assertEqual(sigs[0].status, M.NEW_ADAPTER)
        self.assertGreaterEqual(sigs[0].score, 70)

    def test_audited_marked_stale(self) -> None:
        ctx = M.TriageContext(repo_path=".")
        docs = [Doc(rel_path="audits/a.md", text="LegacyThing reviewed in full.", kind="audit")]
        leads = [self._lead("LEAD-001", "LegacyThing.redeem", ["contracts/LegacyThing.sol"])]
        sigs = freshness.assess_freshness(ctx, Path("."), leads, docs)
        self.assertEqual(sigs[0].status, M.STALE)

    def test_unknown_without_baseline(self) -> None:
        ctx = M.TriageContext(repo_path=".")
        leads = [self._lead("LEAD-001", "Plain.move", ["contracts/Plain.sol"])]
        sigs = freshness.assess_freshness(ctx, Path("."), leads, [])
        self.assertEqual(sigs[0].status, M.UNKNOWN_FRESHNESS)


if __name__ == "__main__":
    unittest.main()
