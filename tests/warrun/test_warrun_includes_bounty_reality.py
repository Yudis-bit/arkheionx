import unittest

from ._helpers import run_fixture


class WarRunBountyRealityArtifactTest(unittest.TestCase):
    def test_includes_bounty_reality(self):
        result = run_fixture("generic_signature_binding_bug")
        self.assertIn("17-bounty-reality.json", result["jsons"])
        self.assertIn("17-bounty-reality.md", result["contents"])
        self.assertIn("bounty_reality", result["triage"])


if __name__ == "__main__":
    unittest.main()
