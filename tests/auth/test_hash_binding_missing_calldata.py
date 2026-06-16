import unittest

from arkheionx.auth import models as M
from arkheionx.auth.operation_hash import analyze_operation


class MissingCalldataBindingTest(unittest.TestCase):
    def test_calldata_is_critical(self):
        body = """
        bytes32 operationHash = keccak256(abi.encode(destination, value, nonce));
        address signer = ecrecover(operationHash, v, r, s);
        nonce += 1;
        destination.call{value: value}(data);
        """
        operation = analyze_operation("GenericWallet", "execute", body)
        self.assertEqual(operation.binding_matrix.field("calldata").verdict, M.UNBOUND_CRITICAL)


if __name__ == "__main__":
    unittest.main()
