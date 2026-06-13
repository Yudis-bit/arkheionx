"""Guard: the homepage and docs landing page stay clean and current.

Fails if the rebuilt homepage loses its hero, safety boundary, or install command,
grows past seven sections, or if the homepage / docs index drift back into version
soup, target-specific names, or AI-hype wording.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "src" / "pages" / "index.astro"
DOCS_INDEX = ROOT / "site" / "src" / "pages" / "docs" / "index.astro"

AI_HYPE = [
    "ai-powered", "revolutionize", "revolutionary", "cutting-edge", "supercharge",
    "ultimate", "game-changing", "next-generation",
]


class SiteIsCleanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.home = INDEX.read_text(encoding="utf-8")
        cls.docs = DOCS_INDEX.read_text(encoding="utf-8")
        cls.home_lower = cls.home.lower()
        cls.docs_lower = cls.docs.lower()

    def test_homepage_has_clear_hero(self) -> None:
        self.assertIn(
            "Local-first security research workflow for Solidity and DeFi repos.",
            self.home,
        )
        self.assertIn(
            "Arkheionx turns scope, value flow, protocol behavior, invariants, and local evidence",
            self.home,
        )

    def test_homepage_has_safety_boundary(self) -> None:
        self.assertIn(
            "No RPC. No live-chain scanning. No auto-submit. Human review required.",
            self.home,
        )
        self.assertIn("does not confirm vulnerabilities", self.home_lower)

    def test_homepage_has_install_command(self) -> None:
        self.assertIn("curl -fsSL https://arkheionx.dev/install.sh | bash", self.home)

    def test_homepage_has_exactly_seven_sections(self) -> None:
        self.assertEqual(self.home.count("<section"), 7)

    def test_homepage_and_docs_avoid_ai_hype(self) -> None:
        for word in AI_HYPE:
            self.assertNotIn(word, self.home_lower)
            self.assertNotIn(word, self.docs_lower)

    def test_no_target_specific_names(self) -> None:
        for blob in (self.home_lower, self.docs_lower):
            self.assertNotIn("morpho", blob)
            self.assertNotIn("midnight", blob)
            self.assertIsNone(re.search(r"\bdre\b", blob))

    def test_homepage_has_no_version_soup(self) -> None:
        for token in [
            "Scope-Aware Orchestration",
            "Blind Spot Intelligence",
            "Evidence Graph + Interaction Matrix",
            "technical paper",
            "Try the demo",
        ]:
            self.assertNotIn(token, self.home)
        # No current-version badge and no old per-version doc links on the homepage.
        self.assertNotIn("v8.0.0", self.home)
        self.assertNotIn("v8.0.1", self.home)
        self.assertNotIn("/docs/v7", self.home)
        self.assertNotIn("/docs/v5", self.home)

    def test_docs_index_is_a_guided_path_not_a_dump(self) -> None:
        self.assertIn("Start here", self.docs)
        self.assertIn("Archive", self.docs)
        # The old file-dump section heading must be gone.
        self.assertNotIn("Workflows &amp; release", self.docs)


if __name__ == "__main__":
    unittest.main()
