"""Tests for deterministic protocol intelligence IDs (v3.5, internal)."""
from __future__ import annotations

import unittest

from arkheionx.intelligence import ids


class StableIdTests(unittest.TestCase):
    def test_ids_are_deterministic_across_calls(self) -> None:
        cid1 = ids.contract_id("src/Vault.sol", "Vault", "/repo")
        cid2 = ids.contract_id("src/Vault.sol", "Vault", "/repo")
        self.assertEqual(cid1, cid2)
        self.assertTrue(cid1.startswith("contract:"))
        self.assertEqual(ids.function_id(cid1, "deposit(uint256)"),
                         ids.function_id(cid2, "deposit(uint256)"))

    def test_no_timestamp_or_random_seed(self) -> None:
        # Repeated protocol/value-path IDs for identical input must be stable.
        self.assertEqual(ids.protocol_id("/repo"), ids.protocol_id("/repo"))
        self.assertEqual(
            ids.value_path_id("function:a:1", "function:b:2", "label"),
            ids.value_path_id("function:a:1", "function:b:2", "label"),
        )

    def test_path_normalization_to_posix(self) -> None:
        self.assertEqual(ids.normalize_path("a\\b\\C.sol"), "a/b/C.sol")
        self.assertEqual(ids.normalize_path(""), "")

    def test_signature_normalization_preserves_argument_text(self) -> None:
        self.assertEqual(ids.normalize_signature("  swap(  uint256 a , address b ) "),
                         "swap( uint256 a , address b )")

    def test_overloaded_signatures_get_distinct_function_ids(self) -> None:
        cid = ids.contract_id("src/Pool.sol", "Pool", "/repo")
        self.assertNotEqual(
            ids.function_id(cid, "swap(uint256)"),
            ids.function_id(cid, "swap(uint256,address)"),
        )

    def test_same_function_in_different_contracts_differs(self) -> None:
        a = ids.contract_id("src/A.sol", "A", "/repo")
        b = ids.contract_id("src/B.sol", "B", "/repo")
        self.assertNotEqual(ids.function_id(a, "f()"), ids.function_id(b, "f()"))

    def test_human_readable_prefixes(self) -> None:
        self.assertTrue(ids.test_gap_id("fid", "scenario").startswith("test-gap:"))
        self.assertTrue(ids.assumption_id("oracle", "fid").startswith("assumption:oracle:"))
        self.assertTrue(ids.evidence_link_id("proof", "fid").startswith("evidence-link:proof:"))


if __name__ == "__main__":
    unittest.main()
