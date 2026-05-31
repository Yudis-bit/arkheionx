import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STABLE_ACTION = "Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v2.9.0"


class V1StabilityTests(unittest.TestCase):
    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def test_public_docs_name_stable_surface(self) -> None:
        readme = self.read("README.md")
        self.assertIn("Latest stable release: **v2.9.0", readme)
        self.assertIn(STABLE_ACTION, readme)
        self.assertIn("docs/CLI_REFERENCE.md", readme)

        action_docs = self.read("docs/GITHUB_ACTION_USAGE.md")
        self.assertIn("Stable v2.0.0 Inputs", action_docs)
        self.assertIn(STABLE_ACTION, action_docs)

    def test_v1_reference_files_exist(self) -> None:
        for path in [
            "docs/CLI_REFERENCE.md",
            "docs/SCHEMA_REFERENCE.md",
            "docs/OUTPUT_ARTIFACTS.md",
            "docs/V1_0_RELEASE_NOTES_DRAFT.md",
            "Makefile",
            "scripts/check_docs_links.py",
            "scripts/check_version_consistency.py",
            "scripts/check_safety_wording.py",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_stability_check_scripts_pass(self) -> None:
        for command in [
            ["python3", "scripts/check_version_consistency.py", "--check"],
            ["python3", "scripts/check_safety_wording.py"],
            ["python3", "scripts/check_docs_links.py", "--check"],
        ]:
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_changelog_and_roadmap_mark_v1_candidate(self) -> None:
        changelog = self.read("CHANGELOG.md")
        self.assertIn("## v2.2.0", changelog)
        self.assertNotIn("## v2.2.0 - Unreleased", changelog)
        self.assertIn("## v2.0.0", changelog)
        self.assertNotIn("## v2.0.0 - Unreleased", changelog)
        self.assertIn("## v1.9.0", changelog)
        self.assertNotIn("## v1.9.0 - Unreleased", changelog)
        self.assertIn("## v1.8.0", changelog)
        self.assertNotIn("## v1.8.0 - Unreleased", changelog)
        self.assertIn("## v1.7.0", changelog)
        self.assertNotIn("## v1.7.0 - Unreleased", changelog)
        self.assertIn("## v1.6.0", changelog)
        self.assertIn("## v1.5.0", changelog)
        self.assertIn("## v1.4.0", changelog)
        self.assertIn("## v1.2.0", changelog)
        self.assertIn("## v1.1.1", changelog)
        self.assertIn("## v1.1.0", changelog)
        self.assertIn("## v1.0.1", changelog)
        roadmap = self.read("docs/ROADMAP.md")
        self.assertIn("v1.0.0: Stable public release", roadmap)
        self.assertIn("v1.2.0: Paid Offer Refinement released", roadmap)
        self.assertIn("v1.3.0: Ecosystem Pack released", roadmap)
        self.assertIn("v1.4.0: AMM + Lending Protocol Packs released", roadmap)
        self.assertIn("v1.5.0: Invariant/Test Plan Generator Upgrade released", roadmap)
        self.assertIn("v1.6.0: Internal Engine Split released", roadmap)
        self.assertIn("v1.7.0: Config + Rule Pack Stabilization released", roadmap)
        self.assertIn("v1.8.0: Report UX + Noise Reduction released", roadmap)
        self.assertIn("v1.9.0: Pre-v2 CLI Candidate released", roadmap)
        self.assertIn("v2.0.0: Installable Arkheionx CLI / Package released", roadmap)
        self.assertIn("v2.2.0: Execution Proof & Trace Workbench shipped", roadmap)
        self.assertIn("v2.3.0: Evidence & Report Package shipped", roadmap)
        self.assertIn("v2.4.0: Evidence Workflow Hardening shipped", roadmap)
        self.assertIn("v2.5.0: Installer & Onboarding shipped", roadmap)


if __name__ == "__main__":
    unittest.main()
