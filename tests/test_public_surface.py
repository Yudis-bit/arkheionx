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
        self.assertIn("# ArkheionX", readme)
        self.assertIn("Local-first review infrastructure for smart contract security.", readme)
        self.assertIn("It does not replace auditors.", readme)
        self.assertIn("It gives auditors a better map.", readme)
        self.assertIn(
            "No RPC. No live-chain scanning. No auto-submit. Human review required.",
            readme,
        )
        # Clean product README structure for the current public ArkheionX surface.
        for heading in [
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
        ]:
            self.assertIn(heading, readme)
        self.assertIn("arkheionx review", readme)
        self.assertIn("review-map", readme)
        self.assertIn("Latest stable release: **v8.0.1", readme)
        # Version soup and old slogans must be gone from the current product surface.
        for legacy in [
            "control plane",
            "Developer-Native Review Map and Local Artifact Foundation",
            "What's Stable in v3",
            "Try the V4 demo",
            "Map the protocol. Prove the path. Prepare the handoff.",
            "Local-first Ethereum security research workflow",
        ]:
            self.assertNotIn(legacy, readme)
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
        self.assertIn("https://github.com/Yudis-bit/arkheionx#readme", surface)

    def test_readme_documentation_links_exist(self) -> None:
        readme = self.read("README.md")
        self.assertIn("## Documentation", readme)
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
