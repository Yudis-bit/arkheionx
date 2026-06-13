"""Tests for the hunter engine self-evaluation."""
import unittest
from pathlib import Path

from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"
SCORE_KEYS = ("scope", "dedup", "freshness", "deployment", "value_flow", "state_machine",
              "lead_discovery", "poc_planning", "submission_risk", "overall")


class EngineEvaluationTests(unittest.TestCase):
    def test_all_scores_present_and_in_range(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        scores = res["pack"].engine_evaluation.scores
        for k in SCORE_KEYS:
            self.assertIn(k, scores)
            self.assertGreaterEqual(scores[k], 0)
            self.assertLessEqual(scores[k], 10)

    def test_blind_corpus_scores_dedup_low(self) -> None:
        b = FX / "dedup_blind"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        self.assertLessEqual(res["pack"].engine_evaluation.scores["dedup"], 3)

    def test_honest_fields_populated(self) -> None:
        b = FX / "dedup_blind"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        e = res["pack"].engine_evaluation
        self.assertTrue(e.what_arkheionx_got_wrong)
        self.assertTrue(e.what_to_fix_next)
        self.assertTrue(e.biggest_uncertainty)
        self.assertTrue(e.false_negative_risk)

    def test_evaluation_in_triage_json(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        ev = res["triage"]["engine_evaluation"]
        self.assertIn("scores", ev)
        self.assertIn("overall", ev["scores"])


if __name__ == "__main__":
    unittest.main()
