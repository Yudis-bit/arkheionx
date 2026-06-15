import unittest

from arkheionx.ingest import HARDHAT_STYLE, detect_framework

from ._helpers import ROOT


class HardhatStyleDetectionTest(unittest.TestCase):
    def test_detects_layout(self):
        self.assertEqual(detect_framework(ROOT / "hardhat_style_basic"), HARDHAT_STYLE)


if __name__ == "__main__":
    unittest.main()
