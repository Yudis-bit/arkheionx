import unittest

from arkheionx.memory import families as F
from arkheionx.memory.root_cause_fingerprint import (
    DEPOSIT_BUFFER_CAPPED,
    KEY_REUSE_OR_DOMAIN_CAPPED,
    ROUNDING_UNIT_CAPPED,
    build_fingerprint,
)


class RootCauseFingerprintTest(unittest.TestCase):
    def test_repayment_rounding_reconciliation(self):
        fp = build_fingerprint(
            "repayment asymmetric rounding between aggregate borrower repayment "
            "and per-tranche lender distribution"
        )
        self.assertEqual(fp.family, F.ROUNDING_REPAYMENT_RECONCILIATION)
        self.assertEqual(fp.lifecycle, "repay")
        self.assertEqual(fp.cap_type, ROUNDING_UNIT_CAPPED)

    def test_repeated_small_repayments(self):
        fp = build_fingerprint(
            "repeated small repayments can close loans while tranche repayments "
            "round down to zero"
        )
        self.assertEqual(
            fp.subfamily,
            "debt_closes_before_lender_distribution_reconciles",
        )

    def test_route_buffer(self):
        fp = build_fingerprint(
            "borrower-controlled cross-token swap data can reduce lender refund buffer"
        )
        self.assertEqual(fp.family, F.LENDER_CONSENT_VALUE_FIELD_BINDING)
        self.assertEqual(
            fp.subfamily,
            "counterparty_controlled_route_affects_refund",
        )
        self.assertEqual(fp.cap_type, DEPOSIT_BUFFER_CAPPED)

    def test_signature_replay_domain(self):
        fp = build_fingerprint(
            "operation hash omits chain id and wallet address allowing replay across domains"
        )
        self.assertEqual(fp.family, F.SIGNATURE_REPLAY_DOMAIN)
        self.assertEqual(fp.subfamily, "domain_not_bound")
        self.assertEqual(fp.cap_type, KEY_REUSE_OR_DOMAIN_CAPPED)

    def test_policy_families(self):
        cases = (
            ("trusted signer activates emergency mode causing grief", F.TRUSTED_ROLE_ASSUMPTION),
            ("zero address signer validation missing", F.OFFCHAIN_VALIDATION_OMISSION),
            (
                "forced value transfer changes contract balance without logic flaw",
                F.FORCED_VALUE_TRANSFER_NO_LOGIC_FLAW,
            ),
        )
        for text, family in cases:
            with self.subTest(family=family):
                self.assertEqual(build_fingerprint(text).family, family)


if __name__ == "__main__":
    unittest.main()
