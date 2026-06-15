import unittest

from ._helpers import run_fixture


class WarRunAuthArtifactTest(unittest.TestCase):
    def test_includes_auth_analysis(self):
        result = run_fixture("hardhat_style_multisig_safe")
        self.assertIn("18-auth-signature-analysis.json", result["jsons"])
        self.assertIn("18-auth-signature-analysis.md", result["contents"])
        self.assertIn("auth_signature_analysis", result["triage"])


if __name__ == "__main__":
    unittest.main()
