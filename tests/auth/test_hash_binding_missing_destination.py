import unittest

from arkheionx.auth import models as M

from ._helpers import analyze


class MissingDestinationBindingTest(unittest.TestCase):
    def test_destination_is_critical(self):
        result = analyze("generic_multisig_missing_destination_in_hash.sol")
        operation = result.signed_operations[0]
        self.assertEqual(operation.binding_matrix.field("destination").verdict, M.UNBOUND_CRITICAL)
        self.assertIn("SIGNATURE_OPERATION_BINDING", [item.family for item in result.candidates])


if __name__ == "__main__":
    unittest.main()
