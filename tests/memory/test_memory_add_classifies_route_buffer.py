import unittest

from ._helpers import run_memory_add


class MemoryAddRouteBufferTest(unittest.TestCase):
    def test_classifies_route_buffer(self):
        temp, code, output = run_memory_add(
            "--target", "lender_consent_route_buffer_benchmark",
            "--root-cause",
            "borrower-controlled cross-token swap data can reduce lender refund buffer",
        )
        self.addCleanup(temp.cleanup)
        self.assertEqual(code, 0)
        self.assertIn("family=LENDER_CONSENT_VALUE_FIELD_BINDING", output)


if __name__ == "__main__":
    unittest.main()
