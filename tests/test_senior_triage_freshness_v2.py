"""Tests for freshness v2 (evidence + audit baseline)."""
import unittest
from pathlib import Path

from arkheionx.senior_triage import corpus_v2 as cv2
from arkheionx.senior_triage import freshness_v2 as f2
from arkheionx.senior_triage import models as M


def audit_doc(text):
    cd = cv2.CorpusDocument(rel_path="audits/a.md", kind="audit", text=text,
                            line_offsets=cv2._line_offsets(text))
    cd.fingerprint = cv2._fingerprint(text)
    return cd


def lead(lead_id, surface, files, materiality=85, notes=None):
    return M.LeadCandidate(id=lead_id, title=surface, surface=surface, linked_files=files,
                           materiality_score=materiality, notes=notes or ["value-out"])


def assess(leads, corpus, baseline_ref="", since_date=""):
    ctx = M.TriageContext(repo_path=".", baseline_ref=baseline_ref, since_date=since_date)
    return {s.lead_id: s for s in f2.assess_freshness(ctx, Path("."), leads, corpus)}


class FreshnessV2Tests(unittest.TestCase):
    def test_new_adapter_high_freshness(self) -> None:
        leads = [lead("L1", "NewAdapter.withdrawTo", ["contracts/NewAdapter.sol"])]
        sig = assess(leads, [audit_doc("CoreVault reviewed.")])["L1"]
        self.assertEqual(sig.status, M.NEW_ADAPTER)
        self.assertGreaterEqual(sig.score, 80)
        self.assertTrue(sig.evidence)

    def test_audited_surface_is_stale_with_evidence(self) -> None:
        leads = [lead("L1", "LegacyVault.redeem", ["contracts/LegacyVault.sol"])]
        sig = assess(leads, [audit_doc("LegacyVault.redeem reviewed in full; accounting verified.")])["L1"]
        self.assertEqual(sig.status, M.STALE)
        self.assertLessEqual(sig.score, 40)
        self.assertTrue(sig.evidence)
        self.assertEqual(sig.evidence[0]["source_path"], "audits/a.md")

    def test_oracle_path_is_new_oracle_path(self) -> None:
        leads = [lead("L1", "PriceRouter.peek", ["contracts/PriceRouter.sol"], notes=["oracle-dependent"])]
        sig = assess(leads, [audit_doc("CoreVault reviewed.")])["L1"]
        self.assertEqual(sig.status, M.NEW_ORACLE_PATH)

    def test_unknown_without_baseline(self) -> None:
        leads = [lead("L1", "Plain.move", ["contracts/Plain.sol"])]
        sig = assess(leads, [])["L1"]
        self.assertEqual(sig.status, M.UNKNOWN_FRESHNESS)
        self.assertEqual(sig.score, 40)

    def test_value_bearing_absent_from_audit_is_fresh_not_priority(self) -> None:
        leads = [lead("L1", "SidePool.collect", ["contracts/SidePool.sol"])]
        sig = assess(leads, [audit_doc("CoreVault reviewed; OldVault reviewed.")])["L1"]
        self.assertEqual(sig.status, M.FRESH)
        self.assertEqual(sig.score, 55)


if __name__ == "__main__":
    unittest.main()
