import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ValueFlowPositioningTests(unittest.TestCase):
    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def test_readme_uses_value_flow_positioning(self) -> None:
        readme = self.read("README.md")
        self.assertIn("Local-first review infrastructure for smart contract security.", readme)
        self.assertIn("value paths", readme)
        self.assertIn("value-flow map", readme)
        self.assertIn("review-map", readme)
        self.assertIn("Not an audit", readme)
        self.assertIn("No severity guarantee.", readme)

    def test_value_flow_docs_exist_and_are_linked(self) -> None:
        for path in [
            "docs/VALUE_FLOW_WORKBENCH.md",
            "docs/VALUE_FLOW_ROADMAP.md",
            "docs/DEVELOPER_RESEARCHER_WORKFLOW.md",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_roadmap_and_changelog_name_current_direction(self) -> None:
        roadmap = self.read("docs/ROADMAP.md")
        value_roadmap = self.read("docs/VALUE_FLOW_ROADMAP.md")
        changelog = self.read("CHANGELOG.md")
        self.assertIn("## v2.2.0", changelog)
        self.assertNotIn("## v2.2.0 - Unreleased", changelog)
        self.assertIn("v2.2.0: Execution Proof & Trace Workbench shipped.", roadmap)
        self.assertIn("v2.1.0 — Value Flow Map MVP", roadmap)
        self.assertIn("v3.0.0 DeFi Value Flow Workbench target.", roadmap)
        self.assertIn("DeFi Value Flow Workbench", value_roadmap)

    def test_advanced_flow_submodes_are_marked_planned(self) -> None:
        docs = "\n".join(
            self.read(path)
            for path in [
                "README.md",
                "docs/CLI_REFERENCE.md",
                "docs/archive/legacy-workflows/CLI_COMMANDS.md",
                "docs/archive/legacy-workflows/CLI_INSTALLABLE.md",
                "docs/INSTALLATION.md",
                "docs/PACKAGING.md",
                "docs/PACKAGE_ARCHITECTURE.md",
                "scripts/README.md",
                "docs/VALUE_FLOW_WORKBENCH.md",
                "docs/VALUE_FLOW_ROADMAP.md",
            ]
        )
        for command in [
            "arkheionx flow --test-gaps",
            "arkheionx flow explain",
            "arkheionx flow test-template",
            "arkheionx flow review-map",
            "arkheionx flow verify",
        ]:
            self.assertIn(command, docs)
        self.assertIn("not available in v2.0.1", docs)
        self.assertIn("planned", docs.lower())

    def test_workbench_commands_documented_as_available(self) -> None:
        cli_ref = self.read("docs/CLI_REFERENCE.md")
        for command in ["review", "review-map", "hunt", "prove", "trace", "evidence", "report"]:
            self.assertIn(command, cli_ref)
        for doc in [
            "docs/PROTOCOL_MAP.md",
            "docs/SOLO_RESEARCH_WORKFLOW.md",
            "docs/TRACE_ENGINE.md",
            "docs/EVIDENCE_PACKAGE.md",
        ]:
            self.assertTrue((REPO_ROOT / doc).exists(), doc)
        workflow = self.read("docs/SOLO_RESEARCH_WORKFLOW.md")
        self.assertIn("Find the money. Map the protocol. Prove the bug.", workflow)

    def test_safety_and_archive_truth_are_preserved(self) -> None:
        readme = self.read("README.md")
        for phrase in [
            "Local repository analysis only.",
            "No RPC by default.",
            "No live-chain mutation.",
            "No private keys or secrets.",
            "No automated exploitation.",
            "No auto-submit.",
            "Not an audit, certification, or replacement for manual review.",
            "No severity guarantee.",
        ]:
            self.assertIn(phrase, readme)

    def test_repositioning_checks_pass(self) -> None:
        for command in [
            ["python3", "scripts/check_version_consistency.py", "--check"],
            ["python3", "scripts/check_docs_links.py", "--check"],
            ["python3", "scripts/check_safety_wording.py", "--strict"],
        ]:
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
