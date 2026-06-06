"""Tests for internal review package dataclasses and serialization (v3.6)."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path, PurePosixPath

from arkheionx import review_package as rp
from arkheionx.review_package import model


class ReviewPackageModelTests(unittest.TestCase):
    def test_minimal_review_workspace(self) -> None:
        ws = model.ReviewWorkspace(workspace_id="workspace:1:2", repo_path="/repo")
        self.assertEqual(ws.artifacts_dir, ".arkheionx/out")
        self.assertEqual(ws.package_root, ".arkheionx/out/review-package")
        self.assertEqual(ws.created_at, "")  # never auto-stamped
        self.assertEqual(ws.metadata, {})
        self.assertEqual(ws.safety_boundary, {})

    def test_minimal_review_package_artifact(self) -> None:
        art = model.ReviewPackageArtifact(artifact_id="package-artifact:x", kind="proof", path="p.json")
        self.assertFalse(art.exists)
        self.assertEqual(art.status, "unknown")
        self.assertFalse(art.required)
        self.assertEqual(art.linked_ids, {})
        self.assertEqual(art.warnings, [])
        self.assertEqual(art.metadata, {})

    def test_manifest_with_included_artifacts(self) -> None:
        art = model.ReviewPackageArtifact(artifact_id="a", kind="review-map", path="review-map.json")
        man = model.ReviewPackageManifest(package_id="review-package:xyz", included_artifacts=[art])
        self.assertEqual(man.manifest_version, "1")
        self.assertTrue(man.manual_review_required)
        self.assertFalse(man.ready_for_submission)
        self.assertEqual(man.included_artifacts[0].kind, "review-map")
        self.assertEqual(man.checksums, {})

    def test_validation_result_defaults(self) -> None:
        res = model.ReviewPackageValidationResult(validation_id="package-validation:1", package_id="review-package:xyz")
        self.assertEqual(res.status, model.PACKAGE_DRAFT)
        self.assertTrue(res.manual_review_required)
        self.assertFalse(res.ready_for_human_review)
        self.assertFalse(res.ready_for_submission)
        for empty in (res.errors, res.warnings, res.missing_required_artifacts,
                      res.checksum_mismatches, res.schema_failures, res.safety_failures):
            self.assertEqual(empty, [])

    def test_export_defaults(self) -> None:
        exp = model.ReviewPackageExport(export_id="package-export:1", package_id="review-package:xyz", export_path="out.zip")
        self.assertEqual(exp.format, "zip")
        self.assertEqual(exp.status, "not_created")
        self.assertEqual(exp.included_files, [])

    def test_to_dict_is_plain_json_safe(self) -> None:
        man = model.ReviewPackageManifest(package_id="p", safety_boundary=dict(model.DEFAULT_REVIEW_PACKAGE_SAFETY_BOUNDARY))
        data = model.to_dict(man)
        self.assertIsInstance(data, dict)
        # Round-trips through json without custom encoders.
        json.dumps(data)
        self.assertIs(data["manual_review_required"], True)
        self.assertIs(data["ready_for_submission"], False)

    def test_to_dict_preserves_nested_included_artifacts(self) -> None:
        art = model.ReviewPackageArtifact(artifact_id="a", kind="proof", path="p.json", warnings=["w"])
        man = model.ReviewPackageManifest(package_id="p", included_artifacts=[art])
        data = model.to_dict(man)
        self.assertEqual(data["included_artifacts"][0]["artifact_id"], "a")
        self.assertEqual(data["included_artifacts"][0]["warnings"], ["w"])

    def test_to_dict_preserves_empty_containers_and_does_not_mutate(self) -> None:
        ws = model.ReviewWorkspace(workspace_id="w", repo_path="/r")
        data = model.to_dict(ws)
        self.assertEqual(data["metadata"], {})
        self.assertEqual(data["export_path"], "")
        # Source object is unchanged and still a dataclass.
        self.assertEqual(ws.metadata, {})
        self.assertTrue(hasattr(ws, "__dataclass_fields__"))

    def test_to_dict_converts_path_values(self) -> None:
        art = model.ReviewPackageArtifact(
            artifact_id="a", kind="proof", path="p.json", metadata={"src": PurePosixPath("a/b.json")}
        )
        data = model.to_dict(art)
        self.assertEqual(data["metadata"]["src"], "a/b.json")
        json.dumps(data)

    def test_to_dict_rejects_unsupported(self) -> None:
        with self.assertRaises(TypeError):
            model.to_dict({1, 2, 3})

    def test_default_safety_boundary_has_no_human_reviewed(self) -> None:
        sb = model.DEFAULT_REVIEW_PACKAGE_SAFETY_BOUNDARY
        self.assertTrue(sb["manual_review_required"])
        self.assertFalse(sb["ready_for_submission"])
        self.assertTrue(sb["local_static_only"])
        self.assertNotIn("HUMAN_REVIEWED", json.dumps(sb))

    def test_package_exposes_expected_symbols(self) -> None:
        for name in (
            "ReviewWorkspace", "ReviewPackageManifest", "ReviewPackageArtifact",
            "ReviewPackageValidationResult", "ReviewPackageExport", "to_dict",
            "review_workspace_id", "review_package_id", "package_artifact_id",
            "package_validation_id", "package_export_id", "repo_fingerprint",
            "normalize_package_path", "package_slug",
            "DEFAULT_REVIEW_PACKAGE_SAFETY_BOUNDARY", "PACKAGE_DRAFT",
            "PACKAGE_PARTIAL", "PACKAGE_READY_FOR_HUMAN_REVIEW",
            "PACKAGE_INVALID", "PACKAGE_EXPORT_READY",
        ):
            self.assertTrue(hasattr(rp, name), name)

    def test_no_filesystem_side_effects_from_model_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                rp.review_workspace_id("/repo")
                model.to_dict(model.ReviewWorkspace(workspace_id="w", repo_path="/repo"))
                entries = list(Path(tmp).iterdir())
            finally:
                os.chdir(cwd)
            self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
