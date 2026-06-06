"""Tests for deterministic review package ID utilities (v3.6, internal)."""
from __future__ import annotations

import unittest

from arkheionx.review_package import ids


class PackageIdTests(unittest.TestCase):
    def test_digest_is_deterministic_and_key_order_independent(self) -> None:
        self.assertEqual(ids._digest(["a", "b"]), ids._digest(["a", "b"]))
        # Sorted keys mean dict insertion order does not change the digest.
        self.assertEqual(ids._digest({"a": 1, "b": 2}), ids._digest({"b": 2, "a": 1}))
        self.assertEqual(len(ids._digest(["x"])), 12)

    def test_digest_supports_path_and_rejects_unsupported(self) -> None:
        from pathlib import PurePosixPath

        self.assertEqual(ids._digest([PurePosixPath("a/b")]), ids._digest(["a/b"]))
        with self.assertRaises(TypeError):
            ids._digest({1, 2, 3})

    def test_normalize_package_path_posix(self) -> None:
        self.assertEqual(ids.normalize_package_path("a\\b\\C.json"), "a/b/C.json")
        self.assertEqual(ids.normalize_package_path("a//b/"), "a/b")
        self.assertEqual(ids.normalize_package_path("./a/b"), "a/b")
        self.assertEqual(ids.normalize_package_path("/"), "/")
        self.assertEqual(ids.normalize_package_path(""), "")

    def test_package_slug_fallback_and_max_length(self) -> None:
        self.assertEqual(ids.package_slug("Review Map!!"), "review-map")
        self.assertEqual(ids.package_slug("  --  "), "unknown")
        self.assertEqual(ids.package_slug(""), "unknown")
        self.assertLessEqual(len(ids.package_slug("x" * 200, max_length=10)), 10)

    def test_repo_fingerprint_deterministic_and_validated(self) -> None:
        self.assertEqual(ids.repo_fingerprint("/repo/a"), ids.repo_fingerprint("/repo/a"))
        self.assertNotEqual(ids.repo_fingerprint("/repo/a"), ids.repo_fingerprint("/repo/b"))
        # Normalized: backslash and POSIX forms agree.
        self.assertEqual(ids.repo_fingerprint("a\\b"), ids.repo_fingerprint("a/b"))
        with self.assertRaises(ValueError):
            ids.repo_fingerprint("")

    def test_review_workspace_id_prefix_and_determinism(self) -> None:
        wid = ids.review_workspace_id("/repo/a")
        self.assertTrue(wid.startswith("workspace:"))
        self.assertEqual(wid, ids.review_workspace_id("/repo/a"))
        self.assertNotEqual(wid, ids.review_workspace_id("/repo/b"))
        self.assertNotEqual(ids.review_workspace_id("/repo/a", seed=1),
                            ids.review_workspace_id("/repo/a", seed=2))
        with self.assertRaises(ValueError):
            ids.review_workspace_id("")

    def test_review_package_id_artifact_ordering_stability(self) -> None:
        a = ids.review_package_id("pm:1", ["b", "a", "c"])
        b = ids.review_package_id("pm:1", ["c", "b", "a"])
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("review-package:"))
        self.assertNotEqual(a, ids.review_package_id("pm:2", ["a", "b", "c"]))
        self.assertNotEqual(a, ids.review_package_id("pm:1", ["a", "b", "c", "d"]))

    def test_package_artifact_id_kind_and_path_sensitivity(self) -> None:
        aid = ids.package_artifact_id("review-map", "review-map/review-map.json")
        self.assertTrue(aid.startswith("package-artifact:review-map:"))
        self.assertNotEqual(
            ids.package_artifact_id("review map", "a/b.json"),
            ids.package_artifact_id("review map", "a/c.json"),
        )
        self.assertNotEqual(
            ids.package_artifact_id("proof", "a/b.json"),
            ids.package_artifact_id("trace", "a/b.json"),
        )
        with self.assertRaises(ValueError):
            ids.package_artifact_id("", "a/b.json")
        with self.assertRaises(ValueError):
            ids.package_artifact_id("proof", "")

    def test_package_validation_id_determinism(self) -> None:
        vid = ids.package_validation_id("review-package:xyz")
        self.assertTrue(vid.startswith("package-validation:"))
        self.assertEqual(vid, ids.package_validation_id("review-package:xyz"))
        self.assertNotEqual(vid, ids.package_validation_id("review-package:other"))
        with self.assertRaises(ValueError):
            ids.package_validation_id("")

    def test_package_export_id_format_sensitivity(self) -> None:
        eid = ids.package_export_id("review-package:xyz", "zip")
        self.assertTrue(eid.startswith("package-export:"))
        self.assertIn(":zip:", eid)
        self.assertNotEqual(eid, ids.package_export_id("review-package:xyz", "tar.gz"))
        with self.assertRaises(ValueError):
            ids.package_export_id("review-package:xyz", "")
        with self.assertRaises(ValueError):
            ids.package_export_id("", "zip")

    def test_ids_have_no_spaces_and_are_stable_no_timestamp(self) -> None:
        produced = [
            ids.review_workspace_id("/repo/a"),
            ids.review_package_id("pm:1", ["a", "b"]),
            ids.package_artifact_id("review map", "a b/c.json"),
            ids.package_validation_id("review-package:xyz"),
            ids.package_export_id("review-package:xyz", "tar.gz"),
        ]
        for value in produced:
            self.assertNotIn(" ", value)
        # Re-running yields identical IDs (no timestamp/random component).
        again = [
            ids.review_workspace_id("/repo/a"),
            ids.review_package_id("pm:1", ["a", "b"]),
            ids.package_artifact_id("review map", "a b/c.json"),
            ids.package_validation_id("review-package:xyz"),
            ids.package_export_id("review-package:xyz", "tar.gz"),
        ]
        self.assertEqual(produced, again)


if __name__ == "__main__":
    unittest.main()
