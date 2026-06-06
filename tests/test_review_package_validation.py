"""Tests for strict review package validation (v3.6, internal)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_package import checksums as ck, manifest as mf, validate as v
from arkheionx.review_package import model as M


def _seed(root: Path, names: list[str], secret: bool = False) -> None:
    for rel in names:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}", encoding="utf-8")
    if secret:
        (root / "review-map/review-map.json").write_text('{"key": "0x' + "a" * 64 + '"}', encoding="utf-8")


_ALL = ["review-map/review-map.json", "review-map/evidence-links.json", "artifacts-index.json"]


def _enriched(tmp: str):
    return ck.checksum_manifest_artifacts(mf.build_review_package_manifest(tmp), tmp)


def _manifest(arts, **kw):
    base = dict(package_id="review-package:test", required_artifacts=["review_map"],
                safety_boundary=dict(M.DEFAULT_REVIEW_PACKAGE_SAFETY_BOUNDARY))
    base.update(kw)
    return M.ReviewPackageManifest(included_artifacts=arts, **base)


class StatusTests(unittest.TestCase):
    def test_empty_manifest_is_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = v.validate_review_package_manifest(mf.build_review_package_manifest(tmp), tmp)
            self.assertEqual(res.status, M.PACKAGE_DRAFT)

    def test_missing_required_is_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", ["review-map/review-map.json"])
            res = v.validate_review_package_manifest(_enriched(tmp), tmp)
            self.assertEqual(res.status, M.PACKAGE_PARTIAL)
            self.assertIn("evidence_links", res.missing_required_artifacts)
            self.assertIn("artifacts_index", res.missing_required_artifacts)

    def test_full_enriched_is_ready_for_human_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _ALL)
            res = v.validate_review_package_manifest(_enriched(tmp), tmp)
            self.assertEqual(res.status, M.PACKAGE_READY_FOR_HUMAN_REVIEW)
            self.assertTrue(res.ready_for_human_review)
            self.assertFalse(res.ready_for_submission)
            self.assertTrue(res.manual_review_required)

    def test_bare_manifest_strict_missing_checksum_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _ALL)
            res = v.validate_review_package_manifest(mf.build_review_package_manifest(tmp), tmp)
            self.assertEqual(res.status, M.PACKAGE_INVALID)


class EntryAndPathTests(unittest.TestCase):
    def test_exists_true_but_file_missing_error(self) -> None:
        art = M.ReviewPackageArtifact(artifact_id="a", kind="review_map",
                                      path=".arkheionx/out/review-map/review-map.json",
                                      relative_path="review-map/review-map.json", exists=True)
        res = v.validate_review_package_manifest(_manifest([art]), "/tmp/does-not-exist-xyz")
        self.assertEqual(res.status, M.PACKAGE_INVALID)
        self.assertTrue(any("missing" in e for e in res.errors))

    def test_exists_false_but_file_present_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".arkheionx" / "out" / "review-map").mkdir(parents=True)
            (Path(tmp) / ".arkheionx" / "out" / "review-map" / "review-map.json").write_text("{}")
            art = M.ReviewPackageArtifact(artifact_id="a", kind="review_map",
                                          path=".arkheionx/out/review-map/review-map.json",
                                          relative_path="review-map/review-map.json", exists=False)
            res = v.validate_review_package_manifest(_manifest([art]), tmp)
            self.assertTrue(any("file present but artifact marked missing" in w for w in res.warnings))

    def test_absolute_path_error_no_leak(self) -> None:
        art = M.ReviewPackageArtifact(artifact_id="a", kind="review_map", path="/etc/secret_xyz",
                                      relative_path="review-map/review-map.json", exists=False)
        res = v.validate_review_package_manifest(_manifest([art]), "/tmp")
        self.assertEqual(res.status, M.PACKAGE_INVALID)
        self.assertTrue(all("/etc/secret_xyz" not in e for e in res.errors))

    def test_absolute_relative_path_error(self) -> None:
        art = M.ReviewPackageArtifact(artifact_id="a", kind="review_map",
                                      path=".arkheionx/out/x.json", relative_path="/abs/x.json", exists=False)
        res = v.validate_review_package_manifest(_manifest([art]), "/tmp")
        self.assertTrue(any("relative_path has absolute path" in e for e in res.errors))

    def test_path_traversal_error(self) -> None:
        art = M.ReviewPackageArtifact(artifact_id="a", kind="review_map",
                                      path=".arkheionx/out/../../escape.json",
                                      relative_path="review-map/x.json", exists=False)
        res = v.validate_review_package_manifest(_manifest([art]), "/tmp")
        self.assertTrue(any("traversal" in e for e in res.errors))

    def test_backslash_path_error(self) -> None:
        art = M.ReviewPackageArtifact(artifact_id="a", kind="review_map",
                                      path=".arkheionx\\out\\x.json", relative_path="review-map/x.json", exists=False)
        res = v.validate_review_package_manifest(_manifest([art]), "/tmp")
        self.assertTrue(any("backslash" in e for e in res.errors))

    def test_size_mismatch_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / ".arkheionx" / "out" / "review-map"
            out.mkdir(parents=True)
            (out / "review-map.json").write_text("{}")
            art = M.ReviewPackageArtifact(artifact_id="a", kind="review_map",
                                          path=".arkheionx/out/review-map/review-map.json",
                                          relative_path="review-map/review-map.json", exists=True, size_bytes=99999)
            res = v.validate_review_package_manifest(_manifest([art]), tmp)
            self.assertTrue(any("size" in w for w in res.warnings))


class ChecksumTests(unittest.TestCase):
    def _artifact(self, tmp, checksum=""):
        out = Path(tmp) / ".arkheionx" / "out" / "review-map"
        out.mkdir(parents=True, exist_ok=True)
        (out / "review-map.json").write_text("{}")
        return M.ReviewPackageArtifact(artifact_id="a", kind="review_map",
                                       path=".arkheionx/out/review-map/review-map.json",
                                       relative_path="review-map/review-map.json", exists=True,
                                       checksum_sha256=checksum)

    def test_missing_checksum_warning_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            checks = v.validate_checksums(_manifest([self._artifact(tmp)]), tmp)
            self.assertTrue(any(c["name"] == "checksum_present" and c["status"] == "WARN" for c in checks))

    def test_malformed_checksum_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = v.validate_review_package_manifest(_manifest([self._artifact(tmp, "bad")]), tmp)
            self.assertTrue(any("malformed" in e for e in res.errors))

    def test_checksum_mismatch_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = v.validate_review_package_manifest(_manifest([self._artifact(tmp, "a" * 64)]), tmp)
            self.assertTrue(res.checksum_mismatches)
            self.assertEqual(res.status, M.PACKAGE_INVALID)

    def test_checksum_match_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            art = self._artifact(tmp)
            art.checksum_sha256 = ck.sha256_file(Path(tmp) / art.path)
            res = v.validate_review_package_manifest(_manifest([art]), tmp)
            self.assertFalse(res.checksum_mismatches)


class SafetyTests(unittest.TestCase):
    def test_manual_review_required_false_fails(self) -> None:
        res = v.validate_review_package_manifest(_manifest([], manual_review_required=False), "/tmp")
        self.assertEqual(res.status, M.PACKAGE_INVALID)
        self.assertTrue(res.safety_failures)

    def test_ready_for_submission_true_fails(self) -> None:
        res = v.validate_review_package_manifest(_manifest([], ready_for_submission=True), "/tmp")
        self.assertTrue(res.safety_failures)

    def test_safety_flag_false_fails(self) -> None:
        boundary = dict(M.DEFAULT_REVIEW_PACKAGE_SAFETY_BOUNDARY, no_rpc=False)
        res = v.validate_review_package_manifest(_manifest([], safety_boundary=boundary), "/tmp")
        self.assertTrue(any("no_rpc" in f for f in res.safety_failures))

    def test_human_reviewed_in_field_fails(self) -> None:
        res = v.validate_review_package_manifest(_manifest([], metadata={"state": "HUMAN_REVIEWED"}), "/tmp")
        self.assertTrue(any("human-reviewed" in f for f in res.safety_failures))

    def test_no_overclaim_terms_accepted(self) -> None:
        # A clean manifest passes safety; result never asserts these claims.
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _ALL)
            blob = json.dumps(__import__("arkheionx.review_package", fromlist=["to_dict"]).to_dict(
                v.validate_review_package_manifest(_enriched(tmp), tmp)))
            for term in ("audit passed", "confirmed vulnerability", "final severity", "bounty eligible"):
                self.assertNotIn(term, blob.lower())


class SecretScanTests(unittest.TestCase):
    def test_private_key_class_only_no_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _ALL, secret=True)
            res = v.validate_review_package_manifest(_enriched(tmp), tmp)
            blob = json.dumps(__import__("arkheionx.review_package", fromlist=["to_dict"]).to_dict(res))
            self.assertIn("private_key_like", blob)
            self.assertNotIn("a" * 64, blob)
            self.assertEqual(res.status, M.PACKAGE_INVALID)

    def test_bearer_token_class_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / ".arkheionx" / "out"
            out.mkdir(parents=True)
            (out / "artifacts-index.json").write_text('{"h": "Bearer abcdef0123456789xyz"}')
            classes = v.scan_artifact_for_secret_patterns(out / "artifacts-index.json")
            self.assertIn("bearer_token_like", classes)
            self.assertNotIn("abcdef0123456789xyz", " ".join(classes))

    def test_binary_file_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "blob.json"
            f.write_bytes(b"\x00\x01\x02 0x" + b"a" * 64)
            self.assertEqual(v.scan_artifact_for_secret_patterns(f), [])


class ResultIntegrityTests(unittest.TestCase):
    def test_deterministic_and_validation_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _ALL)
            man = _enriched(tmp)
            to_dict = __import__("arkheionx.review_package", fromlist=["to_dict"]).to_dict
            r1 = v.validate_review_package_manifest(man, tmp)
            r2 = v.validate_review_package_manifest(man, tmp)
            self.assertEqual(to_dict(r1), to_dict(r2))
            self.assertTrue(r1.validation_id.startswith("package-validation:"))

    def test_does_not_mutate_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _ALL)
            man = _enriched(tmp)
            before = json.dumps(mf.manifest_to_dict(man))
            v.validate_review_package_manifest(man, tmp)
            self.assertEqual(json.dumps(mf.manifest_to_dict(man)), before)

    def test_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / ".arkheionx" / "out"
            _seed(out, _ALL)
            man = _enriched(tmp)
            before = sorted(p.relative_to(tmp).as_posix() for p in Path(tmp).rglob("*"))
            v.validate_review_package_manifest(man, tmp)
            after = sorted(p.relative_to(tmp).as_posix() for p in Path(tmp).rglob("*"))
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
