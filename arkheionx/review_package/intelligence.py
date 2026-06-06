"""Protocol Intelligence Model integration for review packages (v3.6, additive).

Includes a ``protocol-model.json`` sidecar in a review package when one already
exists locally or can be built additively from existing review-map output via
``arkheionx.intelligence``. The sidecar is local/static review context only: the
absolute ``repo_path`` is scrubbed, no timestamp is added, and the package build
never fails when a model is unavailable (absence is a warning, not an error).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from .collector import default_artifacts_root, to_repo_relative_path
from .writer import safe_write_json


def default_protocol_model_package_path(package_root: str | Path) -> Path:
    return Path(str(package_root)) / "artifacts" / "intelligence" / "protocol-model.json"


def find_existing_protocol_model_artifact(repo_path: str | Path, artifacts_root: str | Path | None = None) -> Path | None:
    root = Path(str(artifacts_root)) if artifacts_root is not None else default_artifacts_root(repo_path)
    for candidate in (root / "protocol-model.json", root / "review-map" / "protocol-model.json"):
        if candidate.is_file():
            return candidate
    return None


def load_review_map_payload(repo_path: str | Path, artifacts_root: str | Path | None = None) -> dict[str, object]:
    root = Path(str(artifacts_root)) if artifacts_root is not None else default_artifacts_root(repo_path)
    path = root / "review-map" / "review-map.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def protocol_model_to_package_dict(model: object) -> dict[str, object]:
    """Return a JSON-safe, package-safe model dict (absolute repo_path scrubbed)."""

    if hasattr(model, "to_dict"):
        data = model.to_dict()
    elif isinstance(model, dict):
        data = copy.deepcopy(model)
    else:
        raise TypeError(f"unsupported protocol model type: {type(model).__name__}")
    if isinstance(data, dict) and data.get("repo_path"):
        data["repo_path"] = ""  # never leak an absolute repo path into the package
    return data


def build_protocol_model_for_package(repo_path: str | Path, artifacts_root: str | Path | None = None) -> dict[str, object] | None:
    existing = find_existing_protocol_model_artifact(repo_path, artifacts_root)
    if existing is not None:
        try:
            data = json.loads(existing.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return protocol_model_to_package_dict(data)
        except (OSError, ValueError):
            pass
    payload = load_review_map_payload(repo_path, artifacts_root)
    if not payload:
        return None
    try:
        from arkheionx.intelligence.build import build_protocol_model_from_review_map

        return protocol_model_to_package_dict(build_protocol_model_from_review_map(payload, str(repo_path)))
    except Exception:  # pragma: no cover - defensive: never fail the package build
        return None


def write_protocol_model_sidecar(model: object, package_root: str | Path) -> Path:
    target = default_protocol_model_package_path(package_root)
    safe_write_json(target, protocol_model_to_package_dict(model) if not isinstance(model, dict) else model)
    return target


def include_protocol_model_sidecar(
    repo_path: str | Path,
    package_root: str | Path,
    artifacts_root: str | Path | None = None,
    *,
    no_write: bool = False,
) -> dict[str, object]:
    result: dict[str, object] = {
        "requested": True, "included": False, "in_memory": False,
        "path": "", "protocol_model_id": "", "warnings": [], "errors": [], "model_dict": None,
    }
    model_dict = build_protocol_model_for_package(repo_path, artifacts_root)
    if model_dict is None:
        result["warnings"] = ["protocol model not available (no review-map artifact to build from)"]
        return result
    result["in_memory"] = True
    result["protocol_model_id"] = str(model_dict.get("protocol_id", ""))
    result["model_dict"] = model_dict
    if no_write:
        return result
    path = write_protocol_model_sidecar(model_dict, package_root)
    result["included"] = True
    result["path"] = to_repo_relative_path(path, package_root)
    return result
