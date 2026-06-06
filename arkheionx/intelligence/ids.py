"""Deterministic stable ID utilities for the internal protocol intelligence model.

IDs derive only from normalized structural inputs (repo-relative POSIX paths,
contract names, normalized signatures, and upstream IDs). They never use
timestamps, randomness, or process-specific ``hash()``, so the same source
target produces the same ID across runs. Each ID keeps a human-readable prefix
for debugging; display names and legacy slugs stay aliases, never primary joins.

This module is internal infrastructure. It performs no I/O beyond path
normalization and adds review-context identity only -- never vulnerability
confirmation, severity, or submission readiness.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath

_HASH_LEN = 12


def _digest(*parts: object) -> str:
    """Return a short, stable hex digest of a canonical JSON seed."""

    seed = json.dumps(parts, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:_HASH_LEN]


def slugify(text: str) -> str:
    """Lowercase hyphen slug used only as a human-readable ID hint."""

    return re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")


def normalize_path(path: str | Path, repo_path: str | Path = "") -> str:
    """Return a repo-relative POSIX path when possible, else a POSIX path."""

    raw = str(path or "").replace("\\", "/")
    if not raw:
        return ""
    if repo_path:
        try:
            return Path(raw).resolve().relative_to(Path(str(repo_path)).resolve()).as_posix()
        except (ValueError, OSError):
            pass
    return PurePosixPath(raw).as_posix()


def normalize_signature(signature: str) -> str:
    """Collapse redundant whitespace while preserving argument order and types."""

    return re.sub(r"\s+", " ", str(signature or "").strip())


def protocol_id(repo_path: str | Path) -> str:
    return f"protocol:{_digest(Path(str(repo_path)).name or str(repo_path))}"


def contract_id(path: str | Path, contract_name: str, repo_path: str | Path = "") -> str:
    return f"contract:{_digest(normalize_path(path, repo_path))}:{slugify(contract_name)}"


def function_id(contract_id_value: str, signature: str) -> str:
    hint = slugify(str(contract_id_value).split(":")[-1])
    return f"function:{hint}:{_digest(contract_id_value, normalize_signature(signature))}"


def value_path_id(entry_function_id: str = "", exit_function_id: str = "", label: str = "") -> str:
    return f"value-path:{_digest(entry_function_id, exit_function_id, label)}"


def assumption_id(assumption_type: str, function_id_value: str = "", seed: str = "") -> str:
    return f"assumption:{slugify(assumption_type)}:{_digest(assumption_type, function_id_value, seed)}"


def test_gap_id(function_id_value: str = "", scenario: str = "", seed: str = "") -> str:
    return f"test-gap:{_digest(function_id_value, scenario, seed)}"


def proof_suggestion_id(test_gap_id_value: str = "", function_id_value: str = "", seed: str = "") -> str:
    return f"proof-suggestion:{_digest(test_gap_id_value, function_id_value, seed)}"


def proof_receipt_id(function_id_value: str = "", seed: str = "") -> str:
    return f"proof-receipt:{_digest(function_id_value, seed)}"


def trace_receipt_id(proof_receipt_id_value: str = "", seed: str = "") -> str:
    return f"trace-receipt:{_digest(proof_receipt_id_value, seed)}"


def evidence_package_id(function_id_value: str = "", seed: str = "") -> str:
    return f"evidence:{_digest(function_id_value, seed)}"


def report_id(evidence_package_id_value: str = "", seed: str = "") -> str:
    return f"report:{_digest(evidence_package_id_value, seed)}"


def evidence_link_id(artifact_kind: str = "", function_id_value: str = "", seed: str = "") -> str:
    return f"evidence-link:{slugify(artifact_kind)}:{_digest(artifact_kind, function_id_value, seed)}"
