"""Tests for lens scope parsing on the toy Morpho fixture."""
import unittest
from pathlib import Path

from arkheionx.protocol_lens import models as m
from arkheionx.protocol_lens import scope_parser
from arkheionx.protocol_lens.common import scope_status

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "morpho_midnight_toy"
SCOPE = FIXTURE / "scope.md"


class MorphoScopeParserTests(unittest.TestCase):
    def test_parses_known_accepted_and_out_of_scope(self) -> None:
        scope = scope_parser.parse_scope_file(str(SCOPE))
        self.assertTrue(scope.scope_file_used)
        self.assertTrue(scope.known_issues)
        self.assertTrue(scope.accepted_risks)
        self.assertTrue(scope.out_of_scope)
        self.assertTrue(scope.trusted_roles)
        self.assertTrue(scope.focus_areas)
        self.assertTrue(scope.invariants)
        self.assertEqual(scope_status(scope), "complete")

    def test_requires_medium_high(self) -> None:
        scope = scope_parser.parse_scope_file(str(SCOPE))
        self.assertTrue(scope_parser.requires_medium_high(scope))

    def test_missing_scope_marks_incomplete(self) -> None:
        scope = scope_parser.parse_scope_file(None)
        self.assertFalse(scope.scope_file_used)
        self.assertEqual(scope_status(scope), m.SCOPE_INCOMPLETE_LOCAL_ONLY)
        scope2 = scope_parser.parse_scope_file(str(FIXTURE / "does-not-exist.md"))
        self.assertFalse(scope2.scope_file_used)
        self.assertEqual(scope_status(scope2), m.SCOPE_INCOMPLETE_LOCAL_ONLY)


if __name__ == "__main__":
    unittest.main()
