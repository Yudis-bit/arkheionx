import subprocess
import tempfile
import unittest
from pathlib import Path

from arkheionx.reports.profiles import profile_keys, profile_settings


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"


class OutputProfileTests(unittest.TestCase):
    def test_profile_settings_cover_stable_profiles(self) -> None:
        self.assertEqual(set(profile_keys()), {"concise", "standard", "full", "ci"})
        self.assertEqual(profile_settings("concise")["key"], "concise")
        self.assertEqual(profile_settings("standard")["key"], "standard")
        self.assertEqual(profile_settings("full")["key"], "full")
        self.assertEqual(profile_settings("ci")["key"], "ci")

    def test_invalid_profile_falls_back_to_standard(self) -> None:
        self.assertEqual(profile_settings("surprise")["key"], "standard")

    def test_ci_profile_report_is_shorter_than_full_profile_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ci_report = tmp_path / "ci.md"
            full_report = tmp_path / "full.md"
            for config, output in [
                ("examples/configs/ci.config.json", ci_report),
                ("examples/configs/strict-audit-prep.config.json", full_report),
            ]:
                result = subprocess.run(
                    [
                        "python3",
                        str(SCANNER),
                        "--root",
                        str(REPO_ROOT / "examples/amm-lending-hybrid-fixture"),
                        "--config",
                        config,
                        "--output",
                        str(output),
                    ],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertLess(len(ci_report.read_text(encoding="utf-8")), len(full_report.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
