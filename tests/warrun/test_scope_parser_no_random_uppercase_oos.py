import tempfile
import unittest
from pathlib import Path

from arkheionx.warrun.scope import load_scope


class ScopeParserUppercaseNoiseTest(unittest.TestCase):
    def test_does_not_extract_random_uppercase_words(self):
        with tempfile.TemporaryDirectory() as temp:
            scope = Path(temp) / "scope.yaml"
            scope.write_text(
                "out_of_scope:\n"
                "  - WITHOUT APIs ETH SELFDESTRUCT are prose, not contracts\n"
                "  - Exclude contracts/ExplicitBlocked.sol from review\n"
                "  - Exclude contract ExplicitNamed from review\n",
                encoding="utf-8",
            )
            model = load_scope(str(scope))
        self.assertNotIn("WITHOUT", model.out_of_scope_contracts)
        self.assertNotIn("APIs", model.out_of_scope_contracts)
        self.assertNotIn("ETH", model.out_of_scope_contracts)
        self.assertNotIn("SELFDESTRUCT", model.out_of_scope_contracts)
        self.assertIn("ExplicitBlocked", model.out_of_scope_contracts)
        self.assertIn("ExplicitNamed", model.out_of_scope_contracts)


if __name__ == "__main__":
    unittest.main()
