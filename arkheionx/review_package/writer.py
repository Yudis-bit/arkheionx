"""Deterministic, safe writers for the review package folder (v3.6, additive).

Writes a local review-package folder under ``.arkheionx/out/review-package/``:
``manifest.json``, ``validation.json``, ``README.md``, ``limitations.md``,
copied artifacts under ``artifacts/``, and ``checksums/SHA256SUMS``. All writes
stay inside the package root; artifact copies are refused for absolute,
traversal, or repo-escaping (including symlink-escaping) sources. No archive is
written and no absolute path is recorded in package files.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from .checksums import normalize_checksum_path
from .manifest import manifest_to_dict
from .model import ReviewPackageManifest, ReviewPackageValidationResult, to_dict


def assert_safe_package_relative_path(relative_path: str) -> None:
    value = str(relative_path or "")
    if not value.strip():
        raise ValueError("empty package-relative path")
    if value.startswith("/") or (len(value) > 1 and value[1] == ":"):
        raise ValueError("absolute package-relative path")
    if "\\" in value:
        raise ValueError("backslash in package-relative path")
    if ".." in value.split("/"):
        raise ValueError("path traversal in package-relative path")


def ensure_package_root(package_root: str | Path) -> Path:
    root = Path(str(package_root))
    root.mkdir(parents=True, exist_ok=True)
    return root


def safe_write_json(path: str | Path, data: object) -> None:
    target = Path(str(path))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def safe_write_text(path: str | Path, text: str) -> None:
    target = Path(str(path))
    target.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    target.write_text(text, encoding="utf-8")


def _within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except (ValueError, OSError):
        return False


def copy_package_artifact(artifact, repo_path: str | Path, package_root: str | Path) -> str:
    assert_safe_package_relative_path(artifact.relative_path)
    repo = Path(str(repo_path))
    source = repo / artifact.path
    if not _within(source, repo) or not source.is_file():
        raise ValueError(f"unsafe or missing artifact source: {artifact.relative_path}")
    dest = Path(str(package_root)) / "artifacts" / artifact.relative_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    return f"artifacts/{artifact.relative_path}"


def copy_package_artifacts(
    manifest: ReviewPackageManifest, repo_path: str | Path, package_root: str | Path,
) -> tuple[list[str], list[str]]:
    copied: list[str] = []
    warnings: list[str] = []
    for artifact in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        try:
            copied.append(copy_package_artifact(artifact, repo_path, package_root))
        except (ValueError, OSError):
            warnings.append(f"skipped artifact (missing or unsafe): {artifact.relative_path}")
    return copied, warnings


def write_manifest(manifest: ReviewPackageManifest, package_root: str | Path) -> Path:
    target = Path(str(package_root)) / "manifest.json"
    safe_write_json(target, manifest_to_dict(manifest))
    return target


def write_validation(validation: ReviewPackageValidationResult, package_root: str | Path) -> Path:
    target = Path(str(package_root)) / "validation.json"
    safe_write_json(target, to_dict(validation))
    return target


def write_checksums(manifest: ReviewPackageManifest, package_root: str | Path) -> Path:
    target = Path(str(package_root)) / "checksums" / "SHA256SUMS"
    lines = [f"{digest}  {normalize_checksum_path(path)}" for path, digest in sorted(manifest.checksums.items())]
    safe_write_text(target, "\n".join(lines))
    return target
