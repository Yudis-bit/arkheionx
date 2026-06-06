"""Tests for the deterministic review package export (v3.6, internal)."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from arkheionx.review_package import builder as bld
from arkheionx.review_package import export as ex


def _built(tmp: str) -> Path:
    out = Path(tmp) / ".arkheionx" / "out"
    for rel in ("review-map/review-map.json", "review-map/evidence-links.json",
                "artifacts-index.json", "review-map/value-paths.json"):
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"k": 1}', encoding="utf-8")
    bld.build_review_package(tmp)
    return out / "review-package"


class ExportHelperTests(unittest.TestCase):
    def test_default_exports_dir_and_filename(self) -> None:
        self.assertEqual(ex.default_exports_dir("/p/review-package"), Path("/p/review-package/exports"))
        name = ex.default_export_filename("review-package:abc123", "zip")
        self.assertTrue(name.startswith("arkheionx-review-package-") and name.endswith(".zip"))
        self.assertNotIn(":", name)
        self.assertNotIn(" ", name)

    def test_archive_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "review-package"
            (pkg / "x").mkdir(parents=True)
            f = pkg / "manifest.json"
            f.write_text("{}")
            self.assertEqual(ex.archive_relative_path(f, pkg), "arkheionx-review-package/manifest.json")

    def test_iter_export_files_sorted_and_excludes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = _built(tmp)
            (pkg / "exports").mkdir(exist_ok=True)
            (pkg / "exports" / "old.zip").write_text("x")
            (pkg / "__pycache__").mkdir(exist_ok=True)
            (pkg / "__pycache__" / "y.pyc").write_text("x")
            (pkg / ".DS_Store").write_text("x")
            rels = [p.relative_to(pkg).as_posix() for p in ex.iter_export_files(pkg)]
            self.assertEqual(rels, sorted(rels))
            self.assertFalse(any(r.startswith("exports/") for r in rels))
            self.assertFalse(any("__pycache__" in r for r in rels))
            self.assertNotIn(".DS_Store", rels)
            self.assertIn("manifest.json", rels)


class CreateZipTests(unittest.TestCase):
    def test_create_zip_contents_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = _built(tmp)
            export = ex.export_review_package(tmp)
            self.assertEqual(export.status, "created")
            arc = pkg / "exports" / Path(export.export_path).name
            with zipfile.ZipFile(arc) as z:
                names = z.namelist()
            self.assertEqual(names, sorted(names))
            for expected in ("manifest.json", "validation.json", "README.md", "limitations.md",
                             "checksums/SHA256SUMS"):
                self.assertIn(f"arkheionx-review-package/{expected}", names)
            self.assertTrue(any(n.startswith("arkheionx-review-package/artifacts/") for n in names))
            self.assertFalse(any("exports/" in n for n in names))
            for n in names:
                self.assertFalse(n.startswith("/"))
                self.assertNotIn("..", n.split("/"))
                self.assertNotIn("\\", n)

    def test_fixed_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = _built(tmp)
            export = ex.export_review_package(tmp)
            arc = pkg / "exports" / Path(export.export_path).name
            with zipfile.ZipFile(arc) as z:
                self.assertTrue(all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in z.infolist()))

    def test_repeated_export_same_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = _built(tmp)
            first = ex.export_review_package(tmp)
            arc1 = pkg / "exports" / Path(first.export_path).name
            digest1 = hashlib.sha256(arc1.read_bytes()).hexdigest()
            second = ex.export_review_package(tmp)
            arc2 = pkg / "exports" / Path(second.export_path).name
            self.assertEqual(digest1, hashlib.sha256(arc2.read_bytes()).hexdigest())
            self.assertEqual(first.export_id, second.export_id)

    def test_export_result_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _built(tmp)
            export = ex.export_review_package(tmp)
            self.assertTrue(export.export_id.startswith("package-export:"))
            self.assertEqual(export.format, "zip")
            self.assertFalse(export.export_path.startswith("/"))
            self.assertTrue(all(not f.startswith("/") for f in export.included_files))
            self.assertTrue(export.manifest_checksum and export.validation_checksum)
            d = ex.review_package_export_to_dict(export)
            json.dumps(d)
            self.assertNotIn("ready_for_submission", json.dumps(d))
            self.assertEqual(d["metadata"]["file_count"], len(export.included_files))


class ExportBlockTests(unittest.TestCase):
    def test_missing_package_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(ex.export_review_package(tmp).status, "blocked")

    def test_missing_required_file_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = _built(tmp)
            (pkg / "manifest.json").unlink()
            self.assertEqual(ex.export_review_package(tmp).status, "blocked")

    def test_unsupported_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _built(tmp)
            self.assertEqual(ex.export_review_package(tmp, export_format="tar").status, "unsupported_format")

    def test_safety_failure_blocks_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = _built(tmp)
            data = json.loads((pkg / "validation.json").read_text())
            data["safety_failures"] = ["manual_review_required is true"]
            (pkg / "validation.json").write_text(json.dumps(data))
            self.assertEqual(ex.export_review_package(tmp).status, "blocked")

    def test_strict_invalid_blocks_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = _built(tmp)
            data = json.loads((pkg / "validation.json").read_text())
            data["status"] = "PACKAGE_INVALID"
            (pkg / "validation.json").write_text(json.dumps(data))
            self.assertEqual(ex.export_review_package(tmp, strict=True).status, "blocked")
            self.assertEqual(ex.export_review_package(tmp, strict=False).status, "created")


if __name__ == "__main__":
    unittest.main()
