import unittest

from arkheionx.ingest import TRUFFLE_STYLE, detect_framework

from ._helpers import ROOT


class TruffleStyleDetectionTest(unittest.TestCase):
    def test_detects_layout(self):
        self.assertEqual(detect_framework(ROOT / "truffle_style_basic"), TRUFFLE_STYLE)


if __name__ == "__main__":
    unittest.main()
