"""V10 DeFi entity detection: ERC4626-like vault shape."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.defi import entities as E

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class DefiEntityVaultTest(unittest.TestCase):
    def setUp(self):
        smap = build_semantic_map(_GODEYE / "vault_share_inflation_fixture")
        self.emap = build_defi_entities(smap)

    def test_vault_entities_detected(self):
        types = self.emap.types()
        for expected in (E.ASSET, E.SHARE, E.VAULT):
            self.assertIn(expected, types, f"missing {expected}")

    def test_conversion_detected_as_exchange_rate(self):
        # totalAssets()/conversion is detected as an ExchangeRate entity.
        self.assertIn(E.EXCHANGE_RATE, self.emap.types())

    def test_share_is_internal_direction(self):
        share = self.emap.by_type(E.SHARE)
        self.assertEqual(share.value_direction, E.DIR_INTERNAL)


if __name__ == "__main__":
    unittest.main()
