"""Locks graceful handling of source-tree-only commands in non-editable installs.

The legacy scanner/utilities under scripts/ ship with the source checkout, not
the installed wheel. When they are unavailable, the CLI must fail with clear
guidance (pointing at the packaged review-map workbench) rather than a raw
ModuleNotFoundError traceback -- while still propagating unrelated import errors.
"""
import contextlib
import io
import unittest

from arkheionx.cli import commands, exit_codes


class SourceTreeFallbackTests(unittest.TestCase):
    def test_missing_scripts_module_fails_gracefully(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            rc = commands._module_main("scripts.nonexistent_demo_module_xyz", [])
        self.assertEqual(rc, exit_codes.RUNTIME_ERROR)
        message = stderr.getvalue()
        self.assertIn("source-tree readiness scanner", message)
        self.assertIn("arkheionx review-map", message)
        self.assertNotIn("Traceback", message)

    def test_unrelated_import_error_still_propagates(self) -> None:
        with self.assertRaises(ModuleNotFoundError):
            commands._module_main("totally_made_up_top_level_pkg_xyz", [])


if __name__ == "__main__":
    unittest.main()
