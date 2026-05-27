import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PaidOfferTests(unittest.TestCase):
    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def test_paid_offer_docs_exist(self) -> None:
        for path in [
            "docs/business/PAID_OFFER.md",
            "docs/business/PRICING_LADDER.md",
            "docs/business/SERVICE_PACKAGES.md",
            "docs/business/CLIENT_INTAKE.md",
            "docs/business/SAMPLE_SCOPE_OF_WORK.md",
            "docs/business/SALES_FAQ.md",
            "docs/business/PAID_WORK_BOUNDARIES.md",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_paid_offer_catalog_and_index(self) -> None:
        catalog = json.loads(self.read("metadata/paid_offer_catalog.json"))
        self.assertEqual(catalog["schema_version"], "1.3.0")
        offer_ids = {offer["offer_id"] for offer in catalog["offers"]}
        self.assertIn("readiness-snapshot", offer_ids)
        self.assertIn("pre-audit-sprint", offer_ids)
        self.assertIn("contest-readiness-pack", offer_ids)
        self.assertIn("github-action-setup", offer_ids)
        self.assertIn("ecosystem-readiness-pilot", offer_ids)
        self.assertTrue((REPO_ROOT / "reports/paid_offer_index.md").exists())

    def test_paid_offer_index_generator_check_passes(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/generate_paid_offer_index.py", "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_client_intake_and_scope_templates_exist(self) -> None:
        for path in [
            "templates/client_intake.md",
            "templates/readiness_snapshot_scope.md",
            "templates/pre_audit_sprint_scope.md",
            "templates/contest_readiness_scope.md",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_paid_docs_keep_boundaries(self) -> None:
        combined = "\n".join(
            self.read(path)
            for path in [
                "docs/business/PAID_OFFER.md",
                "docs/business/PRICING_LADDER.md",
                "docs/business/SERVICE_PACKAGES.md",
                "docs/business/CLIENT_INTAKE.md",
                "docs/business/SAMPLE_SCOPE_OF_WORK.md",
                "docs/business/SALES_FAQ.md",
                "docs/business/PAID_WORK_BOUNDARIES.md",
                "reports/paid_offer_index.md",
            ]
        ).lower()
        self.assertIn("not a formal audit", combined)
        self.assertIn("security guarantee", combined)
        self.assertIn("bounty guarantee", combined)
        for phrase in [
            "used by top protocols",
            "trusted by auditors",
            "adopted by teams",
            "proven in production",
            "paid customer",
        ]:
            self.assertNotIn(phrase, combined)

    def test_readme_links_paid_offer_docs(self) -> None:
        readme = self.read("README.md")
        self.assertIn("## Paid Readiness Support", readme)
        self.assertIn("docs/business/PAID_OFFER.md", readme)
        self.assertIn("reports/paid_offer_index.md", readme)

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
