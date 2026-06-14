"""V10 war-run quality gates.

Each gate is verified independently on synthetic candidates (so a gate failure is
testable even though the economic gate enforces most of these upstream), plus an
end-to-end check that all gates pass on the benchmark fixtures and that a violating
SUBMIT candidate is downgraded by enforcement.
"""
import unittest
from pathlib import Path

from arkheionx.attack.models import AttackGraph, AttackCandidate
from arkheionx.severity import apply_gate
from arkheionx.severity import models as S
from arkheionx.warrun import quality_gates as Q
from arkheionx.warrun import run_war_run

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _graph(*cands):
    g = AttackGraph(root="x")
    g.candidates = list(cands)
    return g


def _verdict(cid, impact_type="", proof_quality=S.LOCAL_POC_SKELETON, label=S.SUBMIT_HIGH_CANDIDATE):
    return S.SeverityVerdict(candidate_id=cid, label=label, impact_type=impact_type,
                             proof_quality=proof_quality)


def _gate(gates, gid):
    return next(g for g in gates if g.id == gid)


class QualityGateLogicTest(unittest.TestCase):
    def test_required_fields_gate_fails_on_incomplete_submit(self):
        c = AttackCandidate(id="AC-1", invariant_family="DEPOSIT_CONSUMPTION",
                            attacker_capability="user", victim="", asset="",
                            broken_invariant="", entry_function="C.f",
                            economic_severity=S.SUBMIT_HIGH_CANDIDATE)
        gates = Q.run_quality_gates(_graph(c), [_verdict("AC-1")], [])
        self.assertEqual(_gate(gates, Q.REQUIRED_FIELDS_GATE).status, Q.FAIL)

    def test_no_report_gate(self):
        gates = Q.run_quality_gates(_graph(), [], [], report_generated=True)
        self.assertEqual(_gate(gates, Q.NO_REPORT_GATE).status, Q.FAIL)
        gates = Q.run_quality_gates(_graph(), [], [], report_generated=False)
        self.assertEqual(_gate(gates, Q.NO_REPORT_GATE).status, Q.PASS)

    def test_no_secret_gate(self):
        gates = Q.run_quality_gates(_graph(), [], [], secret_warnings=["leaked rpc url"])
        self.assertEqual(_gate(gates, Q.NO_SECRET_GATE).status, Q.FAIL)

    def test_no_dust_high_gate(self):
        c = AttackCandidate(id="AC-2", invariant_family="DEBT_REPAYMENT_RECONCILIATION",
                            attacker_capability="u", victim="v", asset="a",
                            broken_invariant="i", entry_function="C.f",
                            economic_severity=S.SUBMIT_HIGH_CANDIDATE)
        v = _verdict("AC-2", impact_type=S.DUST_ONLY, label=S.SUBMIT_HIGH_CANDIDATE)
        gates = Q.run_quality_gates(_graph(c), [v], [])
        self.assertEqual(_gate(gates, Q.NO_DUST_HIGH_GATE).status, Q.FAIL)

    def test_no_trusted_role_submit_gate(self):
        c = AttackCandidate(id="AC-3", invariant_family="DEPOSIT_CONSUMPTION",
                            attacker_capability="u", victim="v", asset="a",
                            broken_invariant="i", entry_function="C.f",
                            role_gated=True, economic_severity=S.SUBMIT_HIGH_CANDIDATE)
        gates = Q.run_quality_gates(_graph(c), [_verdict("AC-3")], [])
        self.assertEqual(_gate(gates, Q.NO_TRUSTED_ROLE_SUBMIT_GATE).status, Q.FAIL)

    def test_no_duplicate_submit_gate(self):
        c = AttackCandidate(id="AC-4", invariant_family="DEPOSIT_CONSUMPTION",
                            attacker_capability="u", victim="v", asset="a",
                            broken_invariant="i", entry_function="C.f",
                            duplicate_risk="SAME_ROOT_CAUSE",
                            economic_severity=S.SUBMIT_HIGH_CANDIDATE)
        gates = Q.run_quality_gates(_graph(c), [_verdict("AC-4")], [])
        self.assertEqual(_gate(gates, Q.NO_DUPLICATE_SUBMIT_GATE).status, Q.FAIL)

    def test_fork_dependency_gate_warns_without_plan(self):
        c = AttackCandidate(id="AC-5", invariant_family="LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
                            attacker_capability="u", victim="v", asset="a",
                            broken_invariant="i", entry_function="C.f",
                            economic_severity=S.NEEDS_FORK_PROOF)
        gates = Q.run_quality_gates(_graph(c), [_verdict("AC-5", label=S.NEEDS_FORK_PROOF)], [])
        self.assertEqual(_gate(gates, Q.FORK_DEPENDENCY_GATE).status, Q.WARN)

    def test_enforce_downgrades_violating_submit(self):
        c = AttackCandidate(id="AC-6", invariant_family="DEPOSIT_CONSUMPTION",
                            attacker_capability="u", victim="v", asset="a",
                            broken_invariant="i", entry_function="C.f",
                            role_gated=True, economic_severity=S.SUBMIT_HIGH_CANDIDATE)
        g = _graph(c)
        gates = Q.run_quality_gates(g, [_verdict("AC-6")], [])
        applied = Q.enforce(g, gates)
        self.assertTrue(applied)
        self.assertEqual(c.economic_severity, S.PARK_INCOMPLETE)


class QualityGateEndToEndTest(unittest.TestCase):
    def test_all_gates_pass_on_fixtures(self):
        for fx in ("oracle_decimal_normalization_fixture",
                   "adapter_actual_received_vs_credited_fixture",
                   "cross_chain_supply_conservation_fixture",
                   "trusted_role_fixture"):
            res = run_war_run(_GODEYE / fx, write=False)
            with self.subTest(fixture=fx):
                self.assertEqual(res["gate_status"], Q.PASS)
                self.assertIn("quality-gates.json", res["jsons"])
                self.assertEqual(res["triage"]["quality_gates"]["overall_status"], Q.PASS)
                # No SUBMIT candidate may violate a hard gate (verified by enforcement no-op).
                self.assertFalse(Q.enforce(res["graph"], res["gates"], res["verdicts"]))


if __name__ == "__main__":
    unittest.main()
