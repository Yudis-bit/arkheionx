"""Guard: the root README stays a clean, current product surface.

Fails if the README drifts back into version soup, drops the core story or the
safety boundary, grows past the product-README budget, or reintroduces
target-specific names or AI-hype wording.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AI_HYPE = [
    "ai-powered", "revolutionize", "revolutionary", "cutting-edge", "supercharge",
    "ultimate", "game-changing", "next-generation", "best-in-class", "world-class",
    "seamlessly", "turbocharge",
]
LEGACY_SOUP = [
    "## what's stable in v3",
    "## architecture",
    "try the v4 demo",
    "v4 stable scope",
    "control plane",
    "developer-native review map and local artifact foundation",
    "map the protocol. prove the path. prepare the handoff.",
]
CLEAN_HEADINGS = [
    "## What it does",
    "## What it is not",
    "## Who it is for",
    "## Why it exists",
    "## Quickstart",
    "## Example workflow",
    "## Documentation",
    "## Outputs",
    "## Case studies",
    "## Current status",
    "## Limitations",
    "## Safety boundaries",
    "## Security and ethics",
]


class ReadmeIsCleanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.lower = cls.readme.lower()

    def test_length_is_within_product_budget(self) -> None:
        lines = self.readme.splitlines()
        self.assertGreaterEqual(len(lines), 80, "README is unexpectedly short")
        self.assertLessEqual(len(lines), 160, "README exceeds the 160-line product budget")

    def test_core_story_and_command_present(self) -> None:
        self.assertIn("# ArkheionX", self.readme)
        self.assertIn("Local-first review infrastructure for smart contract security.", self.readme)
        self.assertIn("It does not replace auditors.", self.readme)
        self.assertIn("It gives auditors a better map.", self.readme)
        self.assertIn("arkheionx review", self.readme)
        self.assertIn("review-map", self.readme)

    def test_safety_boundary_present(self) -> None:
        self.assertIn(
            "No RPC. No live-chain scanning. No auto-submit. Human review required.",
            self.readme,
        )

    def test_clean_headings_present(self) -> None:
        for heading in CLEAN_HEADINGS:
            self.assertIn(heading, self.readme)

    def test_no_version_soup(self) -> None:
        for token in LEGACY_SOUP:
            self.assertNotIn(token, self.lower)
        # No per-version section headings for the old layers.
        for heading in ["## v3", "## v4", "## v5", "## v6", "## v7"]:
            self.assertNotIn(heading, self.readme)

    def test_single_current_release_reference(self) -> None:
        self.assertIn("Latest stable release: **v8.0.1", self.readme)
        self.assertNotIn("Latest stable release: **v2", self.readme)

    def test_no_ai_hype(self) -> None:
        for word in AI_HYPE:
            self.assertNotIn(word, self.lower)

    def test_no_target_specific_names(self) -> None:
        for name in ("morpho", "midnight"):
            self.assertNotIn(name, self.lower)
        self.assertIsNone(re.search(r"\bdre\b", self.lower))


if __name__ == "__main__":
    unittest.main()
