"""Fail-closed senior-mode tests: when context is missing, do not pretend certainty."""
import unittest
from pathlib import Path

from arkheionx.senior_triage import models as M
from arkheionx.senior_triage import scoring
from arkheionx.senior_triage.pack import build_senior_triage_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures"


def elig(scope=True):
    return M.EligibilitySignal(
        scope_provided=scope, scope_confidence=M.CONF_HIGH if scope else M.CONF_LOW,
        target_decision=M.TARGET_TOUCH if scope else M.TARGET_NEEDS_CONTEXT,
        severity_ceiling=M.SEV_HIGH if scope else M.SEV_UNKNOWN)


def lead(notes=None, proof=30):
    return M.LeadCandidate(id="LEAD-001", title="X.withdraw", surface="X.withdraw",
                           linked_functions=["X.withdraw"], attacker_reachability_score=85,
                           materiality_score=85, proof_difficulty_score=proof, time_cost_score=45,
                           kill_condition="kill if guarded", notes=notes or ["value-out"])


def known(status=M.KNOWN_NO_MATCH, dup=15, conf=M.CONF_MEDIUM):
    return M.KnownIssueSignal(lead_id="LEAD-001", status=status, duplicate_risk_score=dup, confidence=conf)


def fresh(status=M.FRESH, score=55):
    return M.FreshnessSignal(lead_id="LEAD-001", status=status, score=score)


def score(L, e, k, fr, **caps):
    ctx = {"scope_provided": e.scope_provided, "known_provided": True, "addresses_provided": True,
           "baseline_provided": True, "rpc_ran": True}
    ctx.update(caps.pop("caps_context", {}))
    return scoring.apply_score(L, e, k, fr, repo=".", scope_file="s.md", caps_context=ctx, **caps)


class FailClosedUnitTests(unittest.TestCase):
    def test_no_scope_never_pursue(self) -> None:
        L = lead()
        score(L, elig(scope=False), known(), fresh(M.NEW_ADAPTER, 90),
              caps_context={"scope_provided": False})
        self.assertNotEqual(L.decision, M.LEAD_PURSUE)

    def test_missing_known_caps_to_park(self) -> None:
        # Same lead pursues with known material, parks without it (not strongly fresh).
        with_known = lead()
        score(with_known, elig(), known(), fresh(M.FRESH, 55))
        without = lead()
        score(without, elig(), known(), fresh(M.FRESH, 55), caps_context={"known_provided": False})
        self.assertEqual(with_known.decision, M.LEAD_PURSUE)
        self.assertNotEqual(without.decision, M.LEAD_PURSUE)
        self.assertTrue(any("known/audit" in c for c in without.decision_caps))

    def test_live_wiring_lead_parks_without_rpc(self) -> None:
        L = lead(notes=["value-out", "proxy"])
        score(L, elig(), known(), fresh(M.NEW_IMPLEMENTATION, 90),
              caps_context={"rpc_ran": False})
        self.assertNotEqual(L.decision, M.LEAD_PURSUE)
        self.assertTrue(any("live wiring" in c for c in L.decision_caps))

    def test_unknown_freshness_without_baseline_caps(self) -> None:
        L = lead()
        score(L, elig(), known(), fresh(M.UNKNOWN_FRESHNESS, 40),
              caps_context={"baseline_provided": False})
        self.assertTrue(any("freshness" in c.lower() for c in L.decision_caps))

    def test_strict_context_no_scope_below_park(self) -> None:
        L = lead()
        scoring.apply_score(L, elig(scope=False), known(), fresh(M.NEW_ADAPTER, 90),
                            repo=".", scope_file="", strict_context=True,
                            caps_context={"scope_provided": False, "known_provided": True,
                                          "addresses_provided": False, "baseline_provided": True,
                                          "rpc_ran": False})
        self.assertEqual(L.decision, M.LEAD_KILL)

    def test_verified_mismatch_bypasses_no_known_cap(self) -> None:
        L = lead()
        score(L, elig(), known(), fresh(M.UNKNOWN_FRESHNESS, 40),
              deployment_status=M.DEPLOY_IMPLEMENTATION_CHANGED, deployment_score=95,
              caps_context={"known_provided": False, "baseline_provided": False})
        self.assertEqual(L.decision, M.LEAD_PURSUE)


class FailClosedEndToEndTests(unittest.TestCase):
    def test_no_scope_fixture(self) -> None:
        b = FX / "senior_realworld_no_scope"
        res = build_senior_triage_pack(b, write=False)
        self.assertEqual(res["counts"]["pursue"], 0)
        self.assertEqual(res["triage"]["target_decision"], M.TARGET_NEEDS_CONTEXT)

    def test_strict_context_toy_is_more_conservative(self) -> None:
        b = FX / "senior_triage_toy"
        # Without known/audits, strict context should pursue no more than the default.
        strict = build_senior_triage_pack(b, scope_file=str(b / "scope.md"),
                                          strict_context=True, write=False)
        self.assertLessEqual(strict["counts"]["pursue"], 1)


if __name__ == "__main__":
    unittest.main()
