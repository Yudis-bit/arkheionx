"""Tests for local-validation context in the report workflow (v3.7)."""
from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.reporting.builder import build_report, report_markdown
from arkheionx.reporting.render import render_report

_EVIDENCE = {
    "target": "src/Vault.sol:Vault.withdraw(uint256)",
    "target_id": "src/Vault.sol:Vault.withdraw(uint256)#L10-L20",
    "evidence_package_id": "evidence:Vault_withdraw:abc123def456",
    "evidence_level": "EVIDENCE_READY", "status": "evidence_ready",
    "source_artifacts": {"proof_json": "p.json", "trace_json": "t.json", "trace_status": "linked"},
    "manifest": {"sources": [
        {"kind": "proof", "path": "p.json", "exists": True, "receipt_id": "proof:V"},
        {"kind": "trace", "path": "t.json", "exists": True, "receipt_id": "trace:V"}],
        "checks": {"trace_linked": True, "human_review_required": True}},
    "proof_summary": {"status": "tested_passed", "tests_run": 1, "passed": 1, "failed": 0, "skipped": 0,
                      "foundry_command": "forge test"},
    "trace_summary": {"summary_available": True, "reverts": [], "assertion_failures": [], "call_sequence": [], "logs": []},
    "impact_notes": {"candidate_impact": "x", "affected_components": ["a"],
                     "assumptions": ["a"], "limitations": ["Not a formal audit."]},
}
_SUPPORT = {
    "summary_id": "local-validation-summary:foundry:h:s",
    "run_id": "local-validation-run:foundry:h:s",
    "source": "local-validation/summary.json",
    "tested_count": 2, "trace_bound_count": 1, "needs_review_count": 1,
    "entries": [], "limitations": ["Manual review is required; ready_for_submission is false."],
    "manual_review_required": True, "ready_for_submission": False,
}


def _evidence_with_support():
    ev = deepcopy(_EVIDENCE)
    ev["local_validation_support"] = deepcopy(_SUPPORT)
    return ev


def _build(evidence):
    return build_report(evidence, Path("."), ArtifactWriter(Path(tempfile.mkdtemp())), write=False)


class ReportLocalValidationTests(unittest.TestCase):
    def test_build_succeeds_without_support(self) -> None:
        draft = _build(_EVIDENCE)
        self.assertNotIn("local_validation_support", draft.payload)

    def test_report_includes_support_when_present(self) -> None:
        payload = _build(_evidence_with_support()).payload
        self.assertIn("local_validation_support", payload)
        self.assertIs(payload["local_validation_support"]["observed"], True)

    def test_summarizes_counts(self) -> None:
        lvs = _build(_evidence_with_support()).payload["local_validation_support"]
        self.assertEqual(lvs["tested_support"], 2)
        self.assertEqual(lvs["trace_bound_support"], 1)
        self.assertEqual(lvs["tests_needing_review"], 1)

    def test_report_stays_draft_and_manual_review(self) -> None:
        payload = _build(_evidence_with_support()).payload
        self.assertEqual(payload["review_status"], "NEEDS_HUMAN_REVIEW")
        self.assertEqual(payload["report_readiness"]["status"], "draft")
        self.assertTrue(payload["report_readiness"]["requires_manual_review"])

    def test_support_not_ready_and_no_human_reviewed(self) -> None:
        payload = _build(_evidence_with_support()).payload
        self.assertIs(payload["local_validation_support"]["ready_for_submission"], False)
        self.assertIs(payload["report_readiness"]["ready_for_submission"], False)
        self.assertNotIn("HUMAN_REVIEWED", json.dumps(payload))

    def test_support_note_makes_no_positive_claim(self) -> None:
        note = _build(_evidence_with_support()).payload["local_validation_support"]["note"].lower()
        for positive in ("confirmed vulnerability", "final severity:", "audit passed",
                         "guaranteed bounty", "ready to submit", "human_reviewed"):
            self.assertNotIn(positive, note)

    def test_existing_report_safety_guard_holds_with_support(self) -> None:
        # Mirror the evidence/validate report.json checks against the payload blob.
        blob = json.dumps(_build(_evidence_with_support()).payload).lower()
        for phrase in ("ready to submit", "guaranteed bounty", "guaranteed exploit", "final severity:"):
            self.assertNotIn(phrase, blob)

    def test_render_markdown_includes_context_when_present(self) -> None:
        md = report_markdown(_build(_evidence_with_support()).payload)
        self.assertIn("## Local Validation Context", md)
        self.assertIn("Tested support: 2", md)

    def test_render_markdown_omits_context_when_absent(self) -> None:
        self.assertNotIn("## Local Validation Context", report_markdown(_build(_EVIDENCE).payload))

    def test_render_cli_includes_context_when_present(self) -> None:
        draft = _build(_evidence_with_support())
        self.assertIn("Local Validation Context", render_report(draft, "proj"))


if __name__ == "__main__":
    unittest.main()
