import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class EcosystemPackTests(unittest.TestCase):
    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def load_json(self, path: str) -> dict:
        return json.loads(self.read(path))

    def test_ecosystem_docs_exist(self) -> None:
        for path in [
            "docs/ecosystem/ECOSYSTEM_PACK.md",
            "docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md",
            "docs/ecosystem/ECOSYSTEM_INTAKE.md",
            "docs/ecosystem/ANONYMIZED_REPORTING.md",
            "docs/ecosystem/ECOSYSTEM_READINESS_PILOT.md",
            "docs/ecosystem/COHORT_READINESS_GUIDE.md",
            "docs/ecosystem/ECOSYSTEM_OPERATOR_FAQ.md",
            "docs/ecosystem/ECOSYSTEM_BOUNDARIES.md",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_ecosystem_metadata_parses(self) -> None:
        schema = self.load_json("metadata/ecosystem_pack_schema.json")
        example = self.load_json("metadata/ecosystem_pilot_example.json")
        self.assertEqual(schema["schema_version"], "1.3.0")
        self.assertEqual(example["schema_version"], "1.3.0")
        self.assertEqual(example["repo_count"], 5)
        self.assertTrue(example["repo_entries"])
        self.assertFalse(example["public_permission"])
        self.assertIn("Synthetic", example["ecosystem_name_public"])

    def test_ecosystem_report_generator_check_passes(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/generate_ecosystem_report.py", "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ecosystem_reports_and_templates_exist(self) -> None:
        for path in [
            "reports/ecosystem_readiness_summary.md",
            "reports/ecosystem_common_gaps.md",
            "templates/ecosystem_intake.md",
            "templates/ecosystem_readiness_pilot_scope.md",
            "templates/ecosystem_manifest.example.json",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_readme_links_ecosystem_workflow(self) -> None:
        services = self.read("SERVICES.md")
        self.assertIn("## Ecosystem Pack", services)
        self.assertIn("docs/ecosystem/ECOSYSTEM_PACK.md", services)
        self.assertIn("reports/ecosystem_readiness_summary.md", services)

    def test_ecosystem_docs_keep_boundaries(self) -> None:
        combined = "\n".join(
            self.read(path)
            for path in [
                "docs/ecosystem/ECOSYSTEM_PACK.md",
                "docs/ecosystem/ECOSYSTEM_BOUNDARIES.md",
                "reports/ecosystem_readiness_summary.md",
                "reports/ecosystem_common_gaps.md",
            ]
        ).lower()
        self.assertIn("not a formal audit", combined)
        self.assertIn("authorized repositories", combined)
        self.assertIn("certification", combined)
        for phrase in [
            "used by top protocols",
            "trusted by ecosystems",
            "customer-proven",
            "adopted by ecosystems",
            "official ecosystem partner",
        ]:
            self.assertNotIn(phrase, combined)

    def test_release_checks_pass(self) -> None:
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
