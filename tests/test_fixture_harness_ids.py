"""Tests for the internal fixture-harness deterministic ID utilities (v3.9)."""
from __future__ import annotations

import unittest

from arkheionx.fixture_harness import ids


class CanonicalSeedTests(unittest.TestCase):
    def test_canonical_seed_deterministic_across_dict_order(self) -> None:  # 1
        self.assertEqual(
            ids.canonical_fixture_seed({"b": 1, "a": 2, "c": [3, 2, 1]}),
            ids.canonical_fixture_seed({"c": [3, 2, 1], "a": 2, "b": 1}),
        )

    def test_unsupported_seed_raises_type_error(self) -> None:  # 22
        with self.assertRaises(TypeError):
            ids.canonical_fixture_seed(object())


class ShortHashTests(unittest.TestCase):
    def test_short_hash_deterministic(self) -> None:  # 2
        self.assertEqual(ids.short_fixture_hash({"x": 1}), ids.short_fixture_hash({"x": 1}))

    def test_short_hash_length_configurable(self) -> None:  # 3
        self.assertEqual(len(ids.short_fixture_hash("x")), 12)
        self.assertEqual(len(ids.short_fixture_hash("x", 8)), 8)
        self.assertEqual(len(ids.short_fixture_hash("x", 64)), 64)

    def test_short_hash_invalid_length_raises_value_error(self) -> None:  # 4
        for bad in (0, -1, -12):
            with self.subTest(length=bad):
                with self.assertRaises(ValueError):
                    ids.short_fixture_hash("x", bad)


class SlugifyTests(unittest.TestCase):
    def test_slugify_normalizes_spaces_case_punctuation(self) -> None:  # 5
        self.assertEqual(ids.slugify_fixture_token("My Vault!! (v2)"), "my-vault-v2")
        self.assertEqual(ids.slugify_fixture_token("ERC20  Token"), "erc20-token")
        self.assertEqual(ids.slugify_fixture_token("!!!"), "unknown")  # empty -> fallback


class NormalizePathTests(unittest.TestCase):
    def test_rejects_absolute_by_default(self) -> None:  # 6
        with self.assertRaises(ValueError):
            ids.normalize_fixture_path("/etc/passwd")
        with self.assertRaises(ValueError):
            ids.normalize_fixture_path("C:/win/x.sol")
        self.assertEqual(ids.normalize_fixture_path("/abs/x.sol", allow_absolute=True), "/abs/x.sol")

    def test_rejects_backslashes(self) -> None:  # 7
        with self.assertRaises(ValueError):
            ids.normalize_fixture_path("contracts\\Vault.sol")

    def test_rejects_traversal(self) -> None:  # 8
        with self.assertRaises(ValueError):
            ids.normalize_fixture_path("../escape.sol")
        with self.assertRaises(ValueError):
            ids.normalize_fixture_path("a/../../b.sol")

    def test_empty_path_is_empty_string(self) -> None:
        self.assertEqual(ids.normalize_fixture_path(""), "")
        self.assertEqual(ids.normalize_fixture_path("contracts/Vault.sol"), "contracts/Vault.sol")


class FixtureIdTests(unittest.TestCase):
    def test_fixture_id_deterministic(self) -> None:  # 9
        a = ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT", "contracts/Vault.sol")
        b = ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT", "contracts/Vault.sol")
        self.assertEqual(a, b)

    def test_fixture_id_changes_with_category(self) -> None:  # 10
        a = ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT")
        b = ids.fixture_id("Vault", "FIXTURE_CATEGORY_ERC20")
        self.assertNotEqual(a, b)

    def test_fixture_id_changes_with_name(self) -> None:  # 11
        a = ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT")
        b = ids.fixture_id("Other", "FIXTURE_CATEGORY_LENDING_VAULT")
        self.assertNotEqual(a, b)

    def test_fixture_id_has_expected_prefix(self) -> None:  # 12
        fid = ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT")
        self.assertTrue(fid.startswith("fixture:"))
        self.assertEqual(len(fid.split(":")[-1]), 12)
        self.assertEqual(len(fid.split(":")), 4)  # fixture:<cat>:<name>:<hash>


class CompositeIdTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fid = ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT", "contracts/Vault.sol")

    def test_fixture_artifact_id_deterministic(self) -> None:  # 13
        a = ids.fixture_artifact_id(self.fid, "FIXTURE_ARTIFACT_SOURCE", "contracts/Vault.sol")
        b = ids.fixture_artifact_id(self.fid, "FIXTURE_ARTIFACT_SOURCE", "contracts/Vault.sol")
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("fixture-artifact:"))

    def test_fixture_run_id_deterministic(self) -> None:  # 14
        a = ids.fixture_run_id(self.fid, "pipeline", {"top": 5})
        b = ids.fixture_run_id(self.fid, "pipeline", {"top": 5})
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("fixture-run:pipeline:"))

    def test_fixture_run_id_input_dict_order_stable(self) -> None:  # 15
        a = ids.fixture_run_id(self.fid, "pipeline", {"x": 1, "y": 2, "z": 3})
        b = ids.fixture_run_id(self.fid, "pipeline", {"z": 3, "y": 2, "x": 1})
        self.assertEqual(a, b)

    def test_fixture_result_id_deterministic(self) -> None:  # 16
        run = ids.fixture_run_id(self.fid, "pipeline")
        a = ids.fixture_result_id(run, "graph_counts", "node")
        b = ids.fixture_result_id(run, "graph_counts", "node")
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("fixture-result:"))

    def test_fixture_snapshot_id_deterministic(self) -> None:  # 17
        a = ids.fixture_snapshot_id(self.fid, "graph", ["a", "b"])
        b = ids.fixture_snapshot_id(self.fid, "graph", ["a", "b"])
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("fixture-snapshot:graph:"))

    def test_fixture_snapshot_id_subject_order_stable(self) -> None:  # 18
        a = ids.fixture_snapshot_id(self.fid, "graph", ["z", "a", "m"])
        b = ids.fixture_snapshot_id(self.fid, "graph", ["a", "m", "z"])
        self.assertEqual(a, b)

    def test_all_ids_contain_no_spaces(self) -> None:  # 19
        fid = ids.fixture_id("My Big Vault", "FIXTURE_CATEGORY_LENDING_VAULT", "contracts/My Vault.sol")
        run = ids.fixture_run_id(fid, "the runner", {"a b": "c d"})
        snap = ids.fixture_snapshot_id(fid, "graph counts", ["x y"])
        art = ids.fixture_artifact_id(fid, "FIXTURE ARTIFACT SOURCE")
        res = ids.fixture_result_id(run, "graph counts", "the subject")
        for value in (fid, run, snap, art, res):
            self.assertNotIn(" ", value)

    def test_all_ids_contain_no_backslashes(self) -> None:  # 20
        fid = ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT")
        run = ids.fixture_run_id(fid, "runner")
        for value in (fid, run, ids.fixture_snapshot_id(fid, "graph"),
                      ids.fixture_artifact_id(fid, "kind"), ids.fixture_result_id(run, "kind")):
            self.assertNotIn("\\", value)


class RequiredInputTests(unittest.TestCase):
    def test_empty_required_inputs_raise_value_error(self) -> None:  # 21
        with self.assertRaises(ValueError):
            ids.fixture_id("", "FIXTURE_CATEGORY_MISC")
        with self.assertRaises(ValueError):
            ids.fixture_id("Vault", "")
        with self.assertRaises(ValueError):
            ids.fixture_artifact_id("", "FIXTURE_ARTIFACT_SOURCE")
        with self.assertRaises(ValueError):
            ids.fixture_artifact_id("fixture:x", "")
        with self.assertRaises(ValueError):
            ids.fixture_run_id("")
        with self.assertRaises(ValueError):
            ids.fixture_result_id("", "kind")
        with self.assertRaises(ValueError):
            ids.fixture_result_id("run", "")
        with self.assertRaises(ValueError):
            ids.fixture_snapshot_id("", "graph")
        with self.assertRaises(ValueError):
            ids.fixture_snapshot_id("fixture:x", "")


class StabilityTests(unittest.TestCase):
    def test_no_timestamp_random_or_hash_behavior(self) -> None:  # 23
        fid = ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT", "contracts/Vault.sol")
        run = ids.fixture_run_id(fid, "pipeline", {"top": 5})
        snap = ids.fixture_snapshot_id(fid, "graph", ["a", "b", "c"])
        for _ in range(25):
            self.assertEqual(ids.fixture_id("Vault", "FIXTURE_CATEGORY_LENDING_VAULT", "contracts/Vault.sol"), fid)
            self.assertEqual(ids.fixture_run_id(fid, "pipeline", {"top": 5}), run)
            self.assertEqual(ids.fixture_snapshot_id(fid, "graph", ["c", "b", "a"]), snap)


if __name__ == "__main__":
    unittest.main()
