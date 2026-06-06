"""Tests for the review package artifact collector (v3.6, internal)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from arkheionx.review_package import collector as col


def _make_artifacts(root: Path) -> None:
    files = [
        "review-map/review-map.json", "review-map/review-summary.md",
        "review-map/value-paths.json", "review-map/assumptions.json",
        "review-map/test-gap-map.json", "review-map/proof-plan.json",
        "review-map/evidence-links.json", "artifacts-index.json",
        "proof/LV_borrow/proof.json", "proof/LV_borrow/trace.json",
        "evidence/LV_borrow/evidence.json", "evidence/LV_borrow/manifest.json",
        "evidence/LV_borrow/evidence.txt", "reports/LV_borrow/report.json",
        "reports/LV_borrow/report.md", "misc/notes.json",
    ]
    for rel in files:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}" if rel.endswith(".json") else "x", encoding="utf-8")


class CollectorTests(unittest.TestCase):
    def test_default_artifacts_root(self) -> None:
        self.assertEqual(col.default_artifacts_root("/repo"), Path("/repo/.arkheionx/out"))

    def test_iter_missing_root_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(col.iter_artifact_files(Path(tmp) / "nope"), [])

    def test_iter_files_sorted_and_ignores_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_artifacts(root)
            files = col.iter_artifact_files(root)
            self.assertTrue(all(p.is_file() for p in files))
            rels = [p.relative_to(root).as_posix() for p in files]
            self.assertEqual(rels, sorted(rels))

    def test_classification_known_kinds(self) -> None:
        cases = {
            "review-map/review-map.json": "review_map",
            "review-map/review-summary.md": "review_map_summary",
            "review-map/value-paths.json": "value_paths",
            "review-map/assumptions.json": "assumptions",
            "review-map/test-gap-map.json": "test_gaps",
            "review-map/proof-plan.json": "proof_plan",
            "review-map/evidence-links.json": "evidence_links",
            "artifacts-index.json": "artifacts_index",
            "proof/LV/proof.json": "proof_receipt",
            "proof/LV/trace.json": "trace_receipt",
            "evidence/LV/evidence.json": "evidence_package",
            "evidence/LV/manifest.json": "evidence_manifest",
            "evidence/LV/evidence.txt": "evidence_text",
            "reports/LV/report.json": "report_draft",
            "reports/LV/report.md": "report_text",
        }
        for rel, kind in cases.items():
            self.assertEqual(col.classify_artifact_path(rel, ""), kind, rel)

    def test_classification_unknown(self) -> None:
        self.assertEqual(col.classify_artifact_path("misc/notes.json", ""), "unknown")
        self.assertEqual(col.classify_artifact_path("review-map/weird-extra.json", ""), "unknown")

    def test_relative_path_helpers(self) -> None:
        self.assertEqual(col.to_repo_relative_path("/repo/.arkheionx/out/x.json", "/repo"),
                         ".arkheionx/out/x.json")
        self.assertEqual(col.to_artifacts_relative_path("/repo/.arkheionx/out/review-map/x.json",
                                                         "/repo/.arkheionx/out"), "review-map/x.json")

    def test_collect_no_absolute_paths_and_present_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _make_artifacts(Path(tmp) / ".arkheionx" / "out")
            arts = col.collect_review_package_artifacts(tmp)
            self.assertTrue(arts)
            for art in arts:
                self.assertFalse(art.path.startswith("/"), art.path)
                self.assertFalse(art.relative_path.startswith("/"), art.relative_path)
                self.assertTrue(art.path.startswith(".arkheionx/out/"))
                self.assertTrue(art.exists)
                self.assertEqual(art.status, "present")

    def test_source_command_populated_for_known_kinds(self) -> None:
        self.assertEqual(col.artifact_source_command("review_map"), "review-map")
        self.assertEqual(col.artifact_source_command("evidence_package"), "evidence")
        self.assertEqual(col.artifact_source_command("unknown"), "")

    def test_unknown_kind_warns_not_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _make_artifacts(Path(tmp) / ".arkheionx" / "out")
            arts = col.collect_review_package_artifacts(tmp)
            unknown = [a for a in arts if a.kind == "unknown"]
            self.assertTrue(unknown)
            self.assertTrue(unknown[0].warnings)
            self.assertFalse(unknown[0].required)

    def test_collection_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _make_artifacts(Path(tmp) / ".arkheionx" / "out")
            a = [art.artifact_id for art in col.collect_review_package_artifacts(tmp)]
            b = [art.artifact_id for art in col.collect_review_package_artifacts(tmp)]
            self.assertEqual(a, b)

    def test_required_flags(self) -> None:
        self.assertTrue(col.is_required_artifact_kind("review_map"))
        self.assertTrue(col.is_required_artifact_kind("evidence_links"))
        self.assertTrue(col.is_required_artifact_kind("artifacts_index"))
        self.assertFalse(col.is_required_artifact_kind("proof_receipt"))
        self.assertTrue(col.is_optional_artifact_kind("proof_receipt"))

    def test_collect_no_write_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / ".arkheionx" / "out"
            _make_artifacts(out)
            before = sorted(p.relative_to(tmp).as_posix() for p in Path(tmp).rglob("*"))
            col.collect_review_package_artifacts(tmp)
            after = sorted(p.relative_to(tmp).as_posix() for p in Path(tmp).rglob("*"))
            self.assertEqual(before, after)
            self.assertFalse((out / "review-package").exists())


if __name__ == "__main__":
    unittest.main()
