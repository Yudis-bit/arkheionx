import unittest

from arkheionx.auth import models as M

from ._helpers import analyze


class AllFieldsBoundTest(unittest.TestCase):
    def test_safe_operation_binds_execution_fields(self):
        operation = analyze("generic_multisig_safe.sol").signed_operations[0]
        for name in ("destination", "value", "calldata", "nonce_or_sequence", "chain_id", "wallet_address"):
            with self.subTest(field=name):
                self.assertEqual(operation.binding_matrix.field(name).verdict, M.BOUND)


if __name__ == "__main__":
    unittest.main()
