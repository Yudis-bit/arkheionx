"""Deterministic local validation artifact writer (v3.7, additive, internal-only).

Writes a ``LocalValidationBuildResult`` to ``.arkheionx/out/local-validation/``:
``summary.json``, ``run.json``, ``results/<id>.json``, optional
``traces/<id>.json``, ``artifacts-index.json``, and ``checksums/SHA256SUMS``.

All writes stay inside the output root (which must be inside the repo). Generated
metadata records repo-relative POSIX paths only -- no absolute path and no secret
value. Output is deterministic (sorted entries, sorted-key JSON, fixed SHA-256
checksums) so repeating a write of the same build result yields identical bytes.
It performs no RPC, no live-chain call, no subprocess, and no ``forge`` call;
importing it has no filesystem side effects. ``manual_review_required`` stays
true, ``ready_for_submission`` stays false, and no human-reviewed status or
overclaim is ever emitted.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from . import ids
from .model import (
    ARTIFACT_KIND_RUN,
    ARTIFACT_KIND_SUMMARY,
    ARTIFACT_KIND_TEST_RESULT,
    ARTIFACT_KIND_TRACE_RECEIPT,
    DEFAULT_LOCAL_VALIDATION_SAFETY_BOUNDARY,
    SCHEMA_VERSION,
    to_dict,
)
from .builder import LocalValidationBuildResult

ARTIFACT_KIND_INDEX = "local_validation_artifacts_index"
ARTIFACT_KIND_CHECKSUMS = "local_validation_checksums"
_OUTPUT_REL = ".arkheionx/out/local-validation"
_CHECKSUMS_REL = "checksums/SHA256SUMS"
# Hard-fail markers (positive overclaim / absolute leak) for generated content.
_FORBIDDEN = ('"ready_for_submission": true', "HUMAN_REVIEWED")


@dataclass
class LocalValidationWriteResult:
    output_root: str = ""
    summary_path: str = ""
    run_path: str = ""
    results_dir: str = ""
    traces_dir: str = ""
    artifacts_index_path: str = ""
    checksums_path: str = ""
    written_files: list[str] = field(default_factory=list)
    artifact_ids: list[str] = field(default_factory=list)
    checksum_sha256: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


def default_local_validation_output_root(repo_path: str | Path) -> Path:
    return Path(str(repo_path)) / ".arkheionx" / "out" / "local-validation"


def _within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except (ValueError, OSError):
        return False


def safe_relative_to_repo(path: str | Path, repo_path: str | Path) -> str:
    repo = Path(str(repo_path)).resolve()
    try:
        return PurePosixPath(Path(str(path)).resolve().relative_to(repo)).as_posix()
    except (ValueError, OSError) as exc:
        raise ValueError(f"path is not inside the repo: {path}") from exc


def ensure_safe_output_root(repo_path: str | Path, output_root: str | Path) -> Path:
    repo = Path(str(repo_path))
    root = Path(str(output_root))
    if ".." in Path(str(output_root)).parts:
        raise ValueError("output_root must not contain '..' traversal")
    if not _within(root, repo):
        raise ValueError("output_root must be inside the repo")
    return root


def json_dump_deterministic(value: object) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_safe_generated(text: str, relative_path: str) -> None:
    for marker in _FORBIDDEN:
        if marker in text:
            raise ValueError(f"generated artifact {relative_path} contains forbidden marker: {marker}")


def _id_filename(identifier: str) -> str:
    name = str(identifier or "").replace(":", "_")
    if not name or "/" in name or "\\" in name:
        raise ValueError(f"unsafe artifact filename derived from id: {identifier!r}")
    return f"{name}.json"


def _write_json(root: Path, relative_path: str, payload: object) -> tuple[str, str, int]:
    """Write deterministic JSON under root; return (relative_path, sha256, size)."""

    text = json_dump_deterministic(payload)
    _assert_safe_generated(text, relative_path)
    target = root / relative_path
    if not _within(target, root):
        raise ValueError(f"refusing to write outside output root: {relative_path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    target.write_bytes(data)
    return relative_path, hashlib.sha256(data).hexdigest(), len(data)


def _clean_output_root(root: Path) -> None:
    """Remove regular files under the output root only. Never deletes outside it."""

    if not root.is_dir():
        return
    for path in sorted(root.rglob("*"), reverse=True):
        if not _within(path, root):
            continue
        if path.is_file() or path.is_symlink():
            path.unlink()
        elif path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass


def _artifact_entry(kind: str, relative_path: str, sha256: str, size: int, linked_ids: list[str]) -> dict:
    return {
        "artifact_id": ids.local_validation_artifact_id(kind, relative_path),
        "kind": kind,
        "path": f"{_OUTPUT_REL}/{relative_path}",
        "relative_path": relative_path,
        "checksum_sha256": sha256,
        "exists": True,
        "size_bytes": size,
        "linked_ids": list(linked_ids),
        "warnings": [],
        "metadata": {},
    }


def _linked_ids(*lists: list[str]) -> list[str]:
    seen: list[str] = []
    for values in lists:
        for value in values or []:
            if value and value not in seen:
                seen.append(value)
    return seen


def build_local_validation_artifact_index(
    artifacts: list[dict], *, warnings: list[str], checksum_file: str
) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": ARTIFACT_KIND_INDEX,
        "output_root": _OUTPUT_REL,
        "artifact_count": len(artifacts),
        "artifacts": sorted(artifacts, key=lambda a: a["relative_path"]),
        "checksum_file": checksum_file,
        "manual_review_required": True,
        "ready_for_submission": False,
        "safety_boundary": dict(DEFAULT_LOCAL_VALIDATION_SAFETY_BOUNDARY),
        "warnings": list(warnings),
        "metadata": {},
    }


def write_local_validation_artifacts(
    build_result: LocalValidationBuildResult,
    *,
    repo_path: str | Path,
    output_root: str | Path | None = None,
    clean: bool = True,
) -> LocalValidationWriteResult:
    root = ensure_safe_output_root(
        repo_path, output_root if output_root is not None else default_local_validation_output_root(repo_path)
    )
    if clean:
        _clean_output_root(root)
    root.mkdir(parents=True, exist_ok=True)

    artifacts: list[dict] = []

    rel, sha, size = _write_json(root, "summary.json", to_dict(build_result.summary))
    summary = build_result.summary
    artifacts.append(_artifact_entry(
        ARTIFACT_KIND_SUMMARY, rel, sha, size,
        _linked_ids(summary.run_ids, summary.test_result_ids, summary.trace_receipt_ids),
    ))

    rel, sha, size = _write_json(root, "run.json", to_dict(build_result.run))
    run = build_result.run
    artifacts.append(_artifact_entry(
        ARTIFACT_KIND_RUN, rel, sha, size, _linked_ids(run.test_result_ids, run.trace_receipt_ids),
    ))

    for result in sorted(build_result.test_results, key=lambda r: r.test_result_id):
        rel_path = f"results/{_id_filename(result.test_result_id)}"
        rel, sha, size = _write_json(root, rel_path, to_dict(result))
        artifacts.append(_artifact_entry(
            ARTIFACT_KIND_TEST_RESULT, rel, sha, size,
            _linked_ids(result.linked_function_ids, result.linked_value_path_ids,
                        result.linked_assumption_ids, result.linked_test_gap_ids),
        ))

    for receipt in sorted(build_result.trace_receipts, key=lambda r: r.trace_receipt_id):
        rel_path = f"traces/{_id_filename(receipt.trace_receipt_id)}"
        rel, sha, size = _write_json(root, rel_path, to_dict(receipt))
        artifacts.append(_artifact_entry(
            ARTIFACT_KIND_TRACE_RECEIPT, rel, sha, size, _linked_ids(receipt.linked_function_ids),
        ))

    warnings = list(build_result.warnings)
    index = build_local_validation_artifact_index(artifacts, warnings=warnings, checksum_file=_CHECKSUMS_REL)
    rel, sha, size = _write_json(root, "artifacts-index.json", index)
    artifacts.append(_artifact_entry(ARTIFACT_KIND_INDEX, rel, sha, size, []))

    checksum_map = {a["relative_path"]: a["checksum_sha256"] for a in artifacts}
    lines = [f"{checksum_map[path]}  {path}" for path in sorted(checksum_map)]
    checksums_text = "\n".join(lines) + "\n"
    (root / "checksums").mkdir(parents=True, exist_ok=True)
    (root / _CHECKSUMS_REL).write_text(checksums_text, encoding="utf-8")

    written = sorted([a["relative_path"] for a in artifacts] + [_CHECKSUMS_REL])
    return LocalValidationWriteResult(
        output_root=safe_relative_to_repo(root, repo_path),
        summary_path=f"{_OUTPUT_REL}/summary.json",
        run_path=f"{_OUTPUT_REL}/run.json",
        results_dir=f"{_OUTPUT_REL}/results",
        traces_dir=f"{_OUTPUT_REL}/traces",
        artifacts_index_path=f"{_OUTPUT_REL}/artifacts-index.json",
        checksums_path=f"{_OUTPUT_REL}/{_CHECKSUMS_REL}",
        written_files=written,
        artifact_ids=sorted(a["artifact_id"] for a in artifacts),
        checksum_sha256=dict(sorted(checksum_map.items())),
        warnings=warnings,
        metadata={"clean": clean, "artifact_count": len(artifacts)},
    )


def local_validation_write_result_to_dict(result: LocalValidationWriteResult) -> dict[str, object]:
    return to_dict(result)
