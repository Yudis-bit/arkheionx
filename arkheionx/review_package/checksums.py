"""SHA-256 checksum helpers for the review package layer (v3.6, additive).

Deterministic, local, standard-library-only checksums for review-package
artifacts. Files are read in chunks; digests are lowercase hex. These helpers
write nothing to disk and create no checksum files -- they only compute values
that later validation and export steps use. Higher-level callers decide how to
treat missing files; the low-level file digest raises ``FileNotFoundError``.
"""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path

from .ids import normalize_package_path
from .model import ReviewPackageArtifact, ReviewPackageManifest

_DEFAULT_CHUNK = 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path, chunk_size: int = _DEFAULT_CHUNK) -> str:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_checksum_path(path: str | Path) -> str:
    return normalize_package_path(path)


def is_probable_checksum(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def checksum_artifact_file(path: str | Path) -> str:
    return sha256_file(path)


def checksum_artifact(artifact: ReviewPackageArtifact, repo_path: str | Path) -> str:
    return sha256_file(Path(str(repo_path)) / artifact.path)


def build_checksum_map(artifacts: list[ReviewPackageArtifact], repo_path: str | Path) -> dict[str, str]:
    """Return a deterministic {relative_path: sha256} map for existing files.

    Missing files are skipped (not an error here); validation reports them.
    Keys are relative POSIX package paths; artifacts are not mutated.
    """

    checksums: dict[str, str] = {}
    for artifact in sorted(artifacts, key=lambda a: (a.relative_path, a.path, a.artifact_id)):
        key = normalize_checksum_path(artifact.relative_path or artifact.path)
        target = Path(str(repo_path)) / artifact.path
        if key and target.is_file():
            checksums[key] = sha256_file(target)
    return checksums


def checksum_manifest_artifacts(manifest: ReviewPackageManifest, repo_path: str | Path) -> ReviewPackageManifest:
    """Return a new manifest with ``checksums`` and per-artifact digests filled.

    The input manifest is not mutated (a deep copy is returned). No file is
    written; the checksum map lives only in the returned in-memory object.
    """

    enriched = copy.deepcopy(manifest)
    enriched.checksums = build_checksum_map(enriched.included_artifacts, repo_path)
    for artifact in enriched.included_artifacts:
        target = Path(str(repo_path)) / artifact.path
        if target.is_file():
            artifact.checksum_sha256 = sha256_file(target)
    return enriched
