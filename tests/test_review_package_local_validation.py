"""Tests for review-package integration of local-validation artifacts (v3.7)."""
from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from arkheionx import local_validation as lv
from arkheionx.review_package import builder, collector, validate
from arkheionx.review_package.checksums import checksum_manifest_artifacts
from arkheionx.review_package.manifest import build_review_package_manifest

_FIXTURES = Path(__file__).parent / "fixtures" / "local_validation" / "foundry"
_MODEL = {
    "protocol_id": "p",
    "contracts": [{"contract_id": "c", "name": "LendingVault", "aliases": {"contract_name": "LendingVault"}}],
    "functions": [{"function_id": "function:dep", "contract_id": "c", "signature": "deposit(uint256)",
                   "display_name": "LendingVault.deposit", "aliases": {}}],
    "value_paths": [{"value_path_id": "value-path:vp1", "entry_function_id": "function:dep", "exit_function_id": ""}],
    "assumptions": [{"assumption_id": "assumption:a1", "linked_function_ids": ["function:dep"]}],
    "test_gaps": [{"test_gap_id": "test-gap:g1", "linked_function_id": "function:dep"}],
}
_LV_KINDS = {"local_validation_summary", "local_validation_run", "local_test_result",
             "local_trace_receipt", "local_validation_artifacts_index", "local_validation_checksums"}


def _write_review_map(repo: Path) -> None:
    (repo / ".arkheionx" / "out" / "review-map").mkdir(parents=True, exist_ok=True)
    (repo / ".arkheionx" / "out" / "review-map" / "review-map.json").write_text(
        json.dumps({"schema_version": "1.0.0"}), encoding="utf-8")


def _write_local_validation(repo: Path, *, linked: bool = True, trace: bool = True) -> None:
    parsed = lv.parse_foundry_output((_FIXTURES / "forge-test-json-mixed.json").read_text(encoding="utf-8"))
    if linked:
        meta = {"trace": {"call_count": 1}} if trace else {}
        parsed.test_results.append(lv.LocalTestResult(
            test_name="deposit()", contract_name="LendingVault", function_name="deposit",
            status=lv.TEST_PASSED, metadata=meta))
    build = lv.build_local_validation_from_parsed(
        parsed, repo_fingerprint=lv.repo_fingerprint(str(repo)), protocol_model=_MODEL)
    lv.write_local_validation_artifacts(build, repo_path=str(repo))


def _manifest(repo: Path):
    return checksum_manifest_artifacts(build_review_package_manifest(str(repo)), str(repo))


def _validate(repo: Path, model=_MODEL):
    return validate.validate_review_package_manifest(_manifest(repo), str(repo), protocol_model=model)


class _RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _write_review_map(self.repo)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _lv_summary(self) -> Path:
        return self.repo / ".arkheionx" / "out" / "local-validation" / "summary.json"


class CollectorTests(_RepoCase):
    def test_missing_local_validation_folder_ignored(self) -> None:
        kinds = {a.kind for a in collector.collect_review_package_artifacts(str(self.repo))}
        self.assertFalse(kinds & _LV_KINDS)

    def test_discovers_and_classifies_all_kinds(self) -> None:
        _write_local_validation(self.repo)
        kinds = {a.kind for a in collector.collect_review_package_artifacts(str(self.repo))}
        self.assertTrue(_LV_KINDS <= kinds, _LV_KINDS - kinds)

    def test_local_validation_artifacts_are_optional(self) -> None:
        _write_local_validation(self.repo)
        arts = [a for a in collector.collect_review_package_artifacts(str(self.repo)) if a.kind.startswith("local_")]
        self.assertTrue(arts)
        self.assertTrue(all(not a.required for a in arts))

    def test_required_kinds_unchanged(self) -> None:
        self.assertEqual(collector._REQUIRED_KINDS, {"review_map", "evidence_links", "artifacts_index"})

    def test_paths_repo_relative_no_backslash(self) -> None:
        _write_local_validation(self.repo)
        for a in collector.collect_review_package_artifacts(str(self.repo)):
            self.assertFalse(a.relative_path.startswith("/"))
            self.assertNotIn("\\", a.relative_path)


class ManifestTests(_RepoCase):
    def test_manifest_includes_local_validation(self) -> None:
        _write_local_validation(self.repo)
        man = build_review_package_manifest(str(self.repo))
        self.assertTrue(_LV_KINDS <= {a.kind for a in man.included_artifacts})
        self.assertIs(man.manual_review_required, True)
        self.assertIs(man.ready_for_submission, False)

    def test_package_id_changes_with_local_validation(self) -> None:
        without = build_review_package_manifest(str(self.repo)).package_id
        _write_local_validation(self.repo)
        self.assertNotEqual(without, build_review_package_manifest(str(self.repo)).package_id)


class ValidationTests(_RepoCase):
    def test_passes_when_local_validation_absent(self) -> None:
        res = _validate(self.repo)
        self.assertFalse([e for e in res.errors if "local" in e.lower()])

    def test_valid_local_validation_no_errors(self) -> None:
        _write_local_validation(self.repo)
        res = _validate(self.repo)
        self.assertFalse([e for e in res.errors if "local" in e.lower()], res.errors)
        self.assertFalse(res.safety_failures)

    def _tamper_summary(self, transform) -> None:
        _write_local_validation(self.repo)
        path = self._lv_summary()
        path.write_text(transform(path.read_text(encoding="utf-8")), encoding="utf-8")

    def test_malformed_json_errors(self) -> None:
        self._tamper_summary(lambda _t: "{not valid json")
        res = _validate(self.repo)
        self.assertTrue(any("malformed" in e.lower() for e in res.errors), res.errors)

    def test_checksum_mismatch_errors(self) -> None:
        _write_local_validation(self.repo)
        man = _manifest(self.repo)  # checksums computed from clean files
        self._lv_summary().write_text(self._lv_summary().read_text() + "\n", encoding="utf-8")  # change after checksum
        res = validate.validate_review_package_manifest(man, str(self.repo))
        self.assertTrue(res.checksum_mismatches or any("checksum" in e.lower() for e in res.errors))

    def _inject(self, snippet: str):
        return lambda text: text.rstrip()[:-1] + ', "x": ' + json.dumps(snippet) + "}"

    def test_overclaim_markers_error(self) -> None:
        for snippet in ("Final severity: High", "audit passed", "confirmed vulnerability",
                        "guaranteed bounty payout"):
            with self.subTest(snippet=snippet):
                self._tamper_summary(self._inject(snippet))
                res = _validate(self.repo)
                self.assertTrue(res.safety_failures, snippet)
                self.assertEqual(res.status, "PACKAGE_INVALID")

    def test_human_reviewed_errors(self) -> None:
        self._tamper_summary(self._inject("status HUMAN_REVIEWED"))
        res = _validate(self.repo)
        self.assertTrue(res.safety_failures)

    def test_ready_for_submission_true_errors(self) -> None:
        self._tamper_summary(lambda t: t.replace('"ready_for_submission": false', '"ready_for_submission": true'))
        res = _validate(self.repo)
        self.assertTrue(res.safety_failures)
        self.assertEqual(res.status, "PACKAGE_INVALID")

    def test_absolute_path_in_artifact_path_errors(self) -> None:
        # Path safety is enforced generically; an absolute artifact path is an error.
        _write_local_validation(self.repo)
        man = _manifest(self.repo)
        for art in man.included_artifacts:
            if art.kind == "local_validation_summary":
                art.path = "/etc/passwd"
        res = validate.validate_review_package_manifest(man, str(self.repo))
        self.assertTrue(any("absolute" in e.lower() for e in res.errors), res.errors)


class CrossrefTests(_RepoCase):
    def test_exact_linked_ids_resolve(self) -> None:
        _write_local_validation(self.repo)
        res = _validate(self.repo)
        crossref = [c for c in res.checks if c["name"].startswith("crossref.")]
        resolved = [c for c in crossref if c["status"] == "PASS" and "function:dep" in c["message"]]
        self.assertTrue(resolved, [c["message"] for c in crossref])
        self.assertTrue(any("value-path:vp1" in c["message"] and c["status"] == "PASS" for c in crossref))

    def test_unresolved_link_warns_not_errors(self) -> None:
        _write_local_validation(self.repo)
        empty_model = {"protocol_id": "p", "contracts": [], "functions": [],
                       "value_paths": [], "assumptions": [], "test_gaps": []}
        res = _validate(self.repo, model=empty_model)
        unresolved = [c for c in res.checks if c["name"].startswith("crossref.") and c["status"] == "WARN"]
        self.assertTrue(unresolved)
        self.assertFalse([e for e in res.errors if "crossref" in e.lower()])

    def test_no_substring_or_fuzzy_match(self) -> None:
        _write_local_validation(self.repo)
        near = {"protocol_id": "p", "contracts": [],
                "functions": [{"function_id": "function:deposi", "contract_id": "c",
                               "signature": "deposi()", "display_name": "X.deposi", "aliases": {}}],
                "value_paths": [], "assumptions": [], "test_gaps": []}
        res = _validate(self.repo, model=near)
        self.assertTrue(any(c["name"] == "crossref.function" and c["status"] == "WARN"
                            and "function:dep" in c["message"] for c in res.checks))

    def test_missing_protocol_model_warns(self) -> None:
        _write_local_validation(self.repo)
        res = _validate(self.repo, model=None)
        self.assertFalse([e for e in res.errors if "local" in e.lower()])


class ExportTests(_RepoCase):
    def test_export_includes_local_validation_and_is_deterministic(self) -> None:
        _write_local_validation(self.repo)
        first = builder.build_review_package(str(self.repo), export_format="zip")
        self.assertTrue(first.export_written, first.export_status)
        names = zipfile.ZipFile(self.repo / first.export_path).namelist()
        self.assertTrue(any(n.endswith("local-validation/summary.json") for n in names))
        self.assertTrue(any(n.endswith("local-validation/checksums/SHA256SUMS") for n in names))
        for n in names:
            self.assertFalse(n.startswith("/"))
            self.assertNotIn("\\", n)
        second = builder.build_review_package(str(self.repo), export_format="zip")
        self.assertEqual(first.export_checksum_sha256, second.export_checksum_sha256)


class BuilderCountTests(_RepoCase):
    def test_artifact_count_increases_with_local_validation(self) -> None:
        before = builder.build_review_package(str(self.repo), no_write=True).artifact_count
        _write_local_validation(self.repo)
        after = builder.build_review_package(str(self.repo), no_write=True).artifact_count
        self.assertGreater(after, before)

    def test_review_package_still_works_without_local_validation(self) -> None:
        result = builder.build_review_package(str(self.repo), no_write=True)
        self.assertIs(result.manual_review_required, True)
        self.assertIs(result.ready_for_submission, False)


if __name__ == "__main__":
    unittest.main()
