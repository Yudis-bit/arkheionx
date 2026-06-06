"""Tests for deterministic local validation ID utilities (v3.7, internal)."""
from __future__ import annotations

import unittest
from pathlib import PurePosixPath

from arkheionx.local_validation import ids


class CanonicalAndHashTests(unittest.TestCase):
    def test_canonical_json_is_key_order_independent(self) -> None:
        self.assertEqual(ids.canonical_json_dumps({"a": 1, "b": 2}),
                         ids.canonical_json_dumps({"b": 2, "a": 1}))

    def test_canonical_json_rejects_unsupported(self) -> None:
        with self.assertRaises(TypeError):
            ids.canonical_json_dumps({1, 2, 3})

    def test_short_hash_deterministic(self) -> None:
        self.assertEqual(ids.short_hash(["a", "b"]), ids.short_hash(["a", "b"]))

    def test_short_hash_default_length_is_12(self) -> None:
        self.assertEqual(len(ids.short_hash(["x"])), 12)

    def test_short_hash_custom_length(self) -> None:
        self.assertEqual(len(ids.short_hash(["x"], length=8)), 8)
        with self.assertRaises(ValueError):
            ids.short_hash(["x"], length=0)

    def test_short_hash_path_seed_matches_posix_string(self) -> None:
        self.assertEqual(ids.short_hash([PurePosixPath("a/b")]), ids.short_hash(["a/b"]))


class PathAndSlugTests(unittest.TestCase):
    def test_normalize_id_path_converts_to_posix(self) -> None:
        self.assertEqual(ids.normalize_id_path("a\\b\\C.json"), "a/b/C.json")
        self.assertEqual(ids.normalize_id_path("a//b/"), "a/b")
        self.assertEqual(ids.normalize_id_path("./a/b"), "a/b")
        self.assertEqual(ids.normalize_id_path(""), "")

    def test_normalize_id_path_rejects_absolute_when_required(self) -> None:
        self.assertEqual(ids.normalize_id_path("/a/b", allow_absolute=True), "/a/b")
        with self.assertRaises(ValueError):
            ids.normalize_id_path("/a/b", allow_absolute=False)
        with self.assertRaises(ValueError):
            ids.normalize_id_path("C:\\a\\b", allow_absolute=False)

    def test_slugify_token_lowercases_and_removes_spaces(self) -> None:
        self.assertEqual(ids.slugify_token("Foundry Tool"), "foundry-tool")
        self.assertNotIn(" ", ids.slugify_token("a b c"))

    def test_slugify_token_fallback(self) -> None:
        self.assertEqual(ids.slugify_token("  --  "), "unknown")
        self.assertEqual(ids.slugify_token("", fallback="none"), "none")

    def test_slugify_token_max_length(self) -> None:
        self.assertLessEqual(len(ids.slugify_token("x" * 200, max_length=10)), 10)


class RepoFingerprintTests(unittest.TestCase):
    def test_repo_fingerprint_deterministic(self) -> None:
        self.assertEqual(ids.repo_fingerprint("/repo/a"), ids.repo_fingerprint("/repo/a"))
        self.assertNotEqual(ids.repo_fingerprint("/repo/a"), ids.repo_fingerprint("/repo/b"))
        self.assertEqual(ids.repo_fingerprint("a\\b"), ids.repo_fingerprint("a/b"))

    def test_repo_fingerprint_requires_value(self) -> None:
        with self.assertRaises(ValueError):
            ids.repo_fingerprint("")

    def test_repo_fingerprint_does_not_leak_absolute_path(self) -> None:
        self.assertNotIn("/repo", ids.repo_fingerprint("/repo/secret/path"))


class RunIdTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fp = ids.repo_fingerprint("/repo/a")

    def test_run_id_deterministic_and_prefixed(self) -> None:
        a = ids.local_validation_run_id("foundry", self.fp, ["forge", "test"])
        self.assertTrue(a.startswith("local-validation-run:foundry:"))
        self.assertEqual(a, ids.local_validation_run_id("foundry", self.fp, ["forge", "test"]))

    def test_run_id_changes_when_command_changes(self) -> None:
        a = ids.local_validation_run_id("foundry", self.fp, ["forge", "test", "--match-test", "x"])
        b = ids.local_validation_run_id("foundry", self.fp, ["forge", "test", "--match-test", "y"])
        self.assertNotEqual(a, b)

    def test_run_id_preserves_command_order(self) -> None:
        a = ids.local_validation_run_id("foundry", self.fp, ["forge", "test", "a", "b"])
        b = ids.local_validation_run_id("foundry", self.fp, ["forge", "test", "b", "a"])
        self.assertNotEqual(a, b)

    def test_run_id_accepts_string_command(self) -> None:
        self.assertTrue(ids.local_validation_run_id("foundry", self.fp, "forge test").startswith(
            "local-validation-run:"))

    def test_run_id_requires_inputs(self) -> None:
        for args in [("", self.fp, ["forge"]), ("foundry", "", ["forge"]), ("foundry", self.fp, [])]:
            with self.assertRaises(ValueError):
                ids.local_validation_run_id(*args)


class ResultTraceArtifactSummaryIdTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fp = ids.repo_fingerprint("/repo/a")
        self.run = ids.local_validation_run_id("foundry", self.fp, ["forge", "test"])

    def test_test_result_id_deterministic_and_name_sensitive(self) -> None:
        a = ids.local_test_result_id("foundry", "test_borrow", self.run)
        self.assertTrue(a.startswith("local-test-result:foundry:"))
        self.assertEqual(a, ids.local_test_result_id("foundry", "test_borrow", self.run))
        self.assertNotEqual(a, ids.local_test_result_id("foundry", "test_repay", self.run))

    def test_test_result_id_requires_inputs(self) -> None:
        for args in [("", "t", self.run), ("foundry", "", self.run), ("foundry", "t", "")]:
            with self.assertRaises(ValueError):
                ids.local_test_result_id(*args)

    def test_trace_receipt_id_deterministic(self) -> None:
        result = ids.local_test_result_id("foundry", "test_borrow", self.run)
        a = ids.local_trace_receipt_id("foundry", result, {"calls": 3})
        self.assertTrue(a.startswith("local-trace-receipt:foundry:"))
        self.assertEqual(a, ids.local_trace_receipt_id("foundry", result, {"calls": 3}))

    def test_trace_receipt_id_requires_inputs(self) -> None:
        with self.assertRaises(ValueError):
            ids.local_trace_receipt_id("foundry", "", {"k": 1})
        with self.assertRaises(ValueError):
            ids.local_trace_receipt_id("foundry", "r", "")
        with self.assertRaises(TypeError):
            ids.local_trace_receipt_id("foundry", "r", {1, 2})

    def test_artifact_id_deterministic_and_rejects_absolute(self) -> None:
        a = ids.local_validation_artifact_id("local_validation_run", "runs/r.json")
        self.assertTrue(a.startswith("local-validation-artifact:local-validation-run:"))
        self.assertEqual(a, ids.local_validation_artifact_id("local_validation_run", "runs/r.json"))
        with self.assertRaises(ValueError):
            ids.local_validation_artifact_id("local_validation_run", "/abs/r.json")
        with self.assertRaises(ValueError):
            ids.local_validation_artifact_id("", "runs/r.json")

    def test_summary_id_sorts_artifact_ids(self) -> None:
        a = ids.local_validation_summary_id(self.fp, "foundry", ["b", "a", "c"])
        b = ids.local_validation_summary_id(self.fp, "foundry", ["c", "b", "a"])
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("local-validation-summary:foundry:"))
        self.assertNotEqual(a, ids.local_validation_summary_id(self.fp, "foundry", ["a", "b", "c", "d"]))


class IdHygieneTests(unittest.TestCase):
    def test_ids_have_no_spaces_or_backslashes_and_are_stable(self) -> None:
        fp = ids.repo_fingerprint("/repo/a")
        run = ids.local_validation_run_id("foundry tool", fp, ["forge", "test x"])
        result = ids.local_test_result_id("foundry", "test borrow", run)
        produced = [
            run,
            result,
            ids.local_trace_receipt_id("foundry", result, {"k": 1}),
            ids.local_validation_artifact_id("raw text", "a b/c.json"),
            ids.local_validation_summary_id(fp, "foundry", ["a", "b"]),
        ]
        for value in produced:
            self.assertNotIn(" ", value)
            self.assertNotIn("\\", value)
        again = [
            ids.local_validation_run_id("foundry tool", fp, ["forge", "test x"]),
            ids.local_test_result_id("foundry", "test borrow", run),
            ids.local_trace_receipt_id("foundry", result, {"k": 1}),
            ids.local_validation_artifact_id("raw text", "a b/c.json"),
            ids.local_validation_summary_id(fp, "foundry", ["a", "b"]),
        ]
        self.assertEqual(produced, again)


if __name__ == "__main__":
    unittest.main()
