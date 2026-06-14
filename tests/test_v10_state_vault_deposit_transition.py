"""V10 state transition engine: vault deposit/withdraw lifecycle."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.state import transitions as T

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


class VaultDepositTransitionTest(unittest.TestCase):
    def setUp(self):
        smap = build_semantic_map(_GODEYE / "vault_share_inflation_fixture")
        emap = build_defi_entities(smap)
        self.tmap = build_transitions(smap, emap)

    def test_deposit_is_vault_lifecycle(self):
        dep = self.tmap.for_function("MiniVault.deposit")
        self.assertIsNotNone(dep)
        self.assertEqual(dep.lifecycle, T.LC_VAULT_DEPOSIT)
        self.assertTrue(dep.assets_in)
        self.assertIn("VAULT_SHARE_ASSET_RECONCILIATION", dep.possible_invariants)

    def test_balance_based_assets_flag(self):
        dep = self.tmap.for_function("MiniVault.deposit")
        self.assertIn("balance_based_assets", dep.flags)

    def test_redeem_transition_present(self):
        red = self.tmap.for_function("MiniVault.redeem")
        self.assertIsNotNone(red)
        self.assertIn(red.lifecycle, (T.LC_REDEMPTION, T.LC_VAULT_WITHDRAW))


if __name__ == "__main__":
    unittest.main()
