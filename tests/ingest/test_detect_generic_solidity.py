import unittest

from arkheionx.ingest import GENERIC_SOLIDITY, detect_framework

from ._helpers import ROOT


class GenericSolidityDetectionTest(unittest.TestCase):
    def test_detects_layout(self):
        self.assertEqual(detect_framework(ROOT / "generic_solidity_basic"), GENERIC_SOLIDITY)


if __name__ == "__main__":
    unittest.main()
