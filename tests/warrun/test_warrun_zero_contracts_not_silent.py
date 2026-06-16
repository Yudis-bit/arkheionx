import tempfile
import unittest

from arkheionx.warrun import quality_gates as Q
from arkheionx.warrun import run_war_run


class WarRunZeroContractsTest(unittest.TestCase):
    def test_zero_contracts_warns_and_has_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            result = run_war_run(temp, write=False)
            self.assertTrue(any(
                "ZERO_CONTRACTS_INDEXED" in warning
                for warning in result["ingest_summary"].warnings
            ))
            gate = next(item for item in result["gates"] if item.id == Q.ZERO_CONTRACTS_INDEXED_WARNING)
            self.assertEqual(gate.status, Q.WARN)
            self.assertIn("ZERO_CONTRACTS_INDEXED", "\n".join(result["console"]))


if __name__ == "__main__":
    unittest.main()
