import unittest

from arkheionx.ingest import BROWNIE_STYLE, detect_framework

from ._helpers import ROOT


class BrownieStyleDetectionTest(unittest.TestCase):
    def test_detects_layout(self):
        self.assertEqual(detect_framework(ROOT / "brownie_style_basic"), BROWNIE_STYLE)


if __name__ == "__main__":
    unittest.main()
