import re
import unittest
from pathlib import Path

from arkheionx.version import CURRENT_MILESTONE, NEXT_MILESTONE, __version__

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


class ReleaseReadinessTests(unittest.TestCase):
    def test_version_metadata(self) -> None:
        self.assertEqual(__version__, "2.2.0")
        self.assertEqual(CURRENT_MILESTONE, "v2.2.0")
        self.assertEqual(NEXT_MILESTONE, "v2.3.0")

    def test_release_artifacts_exist(self) -> None:
        for path in [
            "release-notes/v2.2.0.md",
            "docs/EXECUTION_PROOF.md",
            "docs/TRACE_ENGINE.md",
            "docs/RELEASE_CHECKLIST.md",
            "schemas/proof-artifact.schema.json",
            "schemas/trace.schema.json",
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
        self.assertIn("a relevant local Foundry test actually executed", readme)

    def test_changelog_has_v220(self) -> None:
        changelog = read("CHANGELOG.md")
        self.assertIn("## v2.2.0", changelog)
        self.assertNotIn("## v2.2.0 - Unreleased", changelog)

    def test_trace_not_marked_planned(self) -> None:
        # trace is implemented; it must not appear under a "Planned" section.
        for doc in ["docs/SOLO_RESEARCH_WORKFLOW.md", "docs/FOUNDRY_INTEGRATION.md"]:
            text = read(doc)
            planned = text.split("Planned commands", 1)[-1] if "Planned commands" in text else ""
            self.assertNotIn("arkheionx trace", planned)

    def test_generated_output_is_gitignored(self) -> None:
        self.assertIn(".arkheionx/", read(".gitignore"))


if __name__ == "__main__":
    unittest.main()
