"""Tests for semantic dedup v2."""
import unittest

from arkheionx.senior_triage import corpus_v2 as cv2
from arkheionx.senior_triage import dedup_v2
from arkheionx.senior_triage import models as M


def doc(rel, kind, text):
    cd = cv2.CorpusDocument(rel_path=rel, kind=kind, text=text, line_offsets=cv2._line_offsets(text))
    cd.fingerprint = cv2._fingerprint(text)
    return cd


def lead(surface, notes=None, reason=""):
    return M.LeadCandidate(id="LEAD-001", title=surface, surface=surface, reason=reason,
                           linked_functions=[surface], notes=notes or ["value-out"])


def classify(L, corpus, oos=False, provided=True):
    return dedup_v2.classify(L, corpus, trusted_role_oos=oos, corpus_provided=provided)


class DedupV2Tests(unittest.TestCase):
    def test_public_test_coverage_is_killed(self) -> None:
        corpus = [doc("tests/Known.t.sol", "test",
                      "contract KnownTest is Test { function testShareVaultDepositInflation() public {"
                      " // ShareVault deposit inflation share rounding } }")]
        sig = classify(lead("ShareVault.deposit", notes=["value-in"]), corpus)
        self.assertEqual(sig.status, M.KNOWN_PUBLIC_TEST)
        self.assertEqual(sig.confidence, M.CONF_HIGH)

    def test_high_confidence_duplicate(self) -> None:
        corpus = [doc("audits/a.md", "audit",
                      "RoundingVault.withdraw rounding is a duplicate of a prior finding; previously reported.")]
        sig = classify(lead("RoundingVault.withdraw"), corpus)
        self.assertEqual(sig.status, M.KNOWN_LIKELY_DUP)
        self.assertEqual(sig.confidence, M.CONF_HIGH)
        self.assertGreaterEqual(sig.duplicate_risk_score, 85)

    def test_similar_does_not_overclaim_duplicate(self) -> None:
        # Specific behavior overlaps, but on a different contract (no anchor).
        corpus = [doc("known/k.md", "known",
                      "A different protocol once had an inflation issue in its vault shares.")]
        sig = classify(lead("MyVault.inflate", notes=["value-in"], reason="inflation share accounting"), corpus)
        self.assertEqual(sig.status, M.KNOWN_SIMILAR)
        self.assertNotEqual(sig.status, M.KNOWN_LIKELY_DUP)

    def test_neutral_mention_is_no_match(self) -> None:
        # The contract is named but only as "reviewed / added after audit" — not a finding.
        corpus = [doc("audits/a.md", "audit",
                      "NewAdapter was added after this audit and was not in scope here. CoreVault reviewed.")]
        sig = classify(lead("NewAdapter.withdrawTo", notes=["value-out", "adapter"]), corpus)
        self.assertEqual(sig.status, M.KNOWN_NO_MATCH)

    def test_evidence_includes_source_path_and_line_range(self) -> None:
        corpus = [doc("audits/report.md", "audit",
                      "Intro line.\nRoundingVault.withdraw rounding duplicate of a prior finding.\nEnd.")]
        sig = classify(lead("RoundingVault.withdraw"), corpus)
        self.assertTrue(sig.evidence)
        ev = sig.evidence[0]
        self.assertEqual(ev["source_path"], "audits/report.md")
        self.assertGreaterEqual(ev["line_start"], 1)
        self.assertTrue(ev["excerpt"])

    def test_acknowledged_is_killed_status(self) -> None:
        corpus = [doc("known/k.md", "known",
                      "OldVault.deposit inflation is acknowledged and by design; won't fix.")]
        sig = classify(lead("OldVault.deposit", notes=["value-in"]), corpus)
        self.assertEqual(sig.status, M.KNOWN_ACK_RISK)

    def test_no_corpus_is_unknown(self) -> None:
        sig = classify(lead("Brand.new"), [], provided=False)
        self.assertEqual(sig.status, M.KNOWN_UNKNOWN)

    def test_trusted_role_oos_outranks(self) -> None:
        sig = classify(lead("OldVault.sweep", notes=["value-out", "privileged"]), [], oos=True)
        self.assertEqual(sig.status, M.KNOWN_OUT_OF_SCOPE)

    def test_similarity_score_is_reported(self) -> None:
        corpus = [doc("audits/a.md", "audit", "Some audit note about withdraw rounding.")]
        sig = classify(lead("X.withdraw"), corpus)
        self.assertIsInstance(sig.similarity_score, int)
        self.assertTrue(0 <= sig.similarity_score <= 100)


if __name__ == "__main__":
    unittest.main()
