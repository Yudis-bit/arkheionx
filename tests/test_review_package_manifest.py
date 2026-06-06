"""Tests for the review package manifest builder (v3.6, internal)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_package import manifest as mf


def _seed(root: Path, names: list[str]) -> None:
    for rel in names:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")


_BASE = ["review-map/review-map.json", "review-map/evidence-links.json", "artifacts-index.json"]


class ManifestTests(unittest.TestCase):
    def test_empty_root_builds_without_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            man = mf.build_review_package_manifest(tmp)
            self.assertEqual(man.included_artifacts, [])
            self.assertTrue(man.package_id.startswith("review-package:"))

    def test_required_and_optional_lists_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            man = mf.build_review_package_manifest(tmp)
            self.assertEqual(man.required_artifacts, ["artifacts_index", "evidence_links", "review_map"])
            self.assertIn("value_paths", man.optional_artifacts)
            self.assertIn("unknown", man.optional_artifacts)

    def test_flags_and_safety_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            man = mf.build_review_package_manifest(tmp)
            self.assertTrue(man.manual_review_required)
            self.assertFalse(man.ready_for_submission)
            self.assertTrue(man.safety_boundary["manual_review_required"])
            self.assertFalse(man.safety_boundary["ready_for_submission"])

    def test_package_id_deterministic_and_changes_with_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / ".arkheionx" / "out"
            _seed(root, _BASE)
            first = mf.build_review_package_manifest(tmp).package_id
            self.assertEqual(first, mf.build_review_package_manifest(tmp).package_id)
            _seed(root, ["review-map/value-paths.json"])
            self.assertNotEqual(first, mf.build_review_package_manifest(tmp).package_id)

    def test_included_artifacts_sorted_and_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE)
            man = mf.build_review_package_manifest(tmp)
            rels = [a.relative_path for a in man.included_artifacts]
            self.assertEqual(rels, sorted(rels))
            for art in man.included_artifacts:
                self.assertFalse(art.path.startswith("/"))
                self.assertFalse(art.relative_path.startswith("/"))

    def test_no_review_package_directory_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE)
            mf.build_review_package_manifest(tmp)
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package").exists())

    def test_manifest_to_dict_is_json_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE)
            data = mf.manifest_to_dict(mf.build_review_package_manifest(tmp))
            json.dumps(data)
            self.assertIsInstance(data["included_artifacts"], list)
            self.assertEqual(data["included_artifacts"][0]["path"].startswith("/"), False)

    def test_unknown_artifacts_included_honestly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE + ["misc/extra.json"])
            man = mf.build_review_package_manifest(tmp)
            kinds = {a.relative_path: a.kind for a in man.included_artifacts}
            self.assertEqual(kinds["misc/extra.json"], "unknown")

    def test_missing_optionals_not_fabricated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE)
            man = mf.build_review_package_manifest(tmp)
            kinds = {a.kind for a in man.included_artifacts}
            self.assertNotIn("evidence_package", kinds)
            self.assertNotIn("report_draft", kinds)

    def test_protocol_model_id_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            man = mf.build_review_package_manifest(tmp, protocol_model_id="protocol:abc")
            self.assertEqual(man.protocol_model_id, "protocol:abc")

    def test_package_name_fallback_and_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(mf.build_review_package_manifest(tmp).package_name.startswith("review-package-"))
            self.assertEqual(mf.build_review_package_manifest(tmp, package_name="my-pkg").package_name, "my-pkg")

    def test_limitations_have_safety_wording(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = " ".join(mf.build_review_package_manifest(tmp).limitations).lower()
            self.assertIn("not an audit", text)
            self.assertIn("manual review", text)

    def test_no_human_reviewed_in_manifest_dict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE)
            self.assertNotIn("HUMAN_REVIEWED", json.dumps(mf.manifest_to_dict(mf.build_review_package_manifest(tmp))))

    def test_summary_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE)
            man = mf.build_review_package_manifest(tmp)
            summary = mf.summarize_manifest_artifacts(man)
            self.assertEqual(summary["total_artifacts"], len(man.included_artifacts))
            self.assertEqual(summary["required_present"], 3)


if __name__ == "__main__":
    unittest.main()
