"""Tests for the review package builder and writer (v3.6, internal)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_package import builder as b
from arkheionx.review_package import manifest as mf


def _seed(repo: Path, names: list[str] | None = None) -> None:
    out = repo / ".arkheionx" / "out"
    for rel in (names or ["review-map/review-map.json", "review-map/evidence-links.json",
                          "artifacts-index.json", "review-map/value-paths.json"]):
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"k": 1}', encoding="utf-8")


class BuilderTests(unittest.TestCase):
    def test_no_write_builds_in_memory_no_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = b.build_review_package(tmp, no_write=True)
            self.assertTrue(result.no_write)
            self.assertFalse(result.written)
            self.assertIsNotNone(result.manifest)
            self.assertIsNotNone(result.validation)
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package").exists())

    def test_write_creates_package_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = b.build_review_package(tmp)
            pkg = Path(tmp) / ".arkheionx" / "out" / "review-package"
            self.assertTrue(result.written and pkg.is_dir())
            for rel in ("manifest.json", "validation.json", "README.md", "limitations.md",
                        "checksums/SHA256SUMS", "artifacts/review-map/review-map.json"):
                self.assertTrue((pkg / rel).is_file(), rel)

    def test_write_no_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            b.build_review_package(tmp)
            pkg = Path(tmp) / ".arkheionx" / "out" / "review-package"
            self.assertFalse(any(p.suffix in (".zip", ".tar", ".gz", ".tgz") for p in pkg.rglob("*")))

    def test_written_files_have_no_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            b.build_review_package(tmp)
            pkg = Path(tmp) / ".arkheionx" / "out" / "review-package"
            for rel in ("manifest.json", "validation.json", "README.md", "limitations.md", "checksums/SHA256SUMS"):
                self.assertNotIn(tmp, (pkg / rel).read_text(encoding="utf-8"), rel)

    def test_manifest_and_validation_json_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            b.build_review_package(tmp)
            pkg = Path(tmp) / ".arkheionx" / "out" / "review-package"
            manifest = json.loads((pkg / "manifest.json").read_text())
            validation = json.loads((pkg / "validation.json").read_text())
            self.assertFalse(manifest["ready_for_submission"])
            self.assertTrue(manifest["manual_review_required"])
            self.assertNotIn("HUMAN_REVIEWED", json.dumps(manifest))
            self.assertNotIn("HUMAN_REVIEWED", json.dumps(validation))

    def test_readme_and_limitations_safety_wording(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            b.build_review_package(tmp)
            pkg = Path(tmp) / ".arkheionx" / "out" / "review-package"
            readme = (pkg / "README.md").read_text().lower()
            self.assertIn("manual review is required", readme)
            self.assertIn("ready for submission: false", readme)
            self.assertIn("no rpc", readme)
            limits = (pkg / "limitations.md").read_text().lower()
            self.assertIn("not a formal audit", limits)
            self.assertIn("not ready for submission", limits)

    def test_result_flags_and_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = b.build_review_package(tmp)
            self.assertTrue(result.manual_review_required)
            self.assertFalse(result.ready_for_submission)
            self.assertEqual(result.artifact_count, 4)
            d = b.build_review_package_result_dict(result)
            json.dumps(d)
            for key in ("command", "package_root", "manifest_path", "validation_path",
                        "readme_path", "limitations_path", "checksums_path", "artifact_count",
                        "validation_status", "manual_review_required", "ready_for_submission",
                        "written", "no_write", "warnings", "errors"):
                self.assertIn(key, d)
            for key in ("package_root", "manifest_path", "validation_path"):
                self.assertFalse(str(d[key]).startswith("/"))

    def test_missing_root_no_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = b.build_review_package(tmp, no_write=True)
            self.assertEqual(result.artifact_count, 0)

    def test_exclude_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            (Path(tmp) / ".arkheionx" / "out" / "misc.json").write_text("{}")
            full = b.build_review_package(tmp, no_write=True)
            excl = b.build_review_package(tmp, no_write=True, include_unknown=False)
            self.assertTrue(any(a.kind == "unknown" for a in full.manifest.included_artifacts))
            self.assertFalse(any(a.kind == "unknown" for a in excl.manifest.included_artifacts))

    def test_path_traversal_artifact_not_copied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = b.build_review_package(tmp)
            from arkheionx.review_package import writer
            from arkheionx.review_package.model import ReviewPackageArtifact
            bad = ReviewPackageArtifact(artifact_id="a", kind="review_map",
                                        path=".arkheionx/out/../../escape.json",
                                        relative_path="../escape.json", exists=True)
            with self.assertRaises(ValueError):
                writer.copy_package_artifact(bad, tmp, Path(tmp) / ".arkheionx" / "out" / "review-package")
            self.assertTrue(result.written)

    def test_repeated_build_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            first = b.build_review_package(tmp)
            second = b.build_review_package(tmp)
            self.assertEqual(mf.manifest_to_dict(first.manifest), mf.manifest_to_dict(second.manifest))
            self.assertEqual(first.manifest.package_id, second.manifest.package_id)

    def test_does_not_create_archive_or_change_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            src = Path(tmp) / ".arkheionx" / "out" / "review-map" / "review-map.json"
            before = src.read_text()
            b.build_review_package(tmp)
            self.assertEqual(src.read_text(), before)


if __name__ == "__main__":
    unittest.main()
