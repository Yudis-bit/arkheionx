"""Deterministic ID and path utilities for the internal review package layer.

These helpers mint stable, prefix-tagged identifiers for review-package
workspaces, packages, artifacts, validations, and exports. They follow the same
discipline as ``arkheionx.intelligence.ids``: a SHA-256 digest over a canonical
JSON seed (sorted keys, compact separators), a short hex suffix, and a
human-readable prefix. IDs never use timestamps, randomness, or process
``hash()``; identical inputs always produce the same ID across runs.

This module is internal infrastructure. It performs no filesystem, network, git,
or RPC access, does not require any path to exist, and reads or stores no
secrets.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePath, PurePosixPath

_HASH_LEN = 12


def _json_default(value: object) -> str:
    """Convert Path-like seeds to POSIX text; reject anything else clearly."""

    if isinstance(value, PurePath):
        return value.as_posix()
    raise TypeError(f"unsupported review-package id seed type: {type(value).__name__}")


def _canonical(seed: object) -> str:
    """Return canonical JSON for a seed (sorted keys, compact separators)."""

    return json.dumps(seed, sort_keys=True, separators=(",", ":"), default=_json_default)


def _digest(seed: object, length: int = _HASH_LEN) -> str:
    """Return a stable short SHA-256 hex digest of a canonical JSON seed."""

    return hashlib.sha256(_canonical(seed).encode("utf-8")).hexdigest()[:length]


def normalize_package_path(path: str | Path) -> str:
    """Return a POSIX-style, separator-collapsed path. Existence is not required."""

    raw = str(path or "").replace("\\", "/")
    if not raw.strip():
        return ""
    return PurePosixPath(raw).as_posix()


def package_slug(value: str, max_length: int = 80) -> str:
    """Lowercase, filename-safe dash slug; returns ``"unknown"`` when empty."""

    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    if max_length and max_length > 0:
        slug = slug[:max_length].strip("-")
    return slug or "unknown"


def repo_fingerprint(repo_path: str | Path) -> str:
    """Return a deterministic, secret-free fingerprint of a repo path.

    Uses only the normalized path text; performs no git, network, or filesystem
    access and resolves no remote.
    """

    normalized = normalize_package_path(repo_path)
    if not normalized:
        raise ValueError("repo_path is required for repo_fingerprint")
    return _digest(["repo", normalized])


def review_workspace_id(repo_path: str | Path, seed: object | None = None) -> str:
    normalized = normalize_package_path(repo_path)
    if not normalized:
        raise ValueError("repo_path is required for review_workspace_id")
    repo_hash = repo_fingerprint(repo_path)
    return f"workspace:{repo_hash}:{_digest(['workspace', repo_hash, seed])}"


def review_package_id(
    protocol_model_id: str = "",
    artifact_ids: list[str] | None = None,
    repo_fingerprint: str = "",
    seed: object | None = None,
) -> str:
    sorted_ids = sorted(str(a) for a in (artifact_ids or []))
    package_hash = _digest(
        {
            "protocol_model_id": str(protocol_model_id or ""),
            "artifact_ids": sorted_ids,
            "repo_fingerprint": str(repo_fingerprint or ""),
            "seed": seed,
        }
    )
    return f"review-package:{package_hash}"


def package_artifact_id(kind: str, relative_path: str | Path, seed: object | None = None) -> str:
    if not str(kind or "").strip():
        raise ValueError("kind is required for package_artifact_id")
    normalized = normalize_package_path(relative_path)
    if not normalized:
        raise ValueError("relative_path is required for package_artifact_id")
    kind_slug = package_slug(kind)
    return f"package-artifact:{kind_slug}:{_digest(['package-artifact', kind_slug, normalized, seed])}"


def package_validation_id(package_id: str, seed: object | None = None) -> str:
    if not str(package_id or "").strip():
        raise ValueError("package_id is required for package_validation_id")
    package_hash = _digest(["package", str(package_id)])
    return f"package-validation:{package_hash}:{_digest(['package-validation', str(package_id), seed])}"


def package_export_id(package_id: str, export_format: str, seed: object | None = None) -> str:
    if not str(package_id or "").strip():
        raise ValueError("package_id is required for package_export_id")
    if not str(export_format or "").strip():
        raise ValueError("export_format is required for package_export_id")
    package_hash = _digest(["package", str(package_id)])
    fmt = package_slug(export_format)
    return f"package-export:{package_hash}:{fmt}:{_digest(['package-export', str(package_id), fmt, seed])}"
