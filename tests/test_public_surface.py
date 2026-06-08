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
        self.assertIn("Local-first protocol security control plane for DeFi teams.", readme)
        self.assertIn("Map the protocol. Prove the path. Prepare the handoff.", readme)
        self.assertIn("Developer-Native Review Map and Local Artifact Foundation", readme)
        self.assertIn("Foundry tells you which tests passed.", readme)
        self.assertIn("The full v4 Protocol", readme)
        self.assertIn("Security Control Plane remains planned direction", readme)
        self.assertRegex(readme, r"not a completed v3\.2\.0 runtime\s+surface")
        self.assertIn("## What Arkheionx Does", readme)
        self.assertIn("## What It Does Not Do", readme)
        self.assertIn("## Quick Start", readme)
        self.assertIn("## Evidence Model", readme)
        self.assertIn("## Safety Boundaries", readme)
        self.assertIn("## Documentation", readme)
        self.assertIn("Latest stable release: **v5.0.0", readme)
        # Workbench command suite is the front-page focus.
        for command in ["arkheionx open", "arkheionx review-map", "arkheionx hunt",
                        "arkheionx prove", "arkheionx trace", "arkheionx evidence",
                        "arkheionx report"]:
            self.assertIn(command, readme)
        self.assertIn(".arkheionx/out/", readme)
        self.assertIn("generated, local, gitignored, and not intended to", readme)
        self.assertIn("HUMAN_REVIEWED", readme)
        self.assertIn("manual reviewer attestation only", readme)
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
