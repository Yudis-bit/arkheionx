import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ABOUT_DESCRIPTION = (
    "GitHub-native DeFi pre-audit readiness and security memory OS for finding "
    "readiness gaps before audits, contests, and bug bounty launches."
)


class PublicSurfaceTests(unittest.TestCase):
    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def test_readme_front_page_positioning(self) -> None:
        readme = self.read("README.md")
        self.assertIn("GitHub-native DeFi Security Memory", readme)
        self.assertIn("Pre-Audit Readiness OS", readme)
        self.assertIn("Not an audit. A way to prepare for one.", readme)
        self.assertIn("## Start Here", readme)
        self.assertIn("## Safety Boundaries", readme)
        self.assertIn("Latest stable release: **v1.2.0", readme)
        self.assertIn("v1.1.1 | Public surface polish | Released", readme)
        self.assertIn("v1.2.0 | Paid offer refinement | Released", readme)
        self.assertIn("v1.3.0 | Ecosystem Pack | Prepared, not tagged", readme)

    def test_github_repo_surface_doc_exists(self) -> None:
        surface = self.read("docs/GITHUB_REPO_SURFACE.md")
        self.assertIn("## Recommended GitHub About", surface)
        self.assertIn(ABOUT_DESCRIPTION, surface)
        self.assertIn("## Recommended Topics", surface)
        for topic in [
            "arkheionx",
            "pre-audit",
            "audit-readiness",
            "security-memory",
            "rule-calibration",
            "github-actions",
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
