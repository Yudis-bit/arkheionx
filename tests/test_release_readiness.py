import re
import unittest
from pathlib import Path

from arkheionx.version import CURRENT_MILESTONE, NEXT_MILESTONE, __version__

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


class ReleaseReadinessTests(unittest.TestCase):
    def test_version_metadata(self) -> None:
        self.assertEqual(__version__, "10.1.0.dev0")
        self.assertEqual(CURRENT_MILESTONE, "v10.1.0-dev")
        self.assertEqual(NEXT_MILESTONE, "v10.1.0")

    def test_release_artifacts_exist(self) -> None:
        for path in [
            "release-notes/v2.2.0.md",
            "release-notes/v2.3.0.md",
            "release-notes/v2.4.0.md",
            "docs/EXECUTION_PROOF.md",
            "docs/TRACE_ENGINE.md",
            "docs/EVIDENCE_PACKAGE.md",
            "docs/REPORT_DRAFTS.md",
            "docs/EVIDENCE_WORKFLOW_HARDENING.md",
            "docs/ARTIFACT_VALIDATION.md",
            "docs/RELEASE_CHECKLIST.md",
            "schemas/proof-artifact.schema.json",
            "schemas/trace.schema.json",
            "schemas/evidence.schema.json",
            "schemas/report-draft.schema.json",
            "schemas/artifacts-index.schema.json",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_release_notes_define_evidence_and_safety(self) -> None:
        notes = read("release-notes/v2.2.0.md")
        for marker in ["HEURISTIC", "COMPILER_CONFIRMED", "EXECUTION_CONFIRMED", "arkheionx trace", "Safety boundaries"]:
            self.assertIn(marker, notes)
        self.assertIn("not a formal audit", notes.lower())

    def test_no_fake_proof_language(self) -> None:
        proof = read("docs/EXECUTION_PROOF.md")
        self.assertIn("never", proof.lower())
        self.assertIn("does not prove the absence of a bug", proof)
        # EXECUTION_CONFIRMED must be tied to actual execution everywhere it appears.
        readme = read("README.md")
        self.assertIn("a relevant local foundry test executed", readme.lower())

    def test_changelog_has_current_milestone(self) -> None:
        changelog = read("CHANGELOG.md")
        self.assertIn("## v2.4.0", changelog)
        self.assertNotIn("## v2.4.0 - Unreleased", changelog)
        self.assertIn("## v2.3.0", changelog)
        self.assertNotIn("## v2.3.0 - Unreleased", changelog)

    def test_v230_release_notes_define_evidence_and_safety(self) -> None:
        notes = read("release-notes/v2.3.0.md")
        for marker in ["arkheionx evidence", "arkheionx report", "EVIDENCE_READY", "Safety Boundaries"]:
            self.assertIn(marker, notes)
        self.assertIn("not a formal audit", notes.lower())
        self.assertIn("no auto-submit", notes.lower())

    def test_implemented_commands_not_marked_planned(self) -> None:
        # trace/evidence/report are implemented; they must not appear as planned.
        for doc in ["docs/SOLO_RESEARCH_WORKFLOW.md", "docs/FOUNDRY_INTEGRATION.md"]:
            text = read(doc)
            planned = text.split("Planned commands", 1)[-1] if "Planned commands" in text else ""
            for cmd in ["arkheionx trace", "arkheionx evidence", "arkheionx report"]:
                self.assertNotIn(cmd, planned)

    def test_generated_output_is_gitignored(self) -> None:
        self.assertIn(".arkheionx/", read(".gitignore"))

    def test_license_is_resolved(self) -> None:
        # Public-alpha license blocker: a real Apache-2.0 LICENSE must exist and
        # the README must reference it instead of advertising a pending license.
        license_text = read("LICENSE")
        self.assertIn("Apache License", license_text)
        self.assertIn("Version 2.0", license_text)
        readme = read("README.md")
        self.assertIn("](LICENSE)", readme)
        self.assertNotIn("License selection is pending", readme)


if __name__ == "__main__":
    unittest.main()
