"""v3.0.0 public-stable launch-candidate tests."""
import re
import unittest
import xml.dom.minidom
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
V3_VISUALS = [
    "docs/assets/arkheionx-v3-architecture.svg",
    "docs/assets/arkheionx-v3-public-surface.svg",
    "docs/assets/arkheionx-v3-demo-fixtures.svg",
    "docs/assets/arkheionx-v3-stability.svg",
]


def read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8", errors="ignore")


class V3VersionTests(unittest.TestCase):
    def test_version_metadata_is_v34_final(self) -> None:
        from arkheionx.version import (
            CURRENT_MILESTONE,
            NEXT_MILESTONE,
            PACKAGE_VERSION,
            STABLE_RELEASE,
            __version__,
        )

        self.assertEqual(__version__, "4.0.0")
        self.assertEqual(PACKAGE_VERSION, "4.0.0")
        self.assertEqual(STABLE_RELEASE, "v3.1.0")
        self.assertEqual(CURRENT_MILESTONE, "v4.0.0")
        self.assertEqual(NEXT_MILESTONE, "v4.1.0")


class V3ReadmeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.readme = read("README.md")

    def test_v3_launch_positioning(self) -> None:
        self.assertIn("v3.0.0 is the public stable launch", self.readme)
        self.assertIn("## Architecture", self.readme)
        self.assertIn("## What's Stable in v3.0.0", self.readme)

    def test_references_and_parses_v3_visuals(self) -> None:
        for visual in V3_VISUALS:
            self.assertIn(visual, self.readme, f"README missing visual: {visual}")
            path = REPO_ROOT / visual
            self.assertTrue(path.is_file(), visual)
            xml.dom.minidom.parseString(path.read_text(encoding="utf-8"))  # raises on bad XML

    def test_docs_map_links_stability_docs(self) -> None:
        for doc in ("docs/PUBLIC_SURFACE.md", "docs/STABILITY_CONTRACT.md", "docs/V3_READINESS.md"):
            self.assertIn(f"]({doc})", self.readme)

    def test_no_premature_or_distribution_claims(self) -> None:
        lowered = self.readme.lower()
        self.assertNotIn("3.0.0-dev", self.readme)  # dev string must not leak
        for claim in ["v3.0.0 is released", "now on pypi", "available on pypi",
                      "pip install arkheionx", "brew install", "homebrew tap"]:
            self.assertNotIn(claim, lowered)


class V3DocsTests(unittest.TestCase):
    def test_changelog_has_v3_unreleased(self) -> None:
        self.assertIn("## v3.0.0 - 2026-05-31", read("CHANGELOG.md"))

    def test_roadmap_marks_v3_current_and_v2_10_shipped(self) -> None:
        roadmap = read("docs/ROADMAP.md")
        self.assertIn("Current milestone: v4.0.0", roadmap)
        self.assertIn("Next milestone: v4.1.0", roadmap)
        self.assertIn("Latest stable: v3.1.0", roadmap)
        self.assertIn("v3.1.0 — Protocol Review Map", roadmap)

    def test_release_notes_exist_with_required_sections(self) -> None:
        notes = read("release-notes/v3.0.0.md")
        self.assertIn("Arkheionx v3.0.0 — Public Stable Launch", notes)
        self.assertIn("## Known limitations", notes)
        self.assertIn("## Safety boundaries", notes)
        # Not-yet-published / no distribution claims (positive phrasings only;
        # negative disclaimers like "no Homebrew" / "not a formal audit" are fine).
        lowered = notes.lower()
        for claim in ["already published", "now on pypi", "available on pypi",
                      "is a formal audit", "homebrew tap", "pip install arkheionx"]:
            self.assertNotIn(claim, lowered)

    def test_v3_readiness_is_shipped(self) -> None:
        readiness = read("docs/V3_READINESS.md")
        self.assertIn("shipped", readiness.lower())
        self.assertIn("v3.1.0", readiness)


class V3StableTagTests(unittest.TestCase):
    def test_install_and_arkup_track_v3_stable(self) -> None:
        for script in ("install.sh", "arkup"):
            self.assertIn("ARKHEIONX_STABLE_TAG:-v3.1.0", read(script))
        self.assertIn("pre-audit@v3.1.0", read("README.md"))


if __name__ == "__main__":
    unittest.main()
