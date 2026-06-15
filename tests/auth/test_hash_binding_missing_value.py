import unittest

from arkheionx.auth import models as M
from arkheionx.auth.operation_hash import analyze_operation


class MissingValueBindingTest(unittest.TestCase):
    def test_value_is_unbound_value_field(self):
        body = """
        bytes32 operationHash = keccak256(abi.encode(destination, keccak256(data), nonce));
        address signer = ecrecover(operationHash, v, r, s);
        nonce += 1;
        destination.call{value: value}(data);
        """
        operation = analyze_operation("GenericWallet", "execute", body)
        self.assertEqual(operation.binding_matrix.field("value").verdict, M.UNBOUND_VALUE_FIELD)


if __name__ == "__main__":
    unittest.main()
