"""Tests for the local validation artifact writer (v3.7, internal)."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from arkheionx import local_validation as lv
from arkheionx.local_validation import writer

_FIXTURES = Path(__file__).parent / "fixtures" / "local_validation" / "foundry"
_FP = lv.repo_fingerprint("/repo/demo")
_MODEL = {
    "protocol_id": "p",
    "contracts": [{"contract_id": "c", "name": "LendingVault", "aliases": {"contract_name": "LendingVault"}}],
    "functions": [{"function_id": "function:dep", "contract_id": "c", "signature": "deposit(uint256)",
                   "display_name": "LendingVault.deposit", "aliases": {}}],
    "value_paths": [], "assumptions": [], "test_gaps": [],
}


def _build():
    parsed = lv.parse_foundry_output((_FIXTURES / "forge-test-json-mixed.json").read_text(encoding="utf-8"))
    parsed.test_results.append(lv.LocalTestResult(
        test_name="deposit()", contract_name="LendingVault", function_name="deposit",
        status=lv.TEST_PASSED, metadata={"trace": {"call_count": 2}}))
    return lv.build_local_validation_from_parsed(parsed, repo_fingerprint=_FP, protocol_model=_MODEL)


class _RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.build = _build()
        self.write = lv.write_local_validation_artifacts(self.build, repo_path=self.repo)
        self.root = self.repo / ".arkheionx" / "out" / "local-validation"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _index(self) -> dict:
        return json.loads((self.root / "artifacts-index.json").read_text(encoding="utf-8"))

    def _sums(self) -> list[str]:
        return (self.root / "checksums" / "SHA256SUMS").read_text(encoding="utf-8").splitlines()


class LayoutTests(_RepoCase):
    def test_default_output_root(self) -> None:
        self.assertEqual(writer.default_local_validation_output_root(self.repo), self.root)

    def test_core_files_exist(self) -> None:
        for rel in ("summary.json", "run.json", "artifacts-index.json", "checksums/SHA256SUMS"):
            self.assertTrue((self.root / rel).is_file(), rel)

    def test_one_result_file_per_test(self) -> None:
        self.assertEqual(len(list((self.root / "results").glob("*.json"))), len(self.build.test_results))

    def test_trace_files_only_when_receipts_exist(self) -> None:
        self.assertEqual(len(list((self.root / "traces").glob("*.json"))), len(self.build.trace_receipts))
        self.assertEqual(len(self.build.trace_receipts), 1)

    def test_all_json_parseable(self) -> None:
        for path in self.root.rglob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))


class PathSafetyTests(_RepoCase):
    def test_no_absolute_paths_in_generated_json(self) -> None:
        repo_str = str(self.repo.resolve())
        for path in self.root.rglob("*.json"):
            self.assertNotIn(repo_str, path.read_text(encoding="utf-8"))
            self.assertNotIn("/home/", path.read_text(encoding="utf-8"))

    def test_no_backslashes_in_artifact_paths(self) -> None:
        for art in self._index()["artifacts"]:
            self.assertNotIn("\\", art["relative_path"])
            self.assertFalse(art["relative_path"].startswith("/"))

    def test_write_result_paths_repo_relative(self) -> None:
        self.assertEqual(self.write.output_root, ".arkheionx/out/local-validation")
        self.assertEqual(self.write.summary_path, ".arkheionx/out/local-validation/summary.json")

    def test_output_root_outside_repo_raises(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            with self.assertRaises(ValueError):
                lv.write_local_validation_artifacts(self.build, repo_path=self.repo, output_root=outside)

    def test_traversal_output_root_raises(self) -> None:
        with self.assertRaises(ValueError):
            writer.ensure_safe_output_root(self.repo, self.repo / ".." / "evil")

    def test_forced_unsafe_content_rejected(self) -> None:
        for bad in ('{"ready_for_submission": true}', '{"x": "HUMAN_REVIEWED"}'):
            with self.assertRaises(ValueError):
                writer._assert_safe_generated(bad, "x.json")


class DeterminismTests(_RepoCase):
    def test_repeated_write_identical_bytes(self) -> None:
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}
        lv.write_local_validation_artifacts(self.build, repo_path=self.repo)
        after = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}
        self.assertEqual(before, after)

    def test_checksum_map_deterministic_and_correct(self) -> None:
        again = lv.write_local_validation_artifacts(self.build, repo_path=self.repo)
        self.assertEqual(self.write.checksum_sha256, again.checksum_sha256)
        got = hashlib.sha256((self.root / "summary.json").read_bytes()).hexdigest()
        self.assertEqual(self.write.checksum_sha256["summary.json"], got)

    def test_written_files_sorted(self) -> None:
        self.assertEqual(self.write.written_files, sorted(self.write.written_files))


class ChecksumTests(_RepoCase):
    def test_sorted_by_relative_path(self) -> None:
        paths = [line.split("  ", 1)[1] for line in self._sums()]
        self.assertEqual(paths, sorted(paths))

    def test_contains_expected_and_excludes_self(self) -> None:
        paths = {line.split("  ", 1)[1] for line in self._sums()}
        self.assertIn("summary.json", paths)
        self.assertIn("run.json", paths)
        self.assertIn("artifacts-index.json", paths)
        self.assertTrue(any(p.startswith("results/") for p in paths))
        self.assertTrue(any(p.startswith("traces/") for p in paths))
        self.assertNotIn("checksums/SHA256SUMS", paths)

    def test_format_is_hash_two_spaces_path(self) -> None:
        for line in self._sums():
            digest, path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            self.assertTrue(all(c in "0123456789abcdef" for c in digest))


class ArtifactIndexTests(_RepoCase):
    def test_count_matches_and_fields_present(self) -> None:
        index = self._index()
        self.assertEqual(index["artifact_count"], len(index["artifacts"]))
        self.assertEqual(index["kind"], "local_validation_artifacts_index")
        self.assertEqual(index["output_root"], ".arkheionx/out/local-validation")
        for art in index["artifacts"]:
            for key in ("artifact_id", "kind", "relative_path", "checksum_sha256", "size_bytes"):
                self.assertTrue(art[key] not in ("", None), key)
            self.assertIs(art["exists"], True)
            self.assertGreater(art["size_bytes"], 0)

    def test_manual_review_and_not_ready(self) -> None:
        index = self._index()
        self.assertIs(index["manual_review_required"], True)
        self.assertIs(index["ready_for_submission"], False)

    def test_summary_links_run_test_trace(self) -> None:
        entry = next(a for a in self._index()["artifacts"] if a["kind"] == "local_validation_summary")
        self.assertIn(self.build.run.run_id, entry["linked_ids"])
        self.assertTrue(any(i.startswith("local-test-result:") for i in entry["linked_ids"]))
        self.assertTrue(any(i.startswith("local-trace-receipt:") for i in entry["linked_ids"]))

    def test_result_links_explicit_only(self) -> None:
        results = [a for a in self._index()["artifacts"] if a["kind"] == "local_test_result"]
        linked = next(a for a in results if a["linked_ids"])
        self.assertIn("function:dep", linked["linked_ids"])

    def test_artifact_ids_deterministic(self) -> None:
        again = lv.write_local_validation_artifacts(self.build, repo_path=self.repo)
        self.assertEqual(self.write.artifact_ids, again.artifact_ids)


class CleanModeTests(_RepoCase):
    def test_clean_removes_stale_under_root(self) -> None:
        stale = self.root / "results" / "stale.json"
        stale.write_text("{}", encoding="utf-8")
        lv.write_local_validation_artifacts(self.build, repo_path=self.repo, clean=True)
        self.assertFalse(stale.exists())

    def test_clean_does_not_delete_outside_output_root(self) -> None:
        keep = self.repo / "keep.txt"
        keep.write_text("keep", encoding="utf-8")
        lv.write_local_validation_artifacts(self.build, repo_path=self.repo, clean=True)
        self.assertTrue(keep.exists())

    def test_clean_false_preserves_unrelated_file(self) -> None:
        extra = self.root / "extra.json"
        extra.write_text("{}", encoding="utf-8")
        lv.write_local_validation_artifacts(self.build, repo_path=self.repo, clean=False)
        self.assertTrue(extra.exists())


class SafetyContentTests(_RepoCase):
    def test_no_overclaim_tokens_in_generated_content(self) -> None:
        blob = "".join(p.read_text(encoding="utf-8") for p in self.root.rglob("*.json"))
        self.assertNotIn("HUMAN_REVIEWED", blob)
        self.assertNotIn('"ready_for_submission": true', blob)
        lower = blob.lower()
        for token in ("private key", "seed phrase", "mnemonic", "fork-url", "http://", "https://"):
            self.assertNotIn(token, lower)

    def test_write_result_json_serializable(self) -> None:
        json.dumps(lv.local_validation_write_result_to_dict(self.write))


class ExportAndImportTests(unittest.TestCase):
    def test_package_exports_writer_symbols(self) -> None:
        for name in ("LocalValidationWriteResult", "write_local_validation_artifacts",
                     "local_validation_write_result_to_dict", "default_local_validation_output_root",
                     "ensure_safe_output_root", "safe_relative_to_repo", "json_dump_deterministic",
                     "build_local_validation_artifact_index"):
            self.assertTrue(hasattr(lv, name), name)

    def test_import_has_no_filesystem_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                import importlib

                importlib.reload(writer)
                entries = list(Path(tmp).iterdir())
            finally:
                os.chdir(cwd)
            self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
