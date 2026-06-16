"""V10 economic severity engine: decision tree, hard gates, and scoring.

Cold/brutal classification rules, exercised on synthetic candidates so the tree is
tested independently of any one fixture: dust is never High, trusted-role and
duplicate and out-of-scope are killed, SUBMIT requires complete fields (else
PARK_INCOMPLETE), and each verdict carries an explainable numeric score.
"""
import unittest

from arkheionx.attack.models import AttackCandidate
from arkheionx.severity import classify
from arkheionx.severity import models as S


def _complete(family, **kw):
    base = dict(
        id="AC-T", invariant_family=family,
        attacker_capability="external attacker (unprivileged)",
        victim="protocol / depositors", asset="pool funds",
        broken_invariant="the invariant must hold", proof_strategy="local",
    )
    base.update(kw)
    return AttackCandidate(**base)


class SeverityDecisionTreeTest(unittest.TestCase):
    def test_dust_never_high_for_18_decimals(self):
        c = _complete("DEBT_REPAYMENT_RECONCILIATION")
        v = classify(c, context={"asset_decimals": 18})
        self.assertEqual(v.label, S.KILL_DUST)
        self.assertNotIn(v.label, S.SUBMIT_LABELS)

    def test_reconciliation_default_is_low_not_high(self):
        v = classify(_complete("DEBT_REPAYMENT_RECONCILIATION"))
        self.assertEqual(v.label, S.VALID_BUT_LOW)

    def test_trusted_role_killed_even_for_high_impact_family(self):
        c = _complete("DEPOSIT_CONSUMPTION", role_gated=True, role_gates=["onlyOwner"])
        v = classify(c)
        self.assertEqual(v.label, S.KILL_TRUSTED_ROLE)

    def test_duplicate_root_cause_killed(self):
        c = _complete("DEPOSIT_CONSUMPTION", duplicate_risk="SAME_ROOT_CAUSE")
        self.assertEqual(classify(c).label, S.KILL_DUPLICATE_ROOT_CAUSE)

    def test_out_of_scope_killed(self):
        c = _complete("DEPOSIT_CONSUMPTION", scope_risk="OUT_OF_SCOPE")
        self.assertEqual(classify(c).label, S.KILL_OUT_OF_SCOPE)

    def test_incomplete_submit_is_parked(self):
        # Base label would be SUBMIT_HIGH, but missing victim/asset must downgrade.
        c = _complete("DEPOSIT_CONSUMPTION", victim="", asset="")
        v = classify(c)
        self.assertEqual(v.label, S.PARK_INCOMPLETE)
        self.assertTrue(any("missing" in r.lower() for r in v.reasons))

    def test_complete_deposit_consumption_is_high(self):
        self.assertEqual(classify(_complete("DEPOSIT_CONSUMPTION")).label,
                         S.SUBMIT_HIGH_CANDIDATE)

    def test_adapter_overcredit_is_medium_local_fork_otherwise(self):
        self.assertEqual(classify(_complete("SWAP_ACTUAL_RECEIVED_VS_CREDITED")).label,
                         S.SUBMIT_MEDIUM_CANDIDATE)
        fork = _complete("SWAP_ACTUAL_RECEIVED_VS_CREDITED",
                         fork_requirement=True, proof_strategy="fork")
        self.assertEqual(classify(fork).label, S.NEEDS_FORK_PROOF)

    def test_oracle_overborrow_is_high(self):
        self.assertEqual(classify(_complete("ORACLE_DECIMAL_NORMALIZATION")).label,
                         S.SUBMIT_HIGH_CANDIDATE)

    def test_cross_chain_replay_is_high(self):
        self.assertEqual(classify(_complete("CROSS_CHAIN_SUPPLY_CONSERVATION")).label,
                         S.SUBMIT_HIGH_CANDIDATE)


class SeverityScoreTest(unittest.TestCase):
    def test_verdict_carries_typed_dimensions(self):
        v = classify(_complete("ORACLE_DECIMAL_NORMALIZATION"))
        self.assertEqual(v.impact_type, S.ORACLE_OVERBORROW)
        self.assertTrue(v.cap_type)
        self.assertTrue(v.proof_quality)
        self.assertTrue(v.score.get("explanation"))

    def test_dust_family_has_high_cap_penalty(self):
        v = classify(_complete("DEBT_REPAYMENT_RECONCILIATION"))
        self.assertGreaterEqual(v.score["cap_penalty"], 7)
        self.assertEqual(v.impact_type, S.VICTIM_LOSS)

    def test_uncapped_high_family_low_cap_penalty(self):
        v = classify(_complete("CROSS_CHAIN_SUPPLY_CONSERVATION"))
        self.assertLessEqual(v.score["cap_penalty"], 2)
        self.assertEqual(v.impact_type, S.CROSS_CHAIN_OVERMINT)

    def test_proof_quality_reflects_strategy(self):
        local = classify(_complete("DEPOSIT_CONSUMPTION", proof_strategy="local"))
        self.assertEqual(local.proof_quality, S.LOCAL_POC_SKELETON)
        fork = classify(_complete("SWAP_ACTUAL_RECEIVED_VS_CREDITED",
                                  fork_requirement=True, proof_strategy="fork"))
        self.assertEqual(fork.proof_quality, S.FORK_PLAN_ONLY)
        role = classify(_complete("DEPOSIT_CONSUMPTION", role_gated=True))
        self.assertEqual(role.proof_quality, S.MANUAL_REVIEW_REQUIRED)

    def test_taxonomy_constants_exist(self):
        for lbl in (S.SUBMIT_CRITICAL_CANDIDATE, S.NEEDS_LOCAL_POC, S.NEEDS_CAPTURE_PROOF,
                    S.PARK_INCOMPLETE, S.KILL_ADMIN_ONLY, S.KILL_NOT_REACHABLE,
                    S.KILL_EXPECTED_DESIGN):
            self.assertTrue(isinstance(lbl, str) and lbl)


if __name__ == "__main__":
    unittest.main()
