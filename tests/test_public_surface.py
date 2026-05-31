import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ABOUT_DESCRIPTION = (
    "Local-first DeFi value-flow workbench for mapping how assets move through "
    "protocols and finding missing security tests."
)


class PublicSurfaceTests(unittest.TestCase):
    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def test_readme_front_page_positioning(self) -> None:
        readme = self.read("README.md")
        self.assertIn("A local-first DeFi value-flow workbench.", readme)
        self.assertIn("Map the money flow. Find the missing tests.", readme)
        self.assertIn("Foundry tells you if your tests pass.", readme)
        self.assertIn("where value moves", readme)
        self.assertIn("What Arkheionx Is For", readme)
        self.assertIn("Advanced Workflow", readme)
        self.assertIn("## Start Here", readme)
        self.assertIn("## Safety Boundaries", readme)
        self.assertIn("Latest stable release: **v2.0.0", readme)
        self.assertIn("v1.1.1 | Public surface polish | Released", readme)
        self.assertIn("v1.2.0 | Paid offer refinement | Released", readme)
        self.assertIn("v1.3.0 | Ecosystem Pack | Released", readme)
        self.assertIn("v1.4.0 | AMM + Lending Protocol Packs | Released", readme)
        self.assertIn("v1.5.0 | Invariant/Test Plan Generator Upgrade | Released", readme)
        self.assertIn("v1.6.0 | Internal Engine Split | Released", readme)
        self.assertIn("v1.7.0 | Config + Rule Pack Stabilization | Released", readme)
        self.assertIn("v1.8.0 | Report UX + Noise Reduction | Released", readme)
        self.assertIn("v1.9.0 | Pre-v2 CLI Candidate | Released", readme)
        self.assertIn("v2.0.0 | Installable Arkheionx CLI / Package | Released", readme)
        self.assertIn("v2.0.1 | Packaging + Product Repositioning Hotfix | Unreleased", readme)
        self.assertIn("## Pre-v2 CLI Candidate", readme)
        self.assertIn("## Installable CLI", readme)
        self.assertIn("## Engine and CLI Roadmap", readme)

    def test_github_repo_surface_doc_exists(self) -> None:
        surface = self.read("docs/GITHUB_REPO_SURFACE.md")
        self.assertIn("## Recommended GitHub About", surface)
        self.assertIn(ABOUT_DESCRIPTION, surface)
        self.assertIn("## Recommended Topics", surface)
        for topic in [
            "arkheionx",
            "value-flow",
            "security-testing",
            "audit-readiness",
            "test-coverage",
            "local-first",
            "sarif",
        ]:
            self.assertIn(f"`{topic}`", surface)
        self.assertIn("https://github.com/Yudis-bit/DeFi-Exploit-PoCs#readme", surface)

    def test_readme_documentation_map_links_exist(self) -> None:
        readme = self.read("README.md")
        for heading in [
            "### Start",
            "### Outputs",
            "### Analysis",
            "### Feedback",
            "### Safety",
            "### Repository Surface",
        ]:
            self.assertIn(heading, readme)
        for path in re.findall(r"\]\(([^)]+)\)", readme):
            if path.startswith(("http://", "https://", "mailto:")) or path.startswith("#"):
                continue
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_public_surface_checks_pass(self) -> None:
        for command in [
            ["python3", "scripts/check_version_consistency.py", "--check"],
            ["python3", "scripts/check_docs_links.py", "--check"],
        ]:
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_fake_adoption_claims_in_public_surface(self) -> None:
        text = "\n".join(
            [
                self.read("README.md"),
                self.read("docs/GITHUB_REPO_SURFACE.md"),
                self.read("docs/marketing/BRAND.md"),
            ]
        ).lower()
        for phrase in [
            "used by top protocols",
            "trusted by auditors",
            "proven in production",
            "adopted by teams",
            "paid customer",
            "customer claim",
        ]:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
