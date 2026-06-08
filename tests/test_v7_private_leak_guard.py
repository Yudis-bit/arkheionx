"""Private-scope leak-guard tests for v7.

Verifies the leak checker catches a private term if it is inserted into a public
file, that the real committed repository surface is clean, that ``.arkheionx/`` is
gitignored, and that no private terms are committed.
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

from arkheionx.scope_orchestration import (
    default_private_terms_path,
    run_private_leak_check,
    scan_text_for_terms,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class LeakGuardUnitTests(unittest.TestCase):
    def test_scan_text_for_terms(self) -> None:
        terms = ["AcmeSecretProtocol", "SponsorXyz"]
        hits = scan_text_for_terms("contract AcmeSecretProtocol {}", terms)
        self.assertEqual(hits, ["AcmeSecretProtocol"])
        self.assertEqual(scan_text_for_terms("nothing private here", terms), [])

    def test_catches_inserted_term_in_temp_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            priv = root / ".arkheionx" / "private"
            priv.mkdir(parents=True)
            (priv / "private-terms.txt").write_text("ZzPrivateTargetName\n# a comment\n\n", encoding="utf-8")
            # A public file that leaks the private term.
            (root / "leaky.md").write_text("This mentions ZzPrivateTargetName in public.", encoding="utf-8")
            # A private file that legitimately contains it (must be ignored by the scan).
            (priv / "scope.md").write_text("ZzPrivateTargetName scope notes", encoding="utf-8")
            result = run_private_leak_check(root)
            self.assertTrue(result["terms_file_present"])
            self.assertFalse(result["clean"])
            leaked_files = {leak["file"] for leak in result["leaks"]}
            self.assertIn("leaky.md", leaked_files)
            # The private file under .arkheionx/ must not be reported as a leak.
            self.assertNotIn(".arkheionx/private/scope.md", leaked_files)

    def test_clean_when_no_terms_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("nothing here", encoding="utf-8")
            result = run_private_leak_check(root)
            self.assertFalse(result["terms_file_present"])
            self.assertTrue(result["clean"])


class RealRepoLeakTests(unittest.TestCase):
    def test_real_repo_clean_when_terms_present(self) -> None:
        # If the founder has a local private-terms file, the public surface must be clean.
        terms_path = default_private_terms_path(REPO_ROOT)
        if not terms_path.is_file():
            self.skipTest("no local private-terms.txt present (expected in CI / public clone)")
        result = run_private_leak_check(REPO_ROOT)
        self.assertTrue(result["clean"], f"private terms leaked into public files: {result['leaks']}")

    def test_arkheionx_dir_is_gitignored(self) -> None:
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".arkheionx/", gitignore)

    def test_no_private_dir_committed(self) -> None:
        result = subprocess.run(["git", "ls-files", ".arkheionx"], cwd=REPO_ROOT,
                                text=True, capture_output=True)
        self.assertEqual(result.stdout.strip(), "", "nothing under .arkheionx/ should be tracked")


if __name__ == "__main__":
    unittest.main()
