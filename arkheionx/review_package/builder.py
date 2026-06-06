"""Review package build orchestration (v3.6, additive, internal-only).

Builds a local review package from existing ``.arkheionx/out/`` artifacts:
collects + checksum-enriches a manifest, validates it, generates reviewer text,
and (unless ``no_write``) writes the package folder. It writes no archive,
changes no metadata, deletes no unrelated files, and records only repo-relative
paths. ``ready_for_submission`` stays false and ``manual_review_required`` stays
true.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .checksums import checksum_manifest_artifacts, sha256_file
from .collector import default_artifacts_root, to_repo_relative_path
from .ids import package_artifact_id
from .intelligence import include_protocol_model_sidecar, write_protocol_model_sidecar
from .manifest import build_review_package_manifest
from .model import ReviewPackageArtifact, ReviewPackageManifest, ReviewPackageValidationResult
from .readme import build_limitations_text, build_reviewer_readme
from .validate import validate_review_package_manifest
from . import writer

COMMAND_NAME = "review-package"


@dataclass
class ReviewPackageBuildResult:
    package_root: str
    manifest_path: str = ""
    validation_path: str = ""
    readme_path: str = ""
    limitations_path: str = ""
    checksums_path: str = ""
    artifact_count: int = 0
    copied_artifacts: list[str] = field(default_factory=list)
    validation_status: str = ""
    manual_review_required: bool = True
    ready_for_submission: bool = False
    written: bool = False
    no_write: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    export_requested: bool = False
    export_format: str = ""
    export_path: str = ""
    export_id: str = ""
    export_status: str = ""
    export_file_count: int = 0
    export_size_bytes: int = 0
    export_checksum_sha256: str = ""
    export_written: bool = False
    protocol_model_requested: bool = False
    protocol_model_included: bool = False
    protocol_model_path: str = ""
    protocol_model_id: str = ""
    crossref_check_count: int = 0
    crossref_warning_count: int = 0
    crossref_error_count: int = 0
    manifest: ReviewPackageManifest | None = None
    validation: ReviewPackageValidationResult | None = None


def build_review_package(
    repo_path: str | Path,
    *,
    output: str | Path | None = None,
    no_write: bool = False,
    strict: bool = False,
    include_unknown: bool = True,
    copy_artifacts: bool = True,
    protocol_model_id: str = "",
    package_name: str = "",
    include_protocol_model: bool = True,
    export_format: str = "",
    export_output: str | Path | None = None,
) -> ReviewPackageBuildResult:
    repo = Path(str(repo_path))
    pkg_abs = Path(str(output)) if output else default_artifacts_root(repo) / "review-package"

    manifest = build_review_package_manifest(repo, protocol_model_id=protocol_model_id, package_name=package_name)
    if not include_unknown:
        manifest.included_artifacts = [a for a in manifest.included_artifacts if a.kind != "unknown"]
    manifest = checksum_manifest_artifacts(manifest, repo)

    model_info: dict = {"protocol_model_id": "", "model_dict": None}
    if include_protocol_model:
        model_info = include_protocol_model_sidecar(repo, pkg_abs, no_write=True)
        if model_info.get("protocol_model_id"):
            manifest.protocol_model_id = str(model_info["protocol_model_id"])
    model_dict = model_info.get("model_dict")
    validation = validate_review_package_manifest(manifest, repo, strict=strict, protocol_model=model_dict)
    crossref_checks = [c for c in validation.checks if str(c.get("name", "")).startswith("crossref")]

    def rel(path: Path) -> str:
        return to_repo_relative_path(path, repo)

    result = ReviewPackageBuildResult(
        package_root=rel(pkg_abs),
        manifest_path=rel(pkg_abs / "manifest.json"),
        validation_path=rel(pkg_abs / "validation.json"),
        readme_path=rel(pkg_abs / "README.md"),
        limitations_path=rel(pkg_abs / "limitations.md"),
        artifact_count=len(manifest.included_artifacts),
        validation_status=validation.status,
        no_write=no_write,
        warnings=list(validation.warnings),
        errors=list(validation.errors),
        protocol_model_requested=include_protocol_model,
        protocol_model_id=str(model_info.get("protocol_model_id", "")),
        crossref_check_count=len(crossref_checks),
        crossref_warning_count=sum(1 for c in crossref_checks if c.get("severity") == "warning"),
        crossref_error_count=sum(1 for c in crossref_checks if c.get("severity") == "error"),
        manifest=manifest,
        validation=validation,
    )
    if manifest.checksums:
        result.checksums_path = rel(pkg_abs / "checksums" / "SHA256SUMS")
    result.export_requested = bool(export_format)
    result.export_format = export_format

    if no_write:
        return result

    writer.ensure_package_root(pkg_abs)
    if copy_artifacts:
        copied, copy_warnings = writer.copy_package_artifacts(manifest, repo, pkg_abs)
        result.copied_artifacts = copied
        result.warnings += copy_warnings
    if model_dict is not None:
        sidecar = write_protocol_model_sidecar(model_dict, pkg_abs)
        sidecar_rel = "intelligence/protocol-model.json"
        manifest.included_artifacts.append(ReviewPackageArtifact(
            artifact_id=package_artifact_id("protocol_model", sidecar_rel),
            kind="protocol_model", path=rel(sidecar), relative_path=sidecar_rel, exists=True,
            checksum_sha256=sha256_file(sidecar), source_command="review-package", status="present",
            linked_ids=({"protocol_model_id": result.protocol_model_id} if result.protocol_model_id else {}),
            metadata={"built_from": "review-map"},
        ))
        manifest.checksums[sidecar_rel] = sha256_file(sidecar)
        result.protocol_model_included = True
        result.protocol_model_path = rel(sidecar)
    writer.write_manifest(manifest, pkg_abs)
    writer.write_validation(validation, pkg_abs)
    writer.safe_write_text(pkg_abs / "README.md", build_reviewer_readme(manifest, validation))
    writer.safe_write_text(pkg_abs / "limitations.md", build_limitations_text(manifest, validation))
    if manifest.checksums:
        writer.write_checksums(manifest, pkg_abs)
    result.written = True

    if export_format:
        from . import export as export_mod

        export_result = export_mod.export_review_package(
            repo, package_root=pkg_abs, export_format=export_format,
            export_output=export_output, strict=strict,
        )
        result.export_status = export_result.status
        result.export_id = export_result.export_id
        result.export_file_count = len(export_result.included_files)
        result.export_size_bytes = int(export_result.metadata.get("size_bytes", 0) or 0)
        result.export_checksum_sha256 = str(export_result.metadata.get("export_checksum_sha256", ""))
        if export_result.status == "created":
            result.export_path = rel(pkg_abs / "exports" / Path(export_result.export_path).name)
            result.export_written = True
        else:
            result.errors.append(f"export not created: {export_result.status}")
    return result


def build_review_package_result_dict(result: ReviewPackageBuildResult) -> dict[str, object]:
    return {
        "command": COMMAND_NAME,
        "package_root": result.package_root,
        "manifest_path": result.manifest_path,
        "validation_path": result.validation_path,
        "readme_path": result.readme_path,
        "limitations_path": result.limitations_path,
        "checksums_path": result.checksums_path,
        "artifact_count": result.artifact_count,
        "validation_status": result.validation_status,
        "manual_review_required": result.manual_review_required,
        "ready_for_submission": result.ready_for_submission,
        "written": result.written,
        "no_write": result.no_write,
        "copied_artifacts": list(result.copied_artifacts),
        "warnings": list(result.warnings),
        "errors": list(result.errors),
        "export_requested": result.export_requested,
        "export_format": result.export_format,
        "export_path": result.export_path,
        "export_id": result.export_id,
        "export_status": result.export_status,
        "export_file_count": result.export_file_count,
        "export_size_bytes": result.export_size_bytes,
        "export_checksum_sha256": result.export_checksum_sha256,
        "export_written": result.export_written,
        "protocol_model_requested": result.protocol_model_requested,
        "protocol_model_included": result.protocol_model_included,
        "protocol_model_path": result.protocol_model_path,
        "protocol_model_id": result.protocol_model_id,
        "crossref_check_count": result.crossref_check_count,
        "crossref_warning_count": result.crossref_warning_count,
        "crossref_error_count": result.crossref_error_count,
    }
