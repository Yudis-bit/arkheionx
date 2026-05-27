import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class InternalEngineSplitTests(unittest.TestCase):
    def test_package_docs_exist(self) -> None:
        for path in [
            "docs/INTERNAL_ENGINE_SPLIT.md",
            "docs/PACKAGE_ARCHITECTURE.md",
            "docs/CLI_ROADMAP.md",
            "arkheionx/core/models.py",
            "arkheionx/rules/registry.py",
            "arkheionx/generators/test_plan.py",
            "arkheionx/cli/main.py",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_old_script_checks_still_run(self) -> None:
        commands = [
            ["python3", "scripts/generate_test_plan.py", "--check"],
            ["python3", "scripts/generate_ecosystem_report.py", "--check"],
            ["python3", "scripts/generate_paid_offer_index.py", "--check"],
            ["python3", "scripts/generate_feedback_dashboard.py", "--check"],
            ["python3", "scripts/validate_config.py", "--config", "examples/arkheionx.config.example.json"],
            ["python3", "scripts/check_docs_links.py", "--check"],
            ["python3", "scripts/check_version_consistency.py", "--check"],
            ["python3", "scripts/check_safety_wording.py", "--strict"],
        ]
        for command in commands:
            result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, " ".join(command) + "\n" + result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
