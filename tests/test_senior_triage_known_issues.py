"""Known-issue / dedup tests for `arkheionx triage`."""
import unittest
from pathlib import Path

from arkheionx.senior_triage import known_issues as ki
from arkheionx.senior_triage import models as M
from arkheionx.senior_triage.corpus import Doc
from arkheionx.senior_triage.pack import build_senior_triage_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "senior_triage_toy"


def build(**kw):
    defaults = dict(
        scope_file=str(FIXTURE / "scope.md"),
        known_path=str(FIXTURE / "known"),
        audits_path=str(FIXTURE / "audits"),
        addresses_file=str(FIXTURE / "addresses.json"),
        write=False,
    )
    defaults.update(kw)
    return build_senior_triage_pack(FIXTURE, **defaults)


def index_by_surface(result) -> dict:
    leads = result["pack"].leads
    known = {k.lead_id: k for k in result["pack"].known_issue_map}
    out = {}
    for lead in leads:
        out[lead.surface] = (lead, known.get(lead.id))
    return out


class KnownIssueFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.idx = index_by_surface(build())

    def _lead(self, surface):
        for key, val in self.idx.items():
            if key == surface or key.endswith(surface):
                return val
        raise AssertionError(f"lead not found for surface {surface}; have {list(self.idx)}")

    def test_known_duplicate_forces_kill(self) -> None:
        lead, known = self._lead("OldVault.deposit")
        self.assertIn(known.status, (M.KNOWN_PUBLIC_TEST, M.KNOWN_LIKELY_DUP, M.KNOWN_ACK_RISK))
        self.assertEqual(lead.decision, M.LEAD_KILL)

    def test_oos_trusted_role_forces_kill(self) -> None:
        lead, known = self._lead("OldVault.sweep")
        self.assertIn(known.status, (M.KNOWN_OUT_OF_SCOPE, M.KNOWN_TRUSTED_ROLE))
        self.assertNotEqual(lead.decision, M.LEAD_PURSUE)

    def test_fresh_adapter_has_no_known_match_and_is_pursued(self) -> None:
        lead, known = self._lead("FreshAdapter.withdrawTo")
        self.assertEqual(known.status, M.KNOWN_NO_MATCH)
        self.assertEqual(lead.decision, M.LEAD_PURSUE)

    def test_dedup_confidence_low_without_known_material(self) -> None:
        result = build(known_path="", audits_path="")
        known_md = result["contents"]["02-known-issue-map.md"]
        self.assertIn("NOT_PROVIDED", known_md)
        self.assertIn("Dedup confidence: LOW", known_md)


class KnownIssueUnitTests(unittest.TestCase):
    def _lead(self, surface, notes=None):
        return M.LeadCandidate(id="LEAD-001", title=surface, surface=surface,
                               linked_functions=[surface], notes=notes or ["value-out"])

    def test_acknowledged_audit_note_is_acknowledged_risk(self) -> None:
        docs = [Doc(rel_path="audits/a.md",
                    text="OldVault.redeem accounting was acknowledged as by design.",
                    kind="audit")]
        sig = ki.map_known_issue(self._lead("OldVault.redeem"), docs,
                                 trusted_role_oos=False, corpus_provided=True)
        self.assertEqual(sig.status, M.KNOWN_ACK_RISK)
        self.assertGreaterEqual(sig.duplicate_risk_score, 75)

    def test_similar_when_behavior_only(self) -> None:
        # Behavior word matches but neither the contract nor function name appears.
        docs = [Doc(rel_path="known/k.md",
                    text="A different contract had a withdraw rounding issue once.",
                    kind="known")]
        lead = self._lead("WidgetVault.pullValue", notes=["value-out"])  # behaviors -> withdraw
        sig = ki.map_known_issue(lead, docs, trusted_role_oos=False, corpus_provided=True)
        self.assertEqual(sig.status, M.KNOWN_SIMILAR)

    def test_no_match_with_corpus(self) -> None:
        docs = [Doc(rel_path="known/k.md", text="Totally unrelated note about governance.",
                    kind="known")]
        sig = ki.map_known_issue(self._lead("BrandNew.flow", notes=["value-out"]), docs,
                                 trusted_role_oos=False, corpus_provided=True)
        self.assertEqual(sig.status, M.KNOWN_NO_MATCH)

    def test_unknown_without_corpus(self) -> None:
        sig = ki.map_known_issue(self._lead("BrandNew.flow"), [],
                                 trusted_role_oos=False, corpus_provided=False)
        self.assertEqual(sig.status, M.KNOWN_UNKNOWN)

    def test_trusted_role_oos_outranks_other_status(self) -> None:
        sig = ki.map_known_issue(self._lead("OldVault.sweep", notes=["value-out", "privileged"]),
                                 [], trusted_role_oos=True, corpus_provided=True)
        self.assertEqual(sig.status, M.KNOWN_OUT_OF_SCOPE)


if __name__ == "__main__":
    unittest.main()
