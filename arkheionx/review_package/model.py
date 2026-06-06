"""Internal review package workspace dataclasses (v3.6, additive, internal-only).

These dataclasses describe a local, static review package: a workspace, a package
manifest, per-artifact records, a validation result, and an export descriptor.
They are reviewer-handoff scaffolding only. They never assert confirmed
vulnerabilities, a final severity, an audit outcome, or submission readiness, and
they perform no RPC, live-chain, key-handling, or exploit behavior.

This module defines shapes only. It writes nothing to disk, adds no CLI command,
and changes no existing public artifact or schema. Artifact collection, manifest
building, checksums, validation, and export are later v3.6 work.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import PurePath

SCHEMA_VERSION = "0.1.0"

# Package readiness states. HUMAN_REVIEWED is intentionally not one of them and
# is never emitted automatically by the review package layer.
PACKAGE_DRAFT = "PACKAGE_DRAFT"
PACKAGE_PARTIAL = "PACKAGE_PARTIAL"
PACKAGE_READY_FOR_HUMAN_REVIEW = "PACKAGE_READY_FOR_HUMAN_REVIEW"
PACKAGE_INVALID = "PACKAGE_INVALID"
PACKAGE_EXPORT_READY = "PACKAGE_EXPORT_READY"

# Review packages are local/static review guidance only. This boundary records
# what a package must never do: it performs no RPC, holds no private keys, reads
# no seed phrases, makes no live-chain calls, broadcasts no transactions, runs no
# exploit automation, and never auto-submits. It never emits HUMAN_REVIEWED and
# never claims a confirmed vulnerability, a final severity, an audit-passed
# outcome, or bounty eligibility. Manual review is required and a package is not
# ready for submission.
DEFAULT_REVIEW_PACKAGE_SAFETY_BOUNDARY: dict[str, object] = {
    "local_static_only": True,
    "no_rpc": True,
    "no_private_keys": True,
    "no_seed_phrases": True,
    "no_live_chain_calls": True,
    "no_transaction_broadcasting": True,
    "no_exploit_automation": True,
    "no_auto_submit": True,
    "no_automatic_human_reviewed": True,
    "no_confirmed_vulnerabilities": True,
    "no_final_severity": True,
    "no_audit_passed_claim": True,
    "no_bounty_eligibility": True,
    "manual_review_required": True,
    "ready_for_submission": False,
}


@dataclass
class ReviewWorkspace:
    workspace_id: str
    repo_path: str
    artifacts_dir: str = ".arkheionx/out"
    package_root: str = ".arkheionx/out/review-package"
    package_id: str = ""
    manifest_path: str = ""
    validation_path: str = ""
    export_path: str = ""
    created_at: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    safety_boundary: dict[str, object] = field(default_factory=dict)


@dataclass
class ReviewPackageArtifact:
    artifact_id: str
    kind: str
    path: str
    relative_path: str = ""
    exists: bool = False
    checksum_sha256: str = ""
    size_bytes: int = 0
    schema: str = ""
    source_command: str = ""
    required: bool = False
    status: str = "unknown"
    linked_ids: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ReviewPackageManifest:
    manifest_version: str = "1"
    package_id: str = ""
    package_name: str = ""
    created_at: str = ""
    arkheionx_version: str = ""
    current_milestone: str = ""
    repo_fingerprint: str = ""
    protocol_model_id: str = ""
    included_artifacts: list[ReviewPackageArtifact] = field(default_factory=list)
    required_artifacts: list[str] = field(default_factory=list)
    optional_artifacts: list[str] = field(default_factory=list)
    checksums: dict[str, str] = field(default_factory=dict)
    validation_summary: dict[str, object] = field(default_factory=dict)
    safety_boundary: dict[str, object] = field(default_factory=dict)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    limitations: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ReviewPackageValidationResult:
    validation_id: str
    package_id: str
    status: str = PACKAGE_DRAFT
    checked_at: str = ""
    checks: list[dict[str, object]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    missing_required_artifacts: list[str] = field(default_factory=list)
    stale_artifacts: list[str] = field(default_factory=list)
    checksum_mismatches: list[str] = field(default_factory=list)
    schema_failures: list[str] = field(default_factory=list)
    safety_failures: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_human_review: bool = False
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ReviewPackageExport:
    export_id: str
    package_id: str
    export_path: str
    format: str = "zip"
    created_at: str = ""
    included_files: list[str] = field(default_factory=list)
    manifest_checksum: str = ""
    validation_checksum: str = ""
    status: str = "not_created"
    limitations: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


def to_dict(value: object) -> object:
    """Recursively convert a review-package dataclass/container to JSON-safe data.

    Converts dataclasses, lists/tuples, and dicts recursively; converts Path-like
    values to POSIX strings; preserves booleans and empty containers; does not
    mutate the source; and raises ``TypeError`` for unsupported objects.
    """

    if isinstance(value, bool) or value is None or isinstance(value, (str, int, float)):
        return value
    if isinstance(value, PurePath):
        return value.as_posix()
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: to_dict(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {str(key): to_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_dict(item) for item in value]
    raise TypeError(f"to_dict cannot serialize object of type {type(value).__name__}")
