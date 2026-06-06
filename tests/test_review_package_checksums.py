"""Tests for review package checksum helpers (v3.6, internal)."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_package import checksums as ck, manifest as mf


def _seed(root: Path, names: list[str]) -> None:
    for rel in names:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}", encoding="utf-8")


_BASE = ["review-map/review-map.json", "review-map/evidence-links.json", "artifacts-index.json"]


class ChecksumTests(unittest.TestCase):
    def test_sha256_bytes_deterministic(self) -> None:
        self.assertEqual(ck.sha256_bytes(b"abc"), hashlib.sha256(b"abc").hexdigest())
        self.assertEqual(ck.sha256_bytes(b"abc"), ck.sha256_bytes(b"abc"))

    def test_sha256_file_known_digest_and_chunking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "x.bin"
            f.write_bytes(b"hello world" * 1000)
            expected = hashlib.sha256(b"hello world" * 1000).hexdigest()
            self.assertEqual(ck.sha256_file(f), expected)
            self.assertEqual(ck.sha256_file(f, chunk_size=7), expected)

    def test_sha256_file_missing_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                ck.sha256_file(Path(tmp) / "missing.json")

    def test_sha256_file_chunk_size_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "x"
            f.write_bytes(b"x")
            with self.assertRaises(ValueError):
                ck.sha256_file(f, chunk_size=0)

    def test_normalize_checksum_path_posix(self) -> None:
        self.assertEqual(ck.normalize_checksum_path("a\\b\\c.json"), "a/b/c.json")

    def test_is_probable_checksum(self) -> None:
        self.assertTrue(ck.is_probable_checksum("a" * 64))
        self.assertFalse(ck.is_probable_checksum("a" * 63))
        self.assertFalse(ck.is_probable_checksum("Z" * 64))
        self.assertFalse(ck.is_probable_checksum("not-a-checksum"))

    def test_build_checksum_map_relative_keys_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE)
            man = mf.build_review_package_manifest(tmp)
            first = ck.build_checksum_map(man.included_artifacts, tmp)
            second = ck.build_checksum_map(man.included_artifacts, tmp)
            self.assertEqual(first, second)
            self.assertTrue(first)
            for key, value in first.items():
                self.assertFalse(key.startswith("/"))
                self.assertNotIn("\\", key)
                self.assertTrue(ck.is_probable_checksum(value))

    def test_checksum_manifest_artifacts_no_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE)
            man = mf.build_review_package_manifest(tmp)
            before = json.dumps(mf.manifest_to_dict(man))
            enriched = ck.checksum_manifest_artifacts(man, tmp)
            self.assertEqual(json.dumps(mf.manifest_to_dict(man)), before)
            self.assertTrue(enriched.checksums)
            self.assertTrue(all(a.checksum_sha256 for a in enriched.included_artifacts))

    def test_checksum_artifact_matches_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp) / ".arkheionx" / "out", _BASE)
            man = mf.build_review_package_manifest(tmp)
            art = man.included_artifacts[0]
            self.assertEqual(ck.checksum_artifact(art, tmp),
                             ck.sha256_file(Path(tmp) / art.path))

    def test_checksum_helpers_write_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / ".arkheionx" / "out"
            _seed(out, _BASE)
            before = sorted(p.relative_to(tmp).as_posix() for p in Path(tmp).rglob("*"))
            man = mf.build_review_package_manifest(tmp)
            ck.checksum_manifest_artifacts(man, tmp)
            ck.build_checksum_map(man.included_artifacts, tmp)
            after = sorted(p.relative_to(tmp).as_posix() for p in Path(tmp).rglob("*"))
            self.assertEqual(before, after)
            self.assertFalse((out / "review-package").exists())
            self.assertFalse((out / "checksums").exists())


if __name__ == "__main__":
    unittest.main()
