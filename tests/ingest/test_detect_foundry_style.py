import unittest

from arkheionx.ingest import FOUNDRY_STYLE, detect_framework

from ._helpers import ROOT


class FoundryStyleDetectionTest(unittest.TestCase):
    def test_detects_layout(self):
        self.assertEqual(detect_framework(ROOT / "foundry_style_basic"), FOUNDRY_STYLE)


if __name__ == "__main__":
    unittest.main()
