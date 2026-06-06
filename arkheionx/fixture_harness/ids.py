"""Deterministic ID and path utilities for the internal fixture harness layer.

These helpers mint stable, prefix-tagged identifiers for protocol fixtures,
fixture artifacts, fixture runs, fixture results, and fixture snapshots. They
follow the same discipline as ``arkheionx.local_validation.ids`` and
``arkheionx.intelligence.ids``: a SHA-256 digest over a canonical JSON seed
(sorted keys, compact separators), a short lowercase-hex suffix, and a
human-readable prefix. IDs never use timestamps, randomness, or process
``hash()``; identical inputs always produce the same ID across runs, regardless
of dict key order.

This module is internal infrastructure (v3.9, additive). It performs no
filesystem, network, git, subprocess, or RPC access, requires no path to exist,
depends on no Foundry tool or live chain, reads or stores no secret value, and
asserts no confirmed vulnerability, final severity, audit outcome, or submission
readiness. Importing it has no side effects.
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
    raise TypeError(f"unsupported fixture id seed type: {type(value).__name__}")


def canonical_fixture_seed(value: object) -> str:
    """Return canonical JSON for a seed (sorted keys, compact separators).

    The output is stable across dict key order. Unsupported (non-JSON-native,
    non-Path) objects raise ``TypeError``.
    """

    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=_json_default)


def short_fixture_hash(value: object, length: int = _HASH_LEN) -> str:
    """Return a stable lowercase SHA-256 hex digest of a canonical JSON seed."""

    if length <= 0:
        raise ValueError("length must be positive")
    return hashlib.sha256(canonical_fixture_seed(value).encode("utf-8")).hexdigest()[:length]


def slugify_fixture_token(value: str, *, max_length: int = 48, fallback: str = "unknown") -> str:
    """Lowercase, filename-safe dash slug; returns ``fallback`` when empty.

    Spaces, case, and punctuation collapse to single dashes, so a slug never
    contains a space or a backslash.
    """

    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    if max_length and max_length > 0:
        slug = slug[:max_length].strip("-")
    return slug or fallback


def _looks_absolute(raw: str) -> bool:
    return raw.startswith("/") or bool(re.match(r"^[A-Za-z]:[\\/]", raw))


def normalize_fixture_path(path: str | Path, *, allow_absolute: bool = False) -> str:
    """Return a normalized POSIX fixture path; existence is not required.

    An empty path returns ``""``. A backslash separator is rejected (fixtures use
    POSIX paths only). A leading-slash or drive-letter absolute path is rejected
    unless ``allow_absolute`` is true. A ``..`` traversal segment is always
    rejected. Each rejection raises ``ValueError``.
    """

    raw = str(path or "").strip()
    if not raw:
        return ""
    if "\\" in raw:
        raise ValueError("backslash is not allowed in a fixture path")
    if not allow_absolute and _looks_absolute(raw):
        raise ValueError("absolute path is not allowed for a fixture path")
    normalized = PurePosixPath(raw).as_posix()
    if ".." in normalized.split("/"):
        raise ValueError("path traversal is not allowed in a fixture path")
    return normalized


def _require(value: object, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def fixture_id(name: str, category: str, relative_path: str = "") -> str:
    """Deterministic fixture ID: ``fixture:<category>:<name>:<12hex>``.

    Requires a non-empty ``name`` and ``category``. The hash incorporates the
    category, the name, and the normalized relative path, so the ID changes with
    any of them.
    """

    name_text = _require(name, "name")
    category_text = _require(category, "category")
    normalized = normalize_fixture_path(relative_path)
    seed = {"category": category_text, "name": name_text, "relative_path": normalized}
    return f"fixture:{slugify_fixture_token(category_text)}:{slugify_fixture_token(name_text)}:{short_fixture_hash(seed)}"


def fixture_artifact_id(fixture_id: str, artifact_kind: str, relative_path: str = "") -> str:
    """Deterministic fixture artifact ID: ``fixture-artifact:<kind>:<12hex>``."""

    fid = _require(fixture_id, "fixture_id")
    kind = _require(artifact_kind, "artifact_kind")
    normalized = normalize_fixture_path(relative_path)
    seed = {"fixture_id": fid, "artifact_kind": kind, "relative_path": normalized}
    return f"fixture-artifact:{slugify_fixture_token(kind)}:{short_fixture_hash(seed)}"


def fixture_run_id(fixture_id: str, runner: str = "", inputs: dict[str, object] | None = None) -> str:
    """Deterministic fixture run ID: ``fixture-run:<runner>:<12hex>``.

    Requires a non-empty ``fixture_id``. ``runner`` is optional (an empty runner
    slugs to ``unknown``). ``inputs`` is canonicalized, so dict key order does not
    change the ID.
    """

    fid = _require(fixture_id, "fixture_id")
    runner_text = str(runner or "").strip()
    seed = {"fixture_id": fid, "runner": runner_text, "inputs": inputs or {}}
    return f"fixture-run:{slugify_fixture_token(runner_text)}:{short_fixture_hash(seed)}"


def fixture_result_id(run_id: str, result_kind: str, subject_id: str = "") -> str:
    """Deterministic fixture result ID: ``fixture-result:<kind>:<12hex>``."""

    run = _require(run_id, "run_id")
    kind = _require(result_kind, "result_kind")
    seed = {"run_id": run, "result_kind": kind, "subject_id": str(subject_id or "").strip()}
    return f"fixture-result:{slugify_fixture_token(kind)}:{short_fixture_hash(seed)}"


def fixture_snapshot_id(fixture_id: str, snapshot_kind: str, subject_ids: list[str] | None = None) -> str:
    """Deterministic fixture snapshot ID: ``fixture-snapshot:<kind>:<12hex>``.

    ``subject_ids`` are sorted before hashing, so subject order does not change
    the ID.
    """

    fid = _require(fixture_id, "fixture_id")
    kind = _require(snapshot_kind, "snapshot_kind")
    sorted_subjects = sorted(str(s) for s in (subject_ids or []))
    seed = {"fixture_id": fid, "snapshot_kind": kind, "subject_ids": sorted_subjects}
    return f"fixture-snapshot:{slugify_fixture_token(kind)}:{short_fixture_hash(seed)}"
