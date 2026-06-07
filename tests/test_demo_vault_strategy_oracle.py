"""Locks the multi-contract value-flow demo fixture (vault-strategy-oracle).

These assertions run the real review-map engine against the bundled example and
prove the public "value paths you forgot to test" story holds on a multi-contract
protocol -- without faking output. The guard tests confirm the result reflects
the fixture's actual partial test coverage (deposit is tested; the value exits
and admin setters are not), so the demo cannot silently degrade into a hardcoded
or single-contract toy.
"""
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "vault-strategy-oracle-fixture"


class VaultStrategyOracleDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rm = build_review_map(FIXTURE)

    def test_fixture_files_exist(self) -> None:
        for rel in ("foundry.toml", "src/Vault.sol", "src/Strategy.sol",
                    "src/PriceOracle.sol", "src/MockToken.sol", "test/Vault.t.sol",
                    "README.md"):
            self.assertTrue((FIXTURE / rel).is_file(), rel)

    def test_is_multi_contract(self) -> None:
        names = {c.name for c in self.rm.contracts}
        # At least two protocol contracts; the core trio must be present.
        self.assertGreaterEqual(len(names), 2, names)
        for expected in ("Vault", "Strategy", "PriceOracle"):
            self.assertIn(expected, names)

    def test_has_uncovered_value_paths(self) -> None:
        self.assertGreaterEqual(len(self.rm.value_paths), 1)
        uncovered = [p for p in self.rm.value_paths if p.test_coverage_hint == "none"]
        self.assertGreaterEqual(len(uncovered), 1, "expected at least one uncovered value path")
        # The story spans more than one contract: Vault and Strategy both expose
        # an uncovered value exit.
        exit_contracts = {p.exit_function.split(".")[0] for p in uncovered if p.exit_function}
        self.assertIn("Vault", exit_contracts)
        self.assertIn("Strategy", exit_contracts)

    def test_surfaces_expected_test_gaps(self) -> None:
        gap_ids = {g.id for g in self.rm.test_gaps}
        for expected in ("gap-vault-withdraw", "gap-vault-emergencywithdraw",
                         "gap-strategy-divest", "gap-vault-setoracle"):
            self.assertIn(expected, gap_ids, gap_ids)

    def test_assumptions_have_ids(self) -> None:
        self.assertTrue(self.rm.assumptions)
        self.assertTrue(all(a.id.startswith("asm-") for a in self.rm.assumptions))

    def test_reflects_real_coverage_not_hardcoded(self) -> None:
        # deposit() is the one path the fixture's test covers, so it must NOT be
        # reported as a gap; withdraw() is untested, so it must be. This proves
        # the demo output tracks the actual test file rather than being faked.
        gap_ids = {g.id for g in self.rm.test_gaps}
        self.assertNotIn("gap-vault-deposit", gap_ids)
        self.assertIn("gap-vault-withdraw", gap_ids)

    def test_deterministic_ids(self) -> None:
        rm2 = build_review_map(FIXTURE)
        self.assertEqual([c.name for c in self.rm.contracts], [c.name for c in rm2.contracts])
        self.assertEqual([p.id for p in self.rm.value_paths], [p.id for p in rm2.value_paths])
        self.assertEqual([g.id for g in self.rm.test_gaps], [g.id for g in rm2.test_gaps])


if __name__ == "__main__":
    unittest.main()
