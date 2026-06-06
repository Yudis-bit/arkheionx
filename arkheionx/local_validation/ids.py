"""Deterministic ID and path utilities for the internal local validation layer.

These helpers mint stable, prefix-tagged identifiers for local validation runs,
test results, trace receipts, artifacts, and summaries. They follow the same
discipline as ``arkheionx.review_package.ids`` and ``arkheionx.intelligence.ids``:
a SHA-256 digest over a canonical JSON seed (sorted keys, compact separators), a
short lowercase-hex suffix, and a human-readable prefix. IDs never use
timestamps, randomness, or process ``hash()``; identical inputs always produce
the same ID across runs.

This module is internal infrastructure (v3.7, additive). It performs no
filesystem, network, git, subprocess, or RPC access, requires no path to exist,
calls no Foundry tool, and reads or stores no secret value.
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
    raise TypeError(f"unsupported local-validation id seed type: {type(value).__name__}")


def canonical_json_dumps(value: object) -> str:
    """Return canonical JSON for a seed (sorted keys, compact separators)."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=_json_default)


def short_hash(value: object, length: int = _HASH_LEN) -> str:
    """Return a stable lowercase SHA-256 hex digest of a canonical JSON seed."""

    if length <= 0:
        raise ValueError("length must be positive")
    return hashlib.sha256(canonical_json_dumps(value).encode("utf-8")).hexdigest()[:length]


def _looks_absolute(raw: str) -> bool:
    return raw.startswith("/") or bool(re.match(r"^[A-Za-z]:[\\/]", raw))


def normalize_id_path(path: str | Path, *, allow_absolute: bool = True) -> str:
    """Return a POSIX-style, separator-collapsed path. Existence is not required.

    When ``allow_absolute`` is false, a leading-slash or drive-letter absolute
    path raises ``ValueError`` (used for artifact-relative paths).
    """

    raw = str(path or "").replace("\\", "/")
    if not raw.strip():
        return ""
    if not allow_absolute and _looks_absolute(raw):
        raise ValueError("absolute path is not allowed for a relative artifact path")
    return PurePosixPath(raw).as_posix()


def slugify_token(value: str, *, max_length: int = 48, fallback: str = "unknown") -> str:
    """Lowercase, filename-safe dash slug; returns ``fallback`` when empty."""

    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    if max_length and max_length > 0:
        slug = slug[:max_length].strip("-")
    return slug or fallback


def _require(value: object, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def _require_slug(value: object, name: str) -> str:
    _require(value, name)
    return slugify_token(str(value))


def repo_fingerprint(repo_path: str | Path) -> str:
    """Return a deterministic, secret-free fingerprint of a repo path.

    Uses only the normalized path text; performs no git, network, or filesystem
    access and resolves no remote. The output is a bare hash, so no absolute
    path appears in it.
    """

    normalized = normalize_id_path(repo_path)
    if not normalized:
        raise ValueError("repo_path is required for repo_fingerprint")
    return short_hash(["repo", normalized])


def local_validation_run_id(tool: str, repo_fingerprint: str, command: str | list[str]) -> str:
    tool_slug = _require_slug(tool, "tool")
    repo_hash = _require(repo_fingerprint, "repo_fingerprint")
    command_list = [str(command)] if isinstance(command, str) else [str(part) for part in (command or [])]
    if not any(part.strip() for part in command_list):
        raise ValueError("command is required for local_validation_run_id")
    short = short_hash({"tool": tool_slug, "repo": repo_hash, "command": command_list})
    return f"local-validation-run:{tool_slug}:{repo_hash}:{short}"


def local_test_result_id(tool: str, test_name: str, run_id: str) -> str:
    tool_slug = _require_slug(tool, "tool")
    name = _require(test_name, "test_name")
    run = _require(run_id, "run_id")
    test_hash = short_hash(["test", name])
    short = short_hash({"tool": tool_slug, "test_name": name, "run_id": run})
    return f"local-test-result:{tool_slug}:{test_hash}:{short}"


def local_trace_receipt_id(tool: str, test_result_id: str, trace_seed: object) -> str:
    tool_slug = _require_slug(tool, "tool")
    result = _require(test_result_id, "test_result_id")
    if trace_seed is None or (isinstance(trace_seed, (str, bytes, list, tuple, dict, set)) and len(trace_seed) == 0):
        raise ValueError("trace_seed is required for local_trace_receipt_id")
    short = short_hash({"tool": tool_slug, "test_result_id": result, "trace_seed": trace_seed})
    return f"local-trace-receipt:{tool_slug}:{short}"


def local_validation_artifact_id(kind: str, relative_path: str | Path) -> str:
    kind_slug = _require_slug(kind, "kind")
    if not str(relative_path or "").strip():
        raise ValueError("relative_path is required for local_validation_artifact_id")
    normalized = normalize_id_path(relative_path, allow_absolute=False)
    path_hash = short_hash(["artifact", kind_slug, normalized])
    return f"local-validation-artifact:{kind_slug}:{path_hash}"


def local_validation_summary_id(repo_fingerprint: str, tool: str, artifact_ids: list[str]) -> str:
    repo_hash = _require(repo_fingerprint, "repo_fingerprint")
    tool_slug = _require_slug(tool, "tool")
    sorted_ids = sorted(str(a) for a in (artifact_ids or []))
    short = short_hash({"repo": repo_hash, "tool": tool_slug, "artifact_ids": sorted_ids})
    return f"local-validation-summary:{tool_slug}:{repo_hash}:{short}"
