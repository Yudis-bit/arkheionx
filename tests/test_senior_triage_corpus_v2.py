"""Tests for the v2 known corpus engine."""
import unittest
from pathlib import Path

from arkheionx.senior_triage import corpus_v2 as cv2
from arkheionx.senior_triage import models as M

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "senior_triage_toy"


class CorpusBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ctx = M.TriageContext(
            repo_path=str(FIXTURE),
            known_path=str(FIXTURE / "known"),
            audits_path=str(FIXTURE / "audits"),
        )
        cls.corpus = cv2.build_corpus(ctx, FIXTURE)

    def test_corpus_extracts_documents(self) -> None:
        self.assertTrue(self.corpus)
        kinds = {d.kind for d in self.corpus}
        self.assertIn("known", kinds)
        self.assertIn("audit", kinds)

    def test_documents_have_line_offsets_and_line_lookup(self) -> None:
        doc = next(d for d in self.corpus if d.kind == "audit")
        self.assertTrue(doc.line_offsets)
        # Offset 0 is line 1; a later offset maps to a later line.
        self.assertEqual(doc.line_offsets[0], 0)
        self.assertGreaterEqual(doc.line_of(len(doc.text) - 1), 1)

    def test_records_carry_entities_behaviors_statuses(self) -> None:
        doc = next(d for d in self.corpus if d.kind == "known")
        rec = doc.to_record()
        self.assertIn("source_path", rec)
        self.assertTrue(rec["detected_behaviors"])
        # The known-issues fixture mentions deposit/inflation and acknowledged/duplicate.
        self.assertTrue(set(doc.fingerprint.behaviors) & {"deposit", "inflation", "share"})
        self.assertTrue(doc.fingerprint.statuses)


class DetectionUnitTests(unittest.TestCase):
    def test_detect_behaviors(self) -> None:
        beh = cv2.detect_behaviors("The withdraw path has an inflation rounding bug in shares.")
        self.assertIn("withdraw", beh)
        self.assertIn("inflation", beh)
        self.assertIn("rounding", beh)

    def test_detect_statuses(self) -> None:
        st = cv2.detect_statuses("This is acknowledged and a known issue, by design. Spearbit reviewed it.")
        self.assertIn("acknowledged", st)
        self.assertIn("spearbit", st)

    def test_detect_entities_camel_and_calls(self) -> None:
        ent = cv2.detect_entities("OldVault.deposit() calls SafeTransfer and the owner role.")
        self.assertIn("oldvault", {e.lower() for e in ent})
        self.assertIn("owner", {e.lower() for e in ent})

    def test_token_shingles(self) -> None:
        sh = cv2.token_shingles("alpha beta gamma", 2)
        self.assertIn("alpha beta", sh)
        self.assertIn("beta gamma", sh)


class PdfTests(unittest.TestCase):
    def test_pdf_marked_unavailable_without_lib(self) -> None:
        import importlib.util
        have_lib = any(importlib.util.find_spec(n) is not None for n in ("pypdf", "PyPDF2", "pdfminer"))
        if have_lib:
            self.skipTest("a PDF library is installed; the unavailable path is not exercised")
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "report.pdf").write_bytes(b"%PDF-1.4 fake")
            ctx = M.TriageContext(repo_path=tmp, audits_path=tmp)
            docs = cv2._maybe_pdf_documents("", tmp)
            self.assertTrue(docs)
            self.assertEqual(docs[0].note, "UNPARSED_PDF_TEXT_EXTRACTION_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
