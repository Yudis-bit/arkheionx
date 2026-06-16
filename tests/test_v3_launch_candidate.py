"""v8.0.1 public-stable surface tests (originally the v3 launch-candidate suite).

The clean v8.0.1 product README no longer carries the v3 launch positioning or the
architecture image wall. These tests assert the current clean surface and keep the
meaningful guards: version metadata, asset XML validity, no premature/distribution
claims, changelog history, and source-installer stable-tag tracking.
"""
import unittest
import xml.dom.minidom
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
# These SVG assets back the docs site. The README is now text-first, but the assets
# must still be present and valid XML.
DOC_VISUALS = [
    "docs/assets/arkheionx-v3-architecture.svg",
    "docs/assets/arkheionx-v3-public-surface.svg",
    "docs/assets/arkheionx-v3-demo-fixtures.svg",
    "docs/assets/arkheionx-v3-stability.svg",
]


def read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8", errors="ignore")


class VersionMetadataTests(unittest.TestCase):
    def test_version_metadata(self) -> None:
        from arkheionx.version import (
            CURRENT_MILESTONE,
            NEXT_MILESTONE,
            PACKAGE_VERSION,
            STABLE_RELEASE,
            __version__,
        )

        self.assertEqual(__version__, "10.1.0.dev0")
        self.assertEqual(PACKAGE_VERSION, "10.1.0.dev0")
        self.assertEqual(STABLE_RELEASE, "v8.0.1")
        self.assertEqual(CURRENT_MILESTONE, "v10.1.0-dev")
        self.assertEqual(NEXT_MILESTONE, "v10.1.0")


class ReadmeSurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.readme = read("README.md")

    def test_clean_product_positioning(self) -> None:
        self.assertIn("# ArkheionX", self.readme)
        self.assertIn("Local-first review infrastructure for smart contract security.", self.readme)
        self.assertIn("It does not replace auditors.", self.readme)
        self.assertIn("It gives auditors a better map.", self.readme)
        self.assertIn("Latest stable release: **v8.0.1", self.readme)
        # Legacy launch soup must be gone from the current product surface.
        for legacy in [
            "v3.0.0 is the public stable launch",
            "## Architecture",
            "## What's Stable in v3.0.0",
        ]:
            self.assertNotIn(legacy, self.readme)

    def test_doc_visuals_are_valid_xml(self) -> None:
        for visual in DOC_VISUALS:
            path = REPO_ROOT / visual
            self.assertTrue(path.is_file(), visual)
            xml.dom.minidom.parseString(path.read_text(encoding="utf-8"))  # raises on bad XML

    def test_docs_map_links_command_surface(self) -> None:
        self.assertIn("](docs/PUBLIC_SURFACE.md)", self.readme)

    def test_no_premature_or_distribution_claims(self) -> None:
        lowered = self.readme.lower()
        for claim in ["v8.0.1 is released", "now on pypi", "available on pypi",
                      "pip install arkheionx", "brew install", "homebrew tap"]:
            self.assertNotIn(claim, lowered)


class DocsTests(unittest.TestCase):
    def test_changelog_keeps_history_and_current(self) -> None:
        changelog = read("CHANGELOG.md")
        self.assertIn("## v3.0.0 - 2026-05-31", changelog)
        self.assertIn("## v8.0.1", changelog)

    def test_roadmap_marks_current_and_history(self) -> None:
        roadmap = read("docs/ROADMAP.md")
        self.assertIn("Current milestone: v10.1.0-dev.", roadmap)
        self.assertIn("Next milestone: v10.1.0.", roadmap)
        self.assertIn("Latest stable: v8.0.1", roadmap)
        self.assertIn("v3.1.0 — Protocol Review Map", roadmap)
        self.assertIn("v10.1.0-dev — current development milestone in this checkout.", roadmap)

    def test_release_notes_exist_with_required_sections(self) -> None:
        notes = read("release-notes/v3.0.0.md")
        self.assertIn("Arkheionx v3.0.0 — Public Stable Launch", notes)
        self.assertIn("## Known limitations", notes)
        self.assertIn("## Safety boundaries", notes)
        lowered = notes.lower()
        for claim in ["already published", "now on pypi", "available on pypi",
                      "is a formal audit", "homebrew tap", "pip install arkheionx"]:
            self.assertNotIn(claim, lowered)


class StableTagTests(unittest.TestCase):
    def test_install_and_arkup_track_stable(self) -> None:
        for script in ("install.sh", "arkup"):
            self.assertIn("ARKHEIONX_STABLE_TAG:-v8.0.1", read(script))
        self.assertIn("pre-audit@v8.0.1", read("docs/GITHUB_ACTION_USAGE.md"))


if __name__ == "__main__":
    unittest.main()
