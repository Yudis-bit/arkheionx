import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ABOUT_DESCRIPTION = (
    "Foundry-style local security workbench for DeFi protocol mapping, "
    "money-flow analysis, proof/trace evidence, and report drafting."
)


class PublicSurfaceTests(unittest.TestCase):
    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def test_readme_front_page_positioning(self) -> None:
        readme = self.read("README.md")
        self.assertIn("# Arkheionx", readme)
        self.assertIn("A Foundry-style local security workbench for DeFi protocol research.", readme)
        self.assertIn("Find the money. Map the protocol. Prove the path.", readme)
        self.assertIn("Foundry tells you whether your tests pass.", readme)
        self.assertIn("## Why Arkheionx", readme)
        self.assertIn("## 60-Second Quickstart", readme)
        self.assertIn("## Evidence Model", readme)
        self.assertIn("## Safety Boundaries", readme)
        self.assertIn("## Documentation", readme)
        self.assertIn("Latest stable release: **v2.4.0", readme)
        # Workbench command suite is the front-page focus.
        for command in ["arkheionx open", "arkheionx hunt", "arkheionx prove",
                        "arkheionx trace", "arkheionx evidence", "arkheionx report"]:
            self.assertIn(command, readme)
        # No stale v2.3.0-as-latest-stable wording.
        self.assertNotIn("Latest stable release: **v2.3.0", readme)

    def test_github_repo_surface_doc_exists(self) -> None:
        surface = self.read("docs/GITHUB_REPO_SURFACE.md")
        self.assertIn("## Recommended GitHub About", surface)
        self.assertIn(ABOUT_DESCRIPTION, surface)
        self.assertIn("## Recommended Topics", surface)
        for topic in [
            "arkheionx",
            "defi-security",
            "smart-contract-security",
            "foundry",
            "solidity",
            "security-tools",
            "web3-security",
            "audit-readiness",
            "local-first",
            "static-analysis",
            "trace-analysis",
            "invariant-testing",
            "developer-tools",
        ]:
            self.assertIn(f"`{topic}`", surface)
        self.assertIn("https://github.com/Yudis-bit/DeFi-Exploit-PoCs#readme", surface)

    def test_readme_documentation_links_exist(self) -> None:
        readme = self.read("README.md")
        self.assertIn("## Documentation", readme)
        for section in ["Start:", "Core workflow:", "Advanced:"]:
            self.assertIn(section, readme)
        for path in re.findall(r"(?<!!)\]\(([^)]+)\)", readme):
            if path.startswith(("http://", "https://", "mailto:")) or path.startswith("#"):
                continue
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_public_surface_checks_pass(self) -> None:
        for command in [
            ["python3", "scripts/check_version_consistency.py", "--check"],
            ["python3", "scripts/check_docs_links.py", "--check"],
        ]:
            result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
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
            "world leading",
            "guaranteed bug discovery",
        ]:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
