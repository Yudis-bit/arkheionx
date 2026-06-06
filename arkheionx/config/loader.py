"""Stable JSON config loader used by Arkheionx scripts and package modules."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from arkheionx.core.files import load_json
from arkheionx.core.paths import repo_relative
from arkheionx.config.schema import ConfigValidationResult, load_config_file, normalize_config


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = load_json(path)
    return payload if isinstance(payload, dict) else {}


def resolve_config_path(path: Path | None, root: Path) -> Path | None:
    if path is None:
        return None
    if path.is_absolute():
        return path
    cwd_candidate = Path.cwd() / path
    root_candidate = root / path
    return cwd_candidate if cwd_candidate.exists() else root_candidate


def load_and_validate_config(path: Path | None, root: Path) -> ConfigValidationResult:
    config_path = resolve_config_path(path, root)
    if config_path is None or not config_path.exists():
        return normalize_config({}, source="")
    raw, error = load_config_file(config_path)
    source = repo_relative(config_path)
    if error:
        result = normalize_config({}, source=source)
        return ConfigValidationResult(False, [error], result.warnings, result.normalized_config, source)
    return normalize_config(raw, source=source)
