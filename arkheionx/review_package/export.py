"""Deterministic, local review package export (v3.6, additive, internal-only).

Creates a reproducible ``.zip`` archive of a built review-package folder using
the standard-library ``zipfile`` with fixed entry metadata (1980-01-01, stable
permissions, stable compression) and lexicographically sorted, archive-relative
entries. The archive excludes itself, the ``exports/`` directory, caches, VCS
metadata, and symlink-escaping files, and records no absolute path or secret
value. It is local-only: nothing is transmitted, and the package remains review
guidance requiring manual review, never ready for submission.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

from .checksums import sha256_file
from .collector import to_repo_relative_path
from .ids import package_export_id, package_slug
from .model import ReviewPackageExport

ARCHIVE_ROOT = "arkheionx-review-package"
SUPPORTED_FORMATS = ("zip",)
_REQUIRED_FILES = ("manifest.json", "validation.json", "README.md", "limitations.md")
_ARCHIVE_SUFFIXES = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz"}
_FIXED_DATE = (1980, 1, 1, 0, 0, 0)
_EXPORT_LIMITATIONS = [
    "Local-only export; nothing is published or transmitted.",
    "Not a formal audit and not a vulnerability confirmation.",
    "No final severity and no bounty eligibility.",
    "Manual review is required; not ready for submission.",
]


def default_exports_dir(package_root: str | Path) -> Path:
    return Path(str(package_root)) / "exports"


def default_export_filename(package_id: str, export_format: str = "zip") -> str:
    ext = package_slug(export_format, max_length=8)
    short = package_slug(str(package_id).split(":")[-1] or "package", max_length=16)
    return f"arkheionx-review-package-{short}.{ext}"


def default_export_path(package_root: str | Path, package_id: str, export_format: str = "zip") -> Path:
    return default_exports_dir(package_root) / default_export_filename(package_id, export_format)


def _within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except (ValueError, OSError):
        return False


def is_exportable_package_file(path: str | Path, package_root: str | Path) -> bool:
    target = Path(str(path))
    root = Path(str(package_root))
    if not target.is_file():
        return False
    if not _within(target, root):  # symlink-escaping or outside root
        return False
    try:
        rel = target.relative_to(root)
    except ValueError:
        return False
    parts = rel.parts
    if not parts or parts[0] == "exports":
        return False
    if any(p in ("__pycache__", ".git") for p in parts):
        return False
    name = parts[-1]
    if name == ".DS_Store" or name.endswith((".pyc", "~")):
        return False
    if target.suffix.lower() in _ARCHIVE_SUFFIXES:
        return False
    return True


def iter_export_files(package_root: str | Path) -> list[Path]:
    root = Path(str(package_root))
    if not root.is_dir():
        return []
    files = [p for p in root.rglob("*") if is_exportable_package_file(p, root)]
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def archive_relative_path(path: str | Path, package_root: str | Path, archive_root: str = ARCHIVE_ROOT) -> str:
    rel = Path(str(path)).relative_to(Path(str(package_root))).as_posix()
    if rel.startswith("/") or "\\" in rel or ".." in rel.split("/"):
        raise ValueError(f"unsafe archive-relative path: {rel}")
    return f"{archive_root}/{rel}"


def _fixed_zipinfo(arcname: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(arcname, date_time=_FIXED_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    return info


def _missing_required(package_root: Path) -> list[str]:
    return [name for name in _REQUIRED_FILES if not (package_root / name).is_file()]


def create_review_package_zip(
    package_root: str | Path, export_path: str | Path, *, archive_root: str = ARCHIVE_ROOT
) -> ReviewPackageExport:
    root = Path(str(package_root))
    if not root.is_dir():
        raise ValueError(f"package root does not exist: {root}")
    missing = _missing_required(root)
    if missing:
        raise ValueError(f"missing required package files: {', '.join(missing)}")

    export_abs = Path(str(export_path))
    files = iter_export_files(root)
    entries = sorted((archive_relative_path(p, root, archive_root), p) for p in files)

    export_abs.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(export_abs, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for arcname, source in entries:
            archive.writestr(_fixed_zipinfo(arcname), source.read_bytes())

    package_id = ""
    try:
        package_id = str(json.loads((root / "manifest.json").read_text(encoding="utf-8")).get("package_id", ""))
    except (OSError, ValueError):
        package_id = ""
    included = [arcname for arcname, _ in entries]
    return ReviewPackageExport(
        export_id=package_export_id(package_id or "review-package:unknown", "zip", seed=included),
        package_id=package_id,
        export_path=to_repo_relative_path(export_abs, root),
        format="zip",
        included_files=included,
        manifest_checksum=sha256_file(root / "manifest.json"),
        validation_checksum=sha256_file(root / "validation.json"),
        status="created",
        limitations=list(_EXPORT_LIMITATIONS),
        metadata={
            "size_bytes": export_abs.stat().st_size,
            "export_checksum_sha256": sha256_file(export_abs),
            "file_count": len(included),
            "archive_root": archive_root,
        },
    )


def _blocked(export_format: str, status: str, package_id: str = "") -> ReviewPackageExport:
    return ReviewPackageExport(
        export_id="", package_id=package_id, export_path="", format=export_format,
        status=status, limitations=list(_EXPORT_LIMITATIONS),
    )


def export_review_package(
    repo_path: str | Path,
    *,
    package_root: str | Path | None = None,
    export_format: str = "zip",
    export_output: str | Path | None = None,
    strict: bool = False,
) -> ReviewPackageExport:
    if export_format not in SUPPORTED_FORMATS:
        return _blocked(export_format, "unsupported_format")

    root = Path(str(package_root)) if package_root else Path(str(repo_path)) / ".arkheionx" / "out" / "review-package"
    if not root.is_dir() or _missing_required(root):
        return _blocked(export_format, "blocked")

    package_id = ""
    safety_failures: list = []
    invalid = False
    try:
        validation = json.loads((root / "validation.json").read_text(encoding="utf-8"))
        safety_failures = validation.get("safety_failures", []) or []
        invalid = validation.get("status") == "PACKAGE_INVALID"
        if validation.get("ready_for_submission") is True:
            safety_failures = list(safety_failures) + ["ready_for_submission true"]
    except (OSError, ValueError):
        return _blocked(export_format, "blocked")
    try:
        package_id = str(json.loads((root / "manifest.json").read_text(encoding="utf-8")).get("package_id", ""))
    except (OSError, ValueError):
        package_id = ""

    if safety_failures or (strict and invalid):
        return _blocked(export_format, "blocked", package_id)

    export_path = Path(str(export_output)) if export_output else default_export_path(root, package_id, export_format)
    return create_review_package_zip(root, export_path)


def review_package_export_to_dict(export: ReviewPackageExport) -> dict[str, object]:
    from .model import to_dict

    return to_dict(export)
