"""Internal artifact collector for the review package layer (v3.6, additive).

Discovers existing local artifacts under ``.arkheionx/out/`` and turns them into
``ReviewPackageArtifact`` records with repo-relative and artifacts-root-relative
POSIX paths. It reads only file metadata (existence, size) -- never artifact
contents, never secrets -- writes nothing, and creates no directories. Missing
artifacts are recorded honestly as absent rather than fabricated.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath

from .ids import normalize_package_path, package_artifact_id
from .model import ReviewPackageArtifact

_ARTIFACT_EXTENSIONS = {".json", ".md", ".txt", ".mmd"}

# Globally-unique artifact filenames map directly to a kind regardless of dir.
_GLOBAL_NAMES = {
    "artifacts-index.json": "artifacts_index",
    "protocol-model.json": "protocol_model",
    "review-map.json": "review_map",
    "review-map.md": "review_map",
    "review-map.mmd": "review_map",
    "review-summary.md": "review_map_summary",
    "value-paths.json": "value_paths",
    "assumptions.json": "assumptions",
    "test-gaps.json": "test_gaps",
    "test-gap-map.json": "test_gaps",
    "test-gap-map.md": "test_gaps",
    "proof-plan.json": "proof_plan",
    "evidence-links.json": "evidence_links",
}

_SOURCE_COMMANDS = {
    "review_map": "review-map",
    "review_map_summary": "review-map",
    "review_map_targets": "review-map",
    "value_paths": "value-paths",
    "assumptions": "assumptions",
    "test_gaps": "test-gap-map",
    "proof_plan": "proof-plan",
    "evidence_links": "evidence-links",
    "artifacts_index": "validate-artifacts",
    "proof_receipt": "prove",
    "trace_receipt": "trace",
    "evidence_package": "evidence",
    "evidence_manifest": "evidence",
    "evidence_text": "evidence",
    "report_draft": "report",
    "report_text": "report",
    "protocol_model": "review-map",
    "local_validation_summary": "local-validate",
    "local_validation_run": "local-validate",
    "local_test_result": "local-validate",
    "local_trace_receipt": "local-validate",
    "local_validation_artifacts_index": "local-validate",
    "local_validation_checksums": "local-validate",
}

_SCHEMAS = {
    "review_map": "review-map.schema.json",
    "value_paths": "review-map.schema.json",
    "assumptions": "assumptions.schema.json",
    "test_gaps": "test-gap-map.schema.json",
    "evidence_package": "evidence.schema.json",
    "evidence_manifest": "evidence.schema.json",
    "report_draft": "report-draft.schema.json",
    "proof_receipt": "proof-artifact.schema.json",
    "trace_receipt": "trace.schema.json",
    "artifacts_index": "artifacts-index.schema.json",
}

_REQUIRED_KINDS = {"review_map", "evidence_links", "artifacts_index"}


def default_artifacts_root(repo_path: str | Path) -> Path:
    return Path(str(repo_path)) / ".arkheionx" / "out"


def to_repo_relative_path(path: str | Path, repo_path: str | Path) -> str:
    return _relativize(path, repo_path)


def to_artifacts_relative_path(path: str | Path, artifacts_root: str | Path) -> str:
    return _relativize(path, artifacts_root)


def _relativize(path: str | Path, base: str | Path) -> str:
    raw = normalize_package_path(path)
    root = normalize_package_path(base)
    if root and raw == root:
        return ""
    if root and raw.startswith(root + "/"):
        return raw[len(root) + 1:]
    try:
        rel = Path(str(path)).resolve().relative_to(Path(str(base)).resolve())
        return PurePosixPath(rel).as_posix()
    except (ValueError, OSError):
        return raw


def iter_artifact_files(artifacts_root: str | Path) -> list[Path]:
    root = Path(str(artifacts_root))
    if not root.is_dir():
        return []
    files = [
        p for p in root.rglob("*")
        if p.is_file()
        and p.relative_to(root).parts[0] != "review-package"
        and (
            p.suffix.lower() in _ARTIFACT_EXTENSIONS
            or (
                p.name == "SHA256SUMS"
                and p.relative_to(root).parts[0] in ("local-validation", "protocol-graph")
            )
        )
    ]
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def classify_artifact_path(path: str | Path, artifacts_root: str | Path | None = None) -> str:
    rel = to_artifacts_relative_path(path, artifacts_root) if artifacts_root is not None else normalize_package_path(path)
    parts = [p for p in rel.split("/") if p]
    if not parts:
        return "unknown"
    name = parts[-1]
    top = parts[0]
    if top == "proof":
        if name == "proof.json":
            return "proof_receipt"
        if name == "trace.json":
            return "trace_receipt"
    if top == "evidence":
        if name == "evidence.json":
            return "evidence_package"
        if name == "manifest.json":
            return "evidence_manifest"
        if name == "evidence.txt":
            return "evidence_text"
    if top in ("reports", "report"):
        if name == "report.json":
            return "report_draft"
        if name in ("report.md", "report.txt"):
            return "report_text"
    if top == "local-validation":
        if name == "summary.json":
            return "local_validation_summary"
        if name == "run.json":
            return "local_validation_run"
        if name == "artifacts-index.json":
            return "local_validation_artifacts_index"
        if name == "SHA256SUMS":
            return "local_validation_checksums"
        if len(parts) >= 2 and parts[1] == "results" and name.endswith(".json"):
            return "local_test_result"
        if len(parts) >= 2 and parts[1] == "traces" and name.endswith(".json"):
            return "local_trace_receipt"
        return "unknown"
    if top == "protocol-graph":
        # Optional protocol intelligence graph artifacts (v3.8). Classified before
        # the global-name fallback so that protocol-graph/artifacts-index.json is
        # never mistaken for the global artifacts_index, and the extension-less
        # protocol-graph/checksums/SHA256SUMS is classified, not ignored.
        if name == "graph.json":
            return "protocol_graph"
        if name == "coverage-summary.json":
            return "protocol_graph_coverage_summary"
        if name == "artifacts-index.json":
            return "protocol_graph_artifacts_index"
        if name == "SHA256SUMS":
            return "protocol_graph_checksums"
        if len(parts) >= 2 and parts[1] == "nodes" and name.endswith(".json"):
            return "protocol_graph_node"
        if len(parts) >= 2 and parts[1] == "edges" and name.endswith(".json"):
            return "protocol_graph_edge"
        if len(parts) >= 2 and parts[1] == "checks" and name.endswith(".json"):
            return "protocol_graph_check"
        return "unknown"
    return _GLOBAL_NAMES.get(name, "unknown")


def artifact_source_command(kind: str) -> str:
    return _SOURCE_COMMANDS.get(kind, "")


def artifact_schema_for_kind(kind: str) -> str:
    return _SCHEMAS.get(kind, "")


def is_required_artifact_kind(kind: str) -> bool:
    return kind in _REQUIRED_KINDS


def is_optional_artifact_kind(kind: str) -> bool:
    return not is_required_artifact_kind(kind)


def make_review_package_artifact(
    file_path: str | Path, repo_path: str | Path, artifacts_root: str | Path
) -> ReviewPackageArtifact:
    kind = classify_artifact_path(file_path, artifacts_root)
    relative_path = to_artifacts_relative_path(file_path, artifacts_root)
    repo_relative = to_repo_relative_path(file_path, repo_path)
    target = Path(str(file_path))
    exists = target.is_file()
    warnings: list[str] = []
    if kind == "unknown":
        warnings.append(f"unclassified artifact: {relative_path or repo_relative}")
    return ReviewPackageArtifact(
        artifact_id=package_artifact_id(kind, relative_path or repo_relative),
        kind=kind,
        path=repo_relative,
        relative_path=relative_path,
        exists=exists,
        checksum_sha256="",
        size_bytes=target.stat().st_size if exists else 0,
        schema=artifact_schema_for_kind(kind),
        source_command=artifact_source_command(kind),
        required=is_required_artifact_kind(kind),
        status="present" if exists else "missing",
        warnings=warnings,
        metadata={"artifact_root_relative": relative_path},
    )


def collect_review_package_artifacts(
    repo_path: str | Path, artifacts_root: str | Path | None = None
) -> list[ReviewPackageArtifact]:
    root = Path(str(artifacts_root)) if artifacts_root is not None else default_artifacts_root(repo_path)
    return [make_review_package_artifact(f, repo_path, root) for f in iter_artifact_files(root)]
