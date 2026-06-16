import unittest

from pathlib import Path

from arkheionx.auth import analyze_authorization
from arkheionx.semantic import build_semantic_map


class GenericMultisigSafeRepositoryTest(unittest.TestCase):
    def test_safe_repository_has_no_auth_candidate(self):
        root = Path(__file__).resolve().parents[1] / "fixtures" / "repos" / "hardhat_style_multisig_safe"
        result = analyze_authorization(build_semantic_map(root))
        self.assertTrue(result.active)
        self.assertFalse(result.candidates)


if __name__ == "__main__":
    unittest.main()
