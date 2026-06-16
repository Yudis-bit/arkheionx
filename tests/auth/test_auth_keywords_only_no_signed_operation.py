import unittest
from pathlib import Path

from arkheionx.auth import analyze_authorization
from arkheionx.semantic import build_semantic_map
from arkheionx.warrun import quality_gates as Q
from arkheionx.warrun import run_war_run


ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "repos"


class AuthKeywordsOnlyTest(unittest.TestCase):
    def test_keywords_without_signed_operation_warns(self):
        smap = build_semantic_map(ROOT / "auth_keywords_only_no_signed_operation")
        result = analyze_authorization(smap)
        self.assertTrue(result.activation_signals)
        self.assertFalse(result.signed_operations)
        self.assertTrue(any("AUTH_KEYWORDS_ONLY_NO_SIGNED_OPERATION" in w for w in result.warnings))
        payload = result.to_dict()
        self.assertTrue(payload["activation_signals_detected"])
        self.assertFalse(payload["signed_operations_detected"])
        self.assertFalse(payload["auth_candidates_detected"])

    def test_warrun_quality_gate_warns(self):
        result = run_war_run(ROOT / "auth_keywords_only_no_signed_operation", write=False)
        gate = next(g for g in result["gates"] if g.id == Q.AUTH_KEYWORDS_ONLY_NO_SIGNED_OPERATION)
        self.assertEqual(gate.status, Q.WARN)


if __name__ == "__main__":
    unittest.main()
