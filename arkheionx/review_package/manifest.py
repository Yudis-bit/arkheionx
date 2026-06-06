"""Internal review package manifest builder (v3.6, additive, internal-only).

Builds an in-memory ``ReviewPackageManifest`` from artifacts discovered by the
collector. It is deterministic (no timestamp, no randomness), records required
and optional artifact kinds honestly, never marks missing artifacts as present,
and writes nothing to disk. Checksums and strict validation are later v3.6 work.
"""
from __future__ import annotations

from pathlib import Path

from .collector import collect_review_package_artifacts
from .ids import package_slug, repo_fingerprint, review_package_id
from .model import (
    DEFAULT_REVIEW_PACKAGE_SAFETY_BOUNDARY,
    PACKAGE_DRAFT,
    ReviewPackageArtifact,
    ReviewPackageManifest,
    to_dict,
)

_REQUIRED_KINDS = ["artifacts_index", "evidence_links", "review_map"]
_OPTIONAL_KINDS = [
    "assumptions",
    "evidence_manifest",
    "evidence_package",
    "evidence_text",
    "local_test_result",
    "local_trace_receipt",
    "local_validation_artifacts_index",
    "local_validation_checksums",
    "local_validation_run",
    "local_validation_summary",
    "proof_plan",
    "proof_receipt",
    "protocol_graph",
    "protocol_graph_artifacts_index",
    "protocol_graph_check",
    "protocol_graph_checksums",
    "protocol_graph_coverage_summary",
    "protocol_graph_edge",
    "protocol_graph_node",
    "protocol_model",
    "report_draft",
    "report_text",
    "review_map_summary",
    "review_map_targets",
    "test_gaps",
    "trace_receipt",
    "unknown",
    "value_paths",
]

_LIMITATIONS = [
    "Local/static review-package draft only; not an audit.",
    "Manual review is required; ready_for_submission is false.",
    "Checksums and strict validation are added by later v3.6 work; not computed here.",
]


def default_required_artifact_kinds() -> list[str]:
    return list(_REQUIRED_KINDS)


def default_optional_artifact_kinds() -> list[str]:
    return list(_OPTIONAL_KINDS)


def _safe_version() -> str:
    try:
        from arkheionx.version import __version__

        return __version__
    except Exception:  # pragma: no cover - defensive only
        return ""


def _safe_milestone() -> str:
    try:
        from arkheionx.version import CURRENT_MILESTONE

        return CURRENT_MILESTONE
    except Exception:  # pragma: no cover - defensive only
        return ""


def _summarize(artifacts: list[ReviewPackageArtifact]) -> dict[str, object]:
    by_kind: dict[str, int] = {}
    for artifact in artifacts:
        by_kind[artifact.kind] = by_kind.get(artifact.kind, 0) + 1
    return {
        "total_artifacts": len(artifacts),
        "count_by_kind": dict(sorted(by_kind.items())),
        "required_present": sum(1 for a in artifacts if a.required and a.exists),
        "optional_present": sum(1 for a in artifacts if not a.required and a.exists),
        "manual_review_required": True,
    }


def summarize_manifest_artifacts(manifest: ReviewPackageManifest) -> dict[str, object]:
    return _summarize(list(manifest.included_artifacts))


def build_review_package_manifest(
    repo_path: str | Path,
    artifacts_root: str | Path | None = None,
    protocol_model_id: str = "",
    package_name: str = "",
) -> ReviewPackageManifest:
    artifacts = collect_review_package_artifacts(repo_path, artifacts_root)
    included = sorted(artifacts, key=lambda a: (a.relative_path, a.kind, a.artifact_id))
    fingerprint = repo_fingerprint(repo_path)
    package_id = review_package_id(
        protocol_model_id=protocol_model_id,
        artifact_ids=[a.artifact_id for a in included],
        repo_fingerprint=fingerprint,
    )
    name = package_name or f"review-package-{package_slug(Path(str(repo_path)).name or 'repo')}"
    return ReviewPackageManifest(
        package_id=package_id,
        package_name=name,
        arkheionx_version=_safe_version(),
        current_milestone=_safe_milestone(),
        repo_fingerprint=fingerprint,
        protocol_model_id=protocol_model_id,
        included_artifacts=included,
        required_artifacts=default_required_artifact_kinds(),
        optional_artifacts=default_optional_artifact_kinds(),
        validation_summary={"status": PACKAGE_DRAFT, "validated": False, **_summarize(included)},
        safety_boundary=dict(DEFAULT_REVIEW_PACKAGE_SAFETY_BOUNDARY),
        manual_review_required=True,
        ready_for_submission=False,
        limitations=list(_LIMITATIONS),
    )


def manifest_to_dict(manifest: ReviewPackageManifest) -> dict[str, object]:
    return to_dict(manifest)
