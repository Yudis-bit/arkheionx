import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class OfficialSitePublicSurfaceTests(unittest.TestCase):
    def test_required_pages_exist(self) -> None:
        pages = [
            "site/src/pages/index.astro",
            "site/src/pages/install.astro",
            "site/src/pages/docs/index.astro",
            "site/src/pages/docs/getting-started.astro",
            "site/src/pages/docs/installation.astro",
            "site/src/pages/docs/quickstart.astro",
            "site/src/pages/docs/concepts.astro",
            "site/src/pages/docs/safety-model.astro",
            "site/src/pages/docs/determinism.astro",
            "site/src/pages/docs/fixture-harness.astro",
            "site/src/pages/docs/review-workflow.astro",
            "site/src/pages/docs/cli-reference.astro",
            "site/src/pages/docs/faq.astro",
            "site/src/pages/examples.astro",
            "site/src/pages/roadmap.astro",
            "site/src/pages/security.astro",
            "site/src/pages/changelog.astro",
            "site/src/pages/releases.astro",
        ]
        for page in pages:
            self.assertTrue((ROOT / page).is_file(), page)

    def test_required_components_exist(self) -> None:
        components = [
            "Layout.astro",
            "Header.astro",
            "Footer.astro",
            "CommandBlock.astro",
            "SafetyNotice.astro",
            "SignalCard.astro",
            "DocShell.astro",
            "ProtocolGlyph.astro",
            "ManifestPanel.astro",
        ]
        for component in components:
            self.assertTrue((SITE / "src/components" / component).is_file(), component)

    def test_install_command_is_on_home_and_install_page(self) -> None:
        command = "curl -fsSL https://arkheionx.dev/install.sh | bash"
        self.assertIn(command, read("site/src/pages/index.astro"))
        self.assertIn(command, read("site/src/pages/install.astro"))

    def test_safety_boundary_appears_on_required_pages(self) -> None:
        for page in [
            "site/src/pages/index.astro",
            "site/src/pages/install.astro",
            "site/src/pages/security.astro",
            "site/src/pages/docs/safety-model.astro",
        ]:
            text = read(page)
            self.assertTrue(
                "SafetyNotice" in text or "does not confirm vulnerabilities" in text,
                page,
            )

    def test_metadata_and_theme_contract(self) -> None:
        layout = read("site/src/components/Layout.astro")
        for marker in [
            'name="description"',
            'property="og:title"',
            'property="og:description"',
            'property="og:type"',
            'rel="canonical"',
            'name="robots"',
            'name="theme-color"',
        ]:
            self.assertIn(marker, layout)

        css = read("site/src/styles/global.css")
        for marker in [
            "--bg: #06080d",
            "--panel: #0b1018",
            "--panel-2: #101722",
            "--text: #e7edf7",
            "--muted: #8b98aa",
            "--line: #253044",
            "--amber: #f0b45b",
            "--green: #7ee787",
            "--blue: #7aa2f7",
            "--red: #ff6b6b",
            "prefers-reduced-motion",
            ":focus-visible",
        ]:
            self.assertIn(marker, css)

    def test_no_private_site_directories_or_old_internal_doc_dirs(self) -> None:
        for relative in [
            "site/src/pages/internal",
            "site/src/pages/private",
            "docs/founder",
            "docs/investor",
            "docs/submission",
            "docs/dev",
        ]:
            self.assertFalse((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
